---
name: daily-task-engine-v2-2
description: "6-phase daily task engine with orchestrator-level gmail and deal pre-loading, batched sub-agent launches, lean sub-agent prompts, hybrid email templates, token-optimized architecture, pre-built dashboard injector script, file-piped sub-agent results, deferred companion skill loading, dynamic companion skill versioning, interactive html dashboard output, google calendar briefing, parallel sub-agent evaluation, orphaned deal check, batch approval tables, inbox scan, gmail-first context, successor enforcement, hyperlink enforcement, and centralized voice guide. dashboard features: card/compact/kanban views, inline email editing, drag-and-drop, dark mode, send-to-claude url injection, auto-save, search/filter, batch approve/skip/reject with toggle. triggers: daily tasks, review my tasks, task review, task clean up, help me complete todays tasks, close out my tasks, close tasks, what tasks are due, send fu30 emails, fu30s, 30-day check-ins, run my tasks, morning tasks, task cleanup, finish my tasks, knock out my tasks, lets do tasks, whats on my plate, clear my task list, inbox scan, check my inbox, scan my email."
---

# Daily Task Engine v2.2 (Orchestrator Pre-Load + Batched Sub-Agents)

Trigger router with **orchestrator-level Gmail and deal pre-loading** (eliminates redundant API calls from sub-agents), **batched sub-agent launches** (2-3 batches instead of single massive block), **lean sub-agent prompts** (no voice guide, task-type-specific gate only), **hybrid email templates** (structural template + personalized context), **token-optimized architecture**, **pre-built dashboard injector**, **file-piped sub-agent results**, **deferred companion skill loading**, **dynamic companion skill versioning**, **interactive HTML dashboard output**, **parallel sub-agent evaluation**, **orphaned deal check**, **inline email draft previews**, **clickable Zoho CRM and Gmail links**, **per-task-type evaluation gates**, **batch approval tables**, **gmail-first context evaluation**, **strengthened successor enforcement**, **inbox scan phase**, **revised draft approval rule**, **reply-all thread enforcement**, and **Phase 3 centralized voice/style validation**.

---

See CHANGELOG.md for what changed in each version.

---

## Trigger Patterns

### Full Daily Task Review

Triggers: /DailyTasks, "daily tasks", "review my tasks", "task review", "help me complete todays tasks", "morning tasks", "run my tasks", "lets do tasks", "whats on my plate", "knock out my tasks"

What it does:
1. Phase 0: Google Calendar morning briefing
2. Phase 1: Pull all open tasks owned by Chris Graves, due today or overdue
3. Phase 1b: IR01 pre-filter — batch-classify IR01 tasks before sub-agent launch
4. Phase 1c: Orphaned deal check — find active deals with no open task linked
5. Phase 1d: Deal data pre-load — batch fetch deal records, build lookup map
6. Phase 2a: Gmail batch pre-load — batch search Gmail for all unique contacts
7. Phase 2b: Launch sub-agents in batches of 10-15 with pre-loaded context
8. Phase 2c: Aggregate file-piped results after each batch
9. Phase 3: Pre-presentation gate (spacing + style check) → dashboard output
10. Phase 4: Run Inbox Scan in parallel while user reviews dashboard
11. Phase 5: Execute approved actions sequentially (atomic task lifecycle)

Skills to load at trigger: NONE (companion skills deferred to Phase 5)
Skills loaded just-in-time at Phase 5: resolved dynamically at runtime (see Dynamic Companion Skill Version Resolution)

### Task Cleanup (Close Only)

Triggers: /CloseTasks, "close out my tasks", "close tasks", "task clean up", "task cleanup", "clear my task list", "finish my tasks"

Skills loaded just-in-time at execution: zoho-crm (latest version — resolved dynamically)

### 30-Day Follow-Up Emails

Triggers: /FU30s, "send fu30 emails", "fu30s", "30-day check-ins", "post-sale check-ins", "run fu30s", "customer check-ins"

Skills loaded just-in-time at execution: zoho-crm, zoho-crm-email, fu30-followup-automation (all latest — resolved dynamically)

### Inbox Scan (Standalone)

Triggers: /InboxScan, "check my inbox", "inbox scan", "scan inbox", "scan my email", "what emails need attention"

Skills loaded just-in-time at execution: zoho-crm, zoho-crm-email (latest versions — resolved dynamically)

### Triage Only (No Action)

Triggers: "what tasks are due", "show me my tasks", "task summary", "what do I have today"

Skills loaded just-in-time if action needed: zoho-crm (latest version — resolved dynamically)

---

## Dynamic Companion Skill Version Resolution

Companion skill version numbers are NEVER hardcoded. At Phase 5 JIT load time, resolve the latest available version for each companion skill:

```
1. Glob the plugin path for skills matching the prefix:
   ls /mnt/.local-plugins/cache/stratus-sales-toolkit/stratus-sales-toolkit/*/skills/{prefix}*/

2. Parse version numbers from folder names
   (e.g., zoho-crm-v32 = 32, fu30-followup-automation-v1-4 = 1.4)

3. Load SKILL.md from the highest-versioned matching folder

4. Fallback: if no match found at plugin path, try:
   /mnt/.skills/skills/{prefix}*/
   (standalone skill mounts, same resolution logic)
```

Examples:
- Prefix `zoho-crm-v` → finds v30, v31, v32 → selects `zoho-crm-v32`
- Prefix `fu30-followup-automation-v` → finds v1-3, v1-4 → selects `fu30-followup-automation-v1-4`
- Prefix `zoho-crm-email-v` → finds v3-5, v3-6 → selects `zoho-crm-email-v3-6`

---

## Workflow Overview

```
PHASE 0: CALENDAR BRIEFING (~3s)
PHASE 1: FETCH + IR01 PRE-FILTER (~5s)
  Phase 1b: IR01 batch classification
  Phase 1c: Orphaned deal check
  Phase 1d: Deal data pre-load → /tmp/deal_context.json     ← NEW
PHASE 2: EVALUATION (~15s total)
  Phase 2a: Gmail batch pre-load → /tmp/gmail_context.json   ← NEW
  Phase 2b: Batched sub-agent launches (2-3 batches)         ← CHANGED
  Phase 2c: Result aggregation from /tmp/task_eval_*.json    ← NEW
PHASE 3: PRE-PRESENTATION GATE + DASHBOARD (~5s)
PHASE 4: INBOX SCAN (parallel with user review)
PHASE 5: SEQUENTIAL EXECUTION (JIT skill loading)
```

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

