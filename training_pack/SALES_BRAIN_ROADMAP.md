# Sales Brain Roadmap (Website + Enterprise Systems)

## Target

Build the assistant into a revenue-driving copilot:
- answer accurately
- qualify leads
- push next-step actions
- sync to enterprise systems

## Phase 1: Website Sales Copilot (Now)

### Scope
- Intent classification per turn
- Lead extraction (name/phone/email/company/service intent)
- Lead scoring and hot/warm/cold tiering
- Next-best-action generation
- Conversation and lead logging

### Done in code
- `api/sales_brain.py`
- `api/index.py` integrated with sales metadata
- `public/js/script.js` sends `session_id`

### Output fields
- `sales.intent`
- `sales.lead_tier`
- `sales.lead_score`
- `sales.next_action`
- `sales.missing_fields`

### Data files
- `api/data/conversation_turns.jsonl`
- `api/data/lead_profiles.json`

## Phase 2: CRM Integration

### Add endpoints
- `POST /api/lead/create`
- `POST /api/lead/update`
- `POST /api/lead/followup`

### Integration targets
- CRM: lead owner, source, status, follow-up time
- WeCom/DingTalk: notify sales owner for hot leads

### SLA
- hot lead routed within 5 minutes
- warm lead follow-up within 24 hours

## Phase 3: Sales Playbook Automation

### Capability
- Auto run BANT script
- Auto recommend package by industry/size/timeline
- Auto objection handling templates
- Auto appointment workflow

### Guardrails
- price/contract/legal -> human handoff required
- uncertain policy questions -> human validation required

## Phase 4: Enterprise Brain

### Cross-system orchestration
- ERP project status query
- document checklist completion tracking
- contract workflow status
- ticketing + post-sales service

### Control plane
- role-based data permissions
- audit logs for every tool call
- action rollback and manual override

## KPI Dashboard

- Lead capture rate
- Qualified lead rate
- Meeting booking rate
- Quote conversion rate
- Avg first-response time
- Human handoff ratio
- Wrong-answer rate

## Weekly Operating Cadence

1. Review top 50 failed or handoff chats.
2. Add new FAQs/rules and retrain prompt/RAG.
3. Evaluate metrics trend and bottleneck stage.
4. Update objection handling and follow-up script.

