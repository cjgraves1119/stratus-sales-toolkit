---
name: daily-task-engine-v1-7
description: "canonical zoho query with status filter, ir01 batch pre-filter, sub-agent verbosity cap (json-only return), dr01 closed-won auto-close fix, and zoho-crm-v28 companion reference. parallel sub-agent task evaluation, inline email draft previews in approval table, clickable zoho crm and gmail links on every row, 5-phase workflow with task tool orchestration, inbox scan phase, never-close-won rule, weborder check in dr01 gate, gmail-first context for all deal tasks, strengthened successor enforcement after every action, pipedream/zapier tool identification, revised-draft-before-send rule, and reply-all thread participant enforcement. triggers: daily tasks, review my tasks, task review, task clean up, help me complete todays tasks, close out my tasks, close tasks, what tasks are due, send fu30 emails, fu30s, 30-day check-ins, run my tasks, morning tasks, task cleanup, finish my tasks, knock out my tasks, lets do tasks, whats on my plate, clear my task list, inbox scan, check my inbox, scan my email."
---

# Daily Task Engine v1.7 (Canonical Query + IR01 Pre-Filter + Sub-Agent Verbosity Cap + DR01 Closed Won Fix)

Trigger router with **parallel sub-agent evaluation**, **inline email draft previews in approval table**, **clickable Zoho CRM and Gmail links on every row**, **per-task-type evaluation gates**, **batch approval tables**, **gmail-first context evaluation**, **strengthened successor enforcement after every action**, **inbox scan phase for email action items**, **revised draft must be shown before sending**, and **reply-all thread participant enforcement**.

---

## What's New in v1.7

- **CANONICAL ZOHO QUERY**: Phase 1 now uses a hardcoded query with Status filter to eliminate all failed query attempts. Primary: `(Owner:equals:2570562000141711002)and(Due_Date:less_equal:{TODAY})and(Status:equals:Not Started)`. Fallback defined if Status filter unsupported. NEVER use `not_equals` operator. NEVER fetch without owner filter.
- **IR01 BATCH PRE-FILTER**: Before launching sub-agents in Phase 2, scan all fetched tasks for the IR01 pattern. Batch-classify them as NEEDS_REVIEW in a single table row. Do NOT launch individual sub-agents for IR01 tasks — they are auto-generated noise and waste sub-agent budget.
- **SUB-AGENT VERBOSITY CAP**: Sub-agent prompt template now includes explicit instruction to return ONLY the structured JSON object — no prose, no preamble, no narrative. Keeps each result under ~200 tokens and prevents context exhaustion before Phase 3.
- **DR01 CLOSED WON AUTO-CLOSE**: DR01 gate now immediately auto-closes tasks where the linked deal is already Closed (Won) or Closed (Lost). No email drafted, no successor created. Previously, sub-agents would incorrectly propose post-close check-in emails for fulfilled deals.
- **COMPANION SKILLS UPDATED**: Points to zoho-crm-v28 (product_name field fix for inactive inventory bypass).
- All v1.6 features retained (revised draft approval rule, reply-all thread enforcement, parallel sub-agents, inline drafts, clickable links, 5-phase workflow, inbox scan, never-close-won, Gmail source of truth, successor enforcement, Pipedream/Zapier ID).

## What's New in v1.6

- **REVISED DRAFT APPROVAL RULE**: When a user requests any edits or modifications to a proposed email draft, the FULL REVISED draft must be presented for explicit user approval before sending.
- **REPLY-ALL THREAD ENFORCEMENT**: Before sending ANY reply to an existing email thread, call `gmail_read_thread` to read the full thread and extract ALL recipients (To + CC) from the most recent message.
- All v1.5 features retained.

## What's New in v1.5