{N} meetings today. {free_time_note}
```

### Step 3: Flag Deal-Linked Meetings

If any meeting attendee email matches a contact from the CRM task list (fetched in Phase 1), flag it:

```
⚡ Deal overlap: Your 11:00 AM meeting with John Smith (Acme Corp) has an open task due today.
```

This cross-reference happens AFTER Phase 1 completes. Display the flag inline with the dashboard output in Phase 3 if applicable.

### Step 4: No-Meeting Shortcut

If no events today, display: "📅 No meetings today — clear calendar for task focus." and proceed directly to Phase 1.

---

## Phase 1: Canonical Zoho Query

### Primary Query (Use This First)

```
Criteria: (Owner:equals:2570562000141711002)and(Due_Date:less_equal:{TODAY})and(Status:equals:Not Started)
Page size: 50
Pages: Fetch pages 1, 2, 3 (up to 150 records)
Sort: Created_Time asc (Zoho only supports id, Created_Time, Modified_Time for sort_by — NEVER use Due_Date)
```

Replace `{TODAY}` with today's date in YYYY-MM-DD format.

### Fallback Query (If Status Filter Returns INVALID_QUERY)

If the primary query fails with INVALID_QUERY or returns no results when tasks are expected:

```
Criteria: (Owner:equals:2570562000141711002)and(Due_Date:less_equal:{TODAY})
Page size: 50
Pages: Fetch pages 1, 2, 3
```

Then filter client-side: keep only records where `Status == "Not Started"`.

### Banned Query Patterns (NEVER USE)

- NEVER use `not_equals` operator — Zoho returns INVALID_QUERY
- NEVER fetch without the Owner filter — returns 79KB+ unreadable responses
- NEVER fetch without Due_Date filter alongside a broad owner filter
- NEVER save large results to disk for grep filtering

### Query Result Validation

After fetching, display:
```
Total records fetched: {N}
Status breakdown: Not Started: {X}, Completed: {Y}, Other: {Z}
Proceeding with: {X} open tasks
```

---

## Phase 1b: IR01 Batch Pre-Filter

IR01 tasks are auto-generated "Reminder to Set a Task" alerts linked to the Meraki_ISR module. They follow the pattern:
- Subject contains "IR01:" OR
- Subject matches "IR01: Reminder to Set a Task. ISR [Name]" OR
- Subject matches "Reminder to Set a Task" with no linked deal

BEFORE launching any sub-agents:
1. Scan all fetched task subjects for the IR01 pattern
2. Separate IR01 tasks from substantive tasks
3. Display: "IR01 tasks (batch): {N} | Substantive tasks (sub-agents): {M}"
4. Launch sub-agents ONLY for the {M} substantive tasks
5. Add IR01 tasks as a single batch row in the Phase 3 dashboard

IR01 Dashboard Entry Format:
```javascript
{
  id: 'ir01_batch',
  type: 'IR01_BATCH',
  dealName: 'IR01 BATCH — {N} ISR Reminder Tasks',
  dealUrl: null,
  contactName: 'Various',
  contactEmail: '',
  proposedAction: 'Manual review — auto-generated ISR reminders. Close individually or reassign.',
  gmailContext: 'Tasks: [Subject 1], [Subject 2], + N more',
  emailDraft: null,
  successorDefault: { recommended: false, days: 0, type: 'IR01' },
  ir01TaskIds: ['id1', 'id2', ...]
}
```

---

## Phase 1c: Orphaned Deal Check

An orphaned deal is an open/active deal with no open task currently linked. Surface these so nothing slips through.

### Step 1: Fetch Open Active Deals

Use ZohoCRM_Search_Records on the Deals module:

```
Module: Deals
criteria: (Owner:equals:2570562000141711002)and((Stage:equals:Qualification)or(Stage:equals:Proposal/Negotiation)or(Stage:equals:Verbal Commit/Invoicing))
fields: id,Deal_Name,Stage,Amount,Account_Name,Contact_Name
per_page: 200
```

Fetch all pages if needed. Store result as `open_deals[]`.

### Step 2: Collect Deal IDs from Fetched Tasks

From the tasks fetched in Phase 1, collect the `What_Id` field for any task where `$se_module` equals "Potentials" or "Deals". Store as `task_deal_ids[]` (a set for O(1) lookup).

### Step 3: Identify Orphaned Deals

```python
task_deal_id_set = set(task_deal_ids)
orphaned_deals = [deal for deal in open_deals if deal['id'] not in task_deal_id_set]
```

### Step 4: Surface in Dashboard

If orphaned deals are found, include them as entries in the Phase 3 dashboard with type "ORPHANED_DEAL":

```javascript
{
  id: 'orphaned_' + deal.id,
  type: 'ORPHANED_DEAL',
  dealName: deal.Deal_Name,
  dealUrl: 'https://crm.zoho.com/crm/org647122552/tab/Potentials/' + deal.id,
  taskUrl: null,
  contactName: deal.Contact_Name || 'Unknown',
  contactEmail: null,
  dealStage: deal.Stage,
  dealAmount: deal.Amount,
  proposedAction: 'Create follow-up task — no open task currently linked to this deal',
  actionNotes: 'This active deal has no open successor task. Likely a missed close-without-successor.',
  gmailContext: null,
  emailDraft: null,
  successorDefault: { recommended: true, days: 3, type: 'ORPHANED_DEAL' }
}
```

Group orphaned deals under a "⚠️ Orphaned Deals" section header in the dashboard.
If none found: display "✓ All active deals have open tasks" in the dashboard footer.

---

## Phase 1d: Deal Data Pre-Load (NEW in v2.2)

Instead of having each sub-agent independently fetch deal records (which caused 80%+ failure rate with smaller models and wastes API calls), the orchestrator pre-loads all deal data in bulk and passes it to sub-agents via a shared file.

### Why This Matters

In v2.1, each sub-agent called ZohoCRM_Get_Record for its linked deal. With 30+ tasks, that's 30+ individual API calls inside sub-agents that each need to parse and handle errors. Pre-loading at the orchestrator level means one batch of API calls, consistent data, and sub-agents that focus purely on evaluation logic.

### Step 1: Collect Unique Deal IDs

From Phase 1 task results, extract all unique `What_Id` values where `$se_module` is "Potentials" or "Deals". Deduplicate into a list. You already built `task_deal_ids` in Phase 1c; reuse that set plus any deal IDs from IR01-filtered tasks (for completeness, though IR01s rarely have deals).

### Step 2: Batch Fetch Deal Records

Fetch deal records in batches using ZohoCRM_Get_Records with comma-separated IDs:

```
Module: Deals
ids: {comma-separated deal IDs, up to 10 per call}
fields: id,Deal_Name,Stage,Amount,Account_Name,Contact_Name,Closing_Date,Description
```

Zoho supports up to 10 record IDs per `ids` parameter. For 30 deals, that's 3 API calls instead of 30.

### Step 3: Build Deal Lookup Map

Structure the results as a map keyed by deal ID:

```python
deal_map = {}
for deal in fetched_deals:
    deal_map[deal['id']] = {
        'deal_name': deal.get('Deal_Name', ''),
        'stage': deal.get('Stage', ''),
        'amount': deal.get('Amount', 0),
        'account_name': deal.get('Account_Name', {}).get('name', '') if isinstance(deal.get('Account_Name'), dict) else str(deal.get('Account_Name', '')),
        'contact_name': deal.get('Contact_Name', {}).get('name', '') if isinstance(deal.get('Contact_Name'), dict) else str(deal.get('Contact_Name', '')),
        'closing_date': deal.get('Closing_Date', ''),
        'description': deal.get('Description', '')
    }
```

### Step 4: Write to Shared File

```python
import json
with open('/tmp/deal_context.json', 'w') as f:
    json.dump(deal_map, f)
