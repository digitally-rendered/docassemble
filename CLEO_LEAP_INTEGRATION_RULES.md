# SettleWise Integration Rules: Cleo & Leap Platform Integration

## Overview
This document provides comprehensive architectural rules and implementation patterns for integrating SettleWise's legal workflow orchestration engine with both Cleo and Leap Law Practice Management platforms using hexagonal architecture principles.

## Core Integration Architecture

### Hexagonal Architecture Pattern

The integration follows the Ports and Adapters (Hexagonal) architecture to maintain clean separation between:
- **Domain Layer**: Core workflow orchestration logic
- **Application Layer**: Use cases for platform integration
- **Infrastructure Layer**: Platform-specific adapters (Cleo, Leap)

```typescript
// Domain Layer - Core Integration Entities
interface WorkflowContext {
  readonly workflowId: WorkflowId;
  readonly platform: Platform;
  readonly integrationMode: IntegrationMode;
  readonly contextData: PlatformContextData;
}

interface PlatformContextData {
  readonly matterId?: string;
  readonly clientId?: string;
  readonly userId: string;
  readonly firmId: string;
  readonly customFields: Record<string, unknown>;
}

enum Platform {
  CLEO = 'cleo',
  LEAP = 'leap',
  STANDALONE = 'standalone'
}

enum IntegrationMode {
  EMBEDDED = 'embedded',
  STANDALONE = 'standalone',
  API_SYNC = 'api_sync'
}
```

### Port Definitions (Interfaces)

```typescript
// Primary Ports (Application → Domain)
interface WorkflowOrchestrator {
  startWorkflow(context: WorkflowContext, workflowType: string): Promise<WorkflowExecution>;
  continueWorkflow(executionId: string, stepResult: StepResult): Promise<WorkflowExecution>;
  pauseWorkflow(executionId: string): Promise<void>;
  completeWorkflow(executionId: string): Promise<CompletionResult>;
}

interface PlatformDataSync {
  syncFromPlatform(platform: Platform, externalId: string): Promise<SyncResult>;
  syncToPlatform(platform: Platform, data: WorkflowData): Promise<SyncResult>;
  establishBidirectionalSync(platform: Platform, mapping: FieldMapping): Promise<void>;
}

// Secondary Ports (Domain → Infrastructure)
interface PlatformAdapter {
  authenticate(credentials: PlatformCredentials): Promise<AuthResult>;
  fetchMatterData(matterId: string): Promise<MatterData>;
  uploadDocument(matterId: string, document: GeneratedDocument): Promise<DocumentResult>;
  createBillingEntry(matterId: string, billing: BillingData): Promise<BillingResult>;
  registerWebhook(event: string, callbackUrl: string): Promise<WebhookResult>;
}

interface DocumentGenerationPort {
  generateDocument(template: string, data: InterviewData): Promise<GeneratedDocument>;
  getDocumentStatus(sessionId: string): Promise<DocumentStatus>;
}

interface AuthenticationPort {
  createUnifiedSession(platformUser: PlatformUser): Promise<UnifiedSession>;
  validateSession(token: string): Promise<SessionValidation>;
  refreshSession(refreshToken: string): Promise<AuthResult>;
}
```

## Adapter Implementations

### 1. Cleo Platform Adapter