- **PARALLEL SUB-AGENT EVALUATION**: All tasks evaluated simultaneously using the Task tool. One sub-agent per task, all launched in a single message block.
- **INLINE EMAIL DRAFT PREVIEWS**: Approval table includes the full proposed email body for every actionable item.
- **CLICKABLE ZOHO CRM LINKS**: Every task row includes hyperlinked Task, Deal, Contact, and Account links.
- **CLICKABLE GMAIL THREAD LINKS**: Every inbox row includes direct Gmail thread links.
- **5-PHASE WORKFLOW**: Phase 1 (fetch) -> Phase 2 (parallel sub-agent eval) -> Phase 3 (approval table) -> Phase 4 (inbox scan) -> Phase 5 (sequential execution).
- All v1.4 features retained.

## What's New in v1.4

- **INBOX SCAN PHASE**: New phase scans Gmail inbox for actionable emails.
- **4 INBOX CATEGORIES**: INBOX_REPLY, INBOX_NEW_TASK, INBOX_DEAL_UPDATE, INBOX_FYI.
- **UNIFIED BATCH TABLE**: CRM tasks and inbox action items in one approval table.
- All v1.3 features retained.

## What's New in v1.3

- **NEVER MANUALLY CLOSE WON**: DR01 gate checks for weborder before any close action.
- **GMAIL AS SOURCE OF TRUTH**: All deal-linked task gates require Gmail search before proposing actions.
- **SUCCESSOR AFTER EVERY ACTION**: All open/ongoing deals require a follow-up task after any action.
- **PIPEDREAM/ZAPIER TOOL IDENTIFICATION**: UUID reference embedded.

---

## Trigger Patterns

### Full Daily Task Review

Triggers: /DailyTasks, "daily tasks", "review my tasks", "task review", "help me complete todays tasks", "morning tasks", "run my tasks", "lets do tasks", "whats on my plate", "knock out my tasks"

What it does:
1. Phase 1: Pull all open tasks owned by Chris Graves, due today or overdue (canonical query)
2. Phase 1b: IR01 pre-filter — batch-classify IR01 tasks before sub-agent launch
3. Phase 2: Launch one sub-agent per non-IR01 task simultaneously (Task tool, single message block)
4. Phase 3: Collect sub-agent results, build unified approval table with inline email drafts and clickable links
5. Phase 4: Run Inbox Scan in parallel while user reviews approval table
6. Phase 5: Execute approved actions sequentially (atomic task lifecycle)

Skills to load: zoho-crm-v28, zoho-crm-email-v3-5

### Task Cleanup (Close Only)

Triggers: /CloseTasks, "close out my tasks", "close tasks", "task clean up", "task cleanup", "clear my task list", "finish my tasks"

Skills to load: zoho-crm-v28

### 30-Day Follow-Up Emails

Triggers: /FU30s, "send fu30 emails", "fu30s", "30-day check-ins", "post-sale check-ins", "run fu30s", "customer check-ins"

Skills to load: zoho-crm-v28, zoho-crm-email-v3-5, fu30-followup-automation-v1-3

### Inbox Scan (Standalone)

Triggers: /InboxScan, "check my inbox", "inbox scan", "scan inbox", "scan my email", "what emails need attention"

Skills to load: zoho-crm-v28, zoho-crm-email-v3-5

### Triage Only (No Action)

Triggers: "what tasks are due", "show me my tasks", "task summary", "what do I have today"

Skills to load: zoho-crm-v28

---

## 5-Phase Workflow

### Overview

PHASE 1: FETCH + IR01 PRE-FILTER (~5s)
  Pull all open tasks from Zoho CRM using canonical query
  IR01 pre-filter: batch-classify IR01 tasks, remove from sub-agent list

PHASE 2: PARALLEL SUB-AGENT EVALUATION (~10s flat)
  Launch one sub-agent per non-IR01 task using the Task tool
  ALL agents launched in a SINGLE message block (true parallelism)
  Each agent returns structured JSON ONLY (verbosity cap enforced)

PHASE 3: BUILD APPROVAL TABLE (~5s)
  Collect all sub-agent results
  Build unified approval table with clickable links, inline drafts, IR01 batch row

PHASE 4: INBOX SCAN (runs in parallel while user reviews Phase 3 table)
  Announce: "Scanning inbox while you review the table above..."
  Run Gmail inbox search + Zoho cross-reference
  Append inbox items to approval table

