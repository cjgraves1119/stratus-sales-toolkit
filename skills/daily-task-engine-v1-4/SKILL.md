---
name: daily-task-engine-v1-4
description: "trigger router with inbox scan phase, never-close-won rule, weborder check in DR01 gate, gmail-first context for all deal tasks, strengthened successor enforcement after every action, and pipedream/zapier tool identification. adds gmail inbox scanning for action items, suggested replies, and automatic task creation for untracked email threads. triggers: daily tasks, review my tasks, task review, task clean up, help me complete todays tasks, close out my tasks, close tasks, what tasks are due, send fu30 emails, fu30s, 30-day check-ins, run my tasks, morning tasks, task cleanup, finish my tasks, knock out my tasks, lets do tasks, whats on my plate, clear my task list, inbox scan, check my inbox, scan my email."
---

# Daily Task Engine v1.4 (Inbox Scan Phase + Never Close Won + Gmail Source of Truth + Successor After Every Action)

Trigger router with **per-task-type evaluation gates**, **batch approval tables**, **gmail-first context evaluation**, **strengthened successor enforcement after every action**, and **inbox scan phase for email action items**. All orchestration logic, lifecycle rules, and cascade prevention live in companion skills.

---

## What's New in v1.4

- **INBOX SCAN PHASE**: New phase scans Gmail inbox for actionable emails, suggests replies, and creates tasks for untracked threads. Runs after CRM task triage or standalone via `/InboxScan`.
- **4 NEW INBOX CATEGORIES**: INBOX_REPLY (needs response), INBOX_NEW_TASK (untracked thread), INBOX_DEAL_UPDATE (tracked deal email), INBOX_FYI (informational only).
- **INBOX EVALUATION PIPELINE**: 4-step process: extract key info, cross-reference Zoho CRM, categorize, determine action.
- **DEDUPLICATION LOGIC**: Prevents duplicate task creation by checking open tasks and recent closures before proposing new tasks.
- **THREAD DIRECTION CHECK**: If Chris sent last message in thread, email is FYI. If customer sent last, email may need INBOX_REPLY.
- **UNIFIED BATCH TABLE**: CRM tasks and inbox action items presented together in one approval table.
- **STANDALONE INBOX TRIGGER**: `/InboxScan` runs inbox scan independently of daily task review.
- All v1.3 features retained (never close won, Gmail source of truth, successor enforcement, Pipedream/Zapier identification)

## What's New in v1.3

- **NEVER MANUALLY CLOSE WON**: DR01 gate updated. If deal appears fulfilled but not Closed Won, check for weborder and route through weborder-to-deal-automation-v1-1 instead of manually closing.
- **GMAIL AS SOURCE OF TRUTH**: All deal-linked task evaluation gates now require searching Gmail for actual last contact BEFORE proposing any action. Zoho Last_Activity_Time is supplementary only.
- **SUCCESSOR AFTER EVERY ACTION**: ALL open/ongoing deals require a follow-up task after any action. Only skip if engagement should genuinely end (Closed Lost, informational FU30 with no ask).
- **PIPEDREAM/ZAPIER TOOL IDENTIFICATION**: Embedded UUID reference. Pipedream (4804cd9a) = `instruction` singular, zero credits, Tier 1. Zapier (91a221c4) = `instructions` plural, burns credits, Tier 4.
- **UPDATED COMPANION SKILLS**: Points to zoho-crm-v27, zoho-crm-email-v3-5, fu30-followup-automation-v1-3
- All v1.2 evaluation gates, batch approval, and routing logic retained

## What's New in v1.2

- **Per-Task-Type Evaluation Gates**: Every task type has a mandatory evaluation step before closure. "Complete" means evaluate and take action, not just close.
- **Batch Approval Table**: All tasks must be presented in a structured table with proposed actions before any execution begins.
- **Successor Task Enforcement**: Never close a task on an active deal without confirming or creating a successor task.
- **Business Day Calculator**: Embedded Python function for consistent date math (weekends skipped).
- **Picklist Protection Reference**: Reminder to use exact Zoho picklist values ("Closed (Lost)" not "Closed Lost", "Referal" not "Referral").
- **Updated Companion Skills**: Points to zoho-crm-v26, zoho-crm-email-v3-3, fu30-followup-automation-v1-2
- All v1.1 trigger patterns, triage categories, and companion skill routing retained

---

## Trigger Patterns

