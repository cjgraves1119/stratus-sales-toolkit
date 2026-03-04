---
name: daily-task-engine-v1-6
description: "parallel sub-agent task evaluation, inline email draft previews in approval table, clickable zoho crm and gmail links on every row, 5-phase workflow with task tool orchestration, inbox scan phase, never-close-won rule, weborder check in dr01 gate, gmail-first context for all deal tasks, strengthened successor enforcement after every action, pipedream/zapier tool identification, revised-draft-before-send rule, and reply-all thread participant enforcement. triggers: daily tasks, review my tasks, task review, task clean up, help me complete todays tasks, close out my tasks, close tasks, what tasks are due, send fu30 emails, fu30s, 30-day check-ins, run my tasks, morning tasks, task cleanup, finish my tasks, knock out my tasks, lets do tasks, whats on my plate, clear my task list, inbox scan, check my inbox, scan my email."
---

# Daily Task Engine v1.6 (Revised Draft Approval + Reply-All Thread Enforcement)

Trigger router with **parallel sub-agent evaluation**, **inline email draft previews in approval table**, **clickable Zoho CRM and Gmail links on every row**, **per-task-type evaluation gates**, **batch approval tables**, **gmail-first context evaluation**, **strengthened successor enforcement after every action**, **inbox scan phase for email action items**, **revised draft must be shown before sending**, and **reply-all thread participant enforcement**.

---

## What's New in v1.6

