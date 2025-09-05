# System-Level Agent Enhancement Guide

## Complete List of System Agents

Based on the system prompt, here are all available system-level agents with recommended trigger patterns:

### 1. **code-reviewer**
**Current**: Use after writing significant code
**Enhanced Triggers**: code review, review code, check code, code quality, pull request, PR review, merge request, code standards, best practices, code smell, refactor suggestion
**Proactive Use**: IMMEDIATELY after ANY code creation or modification

### 2. **debugger**
**Current**: For errors, test failures, unexpected behavior
**Enhanced Triggers**: error, bug, issue, broken, not working, fails, exception, stack trace, debug, troubleshoot, fix, crash, undefined, null pointer, memory leak
**Proactive Use**: AUTOMATICALLY when ANY error occurs

### 3. **test-automator**
**Current**: Create comprehensive test suites
**Enhanced Triggers**: test, testing, unit test, integration test, e2e test, test coverage, mock, stub, test suite, pytest, jest, mocha, TDD, BDD
**Proactive Use**: IMMEDIATELY after writing new functions or features

### 4. **backend-architect**
**Current**: Design APIs and microservices
**Enhanced Triggers**: API, REST, GraphQL, microservice, endpoint, route, controller, service, repository, database schema, system design, architecture
**Proactive Use**: BEFORE creating new backend services or APIs

### 5. **performance-engineer**
**Current**: Profile and optimize bottlenecks
**Enhanced Triggers**: slow, performance, optimize, bottleneck, latency, throughput, cache, CDN, load test, profiling, memory usage, CPU usage, scaling
**Proactive Use**: When response times > 1s or high resource usage detected

### 6. **security-auditor**
**Current**: Review code for vulnerabilities
**Enhanced Triggers**: security, vulnerability, CVE, OWASP, XSS, SQL injection, CSRF, authentication, authorization, JWT, OAuth, encryption, SSL, HTTPS, penetration test
**Proactive Use**: BEFORE any deployment or when handling sensitive data

### 7. **database-optimizer**
**Current**: Optimize SQL queries and schemas
**Enhanced Triggers**: query, SQL, index, slow query, explain plan, N+1, join, optimization, database performance, migration, schema design
**Proactive Use**: When queries take > 100ms or during schema design

### 8. **deployment-engineer**
**Current**: Configure CI/CD pipelines
**Enhanced Triggers**: deploy, deployment, CI/CD, pipeline, Docker, Kubernetes, k8s, helm, container, GitHub Actions, Jenkins, GitLab CI, AWS, Azure, GCP
**Proactive Use**: When setting up deployments or modifying infrastructure

### 9. **cloud-architect**
**Current**: Design cloud infrastructure
**Enhanced Triggers**: AWS, Azure, GCP, cloud, infrastructure, Terraform, IaC, auto-scaling, load balancer, VPC, subnet, S3, EC2, Lambda, serverless
**Proactive Use**: For ANY cloud resource creation or modification

### 10. **frontend-developer**
**Current**: Build React components
**Enhanced Triggers**: React, component, UI, UX, frontend, useState, useEffect, props, Redux, Context, CSS, styling, responsive, mobile-first, accessibility
**Proactive Use**: When creating or modifying UI components

### 11. **ml-engineer**
**Current**: Implement ML pipelines
**Enhanced Triggers**: machine learning, ML, AI, model, training, dataset, TensorFlow, PyTorch, scikit-learn, neural network, prediction, classification, regression
**Proactive Use**: For ANY ML model integration or data pipeline

### 12. **data-engineer**
**Current**: Build ETL pipelines
**Enhanced Triggers**: ETL, data pipeline, Spark, Airflow, Kafka, streaming, batch processing, data warehouse, BigQuery, Redshift, Snowflake, data lake
**Proactive Use**: When designing data processing workflows

### 13. **DevOps-troubleshooter**
**Current**: Debug production issues
**Enhanced Triggers**: production issue, outage, incident, monitoring, logs, metrics, alerting, downtime, service degradation, root cause, post-mortem
**Proactive Use**: IMMEDIATELY during production incidents

### 14. **api-documenter**
**Current**: Create OpenAPI/Swagger specs
**Enhanced Triggers**: API documentation, Swagger, OpenAPI, endpoint docs, SDK, client library, API versioning, REST docs, GraphQL schema
**Proactive Use**: After creating or modifying API endpoints

### 15. **mobile-developer**
**Current**: React Native/Flutter apps
**Enhanced Triggers**: mobile, React Native, Flutter, iOS, Android, app store, push notification, offline sync, native module, responsive design
**Proactive Use**: For mobile-specific features or optimizations

### 16. **network-engineer**
**Current**: Debug network connectivity
**Enhanced Triggers**: network, connectivity, DNS, SSL, TLS, CDN, load balancer, firewall, proxy, CORS, websocket, TCP, UDP, latency, packet loss
**Proactive Use**: For networking issues or configuration

### 17. **rust-pro**
**Current**: Write idiomatic Rust
**Enhanced Triggers**: Rust, ownership, lifetime, borrow checker, trait, cargo, unsafe, memory safety, zero-cost abstraction, systems programming
**Proactive Use**: For Rust development or memory-critical code

### 18. **golang-pro**
**Current**: Write idiomatic Go
**Enhanced Triggers**: Go, golang, goroutine, channel, interface, defer, panic, recover, context, concurrency, go mod
**Proactive Use**: For Go development or concurrent systems