```typescript
// Infrastructure Layer - Cleo Adapter
class CleoAdapter implements PlatformAdapter {
  private readonly apiClient: CleoAPIClient;
  private readonly authService: CleoAuthService;

  constructor(
    private readonly config: CleoConfiguration,
    private readonly logger: Logger
  ) {
    this.apiClient = new CleoAPIClient(config);
    this.authService = new CleoAuthService(config);
  }

  async authenticate(credentials: PlatformCredentials): Promise<AuthResult> {
    try {
      const tokenResponse = await this.authService.exchangeCredentials(credentials);
      
      return AuthResult.success({
        accessToken: tokenResponse.access_token,
        refreshToken: tokenResponse.refresh_token,
        expiresAt: new Date(Date.now() + tokenResponse.expires_in * 1000),
        userInfo: await this.fetchUserInfo(tokenResponse.access_token)
      });
    } catch (error) {
      this.logger.error('Cleo authentication failed', { error, credentials: credentials.sanitized() });
      return AuthResult.failure(error.message);
    }
  }

  async fetchMatterData(matterId: string): Promise<MatterData> {
    const [matter, client, documents, billing] = await Promise.all([
      this.apiClient.getMatter(matterId),
      this.apiClient.getClient(matterId),
      this.apiClient.getMatterDocuments(matterId),
      this.apiClient.getMatterBilling(matterId)
    ]);

    return MatterData.fromCleoFormat({
      id: matter.id,
      title: matter.title,
      practiceArea: matter.practice_area,
      status: matter.status,
      client: this.mapCleoClient(client),
      documents: documents.map(this.mapCleoDocument),
      billingInfo: this.mapCleoBilling(billing),
      customFields: matter.custom_fields
    });
  }

  async uploadDocument(matterId: string, document: GeneratedDocument): Promise<DocumentResult> {
    const cleoDocument = await this.apiClient.uploadDocument(matterId, {
      name: document.filename,
      content: document.content,
      mimeType: document.mimeType,
      metadata: {
        source: 'SettleWise',
        workflowId: document.workflowId,
        templateVersion: document.templateVersion,
        generatedAt: document.generatedAt.toISOString()
      }
    });

    return DocumentResult.success({
      externalId: cleoDocument.id,
      downloadUrl: cleoDocument.download_url,
      versionId: cleoDocument.version
    });
  }

  async createBillingEntry(matterId: string, billing: BillingData): Promise<BillingResult> {
    const cleoEntry = await this.apiClient.createTimeEntry(matterId, {
      description: `SettleWise Workflow: ${billing.description}`,
      hours: billing.durationMinutes / 60,
      rate: billing.hourlyRate,
      date: billing.date,
      taskCode: this.mapToCleoTaskCode(billing.category),
      billable: billing.billable,
      customFields: {
        settlewise_workflow_id: billing.workflowId,
        automation_level: billing.automationLevel
      }
    });

    return BillingResult.success({
      externalId: cleoEntry.id,
      amount: cleoEntry.amount
    });
  }

  private mapCleoClient(cleoClient: any): ClientData {
    return ClientData.create({
      id: cleoClient.id,
      firstName: cleoClient.first_name,
      lastName: cleoClient.last_name,
      email: cleoClient.email,
      phone: cleoClient.phone,
      address: Address.fromString(cleoClient.address),
      entityType: cleoClient.entity_type
    });
  }
}
```

### 2. Leap Platform Adapter

```typescript
// Infrastructure Layer - Leap Adapter
class LeapAdapter implements PlatformAdapter {
  private readonly apiClient: LeapAPIClient;
  private readonly desktopBridge: LeapDesktopBridge;

  constructor(
    private readonly config: LeapConfiguration,
    private readonly integrationMode: IntegrationMode,
    private readonly logger: Logger
  ) {
    this.apiClient = new LeapAPIClient(config);
    if (integrationMode === IntegrationMode.EMBEDDED && config.desktop) {
      this.desktopBridge = new LeapDesktopBridge(config.desktop);
    }
  }

  async authenticate(credentials: PlatformCredentials): Promise<AuthResult> {
    if (this.integrationMode === IntegrationMode.EMBEDDED && this.desktopBridge) {
      return this.authenticateDesktop(credentials);
    }
    return this.authenticateWeb(credentials);
  }

  private async authenticateDesktop(credentials: PlatformCredentials): Promise<AuthResult> {
    try {
      const desktopAuth = await this.desktopBridge.getCurrentUser();
      
      return AuthResult.success({
        accessToken: desktopAuth.session_token,
        userInfo: {
          id: desktopAuth.user_id,
          email: desktopAuth.email,
          firmId: desktopAuth.firm_id,
          permissions: desktopAuth.permissions
        }
      });
    } catch (error) {
      this.logger.error('Leap desktop authentication failed', { error });
      return AuthResult.failure(error.message);
    }
  }

  async fetchMatterData(matterId: string): Promise<MatterData> {
    const leapMatter = await this.apiClient.getMatter(matterId);
    const leapClient = await this.apiClient.getClient(leapMatter.clientId);
    
    return MatterData.fromLeapFormat({
      id: leapMatter.id,
      number: leapMatter.number,
      name: leapMatter.name,
      practiceArea: leapMatter.practiceArea,
      status: leapMatter.status,
      client: this.mapLeapClient(leapClient),
      court: leapMatter.court,
      opposingParty: leapMatter.opposingParty,
      customFields: leapMatter.customFields
    });
  }

  async uploadDocument(matterId: string, document: GeneratedDocument): Promise<DocumentResult> {
    if (this.desktopBridge) {
      return this.uploadToDesktop(matterId, document);
    }
    return this.uploadToWeb(matterId, document);
  }

  private async uploadToDesktop(matterId: string, document: GeneratedDocument): Promise<DocumentResult> {
    // Save to local file system first for desktop integration
    const localPath = await this.desktopBridge.saveDocumentLocally(document);
    
    // Import into Leap's document management
    const leapDoc = await this.desktopBridge.importDocument(matterId, localPath, {
      name: document.filename,
      category: 'Generated Documents',
      metadata: {
        source: 'SettleWise',
        workflowId: document.workflowId
      }
    });

    return DocumentResult.success({
      externalId: leapDoc.id,
      localPath: localPath,
      synced: false // Will sync when online
    });
  }
}
```