- **REVISED DRAFT APPROVAL RULE**: When a user requests any edits or modifications to a proposed email draft, the FULL REVISED draft must be presented for explicit user approval before sending. NEVER send a modified draft without showing the updated version first. This applies to all email sends, including inbox replies, follow-ups, and any email where the user requested changes after the initial draft was shown.
- **REPLY-ALL THREAD ENFORCEMENT**: Before sending ANY reply to an existing email thread, call `gmail_read_thread` to read the full thread and extract ALL recipients (To + CC) from the most recent message. Include all of them in the reply. NEVER reply only to the primary From address. The thread may have multiple participants (e.g., Braden started a thread, Ryan was CC'd -- both must be included in any reply).
- All v1.5 features retained (parallel sub-agents, inline drafts, clickable links, 5-phase workflow, inbox scan, never-close-won, Gmail source of truth, successor enforcement, Pipedream/Zapier ID)

## What's New in v1.5

- **PARALLEL SUB-AGENT EVALUATION**: All tasks evaluated simultaneously using the Task tool. One sub-agent per task, all launched in a single message block. Reduces evaluation time from sequential (N x 10s) to parallel (~10s flat regardless of task count).
- **INLINE EMAIL DRAFT PREVIEWS**: Approval table includes the full proposed email body for every actionable item. User approves the actual message being sent, not just "send follow-up email."
- **CLICKABLE ZOHO CRM LINKS**: Every task row includes hyperlinked Task, Deal, Contact, and Account links using the pattern https://crm.zoho.com/crm/org647122552/tab/{MODULE}/{RECORD_ID}.
- **CLICKABLE GMAIL THREAD LINKS**: Every inbox row and deal context reference includes https://mail.google.com/mail/u/0/#all/{THREAD_ID} for direct access.
- **5-PHASE WORKFLOW**: Phase 1 (fetch) -> Phase 2 (parallel sub-agent evaluation) -> Phase 3 (build approval table with drafts + links) -> Phase 4 (inbox scan, runs in parallel during user review) -> Phase 5 (sequential execution).
- All v1.4 features retained (inbox scan, never close won, Gmail source of truth, successor enforcement, Pipedream/Zapier ID)

## What's New in v1.4

- **INBOX SCAN PHASE**: New phase scans Gmail inbox for actionable emails, suggests replies, and creates tasks for untracked threads. Runs after CRM task triage or standalone via /InboxScan.
- **4 NEW INBOX CATEGORIES**: INBOX_REPLY (needs response), INBOX_NEW_TASK (untracked thread), INBOX_DEAL_UPDATE (tracked deal email), INBOX_FYI (informational only).
- **INBOX EVALUATION PIPELINE**: 4-step process: extract key info, cross-reference Zoho CRM, categorize, determine action.
- **DEDUPLICATION LOGIC**: Prevents duplicate task creation by checking open tasks and recent closures before proposing new tasks.
- **THREAD DIRECTION CHECK**: If Chris sent last message in thread, email is FYI. If customer sent last, email may need INBOX_REPLY.
- **UNIFIED BATCH TABLE**: CRM tasks and inbox action items presented together in one approval table.
- **STANDALONE INBOX TRIGGER**: /InboxScan runs inbox scan independently of daily task review.
- All v1.3 features retained (never close won, Gmail source of truth, successor enforcement, Pipedream/Zapier identification)

## What's New in v1.3

- **NEVER MANUALLY CLOSE WON**: DR01 gate updated. If deal appears fulfilled but not Closed Won, check for weborder and route through weborder-to-deal-automation-v1-1 instead of manually closing.
- **GMAIL AS SOURCE OF TRUTH**: All deal-linked task evaluation gates now require searching Gmail for actual last contact BEFORE proposing any action. Zoho Last_Activity_Time is supplementary only.
- **SUCCESSOR AFTER EVERY ACTION**: ALL open/ongoing deals require a follow-up task after any action. Only skip if engagement should genuinely end (deal Closed Lost, informational FU30 with no ask).
- **PIPEDREAM/ZAPIER TOOL IDENTIFICATION**: Embedded UUID reference. Pipedream (4804cd9a) = instruction singular, zero credits, Tier 1. Zapier (91a221c4) = instructions plural, burns credits, Tier 4.
- **UPDATED COMPANION SKILLS**: Points to zoho-crm-v27, zoho-crm-email-v3-5, fu30-followup-automation-v1-3
- All v1.2 evaluation gates, batch approval, and routing logic retained

---

## Trigger Patterns

### Full Daily Task Review

Triggers: /DailyTasks, "daily tasks", "review my tasks", "task review", "help me complete todays tasks", "morning tasks", "run my tasks", "lets do tasks", "whats on my plate", "knock out my tasks"

What it does:
1. Phase 1: Pull all open tasks owned by Chris Graves, due today or overdue
2. Phase 2: Launch one sub-agent per task simultaneously (Task tool, single message block)
3. Phase 3: Collect sub-agent results, build unified approval table with inline email drafts and clickable links
4. Phase 4: Run Inbox Scan in parallel while user reviews approval table
5. Phase 5: Execute approved actions sequentially (atomic task lifecycle)

Skills to load: zoho-crm-v27, zoho-crm-email-v3-5

### Task Cleanup (Close Only)

Triggers: /CloseTasks, "close out my tasks", "close tasks", "task clean up", "task cleanup", "clear my task list", "finish my tasks"

What it does:
1. Pull all open tasks due today or overdue
2. Auto-triage to identify tasks that can be closed
3. Run evaluation gate for each task before proposing closure
4. Present batch approval table with clickable links
5. Close approved tasks with verification
6. No emails, no follow-ups, no inbox scan

Skills to load: zoho-crm-v27

### 30-Day Follow-Up Emails

Triggers: /FU30s, "send fu30 emails", "fu30s", "30-day check-ins", "post-sale check-ins", "run fu30s", "customer check-ins", "check in on closed deals"

What it does:
1. Pull 30-Day Follow-Up tasks due today through +7 days (lookahead)
2. Enrich with contact, deal, quote, invoice data
3. Search Gmail for context on high-value deals ($5k+)
4. Draft personalized check-in emails (shown inline in approval table)
5. Send via atomic lifecycle (send -> close -> verify -> follow-up)

Skills to load: zoho-crm-v27, zoho-crm-email-v3-5, fu30-followup-automation-v1-3

### Inbox Scan (Standalone)

Triggers: /InboxScan, "check my inbox", "inbox scan", "scan inbox", "scan my email", "what emails need attention", "inbox action items", "email triage"

What it does:
1. Search Gmail inbox for recent actionable emails (last 3 days, unread or important)
2. Cross-reference each email against Zoho CRM contacts and deals
3. Categorize into INBOX_REPLY, INBOX_NEW_TASK, INBOX_DEAL_UPDATE, or INBOX_FYI
4. Present inbox action items in approval table with inline draft previews and Gmail thread links
5. Execute approved actions

Skills to load: zoho-crm-v27, zoho-crm-email-v3-5

### Triage Only (No Action)

Triggers: "what tasks are due", "show me my tasks", "task summary", "what do I have today"

What it does:
1. Pull all open tasks due today or overdue
2. Display triage summary table (category, count, details, clickable links)
3. No actions taken, just reporting

Skills to load: zoho-crm-v27

---

## 5-Phase Workflow (NEW IN V1.5)

### Overview

PHASE 1: FETCH (sequential, ~5s)
  Pull all open tasks from Zoho CRM (due today or overdue)
  Auto-triage into categories

PHASE 2: PARALLEL SUB-AGENT EVALUATION (~10s flat, regardless of task count)
  Launch one sub-agent per task using the Task tool
  ALL agents launched in a SINGLE message block (true parallelism)
  Each agent: fetches linked deal/contact, searches Gmail, runs evaluation gate, drafts email if needed
  Agents return structured result objects

PHASE 3: BUILD APPROVAL TABLE (~5s)
  Collect all sub-agent results
  Build unified approval table with:
    - Clickable Zoho CRM links (Task, Deal, Contact, Account)
    - Clickable Gmail thread links
    - Inline email draft preview for every actionable item
  Present to user for approval

PHASE 4: INBOX SCAN (runs in parallel while user reviews Phase 3 table)
  Announce: "Scanning inbox while you review the table above..."
  Run Gmail inbox search + Zoho cross-reference
  Append inbox items to approval table (or show as follow-up table)

PHASE 5: SEQUENTIAL EXECUTION
  For each approved item: atomic task lifecycle
  send -> confirm -> close -> verify -> successor
  NEVER parallelize execution steps
  NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block

### Phase 2: Sub-Agent Launch Pattern

CRITICAL: All sub-agents launched in ONE message block for true parallelism.

Each sub-agent receives this prompt structure:

"Evaluate Zoho task ID {task_id}:
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
   (Chris Graves voice, no em dashes, 1-3 lines per paragraph, end with question or call to action)

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
}"

