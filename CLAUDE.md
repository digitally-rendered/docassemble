# Docassemble Ontario Family Law Forms Project

## Project Context
This is a Docassemble project for creating, testing, and managing Ontario family law legal forms and interviews. The system integrates with Supabase for data persistence and uses Playwright for comprehensive testing.

## Critical Agent Usage Rules

### PROJECT-SPECIFIC AGENTS (ALWAYS USE PROACTIVELY):

#### 1. **docassemble-playwright-tester** - Automated Testing Agent
**TRIGGER WORDS:** test, testing, validate, validation, edge case, workflow, path, coverage, playwright, e2e, end-to-end
**MANDATORY USE WHEN:**
- After ANY modification to interview YAML files (*.yml)
- When creating new Docassemble interviews
- After changing conditional logic or validation rules
- When debugging interview flow issues
- After modifying question blocks or field definitions
- When users mention "interview", "form validation", or "workflow testing"

#### 2. **ontario-family-law-navigator** - Legal Information Agent
**TRIGGER WORDS:** ontario, family law, divorce, custody, support, property, Form [number], legal, court, filing, procedure, equalization, FRO, OCL, MIP
**MANDATORY USE WHEN:**
- ANY question about Ontario family law procedures
- When users mention specific form numbers (Form 8, Form 13, etc.)
- Questions about court procedures or filing requirements
- Inquiries about legal concepts or terminology
- When working on family law interview content
- References to divorce, separation, custody, or support matters

#### 3. **supabase-env-manager** - Database Management Agent
**TRIGGER WORDS:** supabase, database, migration, postgres, sql, table, schema, backup, environment, staging, production, branch
**MANDATORY USE WHEN:**
- Creating or modifying database schemas
- Applying database migrations
- Managing Supabase environments
- Performing database backups or recovery
- Setting up new development branches
- ANY Supabase-related operations

#### 4. **settlewise-product-manager** - Product Strategy Agent
**TRIGGER WORDS:** settlewise, feature, product, roadmap, user story, requirement, priority, feedback, mvp, release
**MANDATORY USE WHEN:**
- Planning new SettleWise features
- Creating user stories or requirements
- Discussing product roadmap
- Analyzing user feedback
- Prioritizing development work

#### 5. **family-law-saas-compliance** - Compliance Agent
**TRIGGER WORDS:** compliance, privacy, PIPEDA, accessibility, AODA, WCAG, UPL, unauthorized practice, legal compliance, terms of service
**MANDATORY USE WHEN:**
- Pre-launch compliance checks
- Privacy policy or terms of service creation
- Accessibility compliance questions
- Unauthorized practice of law (UPL) concerns
- Data protection and security requirements

#### 6. **hexagonal-frontend-architect** - Frontend Architecture Agent
**TRIGGER WORDS:** hexagonal, ports and adapters, container/view, domain logic, use case, dependency injection, frontend architecture, react component
**MANDATORY USE WHEN:**
- Designing React component architecture
- Implementing hexagonal architecture patterns
- Refactoring frontend code for separation of concerns
- Creating domain entities and use cases

### SYSTEM-LEVEL AGENTS (AUTOMATIC ACTIVATION):

#### Critical System Agents (ALWAYS ACTIVE)
1. **code-reviewer** - Activates after EVERY code write/edit
   - Triggers: code review, pull request, PR, code quality, best practices
2. **debugger** - Activates on ANY error or failure
   - Triggers: error, bug, broken, exception, stack trace, troubleshoot
3. **security-auditor** - Activates before deployments or handling sensitive data
   - Triggers: security, vulnerability, OWASP, XSS, SQL injection, auth
4. **test-automator** - Activates after new feature implementation
   - Triggers: test, unit test, integration test, coverage, mock, TDD
5. **incident-responder** - Activates IMMEDIATELY on production issues
   - Triggers: incident, outage, critical, P1, service down, urgent

#### Performance Optimization Agents
- **performance-engineer** - When response time > 1s
  - Triggers: slow, performance, optimize, bottleneck, latency, cache
- **database-optimizer** - When query time > 100ms
  - Triggers: query, SQL, index, slow query, N+1, join optimization
- **error-detective** - When investigating errors
  - Triggers: log analysis, error pattern, correlation, anomaly

#### Architecture & Design Agents
- **backend-architect** - BEFORE creating new services
  - Triggers: API, REST, GraphQL, microservice, endpoint, architecture
- **cloud-architect** - BEFORE provisioning cloud resources
  - Triggers: AWS, Azure, GCP, Terraform, infrastructure, auto-scaling
- **architect-reviewer** - AFTER structural changes
  - Triggers: architecture review, SOLID, design pattern, refactor

#### Development & Deployment Agents
- **deployment-engineer** - For CI/CD and containerization
  - Triggers: deploy, Docker, Kubernetes, pipeline, GitHub Actions
- **api-documenter** - After API changes
  - Triggers: Swagger, OpenAPI, endpoint docs, API versioning
- **legacy-modernizer** - For code > 2 years old
  - Triggers: legacy code, technical debt, migration, upgrade