```

Sub-agents will read this file instead of making their own API calls.

### Step 5: Enrich Task List with Deal Data

Also build an enriched task list that merges task data with deal data, so the sub-agent prompt can include deal context inline:

```python
enriched_tasks = []
for task in substantive_tasks:
    deal_id = task.get('What_Id', {}).get('id', '') if isinstance(task.get('What_Id'), dict) else ''
    deal_data = deal_map.get(deal_id, {})
    enriched_tasks.append({
        'task_id': task['id'],
        'subject': task.get('Subject', ''),
        'due_date': task.get('Due_Date', ''),
        'contact_name': task.get('Contact_Name', ''),
        'contact_email': task.get('Contact_Email', ''),  # may need lookup
        'deal_id': deal_id,
        'deal_name': deal_data.get('deal_name', 'Unknown'),
        'deal_stage': deal_data.get('stage', 'Unknown'),
        'deal_amount': deal_data.get('amount', 0),
        'account_name': deal_data.get('account_name', 'Unknown'),
        'task_type': classify_task_type(task.get('Subject', ''))
    })
```

Display summary:
```
Deal pre-load: {X} unique deals fetched in {Y} API calls
Tasks enriched: {Z}/{M} tasks have valid deal data
```

---

## Phase 2a: Gmail Batch Pre-Load (NEW in v2.2)

Before sub-agent launch, the orchestrator batch-searches Gmail for all unique contact emails. This eliminates redundant Gmail searches from inside sub-agents (the single biggest per-agent API call) and provides consistent context across all evaluations.

### Why This Matters

In v2.1, each sub-agent ran `from:{email} OR to:{email}` independently. With 30 tasks touching 25 unique contacts, that's 25 Gmail API calls inside sub-agents. Pre-loading consolidates this to ~5-7 orchestrator-level calls.

### Step 1: Collect Unique Contact Emails

From the enriched task list (Phase 1d), extract unique non-empty contact_email values. If contact_email is missing from the task record, attempt to resolve it from the deal's Contact_Name via a single Zoho search.

For contacts without email addresses after resolution: mark as `gmail_context: "No email on file"` and skip Gmail search.

### Step 2: Batch Gmail Searches

Group contacts into batches of up to 5 emails per query:

```
Query: "from:alice@company.com OR to:alice@company.com OR from:bob@corp.com OR to:bob@corp.com OR from:carol@org.com OR to:carol@org.com"
maxResults: 10
```

This returns the most recent messages involving any of those contacts. Each query costs one API call.

For 25 unique contacts at 5 per query = 5 Gmail API calls total (vs. 25 inside sub-agents).

### Step 3: Parse and Map Results

For each Gmail result, extract:
- Sender email (from header)
- Date
- Thread ID
- Subject snippet

Map results back to each contact:

```python
gmail_map = {}  # email -> {last_contact_date, thread_id, thread_url, direction, snippet}

for message in gmail_results:
    sender = extract_sender_email(message)
    date = message.get('date', '')
    thread_id = message.get('threadId', '')

    # Determine which contact this message relates to
    for contact_email in batch_emails:
        if contact_email.lower() in sender.lower() or contact_email.lower() in message.get('to', '').lower():
            existing = gmail_map.get(contact_email)
            if not existing or date > existing['last_contact_date']:
                gmail_map[contact_email] = {
                    'last_contact_date': date,
                    'thread_id': thread_id,
                    'thread_url': f'https://mail.google.com/mail/u/0/#all/{thread_id}',
                    'direction': 'from_customer' if contact_email.lower() in sender.lower() else 'from_chris',
                    'snippet': message.get('snippet', '')[:200]
                }
```

### Step 4: Write to Shared File

```python
import json
with open('/tmp/gmail_context.json', 'w') as f:
    json.dump(gmail_map, f)
```

Display summary:
```
Gmail pre-load: {X} unique contacts searched in {Y} queries
Context found: {Z}/{X} contacts have recent Gmail history
```

---

## Phase 2b: Batched Sub-Agent Launches (CHANGED in v2.2)

Sub-agents now receive pre-loaded context and use lean prompts. They are launched in batches of 10-15 instead of all at once, which improves reliability across all model tiers.

### Batching Strategy

```python
BATCH_SIZE = 12  # Sweet spot: enough parallelism, manageable for any model
batches = [enriched_tasks[i:i+BATCH_SIZE] for i in range(0, len(enriched_tasks), BATCH_SIZE)]
```

For 33 substantive tasks: 3 batches of 11-12 each.
For 15 tasks: 2 batches of 8 and 7.

Launch each batch as one Task tool message block (true parallelism within the batch). Wait for the batch to complete before launching the next.

### File-Piped Results (MANDATORY)

Each sub-agent writes its JSON result to `/tmp/task_eval_{task_id}.json` using the Write tool. The sub-agent's chat response should be ONLY: `Result written to /tmp/task_eval_{task_id}.json`

This keeps sub-agent result data OUT of the main conversation context. With 30+ tasks at ~3-4K each, that's 90-120K of context saved.

If a sub-agent fails to write the file (timeout, error), flag it as NEEDS_REVIEW and move on. Do not retry — retries burn context for diminishing returns.

### Lean Sub-Agent Prompt (v2.2)

The sub-agent prompt is intentionally stripped down compared to v2.1. Voice/style validation is handled exclusively in Phase 3 by the orchestrator. Sub-agents focus on evaluation and drafting only.

```
Evaluate task ID {task_id}:
Subject: {subject}
Due: {due_date}
Type: {task_type}