### Full Daily Task Review

Triggers: `/DailyTasks`, "daily tasks", "review my tasks", "task review", "help me complete todays tasks", "morning tasks", "run my tasks", "lets do tasks", "whats on my plate", "knock out my tasks"

**What it does:**
1. Pull all open tasks owned by Chris Graves, due today or overdue
2. Auto-triage into categories using pattern matching
3. **Run per-task-type evaluation gate for EVERY task** (see Evaluation Gates below)
4. Present batch approval table with proposed actions
5. **Run Inbox Scan Phase** (see Inbox Scan Phase below)
6. Present unified approval table (CRM tasks + inbox items)
7. Execute approved actions (emails, closures, follow-ups)
8. Verify each action completed successfully

**Skills to load:** zoho-crm-v27, zoho-crm-email-v3-5

### Task Cleanup (Close Only)

Triggers: `/CloseTasks`, "close out my tasks", "close tasks", "task clean up", "task cleanup", "clear my task list", "finish my tasks"

**What it does:**
1. Pull all open tasks due today or overdue
2. Auto-triage to identify tasks that can be closed
3. **Run evaluation gate for each task before proposing closure**
4. Present batch approval table
5. Close approved tasks with verification
6. No emails, no follow-ups, no inbox scan

**Skills to load:** zoho-crm-v27

### FU30 Follow-Up Emails

Triggers: `/FU30s`, "send fu30 emails", "fu30s", "30-day check-ins", "post-sale check-ins", "run fu30s", "customer check-ins", "check in on closed deals"

**What it does:**
1. Pull FU30 tasks due today through +7 days (lookahead)
2. Enrich with contact, deal, quote, invoice data
3. Search Gmail for context on high-value deals ($5k+)
4. Draft personalized check-in emails
5. Send via atomic lifecycle (send -> close -> verify -> follow-up)

**Skills to load:** zoho-crm-v27, zoho-crm-email-v3-5, fu30-followup-automation-v1-3

### Inbox Scan (Standalone)

Triggers: `/InboxScan`, "check my inbox", "inbox scan", "scan inbox", "scan my email", "what emails need attention", "any emails I need to respond to", "inbox action items", "email triage"

**What it does:**
1. Search Gmail inbox for recent actionable emails (last 3 days, unread or important)
2. Cross-reference each email against Zoho CRM contacts and deals
3. Categorize into INBOX_REPLY, INBOX_NEW_TASK, INBOX_DEAL_UPDATE, or INBOX_FYI
4. Check for existing open tasks to prevent duplicates
5. Present inbox action items in approval table
6. Execute approved actions (draft replies, create tasks, flag for follow-up)

**Skills to load:** zoho-crm-v27, zoho-crm-email-v3-5

### Triage Only (No Action)

Triggers: "what tasks are due", "show me my tasks", "task summary", "what do I have today"

**What it does:**
1. Pull all open tasks due today or overdue
2. Display triage summary table (category, count, details)
3. No actions taken, just reporting

**Skills to load:** zoho-crm-v27

---

## Inbox Scan Phase (NEW IN V1.4)

### Gmail Search Query

Default query for inbox scan:

```
is:inbox (is:unread OR is:important) newer_than:3d -from:me -from:systemgenerated@zohocrm.com -from:notifications@ -from:noreply@ -from:no-reply@ -from:mailer-daemon@ -from:calendar-notification@google.com -from:notify@webex.com
```

**Exclusions explained:**
- `-from:me` — Skip emails Chris sent (only look at incoming)
- `-from:systemgenerated@zohocrm.com` — Skip Zoho system notifications
- `-from:notifications@` — Skip generic notification senders
- `-from:noreply@` and `-from:no-reply@` — Skip automated no-reply emails
- `-from:mailer-daemon@` — Skip bounce-back messages
- `-from:calendar-notification@google.com` — Skip calendar notifications
- `-from:notify@webex.com` — Skip Webex notification emails

**Max results:** 20 emails per scan (prevents overload)

### Inbox Evaluation Pipeline

