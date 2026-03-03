---
name: fu30-followup-automation-v1-3
description: "automates 30-day follow-up emails for closed deals with pipedream-first routing, tool uuid identification, strengthened successor task enforcement, draft presentation rules (no signature in preview), and gmail-sourced deal context. retrieves fu30 tasks from zoho crm, enriches with contact/deal/quote data, checks for active open deals and unpaid invoices, searches gmail for deal context, generates personalized check-in emails, and sends upon approval. triggers: fu30, fu30s, follow-up emails, 30-day check-in, 30 day follow up, post-sale check-in, check in on closed deals, customer check-ins, send fu30 emails, run fu30s."
---

# FU30 Follow-Up Email Automation v1.3

Automates the workflow for sending 30-day post-sale check-in emails to customers. Includes atomic task lifecycle, cascade prevention, **embedded formatting rules**, **Pipedream-first send routing**, **tool UUID identification**, and **draft presentation rules**.

## What's New in v1.3

- **Pipedream-First Routing Clarity**: Pipedream (UUID `4804cd9a`) is ALWAYS Tier 1 primary in Cowork. Zapier (UUID `91a221c4`) is Tier 4 last resort only, burns credits.
- **Tool UUID Identification**: Explicit UUID and parameter name mapping to prevent Pipedream/Zapier confusion
- **Draft Presentation Rules**: Email body ends at closing line ("Best," or "How are things going so far?"). Signature is NEVER shown in draft preview; included only in the send instruction.
- **Strengthened Successor Task Logic**: ALL FU30 emails that ask for feedback, mention invoices, or propose next steps require a follow-up task. Only skip for purely informational check-ins with no ask.
- **Gmail Context for ALL Deals**: Gmail search is now recommended for all deals (not just $5k+) to catch recent support issues or project context
- **Email Opt-Out Scope**: Zoho Email_Opt_Out only blocks Zoho CRM Mail (Tier 2). Pipedream and Zapier sends are NOT blocked by opt-out.
- **Updated Companion Skills**: References zoho-crm-v27, zoho-crm-email-v3-5
- All v1.2 atomic lifecycle, cascade prevention, 7-day lookahead, templates, embedded formatting, and error handling retained

## Quick Start

When triggered, execute these steps in order:

1. **Retrieve FU30 Tasks** -> 2. **Enrich Data** -> 3. **Filter/Flag** -> 4. **Generate Emails** -> 5. **Present for Approval** -> 6. **Atomic Send & Complete**

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Date Range | 7 days | Tasks with Due_Date from today through +7 days |
| Gmail Threshold | $5,000 | Deals >= this amount trigger Gmail context search |
| Auto-Send | false | Requires explicit approval unless told otherwise |
| Owner Filter | Chris Graves (2570562000141711002) | Default task owner |
| Signature | Full | Include full signature unless user says "no sig" |

## Step 1: Retrieve FU30 Tasks

**Zoho Search - Tasks Module:**
```
criteria: (Subject:starts_with:FU30) and (Status:equals:Not Started) and (Owner:equals:2570562000141711002)
fields: id,Subject,Due_Date,What_Id,Who_Id,Status
```