### Phase 2: Sub-Agent Instructions by Task Type

| Task Type | Key Sub-Agent Instructions |
|-----------|---------------------------|
| FU30 | Use fu30 enrichment logic. Get quote total from linked Quote. Check for open invoices. Gmail search for post-sale context. Draft friendly check-in. |
| DA90 | Check license expiration date from Account or Deal notes. If within 30 days: draft renewal email. If 31-90 days: propose reminder task. If 90+ days: close with note. |
| DR01 | Fetch deal stage. Gmail search for last contact. If active + no contact in 14+ days: draft follow-up. If fulfilled but not Closed Won: flag for weborder check. If Closed Won/Lost: close. |
| DEAL_FOLLOWUP | Gmail search is mandatory. Draft follow-up if no contact in 7+ days. Return last contact date. |
| AUTO_CLOSE | Verify the action happened (quote exists, PO logged, key delivered). Return close with verification note. |
| ISR_CHECKIN | Look up Cisco rep from cisco-rep-locator hot cache. Draft Webex message or email to rep. |
| CW01 | Check quote status on linked deal. Draft quote follow-up email if customer has not responded. |
| SR | Check deal/task context for service request resolution. Return close with note or follow-up. |
| NEEDS_REVIEW | Return task details only. No proposed email. Flag for manual decision. |

### Phase 3: Approval Table Format

Every row must follow this structure:

**#{N} - [{Task Subject}]({zoho_task_url})** | {task_type} | Due: {due_date}
Company: [{Account Name}]({zoho_account_url})
Deal: [{Deal Name} -- ${amount}]({zoho_deal_url}) | Stage: {stage}
Contact: [{Contact Name}]({zoho_contact_url}) ({contact_email})
Last Gmail Contact: {date} -- [View thread]({gmail_thread_url})
Proposed Action: {action}

(for actionable items only)
EMAIL DRAFT:
Subject: {email_subject}
---
{full email body}
---

Example approval table:

TASK TRIAGE SUMMARY -- {Date}
Total: {X} tasks | Due today: {Y} | Overdue: {Z} | Inbox items: {N}
Evaluation: {X} sub-agents ran in parallel

--- CRM TASKS ---

