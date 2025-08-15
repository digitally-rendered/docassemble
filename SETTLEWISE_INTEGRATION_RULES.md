# SettleWise-Docassemble Integration Rules & Patterns

## Overview
This document provides comprehensive rules, patterns, and code samples for integrating SettleWise's legal workflow orchestration platform with Docassemble's interview engine using **Option 2: Progressive Integration with Workflow Orchestration**.

## Architecture Pattern

### Core Principle
- **SettleWise**: Workflow orchestration, case management, payments, modern UX
- **Docassemble**: Legal interviews, document generation, complex legal logic
- **Integration**: Bidirectional API communication with embedded interview experience

## 1. Database Schema Rules

### 1.1 SettleWise Core Models

```python
# models/core.py
from django.db import models
import uuid

class Case(models.Model):
    """Primary case management entity"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    case_type = models.CharField(max_length=50, choices=[
        ('divorce', 'Divorce'),
        ('custody', 'Custody & Access'),
        ('support', 'Support'),
        ('property', 'Property Division')
    ])
    jurisdiction = models.CharField(max_length=50, default='ontario-canada')
    status = models.CharField(max_length=50, default='created')
    current_workflow_step = models.CharField(max_length=100, blank=True)
    
    # Financial tracking
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=50, default='pending')
    
    # Document tracking
    documents_generated = models.JSONField(default=list)
    court_filing_status = models.CharField(max_length=50, default='not_filed')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cases'

class WorkflowExecution(models.Model):
    """Tracks workflow execution state"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    workflow_definition_id = models.CharField(max_length=100)
    current_node_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=[
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    
    # State management
    execution_context = models.JSONField(default=dict)  # All collected data
    completed_nodes = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class InterviewSession(models.Model):
    """Tracks docassemble interview sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workflow_execution = models.ForeignKey(WorkflowExecution, on_delete=models.CASCADE)
    node_id = models.CharField(max_length=100)  # Workflow node this session belongs to
    
    # Docassemble integration
    docassemble_session_id = models.CharField(max_length=100)
    interview_filename = models.CharField(max_length=200)
    status = models.CharField(max_length=50, choices=[
        ('created', 'Created'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned')
    ])
    
    # Data synchronization
    input_variables = models.JSONField(default=dict)  # Data sent to docassemble
    output_variables = models.JSONField(default=dict)  # Data received from docassemble
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

### 1.2 Workflow Definition Models

```python
# models/workflow.py
class WorkflowTemplate(models.Model):
    """Defines reusable workflow templates"""
    id = models.CharField(max_length=100, primary_key=True)  # e.g., 'ontario-divorce-simple'
    name = models.CharField(max_length=200)
    jurisdiction = models.CharField(max_length=50)
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Workflow definition
    nodes = models.JSONField()  # Complete workflow definition
    metadata = models.JSONField(default=dict)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WorkflowNode(models.Model):
    """Individual workflow nodes for reusability"""
    id = models.CharField(max_length=100, primary_key=True)
    template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE)
    
    node_type = models.CharField(max_length=50, choices=[
        ('interview', 'Docassemble Interview'),
        ('decision', 'Business Logic Decision'),
        ('document', 'Document Generation'),
        ('payment', 'Payment Processing'),
        ('integration', 'External Integration'),
        ('parallel', 'Parallel Execution')
    ])
    
    # Node configuration
    configuration = models.JSONField()
    data_mapping = models.JSONField(default=dict)  # Input/output mapping
    
    # Flow control
    next_nodes = models.JSONField(default=list)
    conditions = models.JSONField(default=dict)
```

## 2. API Integration Patterns

### 2.1 SettleWise → Docassemble Communication

```python
# services/docassemble_service.py
import requests
import logging
from typing import Dict, Any, Optional