#### Language-Specific Agents (AUTO-DETECT BY FILE)
- **python-pro** - .py files or Python code
  - Triggers: Python, pip, Django, Flask, FastAPI, decorator
- **javascript-pro** - .js/.ts files
  - Triggers: JavaScript, Node.js, React, async, promise, TypeScript
- **rust-pro** - .rs files
  - Triggers: Rust, ownership, lifetime, cargo, trait
- **golang-pro** - .go files
  - Triggers: Go, goroutine, channel, interface, concurrency
- **sql-pro** - .sql files or complex queries
  - Triggers: SQL, SELECT, JOIN, CTE, stored procedure

#### Specialized Technology Agents
- **terraform-specialist** - Infrastructure as Code
  - Triggers: Terraform, HCL, provider, module, state, workspace
- **ml-engineer** - Machine learning integration
  - Triggers: ML, model, TensorFlow, PyTorch, training, prediction
- **data-engineer** - ETL and data pipelines
  - Triggers: ETL, Spark, Airflow, Kafka, data pipeline, warehouse
- **mobile-developer** - Mobile app development
  - Triggers: React Native, Flutter, iOS, Android, mobile, app store

#### Developer Experience Agents
- **dx-optimizer** - After team feedback
  - Triggers: developer experience, tooling, workflow, productivity
- **prompt-engineer** - For LLM optimization
  - Triggers: prompt, LLM, GPT, Claude, few-shot, RAG
- **context-manager** - MANDATORY for > 10k tokens
  - Triggers: large project, multi-agent, context overflow

## Automatic Agent Activation Patterns

### File-Type Based Activation
```
Opening/Editing .py file → python-pro agent
Opening/Editing .js/.ts file → javascript-pro agent
Opening/Editing .rs file → rust-pro agent
Opening/Editing .go file → golang-pro agent
Opening/Editing .sql file → sql-pro agent
Opening/Editing .yml file → docassemble-playwright-tester agent
Opening/Editing .tf file → terraform-specialist agent
```

### Error-Based Activation
```
Console shows "Error" or "Exception" → debugger agent
Test output shows "Failed" → test-automator agent
Production alert triggered → incident-responder agent
Security warning detected → security-auditor agent
Performance threshold exceeded → performance-engineer agent
```

### Workflow-Based Activation

#### Testing Workflow
```
User modifies: *.yml file
→ AUTOMATICALLY invoke docassemble-playwright-tester
→ Create/update tests for modified interview
→ Run tests and report results
```

#### Code Review Workflow
```
After ANY code creation/modification
→ AUTOMATICALLY invoke code-reviewer
→ Check for best practices and standards
→ Suggest improvements
```

#### Legal Information Workflow
```
User asks about: "How do I file for divorce?"
→ AUTOMATICALLY invoke ontario-family-law-navigator
→ Provide procedural guidance with disclaimer
→ Reference specific forms and timelines
```

#### Database Operations Workflow
```
User mentions: "create a table" or "database migration"
→ AUTOMATICALLY invoke supabase-env-manager
→ Generate migration scripts
→ Apply to appropriate environment
```

#### Security Workflow
```
Before deployment OR handling user data
→ AUTOMATICALLY invoke security-auditor
→ Scan for vulnerabilities
→ Check authentication/authorization
→ Verify data encryption
```

#### Performance Optimization Workflow
```
Response time > 1s OR Query time > 100ms
→ AUTOMATICALLY invoke performance-engineer/database-optimizer
→ Profile and identify bottlenecks
→ Suggest optimizations
→ Implement caching strategies
```

## Project-Specific Commands

### Development Commands
- **Lint:** `npm run lint` (JavaScript/TypeScript)
- **Type Check:** `npm run typecheck`
- **Python Lint:** `ruff check`
- **Test Interviews:** `npx playwright test`
- **Test Specific Form:** `npx playwright test tests/ontario-forms/form-[number].spec.js`

### Interview Testing Commands
- **Quick Tests:** `./run-quick-tests.sh`
- **Comprehensive Tests:** `./run-comprehensive-tests.sh`
- **Form-Specific Tests:** `./run-form-tests.sh [form-number]`

## File Structure Context

### Key Directories
- `/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/` - Interview YAML files
- `/docassemble_webapp/playwright/` - Playwright test files
- `/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/utilities/` - Form parsing utilities
- `/docassemble_demo/docassemble/demo/data/questions/examples/` - 100+ example interviews
- `/docassemble_demo/docassemble/demo/` - Python utilities and validation functions
- `/helm-charts/` - Kubernetes deployment configurations

### Critical Files to Monitor
- `*.yml` - Docassemble interview definitions
- `*.spec.js` - Playwright test specifications
- `*.py` - Python utilities and form processors
- `deployment.yaml` - Kubernetes deployment config
- `utilities/parsed_forms/*.json` - Parsed form field definitions
- `utilities/forms_list.json` - Complete Ontario forms registry

## Important Project Resources