PHASE 5: SEQUENTIAL EXECUTION
  For each approved item: atomic task lifecycle
  send -> confirm -> close -> verify -> successor
  NEVER parallelize execution steps
  NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block

---

## Phase 1: Canonical Zoho Query (NEW IN V1.7)

### Primary Query (Use This First)

```
Criteria: (Owner:equals:2570562000141711002)and(Due_Date:less_equal:{TODAY})and(Status:equals:Not Started)
Page size: 50
Pages: Fetch pages 1, 2, 3 (up to 150 records)
Sort: Due_Date asc
```

Replace `{TODAY}` with today's date in YYYY-MM-DD format.

### Fallback Query (If Status Filter Returns INVALID_QUERY)

If the primary query fails with INVALID_QUERY or returns no results when tasks are expected:

```
Criteria: (Owner:equals:2570562000141711002)and(Due_Date:less_equal:{TODAY})
Page size: 50
Pages: Fetch pages 1, 2, 3
```

Then filter client-side: keep only records where `Status == "Not Started"`. Discard `Status == "Completed"` and `Status == "Deferred"`.

### Banned Query Patterns (NEVER USE)

- NEVER use `not_equals` operator — Zoho returns INVALID_QUERY
- NEVER fetch without the Owner filter — returns 79KB+ unreadable responses
- NEVER fetch without Due_Date filter alongside a broad owner filter — returns 85KB+ responses
- NEVER save large results to disk for grep filtering — disk space issues and encoding failures

### Query Result Validation

After fetching, display:
```
Total records fetched: {N}
Status breakdown: Not Started: {X}, Completed: {Y}, Other: {Z}
Proceeding with: {X} open tasks
```

---

## Phase 1b: IR01 Batch Pre-Filter (NEW IN V1.7)

### What IR01 Tasks Are

IR01 tasks are auto-generated "Reminder to Set a Task" alerts linked to the Meraki_ISR module. They follow the pattern:
- Subject contains "IR01:" OR
- Subject matches "IR01: Reminder to Set a Task. ISR [Name]" OR
- Subject matches "Reminder to Set a Task" with no linked deal

These are noise tasks that do not require individual Gmail context lookup or sub-agent evaluation.

### Pre-Filter Steps

BEFORE launching any sub-agents:
1. Scan all fetched task subjects for the IR01 pattern above
2. Separate IR01 tasks from substantive tasks
3. Display: "IR01 tasks (batch): {N} | Substantive tasks (sub-agents): {M}"
4. Launch sub-agents ONLY for the {M} substantive tasks
5. Add IR01 tasks as a single batch row in the Phase 3 approval table

### IR01 Batch Row Format (for Phase 3 Table)

```
**IR01 BATCH — {N} ISR Reminder Tasks** | NEEDS_REVIEW
Tasks: [Subject 1], [Subject 2], + N more
Proposed Action: Manual review — auto-generated ISR reminders. Close individually or reassign.
No email draft. No successor auto-created.
```

---

## Phase 2: Sub-Agent Launch Pattern

CRITICAL: All sub-agents launched in ONE message block for true parallelism.

Each sub-agent receives this prompt:

```
Evaluate Zoho task ID {task_id}:
Subject: {subject}
Due: {due_date}
Linked Deal ID: {deal_id} (Stage: {stage}, Amount: ${amount})
Linked Contact: {contact_name} ({contact_email})
Linked Account: {account_name}

STEPS:
1. Search Gmail for last actual contact with {contact_email}
   (query: 'from:{contact_email} OR to:{contact_email}', max 5 results)
2. Identify last contact date and thread ID
3. Run evaluation gate for task type: {task_type}
4. Determine proposed action
5. If action = send email: draft the full email body
   (Chris Graves voice, no em dashes, 1-3 lines per paragraph, end with question or CTA)

RETURN structured result:
{
  task_id, subject, company, contact_name, contact_email, task_type, due_date,
  deal_id, deal_stage, deal_amount,
  zoho_task_url: 'https://crm.zoho.com/crm/org647122552/tab/Tasks/{task_id}',
  zoho_deal_url: 'https://crm.zoho.com/crm/org647122552/tab/Potentials/{deal_id}',
  zoho_contact_url: 'https://crm.zoho.com/crm/org647122552/tab/Contacts/{contact_id}',
  zoho_account_url: 'https://crm.zoho.com/crm/org647122552/tab/Accounts/{account_id}',
  gmail_last_contact_date, gmail_thread_id,
  gmail_thread_url: 'https://mail.google.com/mail/u/0/#all/{thread_id}',
  proposed_action, action_notes,
  email_draft (full body if action = send email, else null),
  email_subject (if action = send email, else null),
  successor_needed (true/false),
  successor_due (YYYY-MM-DD, 3 business days from today if successor needed)
}

VERBOSITY CAP (CRITICAL): Return ONLY the structured JSON object above. No prose explanation,
no preamble, no analysis narrative, no summary after the JSON. Your entire response must be
one JSON object and nothing else. This is required to prevent context exhaustion.
```

### Sub-Agent Instructions by Task Type

| Task Type | Key Sub-Agent Instructions |
|-----------|---------------------------|
| FU30 | Enrichment logic: get quote total, check open invoices, Gmail post-sale context, draft friendly check-in. |
| DA90 | Check license expiration from Account/Deal notes. Within 30 days: draft renewal. 31-90 days: propose reminder task. 90+ days: close with note. |
| DR01 | Fetch deal stage FIRST. If Closed (Won) or Closed (Lost): AUTO-CLOSE, no email, no successor. If active: Gmail search, draft follow-up if no contact in 14+ days. If fulfilled but not Closed Won: flag for weborder check. |
| DEAL_FOLLOWUP | Gmail search is mandatory. Draft follow-up if no contact in 7+ days. Return last contact date. |
| AUTO_CLOSE | Verify the action happened (quote exists, PO logged, key delivered). Return close with verification note. |
| ISR_CHECKIN | Look up Cisco rep from cisco-rep-locator hot cache. Draft Webex message or email to rep. |
| CW01 | Check quote status on linked deal. Draft quote follow-up email if customer has not responded. |
| SR | Check service request context. Return close with note or follow-up. |
| NEEDS_REVIEW | Return task details only. No proposed email. Flag for manual decision. |

---

## Phase 3: Approval Table Format

Every row must follow this structure:

```
**#{N} - [{Task Subject}]({zoho_task_url})** | {task_type} | Due: {due_date}
Company: [{Account Name}]({zoho_account_url})
Deal: [{Deal Name} -- ${amount}]({zoho_deal_url}) | Stage: {stage}
Contact: [{Contact Name}]({zoho_contact_url}) ({contact_email})
Last Gmail Contact: {date} -- [View thread]({gmail_thread_url})
Proposed Action: {action}

EMAIL DRAFT:
Subject: {email_subject}
---
{full email body}
---
```

Header format:
```
TASK TRIAGE SUMMARY -- {Date}
Total: {X} tasks | Due today: {Y} | Overdue: {Z} | Inbox items: {N} | IR01 batch: {B}
Evaluation: {X} sub-agents ran in parallel

Reply with:
  "approve all" -- execute all proposed actions
  "approve #1, #3" -- execute specific items
  "skip #2" -- remove from batch
  "edit #1 [changes]" -- modify draft before sending
```

---

## Phase 4: Inbox Scan During Review

Announce immediately after presenting Phase 3 table:
"Scanning your inbox while you review -- I'll add any action items below."

### Gmail Search Query

```
is:inbox (is:unread OR is:important) newer_than:3d -from:me -from:systemgenerated@zohocrm.com -from:notifications@ -from:noreply@ -from:no-reply@ -from:mailer-daemon@ -from:calendar-notification@google.com -from:notify@webex.com
```

Max results: 20 emails per scan

### Inbox Evaluation Pipeline