```
FOR EACH email from inbox search:
  STEP 1: EXTRACT KEY INFO
    - Sender email address
    - Sender display name
    - Subject line
    - Thread ID
    - Snippet (first ~100 chars)
    - Received date
    - Labels (IMPORTANT, STARRED, etc.)
    - Is unread?

  STEP 2: CROSS-REFERENCE ZOHO CRM
    - Search Contacts by sender email: ZohoCRM_Search_Records(module="Contacts", email="{sender_email}")
    - If contact found:
      → Get linked Account (Account_Name)
      → Search open Deals: ZohoCRM_Search_Records(module="Deals", criteria="(Account_Name.id:equals:{account_id})and(Stage:not_equals:Closed Won)and(Stage:not_equals:Closed (Lost))")
      → Search open Tasks: ZohoCRM_Search_Records(module="Tasks", criteria="(Status:not_equals:Completed)and(Owner.id:equals:2570562000141711002)")
    - If contact NOT found:
      → Flag as potential new contact/lead

  STEP 3: CATEGORIZE
    - INBOX_REPLY: Contact exists in Zoho, email requires a response, customer sent last message
    - INBOX_NEW_TASK: No matching open task or deal for this thread; needs tracking
    - INBOX_DEAL_UPDATE: Contact exists with active deal, email is deal-related update
    - INBOX_FYI: Informational only (newsletter, CC'd email, automated report, Chris sent last)

  STEP 4: DETERMINE ACTION
    - INBOX_REPLY: Draft reply using zoho-crm-email-v3-5, optionally create successor task
    - INBOX_NEW_TASK: Create Zoho task linked to Account/Deal (if exists) + draft reply
    - INBOX_DEAL_UPDATE: Flag for awareness, create successor task if no open task exists on deal
    - INBOX_FYI: Skip, note in table as informational
```

### Inbox Deduplication Logic

Before proposing any new task creation from an inbox email:

```
1. SEARCH OPEN TASKS: Match by sender name OR subject keywords
   - ZohoCRM_Search_Records(module="Tasks", criteria="(Status:not_equals:Completed)and(Owner.id:equals:2570562000141711002)")
   - Check Subject field for sender company name or key topic
   - If matching open task exists → category is INBOX_DEAL_UPDATE, not INBOX_NEW_TASK

2. SEARCH RECENT CLOSURES: Check if task was closed in last 3 days
   - ZohoCRM_Search_Records(module="Tasks", criteria="(Status:equals:Completed)and(Modified_Time:greater_equal:{3_days_ago})")
   - If recently closed task matches → likely already handled, category is INBOX_FYI

3. THREAD DIRECTION CHECK:
   - Use gmail_read_thread to get full thread
   - If Chris's reply is the LAST message: INBOX_FYI (ball is in their court)
   - If customer's message is the LAST: INBOX_REPLY (needs response)

4. ZOHO NOTIFICATION CHECK:
   - If email is from Zoho (even if not caught by exclusion) about a task/deal already in triage → INBOX_FYI
```

### Inbox Action Item Table

When running as part of `/DailyTasks`, inbox items appear AFTER CRM tasks in the unified approval table:

```
--- CRM TASKS ---
| # | Subject | Company | Type | Due | Proposed Action | Notes |
|---|---------|---------|------|-----|-----------------|-------|
| 1 | FU30: Acme Corp | Acme Corp | FU30 | Feb 27 | Send check-in email | $12k deal |
| 2 | DR01: Beta LLC | Beta LLC | DR01 | Feb 27 | Close (Closed Won) | Complete |

--- INBOX ACTION ITEMS ---
| # | From | Subject | Category | Received | Proposed Action | Context |
|---|------|---------|----------|----------|-----------------|---------|
| 3 | jon@customer.com | Re: Meraki Quote | INBOX_REPLY | Mar 1 | Draft reply | Active deal, awaiting approval |
| 4 | newlead@company.com | Network Assessment | INBOX_NEW_TASK | Mar 1 | Create task + draft reply | No Zoho contact found |
| 5 | rep@cisco.com | Deal Update | INBOX_DEAL_UPDATE | Feb 28 | Flag + successor task | Deal #12345 update |
| 6 | news@techdigest.com | Weekly Roundup | INBOX_FYI | Mar 1 | Skip | Newsletter |

PROPOSED ACTIONS:
- CRM: Send email #1, Close #2
- Inbox: Draft reply #3, Create task + reply #4, Successor task #5, Skip #6

Reply with:
  "approve all" to execute all proposed actions
  "approve #1, #3, #4" to execute specific items
  "skip #6" to remove from batch
  "edit #3 [changes]" to modify proposed action
```

When running standalone via `/InboxScan`, only the inbox section appears.