### Demo Examples Library
Located in `/docassemble_demo/docassemble/demo/data/questions/examples/`:
- **Multi-user patterns**: `multi-user.yml`, `multi-signature.yml`
- **Object collections**: `object-checkboxes.yml`, `objects-from-file.yml`
- **Conditional logic**: `branch-mandatory.yml`, `prevent-dependency-satisfaction.yml`
- **AJAX/real-time**: `ajax.yml`, `realtimegd.yml`
- **Document generation**: `overlay-pdf.yml`, `redact-pdf.yml`
- **Validation examples**: Various validation patterns

### Parsed Forms Database
Located in `utilities/parsed_forms/`:
- Complete field mappings for Forms 8, 10, 13, 13.1, 15, 17A, 25, 26, 28, 29, 33F, 36
- JSON format with field names, types, validation rules
- CSV format for easy viewing and analysis

### Form Processing Utilities
Located in `utilities/`:
- `automated_form_processor.py` - Extracts fields from forms
- `field_validation_mapper.py` - Maps validation rules
- `forms_list.json` - Registry of all Ontario forms
- `ontario_forms_registry.json` - Detailed form metadata
- `VALIDATION_SYSTEM.md` - Documentation of validation patterns

### Test Infrastructure
Located in `/docassemble_webapp/playwright/`:
- **Page Objects**: `BaseFamilyLawFormPage.js`, `Form13Page.js`, `WizardPage.js`
- **Helpers**: `interview-helpers.js`, `test-helpers.js`
- **Test Suites**: Comprehensive tests for all major forms
- **Commands**: `run-quick-tests.sh`, `run-comprehensive-tests.sh`, `run-form-tests.sh`

## Integration Points

### Supabase Integration
- Database URL: Check environment variables
- Tables: Users, Cases, Documents, Interview_Sessions
- Always use mcp__supabase tools for database operations

### Docassemble API
- Base URL: Configured in environment
- Authentication: API keys required
- Interview endpoints for form generation

### Ontario Court Forms Portal
- Forms source: ontariocourtforms.on.ca
- Always verify form versions and updates
- Use WebFetch for form information retrieval

## Testing Requirements

### Before Committing Code
1. Run all relevant Playwright tests
2. Verify lint and type checks pass
3. Test interview flows manually for critical paths
4. Check database migrations if schema changed
5. Verify compliance with accessibility standards

### Test Coverage Requirements
- All interview paths must have test coverage
- Edge cases for each validation rule
- Multi-party scenarios (applicant/respondent)
- Error recovery and session timeout handling

## Agent Collaboration Patterns

### Complex Feature Development
```
1. settlewise-product-manager → Define requirements
2. hexagonal-frontend-architect → Design architecture
3. Development work
4. docassemble-playwright-tester → Create tests
5. supabase-env-manager → Database setup
6. family-law-saas-compliance → Compliance check
```

### Form Implementation Workflow
```
1. ontario-family-law-navigator → Understand form requirements
2. Create/modify interview YAML
3. docassemble-playwright-tester → Test all paths
4. Deploy to staging environment
```

## Performance Monitoring

### Key Metrics to Track
- Interview load time < 2 seconds
- Form generation < 5 seconds
- Database query time < 100ms
- Test suite execution < 10 minutes

## Security Considerations

### Never Commit
- API keys or credentials
- Personal information or test data with PII
- Database connection strings
- SSL certificates or private keys

### Always Validate
- User input sanitization
- SQL injection prevention
- XSS protection in forms
- CSRF token validation

## Debugging Patterns

### Interview Issues
1. Check YAML syntax with validators
2. Review Docassemble logs
3. Use docassemble-playwright-tester for flow validation
4. Check variable definitions and dependencies

### Database Issues
1. Use supabase-env-manager for diagnostics
2. Check migration history
3. Verify connection parameters
4. Review query performance

## Emergency Procedures

### Production Issues
1. Immediately invoke relevant agents
2. Check system logs and monitoring
3. Verify database integrity
4. Run emergency test suite
5. Document incident for post-mortem

### Data Recovery
1. Use supabase-env-manager for backup operations
2. Verify backup integrity
3. Test recovery in staging first
4. Document recovery procedures

## Regular Maintenance Tasks

### Daily
- Monitor test suite results
- Check for failed background jobs
- Review error logs

### Weekly
- Update form definitions if needed
- Review and merge pending PRs
- Update test coverage reports

### Monthly
- Security and compliance audit
- Performance optimization review
- Dependency updates

## Contact and Resources

### Internal Resources
- Documentation: /docs directory
- Test Reports: /playwright/playwright-report/
- Logs: Check Kubernetes pods or Docker containers

### External Resources
- Ontario Court Forms: https://ontariocourtforms.on.ca
- Docassemble Documentation: https://docassemble.org
- Supabase Documentation: https://supabase.com/docs
- Law Society of Ontario: https://lso.ca

## CRITICAL REMINDERS

1. **ALWAYS TEST AFTER CHANGES** - No exceptions
2. **USE AGENTS PROACTIVELY** - Don't wait to be asked
3. **MAINTAIN LEGAL BOUNDARIES** - Never provide legal advice
4. **PROTECT USER DATA** - Follow privacy requirements
5. **DOCUMENT EVERYTHING** - Clear commit messages and comments

---
Last Updated: 2025-09-05
Version: 1.0.0