FOR EACH email from inbox search:
  STEP 1: Extract sender email, subject, thread ID, received date, is unread?
  STEP 2: Cross-reference Zoho CRM by sender email — find Contact, Account, open Deals, open Tasks
  STEP 3: Categorize:
    INBOX_REPLY: Customer sent last, needs response
    INBOX_NEW_TASK: No matching open task or deal
    INBOX_DEAL_UPDATE: Email on tracked deal (informational or needs task)
    INBOX_FYI: Chris sent last, newsletter, notification
  STEP 4: Draft action + email if needed

### Inbox Deduplication Logic

1. Search open Tasks by sender name OR subject keywords
2. Check if task was closed in last 3 days
3. Thread direction check: Chris sent last -> INBOX_FYI; customer sent last -> INBOX_REPLY
4. Zoho notification check: system emails about tasks already in triage -> INBOX_FYI

### Inbox Execution Rules

INBOX_REPLY:
  1. Read full thread via gmail_read_thread (MANDATORY — also extracts reply-all recipients)
  2. Extract ALL To + CC recipients from most recent message
  3. Send draft via Pipedream to all extracted recipients
  4. If active deal with no open task: create successor task

INBOX_NEW_TASK:
  1. Check if sender should be a new Zoho Contact (ask Chris if unclear)
  2. Create Zoho Task linked to Account/Deal if identified
  3. Send reply draft if approved

INBOX_DEAL_UPDATE:
  1. Note the update
  2. If no open task on deal: create successor task
  3. No reply drafted unless Chris requests one

INBOX_FYI:
  1. Listed in table for visibility only
  2. No action taken

---

## Phase 5: Sequential Execution

FOR EACH approved action (in order, one at a time):
  1. Confirm action (draft already shown in Phase 3 table)
  2. IF user requested any edits: show FULL REVISED DRAFT, wait for re-approval BEFORE sending
  3. Send email via Pipedream (Tier 1, instruction singular), confirm sent
  4. Close task via Zoho CRM, confirm via re-fetch
  5. Check successor enforcement (ALL open/ongoing deals need follow-up)
  6. Create follow-up task (skip ONLY if engagement should genuinely end)
  THEN next task

NEVER execute two items simultaneously.
NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block.
NEVER skip confirmation between items.
NEVER send a modified draft without first presenting the revised version for explicit user approval.

---

## Revised Draft Approval Rule (FROM V1.6)

When a user requests ANY edits to a proposed draft, the full revised draft MUST be presented for explicit user approval BEFORE sending.

BEFORE sending any email where the user requested changes:
  1. Apply the requested edits
  2. Present the COMPLETE revised draft:

```
REVISED DRAFT (pending your approval):
Mode: Pipedream (Tier 1) | From: chrisg@stratusinfosystems.com | To: {recipients}
Subject: {subject}
---
{full revised email body}
---
Send this revised version? (yes to send, or request further changes)
```

  3. Wait for explicit approval
  4. ONLY THEN send via Pipedream

This rule applies any time the user: adds a recipient, changes tone/content, adjusts subject, or requests any wording change.

---

## Reply-All Thread Enforcement (FROM V1.6)

Before sending ANY reply to an existing email thread:
  1. Call `gmail_read_thread` with the thread ID
  2. From the MOST RECENT MESSAGE, extract all To + CC addresses
  3. Exclude chrisg@stratusinfosystems.com from recipients
  4. Use extracted addresses as To and CC for the outgoing reply

NEVER reply only to the From address if other participants are in the thread.

---

## Per-Task-Type Evaluation Gates

### DR01 Evaluation Gate (UPDATED IN V1.7)

1. Fetch deal Stage, Amount, Account_Name from Zoho
2. **CHECK DEAL STAGE FIRST:**
   - If Stage = "Closed (Won)": AUTO-CLOSE task. Note: "Deal is Closed Won — task no longer relevant." No email. No successor. Done.
   - If Stage = "Closed (Lost)": AUTO-CLOSE task. Note: "Deal is Closed Lost — task no longer relevant." No email. No successor. Done.
