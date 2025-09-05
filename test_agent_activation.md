# Agent Activation Test Scenarios

## Test 1: Docassemble Testing Agent
**Trigger phrase:** "I just updated the form-8 interview yaml file"
**Expected:** docassemble-playwright-tester agent should activate immediately

## Test 2: Ontario Family Law Navigator
**Trigger phrase:** "What is Form 13 used for in Ontario?"
**Expected:** ontario-family-law-navigator agent should activate immediately

## Test 3: Supabase Environment Manager
**Trigger phrase:** "I need to create a new database table for storing user sessions"
**Expected:** supabase-env-manager agent should activate immediately

## Test 4: SettleWise Product Manager
**Trigger phrase:** "We got user feedback that the document generation is too slow"
**Expected:** settlewise-product-manager agent should activate immediately

## Test 5: Compliance Agent
**Trigger phrase:** "Do we need to update our privacy policy for PIPEDA compliance?"
**Expected:** family-law-saas-compliance agent should activate immediately

## Test 6: Frontend Architecture
**Trigger phrase:** "This React component has business logic mixed with UI code"
**Expected:** hexagonal-frontend-architect agent should activate immediately

## Test 7: Multiple Agent Scenario
**Trigger phrase:** "I'm adding a new feature to collect financial information in Form 13, need to test it and store data in Supabase"
**Expected:** Multiple agents should activate:
- ontario-family-law-navigator (for Form 13 context)
- docassemble-playwright-tester (for testing)
- supabase-env-manager (for database storage)

## Test 8: Workflow Testing
**Trigger phrase:** "The interview validation isn't working properly, getting edge case errors"
**Expected:** docassemble-playwright-tester agent should activate for edge case testing

## Test 9: Database Migration
**Trigger phrase:** "Apply the latest migration to add the new financial_documents table"
**Expected:** supabase-env-manager agent should activate for migration

## Test 10: Product Feature Request
**Trigger phrase:** "Users want a dashboard to track their case progress"
**Expected:** settlewise-product-manager agent should activate for feature analysis

---

## How to Test

1. Start a new conversation
2. Use one of the trigger phrases above
3. Observe if the correct agent(s) activate automatically
4. Document any failures or unexpected behavior

## Success Criteria

- Agents activate without explicit request
- Correct agent matches the domain/context
- Multiple agents activate when appropriate
- Agents provide relevant, proactive assistance