**#1 - [FU30: Acme Corp](https://crm.zoho.com/crm/org647122552/tab/Tasks/12345)** | FU30 | Due: Feb 27
Company: [Acme Corp](https://crm.zoho.com/crm/org647122552/tab/Accounts/67890)
Deal: [Acme Meraki Upgrade -- $12,400](https://crm.zoho.com/crm/org647122552/tab/Potentials/11111) | Stage: Closed Won
Contact: [John Smith](https://crm.zoho.com/crm/org647122552/tab/Contacts/22222) (john@acme.com)
Last Gmail Contact: Feb 15 -- [View thread](https://mail.google.com/mail/u/0/#all/abc123)
Proposed Action: Send 30-day check-in email

EMAIL DRAFT:
Subject: Checking In -- Acme Corp Meraki Deployment
---
Hey John!

Wanted to touch base now that your Meraki deployment has had a chance to settle in. How's everything running on your end? Any questions come up that I can help with?

Also wanted to make sure you're aware of your co-term window -- happy to get ahead of renewals whenever you're ready.

How does everything look so far?

Best,
Chris
---

---

**#2 - [DR01: Beta LLC](https://crm.zoho.com/crm/org647122552/tab/Tasks/33333)** | DR01 | Due: Feb 25 (OVERDUE)
Company: [Beta LLC](https://crm.zoho.com/crm/org647122552/tab/Accounts/44444)
Deal: [Beta License Renewal -- $8,200](https://crm.zoho.com/crm/org647122552/tab/Potentials/55555) | Stage: Proposal/Negotiation
Contact: [Sarah Lee](https://crm.zoho.com/crm/org647122552/tab/Contacts/66666) (sarah@beta.com)
Last Gmail Contact: Feb 10 -- [View thread](https://mail.google.com/mail/u/0/#all/def456)
License Expiration: Mar 15 (18 days out -- URGENT)
Proposed Action: Draft renewal outreach

EMAIL DRAFT:
Subject: Heads Up -- Beta LLC Meraki Licenses Expiring Mar 15
---
Hey Sarah,

Just flagging that your Meraki licenses are coming up for renewal on March 15 -- about 18 days out. Wanted to make sure we're not caught off guard.

I can get a renewal quote over to you right away. Do you have a preferred term length, or should I match what you have now?

Best,
Chris
---

PROPOSED ACTIONS SUMMARY:
- Send emails: #1, #2
- Close tasks: #3
- Manual review: #4

Reply with:
  "approve all" -- execute all proposed actions
  "approve #1, #3" -- execute specific items
  "skip #2" -- remove from batch
  "edit #1 [changes]" -- modify proposed action or draft before sending

### Phase 4: Inbox Scan During Review

When running as part of /DailyTasks, announce inbox scan immediately after presenting the Phase 3 table:

"Scanning your inbox while you review -- I'll add any action items below."

Run inbox scan in parallel with user review time. Append results labeled "--- INBOX ACTION ITEMS ---". If user approves before scan completes, note it and present inbox items as a follow-up table.

Inbox rows also include inline email drafts and Gmail thread links:

**#{N} - INBOX_REPLY** | From: {sender} | [View thread]({gmail_thread_url})
Subject: {email_subject} | Received: {date}
Deal: [{Deal Name}]({zoho_deal_url}) (if applicable)
Proposed Action: Draft reply

EMAIL DRAFT:
Subject: Re: {original_subject}
---
{full email body}
---

### Phase 5: Sequential Execution

FOR EACH approved action (in order, one at a time):
  1. Confirm action (draft already shown in Phase 3 table)
  2. IF user requested any edits/modifications to the draft: show revised draft and wait for re-approval BEFORE sending (see Revised Draft Approval Rule below)
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

## Revised Draft Approval Rule (NEW IN V1.6)

### Rule

When a user requests ANY edits, changes, or modifications to a proposed email draft (whether it was originally shown in the approval table or as an inline draft), the full revised draft MUST be presented for explicit user approval BEFORE sending.

NEVER auto-send a modified draft. The fact that the user asked for the change does not constitute approval to send.

### Enforcement

BEFORE sending any email where the user requested changes:
  1. Apply the requested edits to the draft
  2. Present the COMPLETE revised draft in the following format:

REVISED DRAFT (pending your approval):
Mode: Pipedream (Tier 1) | From: chrisg@stratusinfosystems.com | To: {recipients}
Subject: {subject}
---
{full revised email body}
---

Send this revised version? (yes to send, or request further changes)

  3. Wait for explicit approval ("yes", "send it", "looks good", "approve", etc.)
  4. ONLY THEN send via Pipedream

### What Counts as a Modification

This rule applies any time the user:
- Asks to "loop in" or add an additional recipient
- Changes the tone, content, or ask of the email
- Adds or removes information from the draft
- Asks to adjust the subject line
- Requests any wording change, however small

### What Does NOT Require Re-Approval

- Simple approval of the original draft as-is ("approve #1", "send it", "looks good")
- Cases where the original draft was ALREADY the revised version (i.e., no changes were requested after it was shown)

---

## Reply-All Thread Enforcement (NEW IN V1.6)

### Rule

Before sending ANY reply to an existing email thread (inbox replies, follow-up responses, or any email sent as a reply to a previous thread), call `gmail_read_thread` to read the full thread and extract ALL participants from the most recent message.

Include ALL of those participants in the reply (To + CC), not just the primary sender.

NEVER reply only to the From address of a thread if other participants are listed in the To or CC fields.

### Enforcement Steps

FOR EACH inbox reply or thread reply being executed in Phase 5:
  1. Call `gmail_read_thread` with the thread ID
  2. From the MOST RECENT MESSAGE in the thread, extract:
     - All addresses in the To field
     - All addresses in the CC field
     - Exclude Chris Graves' own address (chrisg@stratusinfosystems.com) from recipients
  3. Use those extracted addresses as the To and CC for the outgoing reply
  4. If the resulting recipient list differs from what was originally shown in the draft, update the draft to reflect the correct recipients before presenting for approval

### Example

Thread has:
- Message from Braden (bradens@company.com) To: chris
- Chris replied To: Braden, CC: Ryan
- Ryan replied To: chris, CC: Braden

Correct reply-all: To: ryand@company.com, BradenS@company.com (all participants except Chris)
WRONG: To: ryand@company.com only (dropped Braden)

### Recipient Deduplication

If the same email address appears in both To and CC across different messages in the thread, place them in To. Avoid duplicate addresses in the final recipient list.

---

## Clickable Link Format (NEW IN V1.5)

### Zoho CRM Link Patterns

Tasks:    https://crm.zoho.com/crm/org647122552/tab/Tasks/{RECORD_ID}
Deals:    https://crm.zoho.com/crm/org647122552/tab/Potentials/{RECORD_ID}
Contacts: https://crm.zoho.com/crm/org647122552/tab/Contacts/{RECORD_ID}
Accounts: https://crm.zoho.com/crm/org647122552/tab/Accounts/{RECORD_ID}
Quotes:   https://crm.zoho.com/crm/org647122552/tab/Quotes/{RECORD_ID}

### Gmail Link Pattern

Thread:   https://mail.google.com/mail/u/0/#all/{THREAD_ID}

### Link Placement Rules

Every approval table row MUST include:
- Task name as clickable link to Zoho Task
- Company name as clickable link to Zoho Account
- Deal name + amount as clickable link to Zoho Deal (if deal exists)
- Contact name as clickable link to Zoho Contact (if contact exists)
- "View thread" as clickable link to Gmail thread (if Gmail context was found)

Every end-of-run summary MUST include clickable links to:
- Closed tasks
- Sent email threads (Gmail link if thread ID available)
- Created successor tasks

### Markdown Link Syntax

[Task Subject](https://crm.zoho.com/crm/org647122552/tab/Tasks/{id})
[Account Name](https://crm.zoho.com/crm/org647122552/tab/Accounts/{id})
[Deal Name -- $X,XXX](https://crm.zoho.com/crm/org647122552/tab/Potentials/{id})
[Contact Name](https://crm.zoho.com/crm/org647122552/tab/Contacts/{id})
[View thread](https://mail.google.com/mail/u/0/#all/{thread_id})

---

## Inline Email Draft Rules (NEW IN V1.5)

### When to Include a Draft

Include an inline email draft in the approval table for EVERY action where an email will be sent:
- FU30 check-in emails
- DA90 renewal outreach
- DR01 and DEAL_FOLLOWUP follow-up emails
- CW01 quote follow-up emails
- ISR_CHECKIN Cisco rep emails or Webex messages
- INBOX_REPLY replies
- INBOX_NEW_TASK reply drafts

Do NOT include a draft for:
- AUTO_CLOSE (no email, just close)
- NEEDS_REVIEW (no action proposed)
- INBOX_FYI (no action taken)
- Task closures with no associated email

### Draft Format

EMAIL DRAFT:
Subject: {subject line}
---
{full email body}
---

### Draft Voice Rules (Apply to All Sub-Agent Email Drafts)

- Friendly and confident, never stiff
- 1-3 lines per paragraph max
- NO em dashes (use commas, parentheses, or periods instead)
- Use contractions naturally: I'll, you're, that's, we've, can't, won't
- End every email with a question or specific call to action
- Never start with "I hope this email finds you well"
- Never use "Best regards" (use "Best," or "Thanks,")
- Anchor urgency to real deadlines when applicable

### Draft Approval Flow

After user approves an item with a draft:
1. Present the draft one more time with send confirmation ("Sending this now...")
2. IF the user requested any changes to the draft: apply changes, show FULL REVISED DRAFT, and wait for re-approval (see Revised Draft Approval Rule section above)
3. ONLY after explicit re-approval of any revisions: send via Pipedream (Tier 1, instruction singular)
4. Confirm sent before moving to next item
5. Do NOT auto-send without the explicit approval step
6. Do NOT auto-send a modified draft even when the user is the one who requested the change

---

## Inbox Scan Phase (FROM V1.4, RETAINED)

### Gmail Search Query

is:inbox (is:unread OR is:important) newer_than:3d -from:me -from:systemgenerated@zohocrm.com -from:notifications@ -from:noreply@ -from:no-reply@ -from:mailer-daemon@ -from:calendar-notification@google.com -from:notify@webex.com

Max results: 20 emails per scan

### Inbox Evaluation Pipeline

FOR EACH email from inbox search:
  STEP 1: EXTRACT KEY INFO
    Sender email, display name, subject, thread ID, snippet, received date, labels, is unread?

  STEP 2: CROSS-REFERENCE ZOHO CRM
    Search Contacts by sender email
    If contact found: get linked Account, search open Deals, search open Tasks
    If contact NOT found: flag as potential new contact/lead

  STEP 3: CATEGORIZE
    INBOX_REPLY: Contact exists, email requires response, customer sent last message
    INBOX_NEW_TASK: No matching open task or deal; needs tracking
    INBOX_DEAL_UPDATE: Contact exists with active deal, email is deal-related update
    INBOX_FYI: Informational only (newsletter, CC, Chris sent last)

  STEP 4: DETERMINE ACTION + DRAFT
    INBOX_REPLY: Draft reply (inline in table), optionally create successor task
    INBOX_NEW_TASK: Create Zoho task + draft reply (inline in table)
    INBOX_DEAL_UPDATE: Flag for awareness, create successor task if no open task on deal
    INBOX_FYI: Skip, note in table as informational

### Inbox Deduplication Logic

1. SEARCH OPEN TASKS: Match by sender name OR subject keywords
2. SEARCH RECENT CLOSURES: Check if task was closed in last 3 days
3. THREAD DIRECTION CHECK: If Chris sent last message -> INBOX_FYI; if customer sent last -> INBOX_REPLY
4. ZOHO NOTIFICATION CHECK: If email is from Zoho about task/deal already in triage -> INBOX_FYI

### Inbox Execution Rules

FOR EACH approved inbox action:
  INBOX_REPLY:
    1. Read full thread via gmail_read_thread (MANDATORY -- also used to extract all reply-all recipients per Reply-All Thread Enforcement rule)
    2. Extract ALL To + CC recipients from the most recent message in the thread
    3. Send draft via Pipedream to all extracted recipients (already shown in approval table)
    4. If active deal with no open task: create successor task

  INBOX_NEW_TASK:
    1. Check if sender should be a new Zoho Contact (ask Chris if unclear)
    2. Create Zoho Task linked to Account/Deal if identified
    3. Send reply draft if approved

  INBOX_DEAL_UPDATE:
    1. Note the update
    2. If no open task exists on the deal: create successor task
    3. No reply drafted unless Chris requests one

  INBOX_FYI:
    1. Listed in table for visibility only
    2. No action taken

---

## Per-Task-Type Evaluation Gates (FROM V1.2, RETAINED)

"Complete a task" means evaluate it and take appropriate action, NOT simply close it.

### Gate Definitions

| Task Type | Pattern | Evaluation Gate | Action if Gate Passes |
|-----------|---------|-----------------|----------------------|
| FU30 | Subject starts with "FU30" | Route to fu30-followup-automation-v1-3 for enrichment and drafting | Email, close, verify, follow-up |
| DA90 | Subject starts with "DA90" | Search Gmail first, check license expiration. If within 30 days: draft renewal. | Renewal email or close with context |
| DR01 | Subject starts with "DR01" | Search Gmail first, check deal status. If fulfilled but NOT Closed Won: weborder check. | Deal-appropriate action or close |
| ISR_CHECKIN | "ISR Check-In" or linked to ISR deal | Look up Cisco rep via cisco-rep-locator. Draft Webex or email. | Webex/email to Cisco rep |
| DEAL_FOLLOWUP | Linked to open deal, no other pattern match | Search Gmail (MANDATORY). Draft follow-up if no contact in 7+ days. | Follow-up email or defer |
| CW01 | Subject starts with "CW01" | Check deal stage and quote status. Draft follow-up if no customer response. | Quote follow-up email |
| SR | Subject starts with "SR" | Check service request context. Determine if resolved or needs action. | Close with note or follow-up |
| AUTO_CLOSE | "Cisco Quote Sent", "PO Submitted", "License Key Sent" | Verify the action happened. | Close with verification |
| NEEDS_REVIEW | Everything else | Present task details only. Do NOT auto-close. | User decides |

### Gate Enforcement Rules

FOR EACH task in triage results:
  1. IDENTIFY task type from Subject pattern
  2. SEARCH GMAIL for last actual contact with customer (MANDATORY for all deal-linked tasks)
  3. RUN the evaluation gate for that type (with Gmail context)
  4. DETERMINE proposed action based on gate result
  5. ADD to batch approval table with proposed action, Gmail last-contact date, clickable links, and inline email draft

NEVER close a task without running its evaluation gate.
NEVER assume a task is done just because it exists.
NEVER rely solely on Zoho Last_Activity_Time; always check Gmail first.
NEVER manually set a Deal to Closed Won (deals auto-close when PO attached).

### DA90 Evaluation Gate (Detailed)

1. Get linked Deal or Account from task (What_Id or parse from Subject)
2. Check license expiration date from Account/Deal notes
3. Determine action:
   - Expired or within 30 days: Draft renewal email (use license-renewal-email skill)
   - 31-90 days out: Create reminder task for closer to expiration
   - 90+ days out: Close task with note "Licenses not expiring soon, next review scheduled"
4. Check for existing renewal deal: If exists, close task with link to deal

### DR01 Evaluation Gate (Detailed)

1. Get linked Deal from What_Id
2. Fetch deal: Stage, Amount, Last_Activity_Time, Account_Name
3. SEARCH GMAIL for actual last contact with customer (MANDATORY)
4. Evaluate:
   - Closed Won: Close task (deal complete)
   - Closed (Lost): Close task (deal dead)
   - Deal appears fulfilled but NOT Closed Won:
     -> NEVER manually close won
     -> Check for weborder (search Sales_Orders or Gmail for order confirmation)
     -> If weborder found: route to weborder-to-deal-automation-v1-1
     -> If no weborder: flag for manual review
   - Active stage + no Gmail contact in 14+ days: Draft follow-up email
   - Active stage + recent Gmail contact: Close task with note "Deal active, last Gmail contact on [date]"
5. If closing on active deal: MUST create successor task

---

## Successor Task Enforcement (FROM V1.3, RETAINED)

Rule: ALL open/ongoing deals always require a follow-up task after any action. Only skip if engagement should genuinely end (deal Closed Lost, informational FU30 with no ask, customer explicitly declined).

### When It Applies

Any task where:
- The linked Deal is in an active stage: Qualification, Proposal/Negotiation, Verbal Commit/Invoicing
- The task is being closed
- An email was sent on a deal (even if task is not being closed)
- A quote was created or updated on a deal
- An inbox email on an active deal has no open task

### Enforcement Workflow

BEFORE closing a task on an active deal:
  1. Search Tasks: (What_Id:equals:{Deal_Id}) and (Status:not_equals:Completed) and (id:not_equals:{current_task_id})
  2. IF other open tasks exist on this deal: OK to close (successor exists)
  3. IF no other open tasks: MUST create a successor task before closing
     - Subject: "Follow Up: {Contact_Name} - {Company}"
     - Due_Date: 3 business days from today (use business day calculator)
     - Owner: Chris Graves (2570562000141711002)
     - What_Id: {Deal_Id}, $se_module: "Deals"

---

## Business Day Calculator (Embedded)

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

---

## Companion Skills (REQUIRED)

| Skill | Version | Purpose |
|-------|---------|---------|
| zoho-crm-v27 | v27 | CRM operations, task lifecycle, cascade prevention, never-close-won, weborder check, Gmail source of truth |
| zoho-crm-email-v3-5 | v3.5 | Email drafting, style guide, Pipedream-first routing, draft presentation rules, tool UUID identification |
| fu30-followup-automation-v1-3 | v1.3 | FU30 enrichment, templates, 7-day lookahead, atomic lifecycle, Pipedream-first routing |
| cisco-rep-locator-v1-1 | v1.1 | Cisco rep ID lookup for ISR deal assignment |
| webex-bots-v1-6 | v1.6 | Webex messaging for Cisco rep outreach |
| license-renewal-email-v1-1 | v1.1 | Renewal outreach for DA90 tasks with expiring licenses |

---

## MCP Connections Used

| Connection | Purpose |
|------------|---------|
| Zoho CRM (Composio) | Task, deal, contact, quote operations |
| Gmail (native MCP) | Thread search, context for email drafts, inbox scan, reply-all participant extraction |
| Pipedream (UUID 4804cd9a) | Email sends, Tier 1, zero credits, parameter: instruction (SINGULAR) |
| Zapier (UUID 91a221c4) | Email sends, Tier 4 fallback only, burns credits, parameter: instructions (PLURAL) |
| Webex (Cisco) | ISR check-in messages |
| Google Calendar (optional) | Meeting context for follow-up scheduling |

---

## Key Rules (Quick Reference)

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
| CW01 | Subject starts with "CW01" | Check quote status, draft follow-up if needed |
| SR | Subject starts with "SR" | Check service request context, close or follow up |
| INBOX_REPLY | Email needs response (customer sent last) | Draft reply inline, optionally create task |
| INBOX_NEW_TASK | New thread, no Zoho tracking | Create Zoho task + draft reply inline |
| INBOX_DEAL_UPDATE | Email on tracked deal | FYI or successor task if stale |
| INBOX_FYI | Informational email | Skip, note in table |
| NEEDS_REVIEW | Everything else | Present for manual decision |

### Atomic Task Lifecycle (Phase 5)

FOR EACH actionable task (sequential, one at a time):
  1. Confirm action (draft already shown in Phase 3 table)
  2. IF user requested changes to draft: show FULL REVISED DRAFT, wait for re-approval
  3. Send email via Pipedream (Tier 1, instruction singular), confirm sent
  4. Close task via Zoho CRM, confirm via re-fetch
  5. Check successor enforcement (ALL open/ongoing deals need follow-up)
  6. Create follow-up task (skip ONLY if engagement should genuinely end)
  THEN next task

NEVER parallelize Phase 5 execution steps.
NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block.
NEVER close without running the evaluation gate first.
NEVER manually set Deal Stage to Closed Won.
NEVER rely solely on Zoho Last_Activity_Time; always check Gmail.
NEVER skip successor task on open/ongoing deals after any action.
NEVER create duplicate tasks; always run deduplication logic first.
NEVER send a modified draft without first presenting the revised version for user approval.
NEVER reply to only the From address; always call gmail_read_thread and extract all To + CC participants.

### Approval Gates

- All email drafts shown inline in the approval table before any action
- Each email still requires explicit send confirmation (or "send all" for batch)
- Modified drafts require a separate re-approval step (show revised version, wait for confirmation)
- Task closures happen only after associated emails are confirmed sent
- Manual review items are never auto-actioned
- Batch operations require "approve all" or per-item confirmation

### Picklist Protection

- Deal Stage: Always use LIVE validation via ZohoCRM_Get_Field (see zoho-crm-v27)
- NEVER manually set Closed Won (deals auto-close when PO attached)
- "Closed (Lost)" with parentheses, exact spelling
- "Referal" with one R (matches Zoho picklist exactly)
- Never create new picklist values; if value does not match, ask user

### Tool UUID Reference

| Tool | UUID | Parameter | Credits | Tier |
|------|------|-----------|---------|------|
| Pipedream Gmail | 4804cd9a | instruction (SINGULAR) | Zero | Tier 1 (ALWAYS FIRST) |
| Zapier Gmail | 91a221c4 | instructions (PLURAL) | Burns credits | Tier 4 (LAST RESORT) |

---

## Changelog

### v1.6 (Current)

- **REVISED DRAFT APPROVAL RULE**: When user requests any edits to a proposed draft, the full revised draft must be presented for explicit approval before sending. NEVER auto-send a modified draft even when the user requested the change. Applies to all email sends in all phases.
- **REPLY-ALL THREAD ENFORCEMENT**: Before sending any reply to an existing thread, call `gmail_read_thread`, extract ALL To + CC recipients from the most recent message, and include all of them in the reply. NEVER reply only to the From address. Enforced in Phase 5 and Inbox Execution Rules.
- **PHASE 5 UPDATED**: Step 2 added -- check for user-requested changes, show revised draft, wait for re-approval before sending.
- **INBOX EXECUTION RULES UPDATED**: INBOX_REPLY now explicitly requires extracting all thread participants for reply-all compliance.
- **KEY RULES UPDATED**: Added two new NEVER rules for modified drafts and reply-all enforcement.
- All v1.5 features retained.

### v1.5

- **PARALLEL SUB-AGENT EVALUATION**: All tasks evaluated simultaneously using Task tool. One agent per task, all launched in single message block. Reduces wall-clock time from N x 10s to ~10s flat.
- **5-PHASE WORKFLOW**: Phase 1 (fetch) -> Phase 2 (parallel sub-agent eval) -> Phase 3 (approval table with drafts + links) -> Phase 4 (inbox scan, parallel during review) -> Phase 5 (sequential execution)
- **SUB-AGENT PROMPT TEMPLATE**: Structured return object with all fields needed for approval table: zoho_task_url, zoho_deal_url, zoho_contact_url, zoho_account_url, gmail_thread_url, email_draft, email_subject, successor_needed, successor_due
- **INLINE EMAIL DRAFT PREVIEWS**: Every actionable row in approval table shows the full proposed email body, not just "send follow-up email"
- **CLICKABLE ZOHO CRM LINKS**: Task, Deal, Contact, Account names are hyperlinked in every approval table row using org647122552 URL pattern
- **CLICKABLE GMAIL THREAD LINKS**: "View thread" links on every row where Gmail context was found
- **LINK FORMAT SECTION**: Full reference for all Zoho CRM and Gmail URL patterns
- **INLINE DRAFT RULES SECTION**: Voice rules, format spec, approval flow, and per-type trigger conditions for email drafts
- All v1.4 features retained (inbox scan, inbox categories, deduplication, thread direction check, unified table, standalone trigger)
- All v1.3 features retained (never close won, Gmail source of truth, successor enforcement, Pipedream/Zapier tool ID)

### v1.4

- **INBOX SCAN PHASE**: New phase scans Gmail inbox for actionable emails
- **4 INBOX CATEGORIES**: INBOX_REPLY, INBOX_NEW_TASK, INBOX_DEAL_UPDATE, INBOX_FYI
- **INBOX EVALUATION PIPELINE**: 4-step process (extract, cross-reference Zoho, categorize, determine action)
- **DEDUPLICATION LOGIC**: Checks open tasks + recent closures before proposing new task creation
- **THREAD DIRECTION CHECK**: Who sent last determines INBOX_REPLY vs INBOX_FYI
- **UNIFIED BATCH TABLE**: CRM tasks and inbox items in one approval table for /DailyTasks
- **STANDALONE /InboxScan TRIGGER**: Run inbox scan independently of daily task review

### v1.3

- **NEVER MANUALLY CLOSE WON**: DR01 gate updated to check for weborder
- **GMAIL AS SOURCE OF TRUTH**: All deal-linked gates require Gmail search before proposing actions
- **SUCCESSOR AFTER EVERY ACTION**: Strengthened to require follow-up on ALL open/ongoing deals
- **PIPEDREAM/ZAPIER TOOL ID**: UUID and parameter reference embedded to prevent tool confusion
- **DR01 WEBORDER CHECK**: Fulfilled-but-not-closed deals routed to weborder-to-deal-automation-v1-1

### v1.2

- **Per-Task-Type Evaluation Gates**: DA90, DR01, FU30, ISR, Deal FU, CW01, SR, AUTO_CLOSE, NEEDS_REVIEW
- **Batch Approval Table**: Structured table with proposed actions before execution
- **Successor Task Enforcement**: Active deals must have open tasks; create if missing
- **Business Day Calculator**: Embedded Python function for consistent date math
- **Picklist Protection Reference**: Exact value reminders to prevent silent picklist corruption

### v1.1

- **Slim Trigger Router**: Removed orchestration logic (now in companion skills)
- **Expanded Triggers**: 20+ natural language phrases for automatic matching

### v1.0

- Initial release as full orchestrator
- 6-phase workflow with batch operations and atomic task lifecycle
- Cascade prevention, triage categories, date scope enforcement