3. If deal is active: SEARCH GMAIL for actual last contact (MANDATORY)
4. Evaluate:
   - Deal appears fulfilled but NOT Closed Won: check for weborder, route to weborder-to-deal-automation-v1-1 if found
   - Active stage + no Gmail contact in 14+ days: Draft follow-up email
   - Active stage + recent Gmail contact (within 7 days): Close task with note, create successor
5. If closing on active deal: MUST create successor task

### DA90 Evaluation Gate

1. Check license expiration date from Account/Deal notes
2. Expired or within 30 days: Draft renewal email (use license-renewal-email skill)
3. 31-90 days out: Create reminder task
4. 90+ days out: Close task with note
5. Check for existing renewal deal — if found, close task with link to deal

### Gate Quick Reference

| Task Type | Pattern | Key Rule |
|-----------|---------|----------|
| FU30 | Subject starts with "FU30" | Route to fu30-followup-automation-v1-3 |
| DA90 | Subject starts with "DA90" | Check license expiration first |
| DR01 | Subject starts with "DR01" | Check deal stage FIRST — Closed=auto-close |
| ISR_CHECKIN | "ISR Check-In" | Look up rep via cisco-rep-locator |
| DEAL_FOLLOWUP | Linked to open deal | Gmail search mandatory |
| CW01 | Subject starts with "CW01" | Check quote status |
| SR | Subject starts with "SR" | Check service request context |
| AUTO_CLOSE | "Cisco Quote Sent", "PO Submitted" | Verify action happened |
| IR01_BATCH | Subject contains "IR01:" | Batch NEEDS_REVIEW — no sub-agent |
| NEEDS_REVIEW | Everything else | Present for manual decision |

---

## Successor Task Enforcement

Rule: ALL open/ongoing deals require a follow-up task after any action. Only skip if:
- Deal is Closed (Lost)
- Deal is Closed (Won) — already fulfilled
- Informational FU30 with no ask
- Customer explicitly declined further contact

### Enforcement Workflow

BEFORE closing a task on an active deal:
  1. Search open Tasks on the deal (excluding current task)
  2. IF other open tasks exist: OK to close
  3. IF no other open tasks: MUST create successor before closing:
     - Subject: "Follow Up: {Contact_Name} - {Company}"
     - Due_Date: 3 business days from today
     - Owner: Chris Graves (2570562000141711002)
     - What_Id: {Deal_Id}, $se_module: "Deals"

---

## Business Day Calculator

```python
from datetime import datetime, timedelta

def add_business_days(start_date, days):
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current

today = datetime.now().date()
due_date = add_business_days(today, 3)
```

---

## Companion Skills

| Skill | Version | Purpose |
|-------|---------|---------|
| zoho-crm-v28 | v28 | CRM operations, task lifecycle, cascade prevention, never-close-won, weborder check, Gmail source of truth, product_name field fix |
| zoho-crm-email-v3-5 | v3.5 | Email drafting, Pipedream-first routing, draft presentation rules, tool UUID identification |
| fu30-followup-automation-v1-3 | v1.3 | FU30 enrichment, templates, 7-day lookahead, atomic lifecycle |
| cisco-rep-locator-v1-1 | v1.1 | Cisco rep ID lookup for ISR deal assignment |
| webex-bots-v1-6 | v1.6 | Webex messaging for Cisco rep outreach |
| license-renewal-email-v1-1 | v1.1 | Renewal outreach for DA90 tasks with expiring licenses |

---

## MCP Connections Used

| Connection | Purpose |
|------------|---------|
| Zoho CRM (Composio) | Task, deal, contact, quote operations |
| Gmail (native MCP) | Thread search, context, inbox scan, reply-all extraction |
| Pipedream (UUID 4804cd9a) | Email sends, Tier 1, zero credits, parameter: instruction (SINGULAR) |
| Zapier (UUID 91a221c4) | Email sends, Tier 4 fallback only, parameter: instructions (PLURAL) |
| Webex (Cisco) | ISR check-in messages |

---

## Key Rules (Quick Reference)