DEAL CONTEXT (pre-loaded):
{inline deal data from deal_map — name, stage, amount, account, contact}

GMAIL CONTEXT (pre-loaded):
Last contact: {date} | Direction: {from_customer/from_chris} | Thread: {thread_id}
Snippet: {snippet}
{If no gmail context: "No recent Gmail history found for this contact."}

TASK-SPECIFIC GATE:
{Insert ONLY the relevant gate for this task_type — see Per-Task-Type Evaluation Gates section}

INSTRUCTIONS:
1. Apply the evaluation gate above to determine the proposed action
2. If action = send email: draft the email body
   - Use a warm, consultative tone with natural sentence variety
   - End with a question or call to action
   - Keep paragraphs to 1-3 lines
   - No filler openers, no em dashes
3. Write your JSON result to /tmp/task_eval_{task_id}.json

RETURN FORMAT (JSON only, no prose):
{
  "task_id": "{task_id}",
  "subject": "{subject}",
  "company": "{account_name}",
  "contact_name": "{contact_name}",
  "contact_email": "{contact_email}",
  "task_type": "{task_type}",
  "due_date": "{due_date}",
  "deal_id": "{deal_id}",
  "deal_stage": "{deal_stage}",
  "deal_amount": {deal_amount},
  "zoho_task_url": "https://crm.zoho.com/crm/org647122552/tab/Tasks/{task_id}",
  "zoho_deal_url": "https://crm.zoho.com/crm/org647122552/tab/Potentials/{deal_id}",
  "gmail_last_contact_date": "{from pre-loaded context}",
  "gmail_thread_id": "{from pre-loaded context}",
  "gmail_thread_url": "{from pre-loaded context}",
  "proposed_action": "{action}",
  "action_notes": "{notes}",
  "email_draft": "{full body if action = send email, else null}",
  "email_subject": "{if action = send email, else null}",
  "successor_needed": true/false,
  "successor_due": "YYYY-MM-DD"
}

Write this JSON to /tmp/task_eval_{task_id}.json. Your chat response: "Result written to /tmp/task_eval_{task_id}.json"
```

### What Changed in the Prompt vs v2.1

| Element | v2.1 | v2.2 | Savings |
|---------|------|------|---------|
| Voice/style guide | ~2K embedded in every prompt | Removed (Phase 3 handles) | ~2K × N agents |
| Gmail search step | "Search Gmail for..." (agent does API call) | Pre-loaded context inline | 1 API call per agent |
| Deal fetch step | "Fetch deal Stage, Amount..." (agent does API call) | Pre-loaded context inline | 1 API call per agent |
| All gate logic | Full gate reference table | Only the relevant gate | ~1K per agent |
| Verbosity cap | Paragraph of warnings | Single line | ~200 bytes |

Net savings per sub-agent: ~4-5K of prompt + 2 fewer API calls.
Net savings for 30 tasks: ~120-150K of total sub-agent context + 60 fewer API calls.

### Hybrid Email Templates (NEW in v2.2)

For task types that commonly result in email sends (DR01, FU30, DA90, CW01), include a structural template in the sub-agent prompt to guide the draft while still allowing personalization:

**DR01 Follow-Up Template:**
```
Hey {first_name}!

{1-2 personalized sentences based on Gmail context — reference last conversation topic}

{Core ask: checking in on deal status, next steps, timeline}

{Closing question}

Thanks,
Chris
```

**FU30 Check-In Template:**
```
Hey {first_name}!

{1-2 personalized sentences — reference what was deployed, how long ago}

{Check-in ask: how things are running, any issues, feedback}

{Closing question}

Thanks,
Chris
```

These templates give sub-agents structure (reducing inconsistency across models) while the personalized sentence slots ensure each email is contextual. The orchestrator's Phase 3 gate validates the final output regardless.

---

## Phase 2c: Result Aggregation (NEW in v2.2)

After each batch of sub-agents completes, collect their file-piped results:

```bash
cat /tmp/task_eval_*.json | python3 -c "
import sys, json, glob
results = []
for f in sorted(glob.glob('/tmp/task_eval_*.json')):
    try:
        with open(f) as fh:
            results.append(json.load(fh))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        results.append({'task_id': f.split('_')[-1].replace('.json',''), 'error': str(e), 'proposed_action': 'NEEDS_REVIEW'})