### Inbox Execution Rules

```
FOR EACH approved inbox action:
  INBOX_REPLY:
    1. Read full thread via gmail_read_thread (for context)
    2. Draft reply using zoho-crm-email-v3-5 (Chris voice, Pipedream Tier 1)
    3. Present draft for approval
    4. On approval: send via Pipedream
    5. If active deal with no open task: create successor task

  INBOX_NEW_TASK:
    1. Check if sender should be a new Zoho Contact (ask Chris if unclear)
    2. Create Zoho Task:
       - Subject: "{Topic from email} - {Sender Company or Name}"
       - Due_Date: 3 business days from today
       - Owner: Chris Graves (2570562000141711002)
       - Description: "Created from inbox scan. Original email: {subject}, from: {sender}"
       - If Account/Deal identified: link via What_Id + $se_module
    3. Draft reply if appropriate
    4. Present draft for approval, send on confirmation

  INBOX_DEAL_UPDATE:
    1. Note the update in approval table
    2. If no open task exists on the deal: create successor task
    3. No reply drafted unless Chris requests one

  INBOX_FYI:
    1. Listed in table for visibility only
    2. No action taken
```

---

## Per-Task-Type Evaluation Gates (CRITICAL, NEW IN V1.2)

**"Complete a task" means evaluate it and take appropriate action, NOT simply close it.** Every task must pass through its type-specific evaluation gate before any action is taken.

### Gate Definitions

| Task Type | Pattern | Evaluation Gate | Action if Gate Passes |
|-----------|---------|-----------------|----------------------|
| FU30 | Subject starts with "FU30" | Route to fu30-followup-automation-v1-3 for enrichment, email drafting, and atomic lifecycle | Email, close, verify, follow-up |
| DA90 | Subject starts with "DA90" | **Search Gmail first**, then check license expiration date on linked dashboard/account. If expired or expiring within 30 days, draft renewal outreach. If not expiring soon, close with note. | Renewal email or close with context |
| DR01 | Subject starts with "DR01" | **Search Gmail first**, then check linked deal status. If deal is active, determine next action. If Closed Won/Lost, close task. If deal appears fulfilled but NOT Closed Won, check for weborder (never manually close won). | Deal-appropriate action or close |
| ISR_CHECKIN | "ISR Check-In" or linked to ISR deal | **Look up Cisco rep** via cisco-rep-locator. Draft Webex message or email to rep. | Webex/email to Cisco rep |
| DEAL_FOLLOWUP | Linked to open deal, not matching other patterns | **Search Gmail for last contact date** with customer (MANDATORY, not optional). Draft follow-up if no contact in 7+ days. | Follow-up email or defer |
| CW01 | Subject starts with "CW01" | **Check deal stage and quote status**. Determine if customer needs follow-up on quote review. | Quote follow-up email |
| SR | Subject starts with "SR" | **Check service request context**. Determine if action is needed or if request was resolved. | Close with note or follow-up |
| AUTO_CLOSE | "Cisco Quote Sent", "PO Submitted", "License Key Sent" | Verify the referenced action actually happened (quote exists, PO logged, key delivered). | Close with verification |
| NEEDS_REVIEW | Everything else | Present task details to user for manual decision. Do NOT auto-close. | User decides |

### Gate Enforcement Rules

```
FOR EACH task in triage results:
  1. IDENTIFY task type from Subject pattern
  2. SEARCH GMAIL for last actual contact with customer (MANDATORY for all deal-linked tasks)
  3. RUN the evaluation gate for that type (with Gmail context)
  4. DETERMINE proposed action based on gate result
  5. ADD to batch approval table with proposed action and Gmail last-contact date

NEVER close a task without running its evaluation gate.
NEVER assume a task is "done" just because it exists.
NEVER rely solely on Zoho Last_Activity_Time; always check Gmail first.
NEVER manually set a Deal to Closed Won (deals auto-close when PO is attached).
"Complete my tasks" = evaluate each one and take appropriate action.
```

### DA90 Evaluation Gate (Detailed)

DA90 tasks are dashboard review tasks. The gate requires checking the customer's license status:

```
1. Get linked Deal or Account from task (What_Id or parse from Subject)
2. Search for Meraki Dashboard record or check Account license dates
3. Determine license expiration:
   - Expired or within 30 days: Draft renewal email (use license-renewal-email skill)
   - 31-90 days out: Create reminder task for closer to expiration
   - 90+ days out: Close task with note "Licenses not expiring soon, next review scheduled"
4. Check for existing renewal deal: If exists, close task with link to deal
```