### NEVER Rules

- NEVER use `not_equals` operator in Zoho CRM search queries
- NEVER fetch without the Owner filter (returns 79KB+ unreadable responses)
- NEVER launch individual sub-agents for IR01 tasks — batch-classify them
- NEVER parallelize Phase 5 execution steps
- NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block
- NEVER close without running the evaluation gate first
- NEVER manually set Deal Stage to Closed Won
- NEVER rely solely on Zoho Last_Activity_Time; always check Gmail
- NEVER skip successor task on open/ongoing deals after any action
- NEVER create duplicate tasks; always run deduplication logic first
- NEVER send a modified draft without first presenting the revised version for user approval
- NEVER reply to only the From address; extract all To + CC participants via gmail_read_thread

### Tool UUID Reference

| Tool | UUID | Parameter | Credits | Tier |
|------|------|-----------|---------|------|
| Pipedream Gmail | 4804cd9a | instruction (SINGULAR) | Zero | Tier 1 (ALWAYS FIRST) |
| Zapier Gmail | 91a221c4 | instructions (PLURAL) | Burns credits | Tier 4 (LAST RESORT) |

### Date Scope

| Workflow | Date Range |
|----------|------------|
| /DailyTasks, /CloseTasks | Due_Date <= today |
| /FU30s | Due_Date: today through +7 days |
| /InboxScan | newer_than:3d |

---

## Changelog

### v1.7 (Current)

- **CANONICAL ZOHO QUERY**: Phase 1 hardcodes the correct query. Primary: `(Owner:equals:2570562000141711002)and(Due_Date:less_equal:{TODAY})and(Status:equals:Not Started)`. Fallback for INVALID_QUERY. Banned patterns documented (no `not_equals`, no missing owner filter).
- **IR01 BATCH PRE-FILTER**: New Phase 1b step. IR01 auto-reminder tasks identified before sub-agent launch and batch-classified as NEEDS_REVIEW in a single approval table row. Prevents wasted sub-agent budget on noise tasks.
- **SUB-AGENT VERBOSITY CAP**: Sub-agent prompt now ends with explicit VERBOSITY CAP — return ONLY the structured JSON object. No prose, no preamble, no narrative. Prevents context exhaustion before Phase 3 when evaluating 20+ tasks.
- **DR01 CLOSED WON AUTO-CLOSE**: DR01 gate checks deal stage first. Closed (Won) or Closed (Lost) -> auto-close the task with a note, no email drafted, no successor created.
- **COMPANION SKILLS UPDATED**: zoho-crm-v27 -> zoho-crm-v28.
- **IR01_BATCH triage category**: Added to gate quick reference and NEVER rules.
- All v1.6 features retained.

### v1.6

- REVISED DRAFT APPROVAL RULE: Full revised draft must be shown before sending any modified email.
- REPLY-ALL THREAD ENFORCEMENT: gmail_read_thread required before any thread reply.
- All v1.5 features retained.

### v1.5

- PARALLEL SUB-AGENT EVALUATION: All tasks evaluated simultaneously in one message block.
- 5-PHASE WORKFLOW: Fetch -> Parallel eval -> Approval table -> Inbox scan -> Sequential execution.
- INLINE EMAIL DRAFT PREVIEWS: Full email body shown in approval table.
- CLICKABLE ZOHO CRM + GMAIL LINKS: All rows hyperlinked.
- All v1.4 features retained.

### v1.4

- INBOX SCAN PHASE, 4 INBOX CATEGORIES, UNIFIED BATCH TABLE, DEDUPLICATION LOGIC.

### v1.3

- NEVER MANUALLY CLOSE WON, GMAIL AS SOURCE OF TRUTH, SUCCESSOR AFTER EVERY ACTION, PIPEDREAM/ZAPIER TOOL ID.

### v1.2

- Per-Task-Type Evaluation Gates, Batch Approval Table, Successor Task Enforcement, Business Day Calculator.

### v1.1

- Slim Trigger Router, 20+ trigger phrases.

### v1.0

- Initial release.