### 19. **python-pro**
**Current**: Write idiomatic Python
**Enhanced Triggers**: Python, pip, virtualenv, decorator, generator, async/await, type hints, dataclass, pytest, Django, Flask, FastAPI
**Proactive Use**: For Python development or scripting

### 20. **javascript-pro**
**Current**: Master modern JavaScript
**Enhanced Triggers**: JavaScript, JS, ES6, async, promise, callback, Node.js, npm, yarn, webpack, babel, TypeScript, arrow function
**Proactive Use**: For JavaScript/Node.js development

### 21. **sql-pro**
**Current**: Write complex SQL queries
**Enhanced Triggers**: SQL, query, SELECT, JOIN, CTE, window function, stored procedure, trigger, view, materialized view, execution plan
**Proactive Use**: For complex database queries or optimization

### 22. **terraform-specialist**
**Current**: Write Terraform modules
**Enhanced Triggers**: Terraform, HCL, provider, module, state, plan, apply, destroy, workspace, backend, drift detection, infrastructure as code
**Proactive Use**: For infrastructure provisioning or changes

### 23. **architect-reviewer**
**Current**: Review architectural consistency
**Enhanced Triggers**: architecture review, design pattern, SOLID, DRY, KISS, coupling, cohesion, microservices, monolith, event-driven, domain-driven
**Proactive Use**: After structural changes or new service creation

### 24. **legacy-modernizer**
**Current**: Refactor legacy codebases
**Enhanced Triggers**: legacy code, technical debt, refactor, modernization, migration, upgrade, deprecated, outdated, backwards compatibility
**Proactive Use**: When working with code > 2 years old

### 25. **incident-responder**
**Current**: Handle production incidents
**Enhanced Triggers**: incident, emergency, critical, P1, P0, outage, service down, urgent, escalation, on-call, war room
**Proactive Use**: IMMEDIATELY when production issues occur

### 26. **prompt-engineer**
**Current**: Optimize LLM prompts
**Enhanced Triggers**: prompt, LLM, GPT, Claude, chat completion, token, context window, few-shot, chain-of-thought, prompt template, RAG
**Proactive Use**: When building AI features or improving agent performance

### 27. **dx-optimizer**
**Current**: Developer Experience specialist
**Enhanced Triggers**: developer experience, DX, tooling, setup, workflow, productivity, onboarding, documentation, CLI, SDK, API ergonomics
**Proactive Use**: When setting up projects or after team feedback

### 28. **context-manager**
**Current**: Manages context across multiple agents
**Enhanced Triggers**: large project, multi-agent, complex task, context overflow, 10k+ tokens, long conversation, memory management
**Proactive Use**: MANDATORY for projects exceeding 10k tokens

### 29. **error-detective**
**Current**: Search logs for error patterns
**Enhanced Triggers**: log analysis, error pattern, stack trace, correlation, root cause, anomaly, debugging, log aggregation, monitoring
**Proactive Use**: When investigating production errors or issues

### 30. **mlops-engineer**
**Current**: Build ML pipelines
**Enhanced Triggers**: MLOps, model deployment, MLflow, Kubeflow, model registry, experiment tracking, A/B testing, model monitoring, drift detection
**Proactive Use**: For ML infrastructure or production ML systems

## Recommended CLAUDE.md Additions

Add this section to your CLAUDE.md file:

```markdown
## System Agent Automatic Activation Rules

### Critical System Agents (ALWAYS ACTIVE)

1. **code-reviewer** - Activates after EVERY code write/edit
2. **debugger** - Activates on ANY error or failure
3. **security-auditor** - Activates before deployments or when handling user data
4. **test-automator** - Activates after new feature implementation
5. **incident-responder** - Activates IMMEDIATELY on production issues

### Performance Agents (THRESHOLD-BASED)

- **performance-engineer** - When response time > 1s
- **database-optimizer** - When query time > 100ms
- **error-detective** - When error rate > 1%

### Architecture Agents (DESIGN-PHASE)

- **backend-architect** - BEFORE creating new services
- **cloud-architect** - BEFORE provisioning cloud resources
- **architect-reviewer** - AFTER structural changes

### Specialized Language Agents (AUTO-DETECT)

- **python-pro** - When working with .py files
- **javascript-pro** - When working with .js/.ts files
- **rust-pro** - When working with .rs files
- **golang-pro** - When working with .go files
- **sql-pro** - When working with .sql files or complex queries

### Context-Aware Activation

- **context-manager** - MANDATORY when token count > 10k
- **legacy-modernizer** - When file last modified > 2 years ago
- **dx-optimizer** - After receiving user feedback about tooling
```

## Proactive Patterns to Implement

### 1. File-Type Detection
```
If file extension = .py → Activate python-pro
If file extension = .rs → Activate rust-pro
If file contains SQL → Activate sql-pro
```

### 2. Error Detection
```
If output contains "Error" or "Exception" → Activate debugger
If output contains "Failed" → Activate test-automator
If output contains "Production" + "Down" → Activate incident-responder
```

### 3. Performance Monitoring
```
If execution time > threshold → Activate performance-engineer
If memory usage > 80% → Activate performance-engineer
If database query > 100ms → Activate database-optimizer
```

### 4. Security Scanning
```
If code contains auth/login → Activate security-auditor
If handling payments → Activate security-auditor
If user data processing → Activate security-auditor
```

### 5. Architecture Review
```
If creating new service → Activate backend-architect
If modifying > 5 files → Activate architect-reviewer
If changing database schema → Activate database-optimizer
```