### 3. Context Detection Service

```typescript
// Application Layer - Context Detection
class PlatformContextDetector {
  detectContext(): WorkflowContext {
    const userAgent = navigator.userAgent;
    const windowContext = this.analyzeWindowContext();
    const urlParams = new URLSearchParams(window.location.search);

    // Check for embedded context
    if (windowContext.isEmbedded) {
      if (windowContext.parentHasCleo) {
        return WorkflowContext.create({
          platform: Platform.CLEO,
          integrationMode: IntegrationMode.EMBEDDED,
          contextData: this.extractCleoContext()
        });
      }
      
      if (windowContext.parentHasLeap) {
        return WorkflowContext.create({
          platform: Platform.LEAP,
          integrationMode: IntegrationMode.EMBEDDED,
          contextData: this.extractLeapContext()
        });
      }
    }

    // Check for desktop integration (Leap-specific)
    if (userAgent.includes('LeapDesktop') || window.external?.LeapAPI) {
      return WorkflowContext.create({
        platform: Platform.LEAP,
        integrationMode: IntegrationMode.EMBEDDED,
        contextData: this.extractLeapDesktopContext()
      });
    }

    // Check for API sync mode
    if (urlParams.has('cleo_matter_id')) {
      return WorkflowContext.create({
        platform: Platform.CLEO,
        integrationMode: IntegrationMode.API_SYNC,
        contextData: PlatformContextData.fromUrlParams(urlParams)
      });
    }

    if (urlParams.has('leap_matter_id')) {
      return WorkflowContext.create({
        platform: Platform.LEAP,
        integrationMode: IntegrationMode.API_SYNC,
        contextData: PlatformContextData.fromUrlParams(urlParams)
      });
    }

    // Default to standalone
    return WorkflowContext.create({
      platform: Platform.STANDALONE,
      integrationMode: IntegrationMode.STANDALONE,
      contextData: PlatformContextData.empty()
    });
  }

  private analyzeWindowContext(): WindowContext {
    return {
      isEmbedded: window.parent !== window,
      parentHasCleo: window.parent?.CLEO !== undefined,
      parentHasLeap: window.parent?.LEAP !== undefined,
      isFrame: window.frameElement !== null
    };
  }
}
```

### 4. Universal Sync Service

