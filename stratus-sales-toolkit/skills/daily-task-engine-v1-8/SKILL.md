---
name: daily-task-engine-v1-8
description: "canonical zoho query with status filter, ir01 batch pre-filter, sub-agent verbosity cap (json-only return), dr01 closed-won auto-close fix, zoho-crm-v28 companion reference, and embedded chris graves voice/style guide + mandatory paragraph spacing in sub-agent prompt. parallel sub-agent task evaluation, inline email draft previews in approval table, clickable zoho crm and gmail links on every row, 5-phase workflow with task tool orchestration, inbox scan phase, never-close-won rule, weborder check in dr01 gate, gmail-first context for all deal tasks, strengthened successor enforcement after every action, pipedream/zapier tool identification, revised-draft-before-send rule, reply-all thread participant enforcement, and phase 3 pre-presentation spacing+style gate. triggers: daily tasks, review my tasks, task review, task clean up, help me complete todays tasks, close out my tasks, close tasks, what tasks are due, send fu30 emails, fu30s, 30-day check-ins, run my tasks, morning tasks, task cleanup, finish my tasks, knock out my tasks, lets do tasks, whats on my plate, clear my task list, inbox scan, check my inbox, scan my email."
---

# Daily Task Engine v1.8 (Voice/Style Guide + Paragraph Spacing Enforcement)

Trigger router with **parallel sub-agent evaluation**, **inline email draft previews in approval table**, **clickable Zoho CRM and Gmail links on every row**, **per-task-type evaluation gates**, **batch approval tables**, **gmail-first context evaluation**, **strengthened successor enforcement after every action**, **inbox scan phase for email action items**, **revised draft must be shown before sending**, **reply-all thread participant enforcement**, and **embedded Chris Graves voice/style guide with mandatory paragraph spacing in sub-agent prompt and Phase 3 pre-presentation gate**.

---

See CHANGELOG.md for what changed in each version.

---

## Trigger Patterns

### Full Daily Task Review

Triggers: /DailyTasks, "daily tasks", "review my tasks", "task review", "help me complete todays tasks", "morning tasks", "run my tasks", "lets do tasks", "whats on my plate", "knock out my tasks"

What it does:
1. Phase 0: Google Calendar morning briefing — show today's meetings, attendees, and prep notes
2. Phase 1: Pull all open tasks owned by Chris Graves, due today or overdue (canonical query)
3. Phase 1b: IR01 pre-filter — batch-classify IR01 tasks before sub-agent launch
4. Phase 2: Launch one sub-agent per non-IR01 task simultaneously (Task tool, single message block)
5. Phase 3: Pre-presentation gate (spacing + style check) → build unified approval table with clickable links, inline drafts, IR01 batch row
6. Phase 4: Run Inbox Scan in parallel while user reviews approval table
7. Phase 5: Execute approved actions sequentially (atomic task lifecycle)

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

## 6-Phase Workflow

### Overview

PHASE 0: GOOGLE CALENDAR MORNING BRIEFING (~3s)
  Fetch today's events from Google Calendar (gcal_list_events)
  Present meeting overview: time, title, attendees, location/link
  Flag any meetings with deal-linked contacts (cross-reference with Zoho task contacts)

PHASE 1: FETCH + IR01 PRE-FILTER (~5s)
  Pull all open tasks from Zoho CRM using canonical query
  IR01 pre-filter: batch-classify IR01 tasks, remove from sub-agent list

PHASE 2: PARALLEL SUB-AGENT EVALUATION (~10s flat)
  Launch one sub-agent per non-IR01 task using the Task tool
  ALL agents launched in a SINGLE message block (true parallelism)
  Each agent returns structured JSON ONLY (verbosity cap enforced)

PHASE 3: PRE-PRESENTATION GATE + BUILD APPROVAL TABLE (~5s)
  Run mandatory spacing + style check on every draft returned by sub-agents
  Then build unified approval table with clickable links, inline drafts, IR01 batch row

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

## Phase 0: Google Calendar Morning Briefing

Before pulling CRM tasks, fetch today's calendar to give Chris a quick overview of the day.

### Step 1: Fetch Today's Events

Use `gcal_list_events` with:
- `calendarId`: "primary"
- `timeMin`: today at 00:00:00 (local time, RFC3339)
- `timeMax`: today at 23:59:59 (local time, RFC3339)
- `timeZone`: "America/Los_Angeles"
- `condenseEventDetails`: false (need attendees)

### Step 2: Present Calendar Overview

Display a compact briefing table:

```
📅 TODAY'S CALENDAR — {Day, Month Date, Year}

| Time | Meeting | Attendees | Link |
|------|---------|-----------|------|
| 9:00 AM - 9:30 AM | Team Standup | 4 attendees | [Join](meet_link) |
| 11:00 AM - 12:00 PM | Acme Corp Demo | John Smith, Sarah Lee | [Join](meet_link) |
| 2:00 PM - 2:30 PM | Cisco 1:1 w/ Rep Name | rep@cisco.com | [Join](meet_link) |

{N} meetings today. {free_time_note}
```