**IMPORTANT:** Use `starts_with` for Subject field, NOT `contains` (Zoho Tasks module doesn't support `contains` on Subject).

### 7-Day Lookahead Date Scope (MANDATORY)

FU30 tasks get a 7-day lookahead window. After retrieving results, filter in code:

```python
from datetime import datetime, timedelta

today = datetime.now().date()
lookahead = today + timedelta(days=7)

fu30_tasks = [
    t for t in all_tasks
    if today <= datetime.strptime(t["Due_Date"], "%Y-%m-%d").date() <= lookahead
]
```

| Scope | Date Range | Use Case |
|-------|------------|----------|
| FU30 / /FU30s | Due_Date: today through +7 days | Proactive outreach before due |

**NEVER include tasks with Due_Date more than 7 days in the future.** The lookahead exists to allow proactive outreach, not to pull the entire backlog.

## Step 2: Enrich Task Data

For each task, retrieve:

### Contact (from Who_Id)
```
fields: id,First_Name,Last_Name,Email,Email_Opt_Out,Account_Name
```

**If Who_Id is empty:** Search Contacts by Account_Name from the related Deal, use first result.

**If still no contact or no email:** Add to "Skipped - Missing Data" list.

### Deal (from What_Id)
```
fields: id,Deal_Name,Amount,Stage,Type,Account_Name
```

### Quote Line Items (Non-Renewals Only)
If `Deal.Type != "Renewal"`:
- Search Quotes module: `Deal_Name.id:equals:{Deal_Id}`
- For each quote, retrieve `Product_Details` subform for product names/SKUs

## Step 3: Filter & Flag

### Check for Active Open Deals

**Per Account, search Deals:**
```
criteria: (Account_Name:equals:{Account}) and ((Stage:equals:Qualification) or (Stage:equals:Proposal/Negotiation) or (Stage:equals:Verbal Commit/Invoicing))
```

**If found:** Skip task, add to "Manual Review - Active Open Deal" list with:
- Contact name, company
- Open deal name, amount, stage

### Check for Unpaid Invoices

**Per Account, search Invoices:**
```
criteria: (Account_Name:equals:{Account}) and (Status:not_equals:Paid)
fields: id,Invoice_Number,Grand_Total,Status
```

**If found:** Store invoice details for email. Generate payment URL:
```
https://www.stratusinfosystems.com/invoicing/?inva={Grand_Total}&invn={Invoice_Number}&curr=usd
```

## Step 4: Gmail Context (Recommended for ALL Deals)

**ALWAYS search Gmail** for recent context before drafting. Gmail is the source of truth for last contact date and conversation tone.

- Search Gmail: `from:{contact_email} OR to:{contact_email}` or company name
- Look for: project details, recent support issues, deployment notes, last contact date
- Extract relevant context for personalization

**For deals >= $5,000:** Gmail search is MANDATORY (not optional). Use context to personalize the email body between greeting and standard check-in.

**For deals < $5,000:** Gmail search is recommended. If recent support issues or project context is found, incorporate it. If no relevant context, proceed with standard template.

## Step 5: Generate Emails

### Embedded Formatting Rules (INLINE, NO EXTERNAL SKILL READ NEEDED)

Every FU30 email MUST follow these rules:

```
MANDATORY SPACING:
- One blank line between EVERY paragraph
- One blank line before signature block
- No two content lines adjacent without a blank line

STYLE RULES:
- No em dashes (use commas, parentheses, or periods)
- Use contractions naturally (I'll, you're, that's)
- Keep paragraphs to 1-3 lines
- Close with a question or next step prompt
- Sound like a colleague, not a form letter
```

### Draft Presentation Rules (CRITICAL)

```
WHEN PRESENTING DRAFTS FOR APPROVAL:
- Email body ends at closing line ("Best," or the final question)
- Signature is NEVER displayed in draft preview
- Signature is included ONLY in the send instruction to Pipedream/Zapier/Zoho
- This prevents cluttering the approval table

EXAMPLE DRAFT PREVIEW (CORRECT):
  "Hey Sarah, [body]... How are things going so far? Best,"

EXAMPLE DRAFT PREVIEW (INCORRECT):
  "Hey Sarah, [body]... Best, Chris Graves Regional Sales Director..."
```

### CRITICAL: Tool UUID Identification

```
MCP TOOL REFERENCE:
┌──────────┬──────────────────────────────────────┬─────────────┬─────────┬──────┐
│ Service  │ UUID                                 │ Parameter   │ Credits │ Tier │
├──────────┼──────────────────────────────────────┼─────────────┼─────────┼──────┤
│ Pipedream│ 4804cd9a-4d6c-47aa-a787-a6c57d5daf6f │ instruction │ Zero    │ 1    │
│ Zapier   │ 91a221c4-ef99-4b89-96f3-ef7396e59fa2 │ instructions│ Limited │ 4    │
└──────────┴──────────────────────────────────────┴─────────────┴─────────┴──────┘

CRITICAL DIFFERENCES:
- Pipedream uses "instruction" (SINGULAR) -> ALWAYS Tier 1, zero credits
- Zapier uses "instructions" (PLURAL) -> Tier 4 ONLY, burns credits
- NEVER confuse these. Wrong parameter = silent failure.
```

### Email Opt-Out Scope

```
OPT-OUT ONLY BLOCKS ZOHO CRM MAIL (TIER 2):
┌──────────────┬───────────────────┐
│ Send Path    │ Blocked by Opt-Out│
├──────────────┼───────────────────┤
│ Pipedream    │ NO                │
│ Zoho CRM Mail│ YES              │
│ Gmail Compose│ NO                │
│ Zapier       │ NO                │
└──────────────┴───────────────────┘

If contact has Email_Opt_Out = true:
- Cowork: Pipedream sends normally (opt-out irrelevant)
- Chat: Zoho CRM Mail is blocked, use Gmail compose link
- The opt-out disable/re-enable flow is only needed for Zoho CRM Mail sends
```

### Email Templates

**Base Template (Renewals):**
```
Subject: Checking In on Your Renewal

Hey {First_Name},

Now that it's been a few weeks since your license renewal went through, I wanted to send a friendly check-in to make sure everything is running smoothly.

How are things going so far?

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

**Hardware Order Template:**
```
Subject: Quick Check-In on Your {Product_Summary}

Hey {First_Name},

Now that it's been a few weeks since you received your {Product_Details}, I wanted to send a friendly check-in to make sure everything went smoothly.

How are things going so far?

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

**High-Value Template ($5k+):**
Add project-specific context from Gmail between greeting and standard check-in.

**Unpaid Invoice Addendum:**
If unpaid invoice exists, add before signature:
```
By the way, I noticed invoice #{Invoice_Number} for ${Grand_Total} is still showing as outstanding. If there's anything I can help with on that front, or if you'd prefer to pay online, here's a quick link: {Payment_URL}
```

**No-Signature Variant:**
If user requests "no sig" or "remove signature", end emails with just:
```
Best,
Chris
```

### Subject Line Variations
- Renewal: "Checking In on Your Renewal" or "Quick Check-In on Your Renewal"
- Hardware: "Quick Check-In on Your {Product}" or "Checking In on Your {Product}"
- Use product-specific subjects when possible (e.g., "Quick Check-In on Your MX75s")

## Step 6: Present for Approval

Organize output into sections:

### Ready to Send
| Contact | Company | Subject | Preview |
|---------|---------|---------|---------|

### Email Opt-Out (Requires Separate Approval)
| Contact | Company | Subject |
|---------|---------|---------|
*Note: These contacts have opted out of marketing emails. Approve to temporarily disable opt-out, send this transactional check-in, then re-enable opt-out.*

### Manual Review - Active Open Deals
| Contact | Company | Open Deal | Amount | Stage |
|---------|---------|-----------|--------|-------|
*These customers have active sales activity. Review before sending follow-up.*

### Skipped - Missing Data
| Task | Issue |
|------|-------|
*Tasks skipped due to missing contact or email address.*

**Wait for user approval before proceeding.**

## Step 7: Atomic Send & Complete (CRITICAL SEQUENCE)

Upon approval, process each FU30 email through the full atomic lifecycle. **NEVER batch or parallelize these steps.**

### Environment-Aware Send Routing (4-Tier)

```
DETECT MODE:
  /sessions/ in paths -> COWORK
  otherwise -> CHAT

COWORK MODE (FU30 emails are always NEW, not replies):
  TIER 1 (PRIMARY):  Pipedream gmail-send-email (UUID: 4804cd9a, param: "instruction" SINGULAR, zero credits)
  TIER 2 (FALLBACK): ZohoCRM_Send_Mail (blocked if contact has Email_Opt_Out)
  TIER 3:            Gmail compose link (manual send)
  TIER 4 (LAST):     Zapier gmail_send_email (UUID: 91a221c4, param: "instructions" PLURAL, burns credits)

CHAT MODE:
  TIER 2 (PRIMARY):  ZohoCRM_Send_Mail
  TIER 3 (FALLBACK): Gmail compose link

CRITICAL: Pipedream is ALWAYS Tier 1 in Cowork. Zapier is ALWAYS Tier 4, last resort only.
NEVER use Zapier when Pipedream is available. NEVER confuse their UUIDs or parameter names.
```

### Pipedream Send Format (Cowork Primary)

```json
{
  "instruction": "Send a new email to {First_Name} {Last_Name} at {email} with subject '{subject}' and body:\n\n{full_email_body_with_blank_lines}",
  "output_hint": "confirmation that email was sent, message id"
}
```

### Atomic Lifecycle Per Task

```
FOR EACH approved FU30 email:
  Step A: SEND EMAIL
    -> Use environment-aware routing (see above)
    -> Wait for confirmation (message ID or compose link opened)
    -> If send fails: try Zoho Send Mail, then ask user (Zapier or Gmail compose)

  Step B: COMPLETE TASK (only after email confirmed)
    -> ZohoCRM_Update_Record: Status = "Completed"
    -> NEVER batch this with Step A

  Step C: VERIFY CLOSURE (only after Step B)
    -> ZohoCRM_Get_Record: re-fetch task, confirm Status = "Completed"
    -> If verification fails: retry once, then flag for manual review

  Step D: CREATE FOLLOW-UP TASK (conditional, only after Step C)
    -> Only if the email asks for feedback, a decision, or next steps
    -> Skip if the email is purely informational ("how are things going?")
    -> See Follow-Up Task Rules below

  THEN move to next task
```

### Cascade Prevention (CRITICAL)

```
CORRECT (sequential):
  pipedream_send -> wait -> zoho_update_task -> wait -> zoho_get_task -> wait -> zoho_create_task

INCORRECT (parallel, NEVER DO THIS):
  parallel:
    - zapier_send
    - zoho_update_task
```

Zoho CRM MCP calls and Pipedream/Zapier MCP calls must NEVER execute in the same parallel block.

### Standard Contacts
1. Send email (environment-aware routing)
2. Verify email sent
3. Update Task: `Status = "Completed"`
4. Verify task closure
5. Create follow-up task (if applicable)

### Opt-Out Contacts (if approved)
1. Update Contact: `Email_Opt_Out = false`
2. Send email (environment-aware routing)
3. Verify email sent
4. Update Contact: `Email_Opt_Out = true`
5. Update Task: `Status = "Completed"`
6. Verify task closure
7. Create follow-up task (if applicable)

### Send Mail API Format (Chat Mode Only)
```json
{
  "data": [{
    "to": [{"email": "{email}", "user_name": "{First_Name} {Last_Name}"}],
    "from": {"email": "chrisg@stratusinfosystems.com", "user_name": "Chris Graves"},
    "subject": "{subject}",
    "content": "{html_content}",
    "mail_format": "html"
  }]
}
```
Path: `moduleName: "Contacts"`, `id: {Contact_Id}`

### Follow-Up Task Rules (Strengthened in v1.3)

**DEFAULT: Create a follow-up task.** Only skip if there is genuinely nothing to follow up on.

**Create a follow-up task when:**
- Email asks for feedback or a decision (most FU30s do this)
- Email mentions unpaid invoice (follow up on payment)
- Email proposes next steps or a call
- Email asks "how are things going?" with product-specific context (expect a response)
- Contact is at a high-value account ($5k+)

**Skip follow-up task ONLY when:**
- Email is a purely generic informational check-in with NO specific ask and NO invoice mention
- Contact had an active open deal (already being tracked separately by deal tasks)

**When in doubt, CREATE the follow-up task.** It's better to have a task you close early than to miss a response.

**Follow-Up Task Payload:**
```json
{
  "data": [{
    "Subject": "Follow Up: {Contact_Name} - {Company}",
    "Due_Date": "{3_business_days_from_today}",
    "Status": "Not Started",
    "Priority": "Normal",
    "Owner": {"id": "2570562000141711002"},
    "What_Id": "{Deal_Id}",
    "$se_module": "Deals",
    "Who_Id": "{Contact_Id}",
    "Description": "Follow up on FU30 check-in email sent {today}. {context}"
  }]
}
```

**Business day calculation:** Skip Saturdays and Sundays. If +3 lands on Saturday, push to Monday. If Sunday, push to Monday.

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
```

## Optimization Notes

### Batch Operations
- Retrieve multiple contacts/deals using `ids` parameter when possible
- Group API calls by module to reduce round trips

### Caching
- Store Account -> Contact mapping to avoid redundant searches
- Store Account -> Open Deals result to avoid re-checking

### Skip Conditions (No Email Sent)
- No contact or email found
- Active open deal exists (Qualification, Proposal/Negotiation, Verbal Commit/Invoicing)
- User declines to approve

## Error Handling

| Error | Action |
|-------|--------|
| Contact email opt-out blocked | Cowork: Pipedream sends normally (opt-out irrelevant). Chat: Add to opt-out approval list for Zoho CRM Mail |
| No email on contact | Skip, add to missing data list |
| Deal lookup fails | Use generic template |
| Gmail search fails | Proceed without context (but note in draft that context was unavailable) |
| Pipedream send fails (Cowork) | Try Zoho CRM Send Mail (Tier 2), then Gmail compose (Tier 3), then Zapier last resort (Tier 4) |
| All send paths fail (Cowork) | Ask user to send manually via Gmail compose link |
| Zoho send fails (Chat) | Generate Gmail compose link |
| Wrong UUID or parameter used | Stop, identify correct tool, retry with correct UUID and parameter name |

## Output Summary

After completion, provide:
- Total emails sent
- Total tasks completed
- Total follow-up tasks created
- Manual review items (with Zoho links)
- Skipped items with reasons
- Any verification failures

## Companion Skills

- zoho-crm-v27 (CRM operations, task lifecycle, cascade prevention, never-close-won, Gmail source of truth)
- zoho-crm-email-v3-5 (4-tier email routing, tool UUID identification, Pipedream-first, draft presentation rules)
- cisco-rep-locator-v1-1 (rep lookup for ISR deal context)

## NEVER Do This

- NEVER use Zapier (Tier 4) when Pipedream (Tier 1) is available in Cowork
- NEVER confuse Pipedream UUID (`4804cd9a`) with Zapier UUID (`91a221c4`)
- NEVER use "instructions" (plural) for Pipedream or "instruction" (singular) for Zapier
- NEVER show the full signature block in draft preview tables
- NEVER present two paragraphs adjacent without a blank line between them
- NEVER skip Gmail search before drafting (especially for deals >= $5k)
- NEVER parallelize send + task closure in the same API call block
- NEVER skip the follow-up task for emails that ask for feedback or mention invoices

## Changelog

### v1.3 (Current)

- **Pipedream-First Routing Clarity**: Explicit 4-tier routing with UUID and parameter identification
- **Tool UUID Identification**: Pipedream (4804cd9a, "instruction" singular) vs Zapier (91a221c4, "instructions" plural)
- **Draft Presentation Rules**: Body ends at closing line, signature never in preview
- **Strengthened Successor Task Logic**: Default to creating follow-up; only skip for purely generic check-ins
- **Gmail Context for ALL Deals**: Recommended for all deals, mandatory for $5k+
- **Email Opt-Out Scope**: Clarifies opt-out only blocks Zoho CRM Mail, not Pipedream/Zapier
- **NEVER List**: 8 explicit anti-patterns to prevent recurring errors
- **Updated Companion Skills**: References zoho-crm-v27, zoho-crm-email-v3-5
- All v1.2 atomic lifecycle, cascade prevention, templates, embedded formatting, and error handling retained

### v1.2

- **Embedded Formatting Rules**: Spacing and style rules inline (no mid-workflow skill read needed)
- **Signature Toggle**: Support for "no sig" requests
- **Cowork Send Path**: Pipedream (primary), Zoho CRM Mail (fallback), user-choice escalation (Zapier or Gmail compose)
- **Environment-Aware Routing**: Detects Chat vs Cowork and routes accordingly
- **Business Day Calculator**: Embedded Python function
- **Updated Companion Skills**: References zoho-crm-v26, zoho-crm-email-v3-3
- All v1.1 atomic lifecycle, cascade prevention, templates, and error handling retained

### v1.1

- **Atomic Task Lifecycle**: Send -> complete -> verify -> follow-up (guaranteed sequential)
- **Cascade Prevention**: Zoho CRM and Zapier MCP calls never in same parallel block
- **7-Day Lookahead Enforcement**: Explicit date scope filtering with code example
- **Zoho Search Fix**: `starts_with` for Subject field (not `contains`)
- **Follow-Up Task Creation**: Conditional follow-up with business day calculation
- **Expanded Trigger Phrases**: fu30s, 30-day check-in, post-sale check-in, etc.
- **Updated Companion Skills**: References zoho-crm-v23, zoho-crm-email-v3-2
- All v1.0 enrichment, templates, filtering, and error handling retained

### v1.0

- Initial release
- FU30 task retrieval and enrichment
- Active deal and unpaid invoice detection
- Gmail context search for high-value deals
- Email templates (renewal, hardware, high-value)
- Opt-out handling with temporary disable/re-enable
- Batch presentation and approval workflow