json.dump(results, sys.stdout)
" > /tmp/task_data_raw.json
```

### Error Handling

If a sub-agent failed to produce valid JSON, the aggregation script catches the error and inserts a NEEDS_REVIEW placeholder. The dashboard will show these as manual review items rather than crashing.

Display aggregation summary:
```
Results collected: {X}/{Y} successful | {Z} flagged NEEDS_REVIEW
```

---

## Phase 3: Pre-Presentation Gate

**MANDATORY: Run this gate on every email draft before building the dashboard.**

This is the ONLY place voice/style validation happens in v2.2. Sub-agents draft emails without the full style guide; the orchestrator applies quality control here.

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

Replace with a direct, context-setting opener.

### Check 3 — AI Phrases

Scan for these phrases and remove/replace:
- "As an AI" → remove entirely
- "I'm delighted" → replace with "I'm glad" or rephrase
- "Here is" (standalone) → rewrite as prose
- "In conclusion" → remove
- "Dive into" → replace with "get into," "look at," etc.
- "Certainly" → remove or use "Sure" / "Of course"
- "Best regards" → replace with "Thanks," or "Best,"

### Check 4 — Em Dashes

Replace any em dash (—) with a comma, parenthesis, or period depending on context.

### Check 5 — Closing CTA

Verify the draft ends with a question or specific call to action.
- If the draft ends with a plain statement, append an appropriate closing question.
- Examples: "How does everything look?", "What has feedback been so far?", "Does that timing work for you?"

After all 5 checks, proceed to dashboard generation with corrected drafts.

---

## Phase 3a: Dashboard Output (Default)

Transform sub-agent results into an interactive HTML dashboard.

### Step 1: Transform Sub-Agent Results to Dashboard Schema

For each sub-agent result, map to this JavaScript object:

```javascript
{
  id: result.task_id,
  type: result.task_type,
  dealName: result.subject,
  dealUrl: result.zoho_deal_url,
  taskUrl: result.zoho_task_url,
  contactName: result.contact_name,
  contactEmail: result.contact_email,
  contactUrl: result.zoho_contact_url || 'https://crm.zoho.com/crm/org647122552/tab/Contacts/' + result.contact_id,
  accountName: result.company,
  accountUrl: result.zoho_account_url || 'https://crm.zoho.com/crm/org647122552/tab/Accounts/' + result.account_id,
  dealStage: result.deal_stage,
  dealAmount: result.deal_amount,
  dueDate: result.due_date,
  proposedAction: result.proposed_action,
  actionNotes: result.action_notes || '',
  gmailContext: 'Last contact: ' + result.gmail_last_contact_date + (result.gmail_thread_url ? '' : ' (no thread)'),
  gmailThreadUrl: result.gmail_thread_url,
  emailDraft: result.email_draft ? {
    to: result.contact_email,
    subject: result.email_subject,
    body: result.email_draft
  } : null,
  successorDefault: {
    recommended: result.successor_needed,
    days: result.successor_needed ? daysBetween(today, result.successor_due) : 3,
    type: result.task_type
  }
}
```

Include IR01 batch entry and ORPHANED_DEAL entries as defined in their respective sections.

### Step 2: Write Task Data to Temp File

```python
import json
with open('/tmp/task_data.json', 'w') as f:
    json.dump(transformed_task_array, f)
```

### Step 3: Run Pre-Built Dashboard Injector

```bash
python assets/build_dashboard.py assets/task-dashboard.html /tmp/task_data.json /mnt/outputs/task-dashboard.html
```

The script uses string find/replace (not regex) to avoid `re.error: bad escape \u` on JSON with URL-encoded characters. If the script fails, fall back to manual string injection using `str.find()` + concatenation (NEVER `re.sub()`).

### Step 4: Present Dashboard Link

```
Your task dashboard is ready with {N} tasks loaded.