```typescript
// Application Layer - Universal Data Synchronization
class UniversalSyncService implements PlatformDataSync {
  private readonly adapters: Map<Platform, PlatformAdapter>;
  private readonly fieldMappings: Map<Platform, FieldMapping>;

  constructor(
    cleoAdapter: CleoAdapter,
    leapAdapter: LeapAdapter,
    mappingService: FieldMappingService
  ) {
    this.adapters = new Map([
      [Platform.CLEO, cleoAdapter],
      [Platform.LEAP, leapAdapter]
    ]);
    
    this.fieldMappings = new Map([
      [Platform.CLEO, mappingService.getCleoMapping()],
      [Platform.LEAP, mappingService.getLeapMapping()]
    ]);
  }

  async syncFromPlatform(platform: Platform, externalId: string): Promise<SyncResult> {
    const adapter = this.adapters.get(platform);
    if (!adapter) {
      return SyncResult.failure(`No adapter found for platform: ${platform}`);
    }

    try {
      const platformData = await adapter.fetchMatterData(externalId);
      const mapping = this.fieldMappings.get(platform)!;
      const workflowData = this.transformToWorkflowFormat(platformData, mapping);

      return SyncResult.success({
        data: workflowData,
        syncedAt: new Date(),
        source: platform
      });
    } catch (error) {
      return SyncResult.failure(`Sync failed: ${error.message}`);
    }
  }

  async syncToPlatform(platform: Platform, data: WorkflowData): Promise<SyncResult> {
    const adapter = this.adapters.get(platform);
    const mapping = this.fieldMappings.get(platform);
    
    if (!adapter || !mapping) {
      return SyncResult.failure(`Integration not available for platform: ${platform}`);
    }

    try {
      const platformData = this.transformToPlatformFormat(data, mapping);
      
      // Sync different data types
      const results = await Promise.allSettled([
        this.syncClientData(adapter, platformData),
        this.syncDocuments(adapter, platformData),
        this.syncBillingData(adapter, platformData)
      ]);

      const hasFailures = results.some(result => result.status === 'rejected');
      
      return hasFailures 
        ? SyncResult.partial(this.extractSyncResults(results))
        : SyncResult.success(this.extractSyncResults(results));
        
    } catch (error) {
      return SyncResult.failure(`Sync to platform failed: ${error.message}`);
    }
  }

  private transformToWorkflowFormat(platformData: MatterData, mapping: FieldMapping): WorkflowData {
    return WorkflowData.builder()
      .withClient(this.mapClient(platformData.client, mapping.clientMapping))
      .withMatter(this.mapMatter(platformData, mapping.matterMapping))
      .withDocuments(platformData.documents.map(doc => this.mapDocument(doc, mapping.documentMapping)))
      .withBilling(this.mapBilling(platformData.billingInfo, mapping.billingMapping))
      .build();
  }
}
```

### 5. Authentication & Session Management

```typescript
// Application Layer - Unified Authentication
class UnifiedAuthenticationService implements AuthenticationPort {
  constructor(
    private readonly cleoAdapter: CleoAdapter,
    private readonly leapAdapter: LeapAdapter,
    private readonly jwtService: JWTService,
    private readonly sessionStore: SessionStore
  ) {}

  async createUnifiedSession(platformUser: PlatformUser): Promise<UnifiedSession> {
    const sessionData: SessionData = {
      userId: platformUser.id,
      platform: platformUser.platform,
      firmId: platformUser.firmId,
      permissions: this.mapPlatformPermissions(platformUser.permissions, platformUser.platform),
      integrationMode: platformUser.integrationMode,
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 8 * 60 * 60 * 1000) // 8 hours
    };

    const accessToken = await this.jwtService.sign(sessionData);
    const refreshToken = await this.jwtService.signRefresh(sessionData);

    const session = UnifiedSession.create({
      accessToken,
      refreshToken,
      user: platformUser,
      expiresAt: sessionData.expiresAt
    });

    await this.sessionStore.store(session.id, session);

    return session;
  }

  async validateSession(token: string): Promise<SessionValidation> {
    try {
      const payload = await this.jwtService.verify(token);
      const session = await this.sessionStore.get(payload.sessionId);

      if (!session || session.isExpired()) {
        return SessionValidation.invalid('Session expired or not found');
      }

      return SessionValidation.valid(session);
    } catch (error) {
      return SessionValidation.invalid(`Token validation failed: ${error.message}`);
    }
  }

  private mapPlatformPermissions(platformPerms: string[], platform: Platform): Permission[] {
    const mappings = {
      [Platform.CLEO]: {
        'matter.read': Permission.WORKFLOW_READ,
        'matter.write': Permission.WORKFLOW_WRITE,
        'client.read': Permission.CLIENT_READ,
        'client.write': Permission.CLIENT_WRITE,
        'document.read': Permission.DOCUMENT_READ,
        'document.write': Permission.DOCUMENT_WRITE,
        'billing.read': Permission.BILLING_READ,
        'billing.write': Permission.BILLING_WRITE
      },
      [Platform.LEAP]: {
        'matter.view': Permission.WORKFLOW_READ,
        'matter.edit': Permission.WORKFLOW_WRITE,
        'client.view': Permission.CLIENT_READ,
        'client.edit': Permission.CLIENT_WRITE,
        'document.view': Permission.DOCUMENT_READ,
        'document.create': Permission.DOCUMENT_WRITE,
        'time.view': Permission.BILLING_READ,
        'time.create': Permission.BILLING_WRITE
      }
    };

    const mapping = mappings[platform];
    return platformPerms
      .map(perm => mapping[perm])
      .filter(Boolean);
  }
}
```

### 6. Document Generation Integration