### DR01 Evaluation Gate (Detailed, UPDATED V1.3)

DR01 tasks are deal review tasks. The gate checks the deal's current status:

```
1. Get linked Deal from What_Id
2. Fetch deal: Stage, Amount, Last_Activity_Time, Account_Name
3. SEARCH GMAIL for actual last contact with customer (MANDATORY)
4. Evaluate:
   - Closed Won: Close task (deal complete)
   - Closed (Lost): Close task (deal dead)
   - Deal appears fulfilled but NOT Closed Won:
     → NEVER manually close won
     → Check for weborder (search Sales_Orders or Gmail for order confirmation)
     → If weborder found: route to weborder-to-deal-automation-v1-1
     → If no weborder: flag for manual review
   - Active stage + Gmail shows no contact > 14 days: Draft follow-up email
   - Active stage + Gmail shows recent contact: Close task with note "Deal active, last Gmail contact on [date]"
5. If closing on active deal: MUST create successor task (see Successor Enforcement)
6. ALL actions on open/ongoing deals require successor task creation
```

---

## Batch Approval Table (CRITICAL, NEW IN V1.2)

Before executing ANY actions, present ALL tasks in a single approval table. This prevents the user from losing visibility into what's happening.

### Table Format

```
TASK TRIAGE SUMMARY, [Date]
Total: [X] tasks | Due today: [Y] | Overdue: [Z] | Inbox items: [N]

| # | Subject | Company | Type | Due | Proposed Action | Notes |
|---|---------|---------|------|-----|-----------------|-------|
| 1 | FU30: Acme Corp | Acme Corp | FU30 | Feb 27 | Send check-in email | $12k deal, hardware |
| 2 | DA90: Beta LLC | Beta LLC | DA90 | Feb 25 | Draft renewal (expires Mar 15) | 4x MR licenses |
| 3 | DR01: Gamma Inc | Gamma Inc | DR01 | Feb 27 | Close (Closed Won) | Deal completed Feb 20 |
| 4 | Cisco Quote Sent, Delta | Delta Co | AUTO_CLOSE | Feb 26 | Close (quote confirmed) | Q-12345 |
| 5 | Follow up, Epsilon | Epsilon Ltd | DEAL_FU | Feb 24 | Draft follow-up email | No contact since Feb 10 |
| 6 | Review pricing request | Zeta Inc | NEEDS_REVIEW | Feb 27 | Manual review needed | Unclear next step |

PROPOSED ACTIONS:
- Send emails: #1, #2, #5
- Close tasks: #3, #4
- Manual review: #6

Reply with:
  "approve all" to execute all proposed actions
  "approve #1, #3, #4" to execute specific items
  "skip #2" to remove from batch
  "edit #5 [changes]" to modify proposed action
```

### Approval Rules

- All email drafts shown individually after batch approval
- Each email still requires "send" confirmation (or "send all" for batch)
- Task closures happen only after associated emails are confirmed sent
- Manual review items are never auto-actioned

---

## Successor Task Enforcement (CRITICAL, STRENGTHENED IN V1.3)

**Rule: ALL open/ongoing deals always require a follow-up task for next steps after any action.** Only skip successor if engagement should genuinely end (deal Closed Lost, informational FU30 with no ask, customer explicitly declined further contact).

### When It Applies