[Open Task Dashboard](computer:///path/to/task-dashboard.html)

Review tasks in the dashboard, then either:
• **Send to Claude** button in the dashboard to route decisions back here
• **Save to Folder** to export decisions as JSON, then share the file
• Or reply here with "approve all", "approve #1, #3", etc.
```

### Fallback: Chat-Based Table

If the dashboard template is missing or writing fails, fall back to Phase 3b (chat-based approval table).

---

## Phase 3b: Chat Approval Table (Fallback)

Use this format only if dashboard generation fails.

### Hyperlink Enforcement (MANDATORY)

Every entity reference MUST be a clickable hyperlink. Required links per row:
- Task subject → `zoho_task_url`
- Account name → `zoho_account_url`
- Deal name → `zoho_deal_url`
- Contact name → `zoho_contact_url`
- Gmail thread → `gmail_thread_url`

If any URL is null, construct from record ID: `https://crm.zoho.com/crm/org647122552/tab/{Module}/{record_id}`. If record ID also missing, display as plain text with "(no link)".

Row structure:
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
Total: {X} tasks | Due today: {Y} | Overdue: {Z} | Inbox items: {N} | IR01 batch: {B} | Orphaned deals: {O}
Evaluation: {X} sub-agents ran in {B} batches

Reply with:
  "approve all" -- execute all proposed actions
  "approve #1, #3" -- execute specific items
  "skip #2" -- remove from batch
  "edit #1 [changes]" -- modify draft before sending
```

---

## Phase 4: Inbox Scan During Review

Announce immediately after presenting dashboard:
"Scanning your inbox while you review — I'll add any action items below."

### Gmail Search Query

```
is:inbox (is:unread OR is:important) newer_than:3d -from:me -from:systemgenerated@zohocrm.com -from:notifications@ -from:noreply@ -from:no-reply@ -from:mailer-daemon@ -from:calendar-notification@google.com -from:notify@webex.com
```

Max results: 20 emails per scan

### Inbox Evaluation Pipeline

FOR EACH email:
  STEP 1: Extract sender email, subject, thread ID, received date, unread status
  STEP 2: Cross-reference Zoho CRM by sender email (Contact, Account, open Deals, open Tasks)
  STEP 3: Categorize:
    INBOX_REPLY: Customer sent last, needs response
    INBOX_NEW_TASK: No matching open task or deal
    INBOX_DEAL_UPDATE: Email on tracked deal
    INBOX_FYI: Chris sent last, newsletter, notification
  STEP 4: Draft action + email if needed

### Inbox Deduplication

1. Search open Tasks by sender name OR subject keywords
2. Check if task was closed in last 3 days
3. Thread direction check: Chris sent last → INBOX_FYI; customer sent last → INBOX_REPLY
4. Zoho notification check: system emails about tasks already in triage → INBOX_FYI

### Inbox Execution Rules

INBOX_REPLY: Read full thread (gmail_read_thread MANDATORY), extract all To + CC, send via Pipedream, create successor if active deal with no open task.
INBOX_NEW_TASK: Check if sender should be new Zoho Contact, create Task, send reply if approved.
INBOX_DEAL_UPDATE: Note update, create successor if no open task on deal.
INBOX_FYI: Listed for visibility only, no action.

---

## Phase 5: Sequential Execution

### Just-In-Time Companion Skill Loading

Companion skills are NOT loaded at trigger time. They are loaded here, right before execution begins. This saves ~20K of context during evaluation phases (0-3).

Before executing, resolve and read relevant companion skill(s) using dynamic version resolution:

- For email sends: resolve `zoho-crm-email-v` (latest)
- For CRM operations: resolve `zoho-crm-v` (latest)
- For FU30 tasks: resolve `fu30-followup-automation-v` (latest)
- For ISR check-ins: resolve `cisco-rep-locator-v` and `webex-bots-v` (latest)

Read once at Phase 5 start, not per-task. Never hardcode version numbers.

### Accepting Decisions

Phase 5 accepts decisions from three sources:

**Source 1: Dashboard Send to Claude** — User pastes JSON payload:
```json
{
  "decisions": { "task_id": "approve|reject|skip" },
  "editedSubjects": { "task_id": "new subject" },
  "editedBodies": { "task_id": "new body" },
  "rejectReasons": { "task_id": "reason" },
  "successors": { "task_id": { "enabled": true, "days": 3 } }
}
```

**Source 2: Dashboard JSON file** — Same schema.

**Source 3: Chat commands** — "approve all", "approve #1, #3", "skip #2", "edit #1 [changes]"

### Execution Loop

FOR EACH approved action (in order, one at a time):
  1. If dashboard source: check for edited subject/body, apply edits
  2. IF edits requested: show FULL REVISED DRAFT, wait for re-approval
  3a. If ORPHANED_DEAL: create new Zoho Task linked to deal. No email. Confirm via re-fetch.
  3b. Otherwise: Send email via Pipedream (Tier 1, instruction singular), confirm sent
  4. Close task via Zoho CRM (skip for ORPHANED_DEAL), confirm via re-fetch
  5. Check successor enforcement (dashboard config or default rules)
  6. Create follow-up task (skip ONLY if engagement should genuinely end)
  THEN next task

NEVER execute two items simultaneously.
NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block.
NEVER skip confirmation between items.
NEVER send a modified draft without presenting revised version first.

### Handling Rejected/Skipped Tasks

Rejected: close task with reject reason as closing note. No email. Successor per config.
Skipped: no action. Task remains open.

---

## Revised Draft Approval Rule

When a user requests ANY edits to a proposed draft, the full revised draft MUST be presented for approval BEFORE sending:

```
REVISED DRAFT (pending your approval):
Mode: Pipedream (Tier 1) | From: chrisg@stratusinfosystems.com | To: {recipients}
Subject: {subject}
---
{full revised email body}
---
Send this revised version? (yes to send, or request further changes)
```

---

## Reply-All Thread Enforcement

Before sending ANY reply to an existing email thread:
1. Call `gmail_read_thread` with the thread ID
2. From the MOST RECENT MESSAGE, extract all To + CC addresses
3. Exclude chrisg@stratusinfosystems.com from recipients
4. Use extracted addresses as To and CC for the outgoing reply

---

## Per-Task-Type Evaluation Gates

### DR01 Evaluation Gate

1. Check deal_stage from pre-loaded context (NOT a new API call)
2. If Stage = "Closed (Won)": AUTO-CLOSE task. Note: "Deal is Closed Won." No email. No successor.
3. If Stage = "Closed (Lost)": AUTO-CLOSE task. Note: "Deal is Closed Lost." No email. No successor.
4. If deal is active: check Gmail context from pre-loaded data
5. Evaluate:
   - Deal appears fulfilled but NOT Closed Won: flag for weborder check
   - Active + no Gmail contact in 14+ days: Draft follow-up email using DR01 template
   - Active + recent contact (within 7 days): Close task with note, create successor
6. If closing on active deal: MUST create successor task

### DA90 Evaluation Gate

1. Check license expiration date from deal description/notes in pre-loaded context
2. Expired or within 30 days: Draft renewal email (license-renewal-email skill at Phase 5)
3. 31-90 days out: Create reminder task
4. 90+ days out: Close task with note
5. Check for existing renewal deal — if found, close task with link

### FU30 Evaluation Gate

1. Use pre-loaded deal and Gmail context
2. Check for open invoices (note: use Invoices module, no `not_equals` operator)
3. Draft friendly check-in using FU30 template
4. If active open deal found: note in action_notes, adjust messaging

### Gate Quick Reference

| Task Type | Pattern | Key Rule |
|-----------|---------|----------|
| FU30 | Subject starts with "FU30" | Route to fu30-followup-automation at Phase 5 |
| DA90 | Subject starts with "DA90" | Check license expiration first |
| DR01 | Subject starts with "DR01" | Check deal stage FIRST — Closed=auto-close |
| ISR_CHECKIN | "ISR Check-In" | Look up rep via cisco-rep-locator |
| DEAL_FOLLOWUP | Linked to open deal | Gmail context mandatory |
| CW01 | Subject starts with "CW01" | Check quote status |
| SR | Subject starts with "SR" | Check service request context |
| AUTO_CLOSE | "Cisco Quote Sent", "PO Submitted" | Verify action happened |
| IR01_BATCH | Subject contains "IR01:" | Batch NEEDS_REVIEW — no sub-agent |
| ORPHANED_DEAL | Phase 1c detection | Create new task — no email, no close |
| NEEDS_REVIEW | Everything else | Present for manual decision |

---

## Successor Task Enforcement

Rule: ALL open/ongoing deals require a follow-up task after any action. Only skip if:
- Deal is Closed (Lost) or Closed (Won)
- Informational FU30 with no ask
- Customer explicitly declined further contact
- Dashboard successor toggle is explicitly disabled

### Enforcement Workflow

BEFORE closing a task on an active deal:
  1. Search open Tasks on the deal (excluding current task)
  2. IF other open tasks exist: OK to close
  3. IF no other open tasks: MUST create successor:
     - Subject: "Follow Up: {Contact_Name} - {Company}"
     - Due_Date: dashboard successor days if provided, else 3 business days
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

Version numbers resolved dynamically at runtime. Never hardcode.

| Skill | Folder Prefix | Purpose |
|-------|---------------|---------|
| zoho-crm | `zoho-crm-v` | CRM operations, task lifecycle, cascade prevention |
| zoho-crm-email | `zoho-crm-email-v` | Email drafting, Pipedream-first routing, style guide |
| fu30-followup-automation | `fu30-followup-automation-v` | FU30 enrichment, templates, atomic lifecycle |
| cisco-rep-locator | `cisco-rep-locator-v` | Cisco rep ID lookup for ISR assignments |
| webex-bots | `webex-bots-v` | Webex messaging for Cisco rep outreach |
| license-renewal-email | `license-renewal-email-v` | Renewal outreach for DA90 tasks |

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
- NEVER fetch without the Owner filter
- NEVER launch individual sub-agents for IR01 tasks — batch-classify them
- NEVER parallelize Phase 5 execution steps
- NEVER batch Zoho CRM + Pipedream/Zapier in same parallel block
- NEVER close without running the evaluation gate first
- NEVER manually set Deal Stage to Closed Won
- NEVER rely solely on Zoho Last_Activity_Time; always check Gmail
- NEVER skip successor task on open/ongoing deals after any action
- NEVER create duplicate tasks; always run deduplication logic first
- NEVER send a modified draft without presenting revised version first
- NEVER reply to only the From address; extract all To + CC participants
- NEVER skip the Phase 3 pre-presentation gate
- NEVER hardcode companion skill version numbers
- NEVER embed the full voice/style guide in sub-agent prompts (Phase 3 handles validation)
- NEVER have sub-agents fetch deal records or search Gmail independently (use pre-loaded context)

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

## Dashboard Asset

The interactive HTML dashboard template is bundled at `assets/task-dashboard.html`. Single-file HTML with embedded CSS and JavaScript, no external dependencies.

Data reads from `window.TASK_DATA_INJECT` (set by Phase 3a) with fallback to built-in sample data.

---

See CHANGELOG.md for version history.