```typescript
// Application Layer - Document Generation with Platform Integration
class IntegratedDocumentService implements DocumentGenerationPort {
  constructor(
    private readonly docassembleClient: DocassembleClient,
    private readonly platformSync: UniversalSyncService,
    private readonly documentStore: DocumentStore
  ) {}

  async generateDocument(template: string, data: InterviewData): Promise<GeneratedDocument> {
    // Generate document using docassemble
    const docResult = await this.docassembleClient.generateDocument(template, {
      ...data.variables,
      platform_context: data.platformContext
    });

    const document = GeneratedDocument.create({
      filename: docResult.filename,
      content: docResult.content,
      mimeType: docResult.mimeType,
      templateName: template,
      templateVersion: docResult.templateVersion,
      workflowId: data.workflowId,
      sessionId: data.sessionId,
      generatedAt: new Date(),
      metadata: {
        platform: data.platformContext.platform,
        matterId: data.platformContext.matterId,
        clientId: data.platformContext.clientId
      }
    });

    // Store locally
    await this.documentStore.store(document);

    // Sync to platform if in integrated mode
    if (data.platformContext.platform !== Platform.STANDALONE) {
      await this.syncDocumentToPlatform(document, data.platformContext);
    }

    return document;
  }

  private async syncDocumentToPlatform(
    document: GeneratedDocument, 
    context: PlatformContextData
  ): Promise<void> {
    if (!context.matterId) {
      throw new Error('Matter ID required for platform document sync');
    }

    const platform = context.platform;
    const adapter = this.getAdapterForPlatform(platform);

    try {
      const result = await adapter.uploadDocument(context.matterId, document);
      
      if (result.isSuccess()) {
        // Update document with platform reference
        document.addPlatformReference(platform, {
          externalId: result.data.externalId,
          downloadUrl: result.data.downloadUrl,
          syncedAt: new Date()
        });
        
        await this.documentStore.update(document);
      }
    } catch (error) {
      // Log error but don't fail the workflow
      console.error(`Failed to sync document to ${platform}:`, error);
    }
  }
}
```

## Integration Rules & Best Practices

### 1. Context-Aware Initialization

```typescript
// Rule: Always detect context before initializing services
class WorkflowInitializationService {
  async initialize(): Promise<IntegratedWorkflowEngine> {
    const context = new PlatformContextDetector().detectContext();
    
    // Configure adapters based on context
    const adapters = await this.configureAdapters(context);
    
    // Set up authentication
    const authService = new UnifiedAuthenticationService(...adapters);
    
    // Configure document generation
    const docService = new IntegratedDocumentService(
      new DocassembleClient(),
      new UniversalSyncService(...Object.values(adapters)),
      new DocumentStore()
    );

    return new IntegratedWorkflowEngine(context, adapters, authService, docService);
  }

  private async configureAdapters(context: WorkflowContext): Promise<AdapterMap> {
    const adapters: AdapterMap = {};

    if (context.platform === Platform.CLEO || context.includesCleoSync) {
      adapters.cleo = new CleoAdapter(
        await this.loadCleoConfig(),
        new Logger('cleo-adapter')
      );
    }

    if (context.platform === Platform.LEAP || context.includesLeapSync) {
      adapters.leap = new LeapAdapter(
        await this.loadLeapConfig(),
        context.integrationMode,
        new Logger('leap-adapter')
      );
    }

    return adapters;
  }
}
```

### 2. Data Consistency Rules

```typescript
// Rule: Always validate data consistency across platforms
class DataConsistencyService {
  async validateConsistency(
    workflowData: WorkflowData, 
    platforms: Platform[]
  ): Promise<ConsistencyReport> {
    const validationResults: ConsistencyCheck[] = [];

    for (const platform of platforms) {
      const platformData = await this.fetchPlatformData(platform, workflowData.matterId);
      const consistency = this.compareData(workflowData, platformData);
      
      validationResults.push({
        platform,
        consistent: consistency.isConsistent,
        conflicts: consistency.conflicts,
        lastSyncedAt: platformData.lastSyncedAt
      });
    }

    return ConsistencyReport.create(validationResults);
  }

  async resolveConflicts(
    conflicts: DataConflict[], 
    resolutionStrategy: ConflictResolutionStrategy
  ): Promise<ConflictResolution[]> {
    return Promise.all(
      conflicts.map(conflict => this.resolveConflict(conflict, resolutionStrategy))
    );
  }

  private async resolveConflict(
    conflict: DataConflict, 
    strategy: ConflictResolutionStrategy
  ): Promise<ConflictResolution> {
    switch (strategy) {
      case ConflictResolutionStrategy.PLATFORM_WINS:
        return this.applyPlatformValue(conflict);
      case ConflictResolutionStrategy.WORKFLOW_WINS:
        return this.applyWorkflowValue(conflict);
      case ConflictResolutionStrategy.MOST_RECENT:
        return this.applyMostRecentValue(conflict);
      case ConflictResolutionStrategy.MANUAL_REVIEW:
        return this.queueForManualReview(conflict);
    }
  }
}
```