Any task where:
- The linked Deal (What_Id) is in an active stage: Qualification, Proposal/Negotiation, Verbal Commit/Invoicing
- The task is being closed (Status to Completed)
- An email was sent on a deal (even if task isn't being closed)
- A quote was created or updated on a deal
- An inbox email on an active deal has no open task (INBOX_DEAL_UPDATE with no successor)

### Enforcement Workflow

```
BEFORE closing a task on an active deal:
  1. Search Tasks: (What_Id:equals:{Deal_Id}) and (Status:not_equals:Completed) and (id:not_equals:{current_task_id})
  2. IF other open tasks exist on this deal: OK to close (successor exists)
  3. IF no other open tasks: MUST create a successor task before closing
     - Subject: "Follow Up: {Contact_Name} - {Company}"
     - Due_Date: 3 business days from today (use business day calculator)
     - Owner: Chris Graves (2570562000141711002)
     - What_Id: {Deal_Id}, $se_module: "Deals"
```

---

## Business Day Calculator (Embedded)

```python
from datetime import datetime, timedelta

def add_business_days(start_date, days):
    """Add business days to a date, skipping weekends."""
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday=0, Friday=4
            added += 1
    return current

# Usage: 3 business days from today
today = datetime.now().date()
due_date = add_business_days(today, 3)
# Friday Feb 27 + 3 business days = Wednesday Mar 4
```

---

## Companion Skills (REQUIRED)

All execution logic lives in these skills. Load them before running any workflow.

| Skill | Version | Purpose |
|-------|---------|---------|
| zoho-crm-v27 | v27 | CRM operations, task lifecycle, cascade prevention, never-close-won, weborder check, Gmail source of truth |
| zoho-crm-email-v3-5 | v3.5 | Email drafting, style guide, Pipedream-first routing, draft presentation rules, tool UUID identification |
| fu30-followup-automation-v1-3 | v1.3 | FU30 enrichment, templates, 7-day lookahead, atomic lifecycle, Pipedream-first routing |
| cisco-rep-locator-v1-1 | v1.1 | Cisco rep ID lookup for ISR deal assignment |
| webex-bots-v1-5 | v1.5 | Webex messaging for Cisco rep outreach |
| license-renewal-email-v1-1 | v1.1 | Renewal outreach for DA90 tasks with expiring licenses |

---

## MCP Connections Used

| Connection | Purpose |
|------------|---------|
| Zoho CRM (Composio) | Task, deal, contact, quote operations |
| Gmail (native MCP) | Thread search, context for email drafts, inbox scan |
| Pipedream (UUID 4804cd9a) | Email sends, Tier 1, zero credits, parameter: `instruction` (SINGULAR) |
| Zapier (UUID 91a221c4) | Email sends, Tier 4 fallback only, burns credits, parameter: `instructions` (PLURAL) |
| Webex (Cisco) | ISR check-in messages |
| Google Calendar (optional) | Meeting context for follow-up scheduling |

---

## Key Rules (Quick Reference)

These rules are fully documented in the companion skills. This is a reminder checklist.

### Date Scope

| Workflow | Date Range |
|----------|------------|
| /DailyTasks, /CloseTasks | Due_Date <= today (NEVER future-dated) |
| /FU30s | Due_Date: today through +7 days |
| /InboxScan | newer_than:3d (last 3 days, unread or important) |

### Triage Categories

| Category | Pattern | Action |
|----------|---------|--------|
| AUTO_CLOSE | "Cisco Quote Sent", "PO Submitted", "License Key Sent" | Verify action happened, then close (with approval) |
| FU30_EMAIL | Subject starts with "FU30" | Route to fu30-followup-automation-v1-3 |
| DA90_REVIEW | Subject starts with "DA90" | Check license expiration, then renew or close |
| DR01_REVIEW | Subject starts with "DR01" | Check deal status, then follow up or close |
| DEAL_FOLLOWUP | Linked to open deal | Search Gmail, draft follow-up if needed |
| ISR_CHECKIN | "ISR Check-In" or linked to ISR deal | Route to cisco-rep-locator + webex |
| QUOTE_ACTION | "Send Quote" or quote-related | Draft quote delivery email |
| INBOX_REPLY | Email needs response (customer sent last) | Draft reply, optionally create task |
| INBOX_NEW_TASK | New thread, no Zoho tracking | Create Zoho task + draft reply |
| INBOX_DEAL_UPDATE | Email on tracked deal | FYI or successor task if stale |
| INBOX_FYI | Informational email | Skip, note in table |
| NEEDS_REVIEW | Everything else | Present for manual decision |

### Atomic Task Lifecycle

```
FOR EACH actionable task:
  1. Search Gmail for last actual contact with customer (MANDATORY for deal-linked tasks)
  2. Run evaluation gate for task type (with Gmail context)
  3. Present proposed action in batch approval table
  4. After approval: Send email via Pipedream (Tier 1), confirm sent
  5. Complete task, confirm via re-fetch
  6. Check successor enforcement (ALL open/ongoing deals need follow-up)
  7. Create follow-up task (skip ONLY if engagement should genuinely end)
  THEN next task

FOR EACH approved inbox action:
  1. Read full thread for context (gmail_read_thread)
  2. Draft reply or create task per category rules
  3. Present draft for approval
  4. Execute on confirmation
  5. Check successor enforcement for deal-linked items
  THEN next inbox item

NEVER parallelize these steps.
NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block.
NEVER close without running the evaluation gate first.
NEVER manually set Deal Stage to Closed Won.
NEVER rely solely on Zoho Last_Activity_Time; always check Gmail.
NEVER skip successor task on open/ongoing deals after any action.
NEVER create duplicate tasks; always run deduplication logic first.
```

### Approval Gates

- All email drafts require explicit "send" approval
- All task closures require explicit approval
- All inbox reply drafts require explicit "send" approval
- All new task creations from inbox require explicit approval
- Batch operations require "approve all" or per-item confirmation
- Manual review items are never auto-actioned

### Picklist Protection

- Deal Stage: Always use LIVE validation via ZohoCRM_Get_Field (see zoho-crm-v27)
- NEVER manually set Closed Won (deals auto-close when PO attached, see zoho-crm-v27)
- "Closed (Lost)" with parentheses, exact spelling
- "Referal" with one R (matches Zoho picklist exactly)
- Never create new picklist values; if value doesn't match, ask user

---

## Changelog

### v1.4 (Current)

- **INBOX SCAN PHASE**: New phase scans Gmail inbox for actionable emails needing replies, task creation, or deal follow-up
- **4 INBOX CATEGORIES**: INBOX_REPLY, INBOX_NEW_TASK, INBOX_DEAL_UPDATE, INBOX_FYI with distinct action paths
- **INBOX EVALUATION PIPELINE**: 4-step process (extract, cross-reference Zoho, categorize, determine action)
- **DEDUPLICATION LOGIC**: Checks open tasks + recent closures before proposing new task creation
- **THREAD DIRECTION CHECK**: Who sent last determines if email is INBOX_REPLY or INBOX_FYI
- **UNIFIED BATCH TABLE**: CRM tasks and inbox items in one approval table for /DailyTasks
- **STANDALONE /InboxScan TRIGGER**: Run inbox scan independently of daily task review
- **INBOX EXECUTION RULES**: Per-category action workflows with approval gates
- All v1.3 features retained (never close won, Gmail source of truth, successor enforcement, Pipedream/Zapier ID)

### v1.3

- **NEVER MANUALLY CLOSE WON**: DR01 gate updated to check for weborder instead of manually closing fulfilled deals
- **GMAIL AS SOURCE OF TRUTH**: All deal-linked task evaluation gates now require Gmail search before proposing actions
- **SUCCESSOR AFTER EVERY ACTION**: Strengthened to require follow-up on ALL open/ongoing deals, not just task closures
- **PIPEDREAM/ZAPIER TOOL ID**: UUID and parameter reference embedded to prevent tool confusion
- **DR01 WEBORDER CHECK**: Fulfilled-but-not-closed deals routed to weborder-to-deal-automation-v1-1
- **UPDATED COMPANION SKILLS**: zoho-crm-v27, zoho-crm-email-v3-5, fu30-followup-automation-v1-3
- All v1.2 evaluation gates, batch approval, and routing logic retained

### v1.2

- **Per-Task-Type Evaluation Gates**: DA90, DR01, FU30, ISR, Deal FU, CW01, SR, AUTO_CLOSE, NEEDS_REVIEW
- **Batch Approval Table**: Structured table with proposed actions before execution
- **Successor Task Enforcement**: Active deals must have open tasks; create if missing
- **Business Day Calculator**: Embedded Python function for consistent date math
- **Picklist Protection Reference**: Exact value reminders to prevent silent picklist corruption
- **Updated Companion Skills**: zoho-crm-v26, zoho-crm-email-v3-3, fu30-followup-automation-v1-2
- All v1.1 trigger patterns, triage categories, and routing logic retained

### v1.1

- **Slim Trigger Router**: Removed orchestration logic (now in companion skills)
- **Expanded Triggers**: 20+ natural language phrases for automatic matching
- **Updated Companion Skills**: zoho-crm-v23, zoho-crm-email-v3-2, fu30-followup-automation-v1-1
- **Quick Reference Rules**: Kept key rules as a checklist (full logic in companions)

### v1.0

- Initial release as full orchestrator (619 lines)
- 6-phase workflow with batch operations and atomic task lifecycle
- Cascade prevention, triage categories, date scope enforcement
- All logic embedded directly (later moved to companion skills in v1.1)