class DocassembleIntegrationService:
    """Service for SettleWise → Docassemble communication"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    async def start_interview(
        self, 
        interview_filename: str,
        input_variables: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start a new docassemble interview with pre-populated data"""
        
        # Flatten nested variables for docassemble format
        da_variables = self._flatten_variables(input_variables)
        
        # Add workflow context for callback tracking
        da_variables.update({
            'settlewise_case_id': workflow_context['case_id'],
            'settlewise_node_id': workflow_context['node_id'],
            'settlewise_callback_url': f"{workflow_context['callback_base_url']}/continue"
        })
        
        try:
            response = self.session.get(f"{self.base_url}/api/session/new", params={
                'i': interview_filename,
                **da_variables
            })
            response.raise_for_status()
            
            data = response.json()
            session_id = data['session']
            
            # Store session mapping
            await self._store_session_mapping(session_id, workflow_context)
            
            return {
                'session_id': session_id,
                'interview_url': f"{self.base_url}/interview?session={session_id}",
                'encrypted': data.get('encrypted', False)
            }
            
        except requests.RequestException as e:
            logging.error(f"Failed to start docassemble interview: {e}")
            raise IntegrationError(f"Could not start interview: {e}")
    
    async def get_interview_status(self, session_id: str) -> Dict[str, Any]:
        """Check if interview is complete and get current state"""
        try:
            response = self.session.get(f"{self.base_url}/api/session/question", params={
                'session': session_id
            })
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'is_complete': data.get('questionType') == 'response',
                'current_question': data.get('question'),
                'variables': data.get('variables', {}),
                'progress': self._calculate_interview_progress(data)
            }
            
        except requests.RequestException as e:
            logging.error(f"Failed to get interview status: {e}")
            raise IntegrationError(f"Could not check interview status: {e}")
    
    async def get_completed_variables(self, session_id: str) -> Dict[str, Any]:
        """Extract all variables from completed interview"""
        try:
            response = self.session.get(f"{self.base_url}/api/session/variables", params={
                'session': session_id
            })
            response.raise_for_status()
            
            variables = response.json()
            
            # Unflatten variables back to nested structure
            return self._unflatten_variables(variables)
            
        except requests.RequestException as e:
            logging.error(f"Failed to get interview variables: {e}")
            raise IntegrationError(f"Could not retrieve interview data: {e}")
    
    def _flatten_variables(self, data: Dict[str, Any], prefix: str = '') -> Dict[str, str]:
        """Convert nested objects to docassemble variable format"""
        flattened = {}
        
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_variables(value, full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        flattened.update(self._flatten_variables(item, f"{full_key}[{i}]"))
                    else:
                        flattened[f"{full_key}[{i}]"] = str(item)
            else:
                flattened[full_key] = str(value) if value is not None else ''
        
        return flattened
    
    def _unflatten_variables(self, flattened: Dict[str, Any]) -> Dict[str, Any]:
        """Convert docassemble flat variables back to nested structure"""
        result = {}
        
        for key, value in flattened.items():
            keys = key.split('.')
            current = result
            
            for i, k in enumerate(keys[:-1]):
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
        
        return result
    
    async def _store_session_mapping(self, session_id: str, context: Dict[str, Any]):
        """Store mapping between docassemble session and SettleWise workflow"""
        # This would store in Redis or database for quick lookup
        pass
    
    def _calculate_interview_progress(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate interview completion progress"""
        # Implement progress calculation based on interview structure
        return {
            'percentage': 75,  # Example
            'current_step': 'Financial Information',
            'total_steps': 8
        }

class IntegrationError(Exception):
    """Custom exception for integration errors"""
    pass
```

### 2.2 Docassemble → SettleWise Webhooks

```python
# api/webhooks.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/docassemble", tags=["docassemble"])

class InterviewStartedWebhook(BaseModel):
    session_id: str
    interview_filename: str
    case_id: str
    node_id: str
    user_id: Optional[str] = None

class InterviewCompletedWebhook(BaseModel):
    session_id: str
    interview_filename: str
    case_id: str
    node_id: str
    variables: Dict[str, Any]
    completion_time: str

class InterviewProgressWebhook(BaseModel):
    session_id: str
    case_id: str
    node_id: str
    progress_percentage: float
    current_step: str

@router.post("/interview/started")
async def handle_interview_started(webhook: InterviewStartedWebhook):
    """Called when docassemble interview begins"""
    try:
        # Get workflow execution
        execution = await WorkflowExecution.objects.aget(
            case_id=webhook.case_id
        )
        
        # Update interview session
        session = await InterviewSession.objects.acreate(
            workflow_execution=execution,
            node_id=webhook.node_id,
            docassemble_session_id=webhook.session_id,
            interview_filename=webhook.interview_filename,
            status='active'
        )
        
        # Update case status
        case = execution.case
        case.status = 'interview_in_progress'
        case.current_workflow_step = webhook.node_id
        await case.asave()
        
        # Send notifications
        await notification_service.notify_interview_started(
            case.id, webhook.interview_filename
        )
        
        return {"status": "success", "session_id": session.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview/completed")
async def handle_interview_completed(webhook: InterviewCompletedWebhook):
    """Called when docassemble interview finishes"""
    try:
        # Update interview session
        session = await InterviewSession.objects.aget(
            docassemble_session_id=webhook.session_id
        )
        session.status = 'completed'
        session.output_variables = webhook.variables
        session.completed_at = timezone.now()
        await session.asave()
        
        # Continue workflow execution
        workflow_engine = WorkflowEngine()
        next_steps = await workflow_engine.continue_after_interview(
            session.workflow_execution.id,
            webhook.node_id,
            webhook.variables
        )
        
        return {"status": "success", "next_steps": next_steps}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview/progress")
async def handle_interview_progress(webhook: InterviewProgressWebhook):
    """Called periodically to update interview progress"""
    try:
        # Update case with current progress
        case = await Case.objects.aget(id=webhook.case_id)
        
        # Store progress in case metadata
        if not case.metadata:
            case.metadata = {}
        
        case.metadata['interview_progress'] = {
            'percentage': webhook.progress_percentage,
            'current_step': webhook.current_step,
            'node_id': webhook.node_id,
            'updated_at': timezone.now().isoformat()
        }
        await case.asave()
        
        # Send real-time updates to frontend
        await websocket_service.broadcast_progress_update(
            case.client_id, webhook.progress_percentage
        )
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 3. Workflow Orchestration Engine

### 3.1 Core Workflow Engine

```python
# services/workflow_engine.py
from typing import Dict, Any, List, Optional
import asyncio
import logging

class WorkflowEngine:
    """Core workflow orchestration engine"""
    
    def __init__(self):
        self.docassemble_service = DocassembleIntegrationService()
        self.document_service = DocumentGenerationService()
        self.payment_service = PaymentService()
    
    async def start_workflow(
        self, 
        workflow_template_id: str,
        case_id: str,
        initial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Start a new workflow execution"""
        
        # Load workflow template
        template = await WorkflowTemplate.objects.aget(id=workflow_template_id)
        
        # Create workflow execution
        execution = await WorkflowExecution.objects.acreate(
            case_id=case_id,
            workflow_definition_id=workflow_template_id,
            current_node_id=template.nodes[0]['id'],
            status='running',
            execution_context=initial_data or {}
        )
        
        # Start with first node
        first_node = template.nodes[0]
        result = await self.execute_node(execution, first_node)
        
        return {
            'execution_id': execution.id,
            'current_step': result
        }
    
    async def execute_node(
        self, 
        execution: WorkflowExecution, 
        node: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow node"""
        
        logging.info(f"Executing node {node['id']} of type {node['type']}")
        
        # Update current node
        execution.current_node_id = node['id']
        await execution.asave()
        
        # Route to appropriate executor
        if node['type'] == 'interview':
            return await self.execute_interview_node(execution, node)
        elif node['type'] == 'decision':
            return await self.execute_decision_node(execution, node)
        elif node['type'] == 'document':
            return await self.execute_document_node(execution, node)
        elif node['type'] == 'payment':
            return await self.execute_payment_node(execution, node)
        elif node['type'] == 'parallel':
            return await self.execute_parallel_node(execution, node)
        else:
            raise WorkflowError(f"Unknown node type: {node['type']}")
    
    async def execute_interview_node(
        self, 
        execution: WorkflowExecution, 
        node: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a docassemble interview node"""
        
        # Prepare input data
        input_data = self.map_data(
            execution.execution_context,
            node.get('data_mapping', {}).get('inputs', [])
        )
        
        # Start interview
        interview_result = await self.docassemble_service.start_interview(
            interview_filename=node['interview_path'],
            input_variables=input_data,
            workflow_context={
                'case_id': execution.case_id,
                'node_id': node['id'],
                'execution_id': execution.id,
                'callback_base_url': settings.SETTLEWISE_BASE_URL
            }
        )
        
        return {
            'type': 'interview_required',
            'session_id': interview_result['session_id'],
            'interview_url': interview_result['interview_url'],
            'node_id': node['id'],
            'title': node.get('title', 'Complete Interview')
        }
    
    async def continue_after_interview(
        self, 
        execution_id: str, 
        completed_node_id: str, 
        interview_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Continue workflow after interview completion"""
        
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        
        # Find the completed node
        template = await WorkflowTemplate.objects.aget(
            id=execution.workflow_definition_id
        )
        completed_node = next(
            (node for node in template.nodes if node['id'] == completed_node_id),
            None
        )
        
        if not completed_node:
            raise WorkflowError(f"Node {completed_node_id} not found")
        
        # Extract and merge output data
        output_data = self.map_data(
            interview_data,
            completed_node.get('data_mapping', {}).get('outputs', [])
        )
        
        # Merge into execution context
        execution.execution_context.update(output_data)
        execution.completed_nodes.append(completed_node_id)
        await execution.asave()
        
        # Determine next node
        next_node_id = completed_node.get('next')
        if next_node_id:
            next_node = next(
                (node for node in template.nodes if node['id'] == next_node_id),
                None
            )
            
            if next_node:
                return await self.execute_node(execution, next_node)
        
        # Workflow complete
        execution.status = 'completed'
        await execution.asave()
        
        return {'type': 'workflow_complete', 'execution_id': execution.id}
    
    async def execute_decision_node(
        self, 
        execution: WorkflowExecution, 
        node: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a business logic decision node"""
        
        condition = node['condition']
        context = execution.execution_context
        
        # Evaluate condition (simple implementation)
        result = self.evaluate_condition(condition, context)
        
        # Choose next path
        next_node_id = node['true_path'] if result else node['false_path']
        
        # Find and execute next node
        template = await WorkflowTemplate.objects.aget(
            id=execution.workflow_definition_id
        )
        next_node = next(
            (n for n in template.nodes if n['id'] == next_node_id),
            None
        )
        
        if next_node:
            return await self.execute_node(execution, next_node)
        else:
            raise WorkflowError(f"Next node {next_node_id} not found")
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a conditional expression safely"""
        # This would use a safe expression evaluator
        # For now, simple string replacement
        
        # Example: "client.has_children === true"
        try:
            # Replace context variables
            for key, value in context.items():
                condition = condition.replace(key, str(value))
            
            # Safe evaluation (would use a proper expression parser in production)
            if '===' in condition:
                left, right = condition.split('===')
                return left.strip() == right.strip()
            elif '>' in condition:
                left, right = condition.split('>')
                return float(left.strip()) > float(right.strip())
            # Add more operators as needed
            
            return False
            
        except Exception as e:
            logging.error(f"Error evaluating condition {condition}: {e}")
            return False
    
    def map_data(self, source: Dict[str, Any], mapping: List[str]) -> Dict[str, Any]:
        """Map data from source using field mapping"""
        if not mapping:
            return source
        
        mapped = {}
        for field_path in mapping:
            value = source
            for key in field_path.split('.'):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            
            if value is not None:
                mapped[field_path] = value
        
        return mapped

class WorkflowError(Exception):
    """Workflow execution error"""
    pass
```

## 4. React Integration Components

### 4.1 Workflow Executor Component

```tsx
// components/WorkflowExecutor.tsx
import React, { useState, useEffect } from 'react';
import { WorkflowStep, WorkflowExecution } from '../types/workflow';
import { InterviewFrame } from './InterviewFrame';
import { DocumentGeneration } from './DocumentGeneration';
import { PaymentFlow } from './PaymentFlow';
import { ProgressIndicator } from './ProgressIndicator';

interface WorkflowExecutorProps {
  caseId: string;
  workflowTemplateId: string;
  onComplete?: (result: any) => void;
}

export const WorkflowExecutor: React.FC<WorkflowExecutorProps> = ({
  caseId,
  workflowTemplateId,
  onComplete
}) => {
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [currentStep, setCurrentStep] = useState<WorkflowStep | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    startWorkflow();
  }, [caseId, workflowTemplateId]);

  const startWorkflow = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/workflow/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          workflow_template_id: workflowTemplateId
        })
      });
      
      if (!response.ok) throw new Error('Failed to start workflow');
      
      const result = await response.json();
      setExecution(result.execution);
      setCurrentStep(result.current_step);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleStepComplete = async (stepResult: any) => {
    try {
      setLoading(true);
      
      // Continue workflow based on step type
      let response;
      
      if (currentStep?.type === 'interview') {
        response = await fetch('/api/workflow/continue-after-interview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            execution_id: execution?.id,
            node_id: currentStep.node_id,
            interview_data: stepResult
          })
        });
      } else {
        response = await fetch('/api/workflow/continue', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            execution_id: execution?.id,
            step_result: stepResult
          })
        });
      }
      
      if (!response.ok) throw new Error('Failed to continue workflow');
      
      const result = await response.json();
      
      if (result.type === 'workflow_complete') {
        onComplete?.(result);
      } else {
        setCurrentStep(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to continue');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="workflow-loading">
        <div className="spinner" />
        <p>Processing your request...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="workflow-error">
        <h3>Workflow Error</h3>
        <p>{error}</p>
        <button onClick={startWorkflow}>Retry</button>
      </div>
    );
  }

  if (!execution || !currentStep) {
    return <div>No workflow step available</div>;
  }

  return (
    <div className="workflow-executor">
      <div className="workflow-header">
        <h2>Family Law Application Process</h2>
        <ProgressIndicator 
          execution={execution}
          currentStep={currentStep}
        />
      </div>

      <div className="workflow-content">
        {currentStep.type === 'interview' && (
          <InterviewFrame
            step={currentStep}
            onComplete={handleStepComplete}
            caseId={caseId}
          />
        )}
        
        {currentStep.type === 'document_generation' && (
          <DocumentGeneration
            step={currentStep}
            onComplete={handleStepComplete}
          />
        )}
        
        {currentStep.type === 'payment' && (
          <PaymentFlow
            step={currentStep}
            onComplete={handleStepComplete}
            caseId={caseId}
          />
        )}
      </div>

      <div className="workflow-controls">
        <button 
          className="secondary"
          onClick={() => saveDraft(execution.id)}
        >
          Save & Continue Later
        </button>
        
        <button 
          className="tertiary"
          onClick={() => requestHelp(caseId)}
        >
          Get Legal Help
        </button>
      </div>
    </div>
  );
};

const saveDraft = async (executionId: string) => {
  // Save current progress
  await fetch(`/api/workflow/save/${executionId}`, {
    method: 'POST'
  });
};

const requestHelp = async (caseId: string) => {
  // Trigger help request flow
  window.open(`/help/request?case_id=${caseId}`, '_blank');
};
```

### 4.2 Interview Frame Component

```tsx
// components/InterviewFrame.tsx
import React, { useState, useEffect, useRef } from 'react';
import { WorkflowStep } from '../types/workflow';

interface InterviewFrameProps {
  step: WorkflowStep;
  onComplete: (data: any) => void;
  caseId: string;
}

export const InterviewFrame: React.FC<InterviewFrameProps> = ({
  step,
  onComplete,
  caseId
}) => {
  const [interviewUrl, setInterviewUrl] = useState<string>('');
  const [progress, setProgress] = useState(0);
  const [currentStepName, setCurrentStepName] = useState('');
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (step.interview_url) {
      setInterviewUrl(step.interview_url);
      setupProgressMonitoring();
    }
  }, [step]);

  const setupProgressMonitoring = () => {
    // Set up WebSocket connection for progress updates
    const ws = new WebSocket(`/ws/interview-progress/${caseId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'progress_update') {
        setProgress(data.percentage);
        setCurrentStepName(data.current_step);
      } else if (data.type === 'interview_complete') {
        onComplete(data.interview_data);
      }
    };

    return () => ws.close();
  };

  const handleIframeLoad = () => {
    // Interview loaded successfully
    const iframe = iframeRef.current;
    if (iframe) {
      // Setup iframe message handling for completion detection
      window.addEventListener('message', handleInterviewMessage);
    }
  };

  const handleInterviewMessage = (event: MessageEvent) => {
    // Handle messages from docassemble iframe
    if (event.data.type === 'docassemble_complete') {
      onComplete(event.data.variables);
    }
  };

  return (
    <div className="interview-frame-container">
      <div className="interview-header">
        <h3>{step.title || 'Complete Interview'}</h3>
        <div className="progress-info">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="progress-text">
            {progress}% Complete
            {currentStepName && ` - ${currentStepName}`}
          </span>
        </div>
      </div>

      <div className="interview-iframe-wrapper">
        {interviewUrl ? (
          <iframe
            ref={iframeRef}
            src={interviewUrl}
            className="docassemble-interview"
            title="Legal Interview"
            onLoad={handleIframeLoad}
            allow="geolocation; microphone; camera"
          />
        ) : (
          <div className="interview-loading">
            <p>Loading interview...</p>
          </div>
        )}
      </div>

      <div className="interview-help">
        <details>
          <summary>Need help with this step?</summary>
          <div className="help-content">
            <p>This interview will collect information needed for your legal documents.</p>
            <ul>
              <li>All information is kept confidential</li>
              <li>You can save and return later at any time</li>
              <li>Help tooltips are available throughout</li>
            </ul>
            <button onClick={() => requestLegalHelp(caseId)}>
              Speak with Legal Expert
            </button>
          </div>
        </details>
      </div>
    </div>
  );
};

const requestLegalHelp = (caseId: string) => {
  // Open legal help modal/page
  window.open(`/legal-help?case_id=${caseId}`, '_blank');
};
```

## 5. Docassemble Integration Extensions

### 5.1 Enhanced Interview Template

```yaml
# ontario-family-law/form-8a-divorce-with-settlewise.yml
---
include:
  - docassemble.settlewise:integration.yml
  - ontario-family-law:ontario-family-law-common.yml
---
metadata:
  title: Ontario Divorce Application (Form 8A) - SettleWise Integration
  short title: Divorce Application
  description: Complete Form 8A divorce application with SettleWise workflow integration
  authors:
    - name: SettleWise Legal Team
  revision_date: 2024-01-15
---
objects:
  - sw: SettleWiseIntegration
  - applicant: Individual
  - respondent: Individual
  - marriage: Marriage
  - children: DAList.using(object_type=Individual)
---
mandatory: True
code: |
  # Initialize SettleWise integration
  sw.initialize_from_context()
  
  # Set up progress tracking
  sw.set_total_steps(8)
  
  # Validate that we have minimum required data
  if not sw.has_required_context():
    sw.request_context_data()
  
  # Pre-populate from SettleWise if available
  if sw.has_context_data():
    sw.populate_interview_objects()
  
  # Main interview flow
  interview_introduction
  sw.update_progress(1, "Introduction completed")
  
  court_information_section
  sw.update_progress(2, "Court information collected")
  
  parties_information_section  
  sw.update_progress(3, "Party information collected")
  
  marriage_information_section
  sw.update_progress(4, "Marriage details collected")
  
  children_information_section
  sw.update_progress(5, "Children information collected")
  
  claims_and_orders_section
  sw.update_progress(6, "Claims specified")
  
  service_information_section
  sw.update_progress(7, "Service details collected")
  
  final_review_section
  sw.update_progress(8, "Review completed")
  
  # Generate document and complete workflow
  generate_form_8a
  sw.complete_interview()
---
# Introduction with SettleWise branding
question: |
  Welcome to Your Divorce Application
subquestion: |
  % if sw.case_id:
  **Case ID:** ${ sw.case_id }
  % endif
  
  This interview will guide you through completing Form 8A - Application (Divorce) 
  for Ontario Superior Court of Justice.
  
  **What we'll collect:**
  - Court and filing information
  - Information about you and your spouse
  - Details about your marriage
  - Information about any children
  - What orders you're requesting
  - How you'll serve your spouse
  
  **Estimated time:** 20-30 minutes
  
  % if sw.has_saved_progress():
  **Previous Progress Found:** We've restored your previous answers. 
  You can review and continue from where you left off.
  % endif
field: interview_introduction
datatype: checkboxes
choices:
  - I'm ready to begin: ready
minlength: 1
---
# Court information with smart defaults
question: |
  Court Information
fields:
  - Court level: court_info.level
    default: superior
    choices:
      - Superior Court of Justice (recommended for divorce): superior
      - Other court level: other
    help: |
      Divorce applications must be filed in Superior Court of Justice.
  - Court location: court_info.location
    datatype: combobox
    choices: ${ sw.get_ontario_court_locations() }
    help: |
      Choose the court closest to where you or your spouse lives.
  - Existing court file number: court_info.file_number
    required: False
    help: |
      Only fill this if you're adding to an existing family court case.
validation code: |
  if court_info.level != 'superior':
    validation_error("Divorce applications must be filed in Superior Court of Justice.")
---
# Enhanced parties information with SettleWise validation
question: |
  Your Information (Applicant)
subquestion: |
  Please provide your current legal information as it should appear on court documents.
fields:
  - First name: applicant.name.first
    validate: sw.validate_name_field
  - Last name: applicant.name.last  
    validate: sw.validate_name_field
  - Address: applicant.address.address
    address autocomplete: True
  - City: applicant.address.city
  - Postal code: applicant.address.zip
    validate: sw.validate_ontario_postal_code
  - Phone number: applicant.phone_number
    validate: sw.validate_canadian_phone
  - Email: applicant.email
    datatype: email
    validate: sw.validate_email_deliverability
---
# Marriage information with date validation
question: |
  Marriage Information
fields:
  - Date of marriage: marriage.date
    datatype: date
    max: ${ today() }
    validate: sw.validate_marriage_date
  - Place of marriage: marriage.place
    help: |
      Include city, province/state, and country
  - Ground for divorce: marriage.divorce_ground
    choices:
      - Separation for one year or more: separation
      - Adultery: adultery  
      - Physical or mental cruelty: cruelty
  - Date of separation: marriage.separation_date
    datatype: date
    max: ${ today() }
    validate: sw.validate_separation_date
validation code: |
  # Cross-validate marriage and separation dates
  sw.validate_marriage_timeline(marriage.date, marriage.separation_date)
---
# Children section with privacy protection
question: |
  Children Information
subquestion: |
  % if children.number() > 0:
  **Current children listed:** ${ children.number() }
  % else:
  Do you have children who are affected by this divorce?
  % endif
  
  **Privacy Note:** Children's information is protected. Only initials will 
  appear on public court documents.
yesno: children.there_are_any
---
question: |
  Child ${ children[i].ordinal() } Information
fields:
  - First name: children[i].name.first
    validate: sw.validate_name_field
  - Last name: children[i].name.last
    validate: sw.validate_name_field
  - Date of birth: children[i].birthdate
    datatype: date
    max: ${ today() }
    validate: sw.validate_child_birthdate
  - Lives with: children[i].lives_with
    choices:
      - Applicant: applicant
      - Respondent: respondent
      - Both parents (shared): shared
      - Other person: other
  - Birth province: children[i].birth_province
    default: Ontario
    code: |
      sw.get_canadian_provinces()
validation code: |
  # Calculate age and validate
  children[i].age = sw.calculate_age(children[i].birthdate)
  if children[i].age >= 18:
    validation_error("This form is for children under 18. Adult children require different procedures.")
---
# Claims section with intelligent defaults
question: |
  What orders are you requesting?
subquestion: |
  Select all that apply. The court can grant these orders if appropriate.
fields:
  - Orders requested: claims_requested
    datatype: checkboxes
    choices:
      - Divorce: divorce
      - Custody of children: custody
      - Access/parenting time: access
      - Child support: child_support
      - Spousal support: spousal_support
      - Division of property: property_division
      - Division of debts: debt_division
      - Exclusive possession of home: exclusive_possession
      - Other relief: other_relief
    minlength: 1
    default: |
      % if marriage.divorce_ground:
      divorce
      % endif
      % if children.number() > 0:
      custody, child_support
      % endif
validation messages:
  minlength: You must request at least one order.
---
# Service information with smart suggestions
question: |
  How will you serve your spouse?
subquestion: |
  You must serve your spouse with copies of all court documents.
  
  % if respondent.address.address:
  **Spouse's address on file:** ${ respondent.address.on_one_line() }
  % endif
field: service_method
choices:
  - Personal service (recommended): personal
  - Service by mail (if address confirmed): mail
  - Service through spouse's lawyer: lawyer
  - Alternative service (requires court order): alternative
help: |
  **Personal service** is most reliable and involves hand-delivering documents.
  **Service by mail** requires confirmed address and spouse likely to accept mail.
---
# Final review with SettleWise integration
question: |
  Review Your Application
subquestion: |
  Please review all information before generating your Form 8A.
  
  **Case Summary:**
  - **Applicant:** ${ applicant.name.full() }
  - **Respondent:** ${ respondent.name.full() }
  - **Marriage Date:** ${ format_date(marriage.date) }
  - **Separation Date:** ${ format_date(marriage.separation_date) }
  - **Ground:** ${ marriage.divorce_ground.title() }
  
  % if children.number() > 0:
  **Children:** ${ children.number() } child${'ren' if children.number() != 1 else ''}
  % for child in children:
  - ${ child.name.full() }, born ${ format_date(child.birthdate) } (age ${ child.age })
  % endfor
  % endif
  
  **Orders Requested:**
  % for claim in claims_requested:
  - ${ claim.replace('_', ' ').title() }
  % endfor
  
  **Service Method:** ${ service_method.title() }
  
  % if sw.estimated_court_fees():
  **Estimated Filing Fees:** ${ currency(sw.estimated_court_fees()) }
  % endif
field: final_review_confirmed
datatype: yesnoradio
---
# Document generation with SettleWise integration
event: generate_form_8a
question: |
  Your Form 8A is Ready
subquestion: |
  Your Ontario divorce application has been completed and is ready for filing.
  
  **Next Steps:**
  1. Download and review your completed form
  2. File with the court and pay filing fees
  3. Serve your spouse within required timeframes
  4. Complete additional forms if required
  
  % if sw.case_id:
  **SettleWise Case ID:** ${ sw.case_id }
  
  Your case progress and documents are saved in your SettleWise account.
  % endif
  
  [Download Form 8A](${ sw.generate_document_url('form_8a') })
  
  % if sw.has_next_workflow_step():
  [Continue to Next Step](${ sw.get_next_step_url() })
  % endif
buttons:
  - Return to SettleWise Dashboard: ${ sw.get_dashboard_url() }
  - Start New Application: restart
---
# SettleWise integration completion
code: |
  # Send completion data back to SettleWise
  completion_data = {
    'court_info': {
      'level': court_info.level,
      'location': court_info.location,
      'file_number': court_info.get('file_number', '')
    },
    'applicant': sw.serialize_individual(applicant),
    'respondent': sw.serialize_individual(respondent),
    'marriage': {
      'date': marriage.date.isoformat(),
      'place': marriage.place,
      'divorce_ground': marriage.divorce_ground,
      'separation_date': marriage.separation_date.isoformat()
    },
    'children': [sw.serialize_individual(child, protect_privacy=True) for child in children],
    'claims_requested': claims_requested,
    'service_method': service_method,
    'interview_completed_at': current_datetime().isoformat()
  }
  
  sw.send_completion_webhook(completion_data)
  sw.trigger_document_generation('form_8a', completion_data)
```

### 5.2 SettleWise Integration Module

```python
# docassemble.settlewise/integration.py
from docassemble.base import *
import requests
import json
from datetime import datetime, date
import logging

class SettleWiseIntegration:
    """Main integration class for SettleWise workflow orchestration"""
    
    def __init__(self):
        self.case_id = None
        self.node_id = None
        self.execution_id = None
        self.api_base = get_config('settlewise_api_base')
        self.api_key = get_config('settlewise_api_key')
        self.total_steps = 8
        self.current_step = 0
        
    def initialize_from_context(self):
        """Initialize from docassemble URL parameters"""
        self.case_id = url_args.get('settlewise_case_id')
        self.node_id = url_args.get('settlewise_node_id') 
        self.execution_id = url_args.get('settlewise_execution_id')
        
        if self.case_id:
            self.send_interview_started()
    
    def has_required_context(self):
        """Check if we have minimum required SettleWise context"""
        return bool(self.case_id and self.node_id)
    
    def populate_interview_objects(self):
        """Pre-populate interview objects from SettleWise case data"""
        if not self.case_id:
            return
            
        try:
            case_data = self.fetch_case_data()
            
            if case_data:
                # Populate applicant information
                if 'applicant' in case_data:
                    self.populate_individual_from_data('applicant', case_data['applicant'])
                
                # Populate respondent information  
                if 'respondent' in case_data:
                    self.populate_individual_from_data('respondent', case_data['respondent'])
                
                # Populate children information
                if 'children' in case_data:
                    self.populate_children_from_data(case_data['children'])
                
                log(f"Pre-populated interview data from SettleWise case {self.case_id}")
                
        except Exception as e:
            log(f"Error pre-populating from SettleWise: {e}")
    
    def fetch_case_data(self):
        """Fetch case data from SettleWise API"""
        try:
            response = requests.get(
                f"{self.api_base}/api/cases/{self.case_id}/data",
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log(f"Failed to fetch case data: {e}")
            return None
    
    def update_progress(self, step_number, step_description):
        """Update progress in SettleWise"""
        self.current_step = step_number
        
        if not self.case_id:
            return
        
        try:
            percentage = int((step_number / self.total_steps) * 100)
            
            requests.post(
                f"{self.api_base}/api/docassemble/interview/progress",
                json={
                    'case_id': self.case_id,
                    'node_id': self.node_id,
                    'session_id': session_id,
                    'progress_percentage': percentage,
                    'current_step': step_description,
                    'updated_at': datetime.now().isoformat()
                },
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            
        except Exception as e:
            log(f"Failed to update progress: {e}")
    
    def complete_interview(self):
        """Send completion notification to SettleWise"""
        if not self.case_id:
            return
            
        try:
            completion_data = self.gather_completion_data()
            
            response = requests.post(
                f"{self.api_base}/api/docassemble/interview/completed",
                json={
                    'case_id': self.case_id,
                    'node_id': self.node_id,
                    'session_id': session_id,
                    'interview_filename': interview_metadata().get('filename'),
                    'variables': completion_data,
                    'completion_time': datetime.now().isoformat()
                },
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            
            response.raise_for_status()
            log(f"Interview completion sent to SettleWise for case {self.case_id}")
            
        except Exception as e:
            log(f"Failed to send completion notification: {e}")
    
    def send_interview_started(self):
        """Notify SettleWise that interview has started"""
        try:
            requests.post(
                f"{self.api_base}/api/docassemble/interview/started",
                json={
                    'case_id': self.case_id,
                    'node_id': self.node_id,
                    'session_id': session_id,
                    'interview_filename': interview_metadata().get('filename'),
                    'user_id': user_info().get('id') if not user_info().anonymous else None
                },
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
        except Exception as e:
            log(f"Failed to send interview started notification: {e}")
    
    def validate_ontario_postal_code(self, postal_code):
        """Validate Ontario postal codes"""
        import re
        
        if not postal_code:
            return False
            
        # Clean and format
        clean_postal = re.sub(r'[^A-Za-z0-9]', '', postal_code.upper())
        
        # Ontario postal codes start with K, L, M, N, or P
        ontario_prefixes = ['K', 'L', 'M', 'N', 'P']
        
        if len(clean_postal) != 6:
            validation_error("Postal code must be 6 characters (e.g., K1A0A6)")
        
        if clean_postal[0] not in ontario_prefixes:
            validation_error("Please enter a valid Ontario postal code")
            
        if not re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', clean_postal):
            validation_error("Invalid postal code format (e.g., K1A 0A6)")
        
        # Format with space
        formatted = clean_postal[:3] + ' ' + clean_postal[3:]
        return formatted
    
    def validate_canadian_phone(self, phone):
        """Validate Canadian phone numbers"""
        import re
        
        digits = re.sub(r'[^0-9]', '', phone)
        
        if len(digits) == 10:
            # Format as (XXX) XXX-XXXX
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # Format as +1 (XXX) XXX-XXXX  
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            validation_error("Please enter a valid 10-digit phone number")
    
    def calculate_age(self, birth_date):
        """Calculate age from birth date"""
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def serialize_individual(self, individual, protect_privacy=False):
        """Convert individual object to serializable format"""
        data = {
            'name': {
                'first': individual.name.first,
                'last': individual.name.last if not protect_privacy else individual.name.last[0] + '.',
                'full': individual.name.full() if not protect_privacy else f"{individual.name.first} {individual.name.last[0]}."
            },
            'address': {
                'address': individual.address.address,
                'city': individual.address.city,
                'province': individual.address.state,
                'postal_code': individual.address.zip,
                'full': individual.address.on_one_line()
            }
        }
        
        if hasattr(individual, 'phone_number'):
            data['phone'] = individual.phone_number
            
        if hasattr(individual, 'email'):
            data['email'] = individual.email
            
        if hasattr(individual, 'birthdate'):
            data['birth_date'] = individual.birthdate.isoformat()
            data['age'] = self.calculate_age(individual.birthdate)
        
        return data
    
    def get_dashboard_url(self):
        """Get URL to return to SettleWise dashboard"""
        if self.case_id:
            return f"{self.api_base}/cases/{self.case_id}/dashboard"
        return f"{self.api_base}/dashboard"
    
    def get_next_step_url(self):
        """Get URL for next workflow step"""
        if self.case_id:
            return f"{self.api_base}/cases/{self.case_id}/continue"
        return self.get_dashboard_url()
        
    def generate_document_url(self, document_type):
        """Generate URL for document download"""
        return url_action('download_document', document_type=document_type)

# Global SettleWise integration instance
sw = SettleWiseIntegration()
```

## 6. Security and Privacy Rules

### 6.1 Data Protection Patterns

```python
# security/privacy.py
from cryptography.fernet import Fernet
import hashlib
import logging

class PrivacyProtectionService:
    """Handles privacy protection for sensitive legal data"""
    
    def __init__(self):
        self.encryption_key = settings.ENCRYPTION_KEY
        self.cipher_suite = Fernet(self.encryption_key)
    
    def protect_children_data(self, children_list, protection_level='standard'):
        """Apply privacy protection to children's information"""
        protected = []
        
        for child in children_list:
            if protection_level == 'high':
                protected_child = {
                    'first_name': child.get('first_name'),
                    'last_initial': child.get('last_name', '')[:1] + '.',
                    'age': child.get('age'),
                    'birth_year': child.get('birth_date', '')[:4] if child.get('birth_date') else None
                }
            else:
                # Standard protection
                protected_child = {
                    'initials': f"{child.get('first_name', '')[:1]}.{child.get('last_name', '')[:1]}.",
                    'age': child.get('age'),
                    'order': len(protected) + 1  # Child 1, Child 2, etc.
                }
            
            protected.append(protected_child)
        
        return protected
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive personal information"""
        if isinstance(data, dict):
            encrypted = {}
            sensitive_fields = ['sin', 'social_security', 'bank_account', 'credit_card']
            
            for key, value in data.items():
                if key.lower() in sensitive_fields and value:
                    encrypted[key] = self.cipher_suite.encrypt(str(value).encode()).decode()
                else:
                    encrypted[key] = value
            return encrypted
        
        return data
    
    def audit_data_access(self, user_id, case_id, data_type, action):
        """Log data access for audit trail"""
        logging.info(f"DATA_ACCESS: user={user_id} case={case_id} type={data_type} action={action}")

class DocumentSecurityService:
    """Handles document security and access control"""
    
    def apply_court_redactions(self, document_data):
        """Apply court-required redactions to documents"""
        # Redact children's full names in public documents
        if 'children' in document_data:
            document_data['children'] = self._redact_children_names(document_data['children'])
        
        # Redact sensitive financial information
        if 'financial_info' in document_data:
            document_data['financial_info'] = self._redact_financial_details(document_data['financial_info'])
        
        return document_data
    
    def _redact_children_names(self, children_list):
        """Replace children's names with initials or Child 1, Child 2, etc."""
        redacted = []
        for i, child in enumerate(children_list):
            redacted_child = child.copy()
            redacted_child['display_name'] = f"Child {i + 1}"
            redacted_child['initials'] = f"{child.get('first_name', '')[:1]}.{child.get('last_name', '')[:1]}."
            # Remove full name from public documents
            del redacted_child['first_name']
            del redacted_child['last_name']
            redacted.append(redacted_child)
        return redacted
```

## 7. Testing Patterns

### 7.1 Integration Testing

```python
# tests/test_workflow_integration.py
import pytest
from unittest.mock import Mock, patch
from services.workflow_engine import WorkflowEngine
from services.docassemble_service import DocassembleIntegrationService

@pytest.fixture
def mock_docassemble_service():
    service = Mock(spec=DocassembleIntegrationService)
    service.start_interview.return_value = {
        'session_id': 'test-session-123',
        'interview_url': 'http://da.test/interview?session=test-session-123'
    }
    return service

@pytest.fixture
def sample_workflow_template():
    return {
        'id': 'ontario-divorce-simple',
        'nodes': [
            {
                'id': 'basic_info',
                'type': 'interview',
                'interview_path': 'ontario-family-law/form-8a-divorce.yml',
                'title': 'Basic Information',
                'data_mapping': {
                    'inputs': ['case_type', 'jurisdiction'],
                    'outputs': ['applicant', 'respondent', 'marriage_info']
                },
                'next': 'document_generation'
            },
            {
                'id': 'document_generation',
                'type': 'document',
                'documents': ['form_8a'],
                'next': None
            }
        ]
    }

@pytest.mark.asyncio
async def test_start_workflow_with_interview_node(
    mock_docassemble_service,
    sample_workflow_template
):
    """Test starting workflow with interview node"""
    
    # Setup
    engine = WorkflowEngine()
    engine.docassemble_service = mock_docassemble_service
    
    case_id = 'test-case-123'
    initial_data = {
        'case_type': 'divorce',
        'jurisdiction': 'ontario-canada'
    }
    
    # Mock database calls
    with patch('models.WorkflowTemplate.objects.aget') as mock_get_template, \
         patch('models.WorkflowExecution.objects.acreate') as mock_create_execution:
        
        mock_get_template.return_value = type('MockTemplate', (), sample_workflow_template)
        mock_execution = Mock()
        mock_execution.id = 'exec-123'
        mock_create_execution.return_value = mock_execution
        
        # Execute
        result = await engine.start_workflow(
            'ontario-divorce-simple',
            case_id,
            initial_data
        )
        
        # Verify
        assert result['execution_id'] == 'exec-123'
        assert result['current_step']['type'] == 'interview_required'
        assert 'session_id' in result['current_step']
        
        # Verify docassemble service was called correctly
        mock_docassemble_service.start_interview.assert_called_once()
        call_args = mock_docassemble_service.start_interview.call_args
        assert call_args[1]['interview_filename'] == 'ontario-family-law/form-8a-divorce.yml'
        assert 'case_type' in call_args[1]['input_variables']

@pytest.mark.asyncio 
async def test_continue_workflow_after_interview():
    """Test continuing workflow after interview completion"""
    
    engine = WorkflowEngine()
    
    # Mock completed interview data
    interview_data = {
        'applicant': {
            'name': {'first': 'John', 'last': 'Doe'},
            'address': {'city': 'Toronto', 'postal_code': 'M5G 1E6'}
        },
        'respondent': {
            'name': {'first': 'Jane', 'last': 'Doe'}  
        },
        'marriage_info': {
            'date': '2010-06-15',
            'place': 'Toronto, Ontario'
        }
    }
    
    # Test continuation logic
    with patch('models.WorkflowExecution.objects.aget') as mock_get_execution:
        mock_execution = Mock()
        mock_execution.execution_context = {}
        mock_execution.completed_nodes = []
        
        result = await engine.continue_after_interview(
            'exec-123',
            'basic_info', 
            interview_data
        )
        
        # Verify data was merged
        assert 'applicant' in mock_execution.execution_context
        assert 'basic_info' in mock_execution.completed_nodes

@pytest.mark.integration
def test_docassemble_api_integration():
    """Integration test with actual docassemble instance"""
    
    service = DocassembleIntegrationService(
        base_url='http://localhost:80',
        api_key='test-api-key'
    )
    
    # Test data flattening
    nested_data = {
        'applicant': {
            'name': {'first': 'John', 'last': 'Doe'},
            'address': {'city': 'Toronto'}
        }
    }
    
    flattened = service._flatten_variables(nested_data)
    
    expected = {
        'applicant.name.first': 'John',
        'applicant.name.last': 'Doe', 
        'applicant.address.city': 'Toronto'
    }
    
    assert flattened == expected
    
    # Test unflattening
    unflattened = service._unflatten_variables(flattened)
    assert unflattened == nested_data

class TestWorkflowIntegrationE2E:
    """End-to-end integration tests"""
    
    @pytest.mark.e2e
    def test_complete_divorce_workflow(self):
        """Test complete divorce workflow from start to finish"""
        # This would test the entire workflow:
        # 1. Start workflow
        # 2. Complete interview  
        # 3. Generate documents
        # 4. Handle completion
        pass
```

## Conclusion

This rules file provides a comprehensive foundation for integrating SettleWise with Docassemble using the Progressive Integration pattern. Key benefits:

1. **Seamless User Experience**: Modern React UI with embedded docassemble interviews
2. **Workflow Orchestration**: Complex legal processes managed as structured workflows  
3. **Data Synchronization**: Bidirectional data flow between systems
4. **Privacy Protection**: Built-in privacy controls for sensitive family law data
5. **Extensible Architecture**: Easy to add new interview types and workflow nodes

The patterns shown here enable you to build a comprehensive legal platform that leverages docassemble's strengths while providing modern UX and business capabilities through SettleWise.