### 3. Error Handling & Resilience

```typescript
// Rule: Implement circuit breakers for platform API calls
class ResilientPlatformService {
  private readonly circuitBreakers: Map<Platform, CircuitBreaker>;

  constructor() {
    this.circuitBreakers = new Map([
      [Platform.CLEO, new CircuitBreaker({ threshold: 5, timeout: 30000 })],
      [Platform.LEAP, new CircuitBreaker({ threshold: 5, timeout: 30000 })]
    ]);
  }

  async executeWithResilience<T>(
    platform: Platform,
    operation: () => Promise<T>
  ): Promise<Result<T>> {
    const circuitBreaker = this.circuitBreakers.get(platform);
    
    if (circuitBreaker?.isOpen()) {
      return Result.failure(`Circuit breaker open for ${platform}`);
    }

    try {
      const result = await this.withTimeout(operation(), 15000);
      circuitBreaker?.recordSuccess();
      return Result.success(result);
    } catch (error) {
      circuitBreaker?.recordFailure();
      
      if (this.isRetryableError(error)) {
        return this.retryWithBackoff(platform, operation, 3);
      }
      
      return Result.failure(error.message);
    }
  }

  private async retryWithBackoff<T>(
    platform: Platform,
    operation: () => Promise<T>,
    maxRetries: number
  ): Promise<Result<T>> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      await this.delay(Math.pow(2, attempt) * 1000); // Exponential backoff
      
      try {
        const result = await operation();
        return Result.success(result);
      } catch (error) {
        if (attempt === maxRetries || !this.isRetryableError(error)) {
          return Result.failure(error.message);
        }
      }
    }
  }
}
```

### 4. Billing Integration Rules

```typescript
// Rule: Always track workflow costs and sync to platform billing
class IntegratedBillingService {
  async trackWorkflowCosts(
    workflowId: string, 
    context: WorkflowContext
  ): Promise<void> {
    const metrics = await this.collectWorkflowMetrics(workflowId);
    const billingData = this.calculateBilling(metrics, context);

    // Store internal billing record
    await this.storeBillingRecord(workflowId, billingData);

    // Sync to platform if integrated
    if (context.platform !== Platform.STANDALONE && context.matterId) {
      await this.syncBillingToPlatform(context.platform, context.matterId, billingData);
    }
  }

  private calculateBilling(metrics: WorkflowMetrics, context: WorkflowContext): BillingData {
    const billingRules = this.getBillingRules(context.platform);
    
    return BillingData.builder()
      .withWorkflowId(metrics.workflowId)
      .withDuration(metrics.totalDurationMinutes)
      .withAutomationSavings(this.calculateSavings(metrics, billingRules))
      .withFixedFees(billingRules.fixedFees)
      .withHourlyCharges(this.calculateHourlyCharges(metrics, billingRules))
      .withDescription(this.generateBillingDescription(metrics))
      .build();
  }

  private getBillingRules(platform: Platform): BillingRules {
    return {
      [Platform.CLEO]: {
        automationDiscount: 0.3, // 30% discount for automated work
        fixedFees: { document_generation: 25, interview_completion: 15 },
        hourlyRates: { attorney: 400, paralegal: 150 }
      },
      [Platform.LEAP]: {
        automationDiscount: 0.25, // 25% discount for automated work
        fixedFees: { document_generation: 30, interview_completion: 20 },
        hourlyRates: { solicitor: 450, paralegal: 120 }
      }
    }[platform];
  }
}
```

## Configuration & Deployment

### Environment-Specific Configuration