### Step 3: Flag Deal-Linked Meetings

If any meeting attendee email matches a contact from the CRM task list (fetched in Phase 1), flag it:

```
⚡ Deal overlap: Your 11:00 AM meeting with John Smith (Acme Corp) has an open task due today.
```

This cross-reference happens AFTER Phase 1 completes. Display the flag inline with the approval table in Phase 3 if applicable.

### Step 4: No-Meeting Shortcut

If no events today, display: "📅 No meetings today — clear calendar for task focus." and proceed directly to Phase 1.

---

## Phase 1: Canonical Zoho Query

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

## Phase 1b: IR01 Batch Pre-Filter

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
5. If action = send email: draft the full email body using ALL rules below

VOICE, STYLE, SPACING, EMAIL STRUCTURE:
Follow the voice guide embedded in the task-evaluator agent definition exactly.
Canonical source: references/chris-email-voice-guide.md
Key reminders: no em dashes, blank line between every paragraph, end with question/CTA, no filler openers, no signature in draft.

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
| DA90 | Check license expiration from Account/Deal notes. Within 30 days: draft renewal email (use license-renewal-email skill). 31-90 days: propose reminder task. 90+ days: close with note. |
| DR01 | Fetch deal stage FIRST. If Closed (Won) or Closed (Lost): AUTO-CLOSE, no email, no successor. If active: Gmail search, draft follow-up if no contact in 14+ days. If fulfilled but not Closed Won: flag for weborder check. |
| DEAL_FOLLOWUP | Gmail search is mandatory. Draft follow-up if no contact in 7+ days. Return last contact date. |
| AUTO_CLOSE | Verify the action happened (quote exists, PO logged, key delivered). Return close with verification note. |
| ISR_CHECKIN | Look up Cisco rep from cisco-rep-locator hot cache. Draft Webex message or email to rep. |
| CW01 | Check quote status on linked deal. Draft quote follow-up email if customer has not responded. |
| SR | Check service request context. Return close with note or follow-up. |
| NEEDS_REVIEW | Return task details only. No proposed email. Flag for manual decision. |

---

## Phase 3: Pre-Presentation Gate

**MANDATORY: Run this gate on every email draft before building the approval table.**

For each `email_draft` returned by sub-agents, apply these checks in order:

### Check 1 — Paragraph Spacing

Scan the draft for adjacent paragraphs with no blank line between them.
- IF any two content paragraphs are adjacent without a blank line → insert blank line between them.
- IF there is no blank line before the closing line ("Thanks," or "Best,") → insert one.
- Rule: no two content paragraphs may touch. Zero exceptions.

### Check 2 — Filler Openers

If the draft opens with any of the following (or similar), rewrite the opening sentence:
- "I hope this email finds you well"
- "I hope you're doing well"
- "Hope all is well"
- "I wanted to reach out"
- "I'm reaching out to"
- Any opener that adds no information

Replace with a direct, context-setting opener (why you're writing now, what's changed, or a warm greeting that gets straight to the point).

### Check 3 — AI Phrases

Scan for these phrases and remove/replace them:
- "As an AI" → remove entirely
- "I'm delighted" → replace with "I'm glad" or rephrase naturally
- "Here is" (as a standalone lead-in) → rewrite as prose
- "In conclusion" → remove; restructure if needed
- "Dive into" → replace with "get into," "look at," or rephrase
- "Certainly" → remove or replace with "Sure" / "Of course"
- "Best regards" → replace with "Thanks," or "Best,"

### Check 4 — Em Dashes

Replace any em dash (—) with a comma, parenthesis, or period depending on context.

### Check 5 — Closing CTA

Verify the draft ends with a question or specific call to action.
- If the draft ends with a plain statement, append an appropriate closing question.
- Examples: "How does everything look?", "What has feedback been so far?", "Does that timing work for you?"

### Gate Output

After running all 5 checks, proceed to building the approval table with the corrected drafts.
No separate display is needed — the gate runs silently. If a draft required corrections, use the corrected version in the table.

---

## Phase 3: Approval Table Format

### Hyperlink Enforcement (MANDATORY)

Every entity reference in the approval table MUST be a clickable hyperlink. Never display a plain-text name when a URL is available. Required links per row:
- Task subject → `zoho_task_url`
- Account name → `zoho_account_url`
- Deal name → `zoho_deal_url`
- Contact name → `zoho_contact_url`
- Gmail thread → `gmail_thread_url`

If any sub-agent returns a row missing a URL field (e.g., `zoho_account_url` is null), construct it from the record ID: `https://crm.zoho.com/crm/org647122552/tab/{Module}/{record_id}`. If the record ID is also missing, display the name as plain text with a "(no link)" note.

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

## Revised Draft Approval Rule

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

## Reply-All Thread Enforcement

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
| zoho-crm-email-v3-5 | v3.5 | Email drafting, Pipedream-first routing, draft presentation rules, tool UUID identification, full Chris Graves style guide |
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
- NEVER skip the Phase 3 pre-presentation gate — spacing and style must be validated before the table is shown

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


---

See CHANGELOG.md for version history.
