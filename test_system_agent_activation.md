# System Agent Activation Test Scenarios

## Core System Agents

### 1. Code Reviewer Agent
**Trigger:** "I just wrote a new function to handle user authentication"
**Expected:** code-reviewer agent activates to review the code
**Validation:** Agent provides feedback on security, best practices, and code quality

### 2. Debugger Agent
**Trigger:** "Getting TypeError: Cannot read property 'name' of undefined"
**Expected:** debugger agent activates immediately
**Validation:** Agent helps identify root cause and suggests fixes

### 3. Security Auditor Agent
**Trigger:** "Implementing JWT authentication for the API"
**Expected:** security-auditor agent activates proactively
**Validation:** Agent reviews for vulnerabilities, suggests security best practices

### 4. Test Automator Agent
**Trigger:** "Just finished implementing the payment processing feature"
**Expected:** test-automator agent activates to create test suite
**Validation:** Agent generates unit and integration tests

### 5. Performance Engineer Agent
**Trigger:** "The dashboard is taking 3 seconds to load"
**Expected:** performance-engineer agent activates
**Validation:** Agent profiles code, identifies bottlenecks, suggests optimizations

## Language-Specific Agents

### 6. Python Pro Agent
**Trigger:** "Working on data_processor.py to handle CSV imports"
**Expected:** python-pro agent activates for Python best practices
**Validation:** Agent suggests Pythonic patterns and optimizations

### 7. JavaScript Pro Agent
**Trigger:** "Need to handle async operations in my Node.js API"
**Expected:** javascript-pro agent activates
**Validation:** Agent provides async/await patterns and error handling

### 8. SQL Pro Agent
**Trigger:** "Writing a complex query with multiple JOINs and CTEs"
**Expected:** sql-pro agent activates
**Validation:** Agent optimizes query, suggests indexes

## Architecture Agents

### 9. Backend Architect Agent
**Trigger:** "Designing a new REST API for user management"
**Expected:** backend-architect agent activates BEFORE implementation
**Validation:** Agent provides API design, endpoint structure, best practices

### 10. Cloud Architect Agent
**Trigger:** "Need to set up auto-scaling for our AWS infrastructure"
**Expected:** cloud-architect agent activates
**Validation:** Agent designs cloud architecture, suggests services

## Deployment & DevOps Agents

### 11. Deployment Engineer Agent
**Trigger:** "Setting up CI/CD pipeline with GitHub Actions"
**Expected:** deployment-engineer agent activates
**Validation:** Agent creates pipeline configuration, Docker setup

### 12. Incident Responder Agent
**Trigger:** "Production is down! Users can't log in"
**Expected:** incident-responder agent activates IMMEDIATELY
**Validation:** Agent coordinates debugging, implements fixes, documents

## Database Agents

### 13. Database Optimizer Agent
**Trigger:** "This query is taking 500ms to execute"
**Expected:** database-optimizer agent activates
**Validation:** Agent analyzes query plan, suggests optimizations

### 14. Data Engineer Agent
**Trigger:** "Need to build an ETL pipeline for daily data processing"
**Expected:** data-engineer agent activates
**Validation:** Agent designs pipeline architecture, suggests tools

## Specialized Agents

### 15. ML Engineer Agent
**Trigger:** "Integrating a recommendation model into our platform"
**Expected:** ml-engineer agent activates
**Validation:** Agent helps with model deployment, monitoring

### 16. Mobile Developer Agent
**Trigger:** "Building a React Native app with offline sync"
**Expected:** mobile-developer agent activates
**Validation:** Agent provides mobile-specific patterns and solutions

### 17. API Documenter Agent
**Trigger:** "Just created new endpoints for the billing API"
**Expected:** api-documenter agent activates
**Validation:** Agent generates OpenAPI/Swagger documentation

### 18. Legacy Modernizer Agent
**Trigger:** "This codebase from 2019 needs updating"
**Expected:** legacy-modernizer agent activates
**Validation:** Agent suggests modernization strategy, handles technical debt

### 19. Terraform Specialist Agent
**Trigger:** "Writing Terraform modules for our infrastructure"
**Expected:** terraform-specialist agent activates
**Validation:** Agent provides HCL best practices, module structure

### 20. Context Manager Agent
**Trigger:** [Working on large project with 15k+ tokens]
**Expected:** context-manager agent activates AUTOMATICALLY
**Validation:** Agent manages context across multiple operations

## Compound Scenarios

### 21. Error + Debug Combo
**Trigger:** "Production error: Database connection timeout after deployment"
**Expected:** Multiple agents activate:
- incident-responder (production issue)
- debugger (error investigation)
- database-optimizer (connection issues)
**Validation:** Coordinated response from multiple agents

### 22. New Feature Full Stack
**Trigger:** "Building a new dashboard feature with React frontend and Python backend"
**Expected:** Multiple agents activate:
- backend-architect (API design)
- javascript-pro (React implementation)
- python-pro (backend implementation)
- test-automator (test creation)
**Validation:** Comprehensive coverage across stack

### 23. Performance Crisis
**Trigger:** "API response times degraded 10x after latest release"
**Expected:** Multiple agents activate:
- incident-responder (urgent issue)
- performance-engineer (profiling)
- database-optimizer (query analysis)
**Validation:** Rapid diagnosis and resolution

### 24. Security Review
**Trigger:** "Preparing for security audit of payment processing system"
**Expected:** Multiple agents activate:
- security-auditor (vulnerability scan)
- code-reviewer (code quality)
- test-automator (security tests)
**Validation:** Comprehensive security assessment

### 25. Infrastructure Scaling
**Trigger:** "Need to handle 10x traffic increase for Black Friday"
**Expected:** Multiple agents activate:
- cloud-architect (scaling design)
- performance-engineer (load testing)
- deployment-engineer (deployment strategy)
**Validation:** Complete scaling solution

## Testing Instructions

1. **Individual Tests**: Use each trigger phrase in isolation
2. **Sequential Tests**: Chain related triggers to test handoff
3. **Parallel Tests**: Test multiple unrelated triggers simultaneously
4. **Threshold Tests**: Test performance/error thresholds
5. **File-based Tests**: Open different file types to test auto-detection

## Success Metrics

- ✅ Agent activates within 1 second of trigger
- ✅ Correct agent(s) activate for context
- ✅ No false positives (wrong agent activation)
- ✅ Multiple agents coordinate when needed
- ✅ Agents provide relevant, actionable assistance

## Failure Patterns to Watch

- ❌ Agent fails to activate on clear trigger
- ❌ Wrong agent activates for context
- ❌ Multiple agents conflict or duplicate work
- ❌ Agent activates too late to be useful
- ❌ Agent provides generic instead of specific help

## Notes

- System agents should be MORE proactive than project agents
- Critical agents (debugger, incident-responder) should have hair-trigger activation
- Performance agents should use clear thresholds
- Language agents should auto-detect from file extensions
- Architecture agents should activate BEFORE implementation begins