```yaml
# config/integration.yml
platforms:
  cleo:
    enabled: true
    api_base_url: ${CLEO_API_BASE_URL}
    client_id: ${CLEO_CLIENT_ID}
    client_secret: ${CLEO_CLIENT_SECRET}
    webhook_secret: ${CLEO_WEBHOOK_SECRET}
    plugin_manifest_url: "https://settlewise.com/cleo/plugin.json"
    
  leap:
    enabled: true
    api_base_url: ${LEAP_API_BASE_URL}
    client_id: ${LEAP_CLIENT_ID}
    client_secret: ${LEAP_CLIENT_SECRET}
    desktop_integration: true
    web_widget_url: "https://settlewise.com/leap/widget.js"

sync:
  enabled: true
  bidirectional: true
  real_time_webhooks: true
  conflict_resolution: "most_recent" # platform_wins | workflow_wins | most_recent | manual_review
  
billing:
  track_workflow_costs: true
  sync_to_platform: true
  automation_discount_percentage: 25

security:
  jwt_secret: ${JWT_SECRET}
  session_timeout_hours: 8
  encryption_key: ${ENCRYPTION_KEY}
```

### Docker Deployment Configuration

```dockerfile
# Dockerfile for integrated deployment
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS runtime

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# Platform integration configs
COPY config/cleo-plugin.json ./public/cleo/
COPY config/leap-widget.js ./public/leap/

EXPOSE 3000
CMD ["npm", "start"]
```

## Testing Strategy

### Integration Test Framework

```typescript
// Test utilities for platform integration
class IntegrationTestSuite {
  async testCleoIntegration(): Promise<TestResult> {
    const mockCleoAdapter = new MockCleoAdapter();
    const workflowEngine = new IntegratedWorkflowEngine(mockCleoAdapter);

    return TestSuite.run([
      () => this.testAuthentication(mockCleoAdapter),
      () => this.testDataSync(workflowEngine),
      () => this.testDocumentGeneration(workflowEngine),
      () => this.testBillingIntegration(workflowEngine)
    ]);
  }

  async testLeapIntegration(): Promise<TestResult> {
    const mockLeapAdapter = new MockLeapAdapter();
    const workflowEngine = new IntegratedWorkflowEngine(mockLeapAdapter);

    return TestSuite.run([
      () => this.testDesktopIntegration(mockLeapAdapter),
      () => this.testWebIntegration(mockLeapAdapter),
      () => this.testOfflineCapabilities(mockLeapAdapter),
      () => this.testDataConsistency(workflowEngine)
    ]);
  }

  private async testDataSync(engine: IntegratedWorkflowEngine): Promise<void> {
    const testMatterId = 'test-matter-123';
    const mockData = TestDataFactory.createMatterData();

    // Test sync from platform
    const syncResult = await engine.syncFromPlatform(Platform.CLEO, testMatterId);
    assert(syncResult.isSuccess(), 'Failed to sync from platform');

    // Test sync to platform
    const workflowData = TestDataFactory.createWorkflowData();
    const uploadResult = await engine.syncToPlatform(Platform.CLEO, workflowData);
    assert(uploadResult.isSuccess(), 'Failed to sync to platform');
  }
}
```

## Monitoring & Analytics

```typescript
// Monitoring service for platform integrations
class IntegrationMonitoringService {
  constructor(
    private readonly metricsCollector: MetricsCollector,
    private readonly alertingService: AlertingService
  ) {}

  trackIntegrationMetrics(event: IntegrationEvent): void {
    this.metricsCollector.increment(`integration.${event.platform}.${event.operation}`);
    this.metricsCollector.histogram(`integration.${event.platform}.duration`, event.duration);
    
    if (event.error) {
      this.metricsCollector.increment(`integration.${event.platform}.errors`);
      this.alertingService.sendAlert({
        severity: event.severity,
        message: `Integration error with ${event.platform}: ${event.error}`,
        context: event.context
      });
    }
  }

  generateHealthReport(): IntegrationHealthReport {
    return {
      cleo: {
        available: this.checkCleoHealth(),
        lastSuccessfulSync: this.getLastSuccessfulSync(Platform.CLEO),
        errorRate: this.getErrorRate(Platform.CLEO)
      },
      leap: {
        available: this.checkLeapHealth(),
        lastSuccessfulSync: this.getLastSuccessfulSync(Platform.LEAP),
        errorRate: this.getErrorRate(Platform.LEAP)
      }
    };
  }
}
```

This comprehensive rules file provides the hexagonal backend architect with all the necessary patterns and implementation details for building robust integrations with both Cleo and Leap platforms while maintaining clean architecture principles and ensuring seamless operation in both embedded and standalone modes.