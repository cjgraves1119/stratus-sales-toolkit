---
name: zoho-crm-email-v3-5
description: "pipedream-first email skill with 4-tier routing, draft presentation rules (no signature in preview), pipedream message ID sourcing, email opt-out scope clarification, tool uuid identification table, and strengthened spacing enforcement. triggers: send email, draft email, reply to email, follow up email, batch emails, email customer, send quote email, email about deal, compose email, write email."
---

# Zoho CRM Email v3.5

Pipedream-first email routing with **4-tier failover**, **draft presentation rules**, **tool UUID identification**, and **strengthened spacing enforcement**. Pipedream gmail-send-email is the primary send path for ALL email types across ALL environments.

---

## What's New in v3.5

- **DRAFT PRESENTATION RULES**: When presenting email drafts for approval, the body ends at the closing line ("Best," or "Thanks,"). Signature is NOT displayed in draft preview. Signature is included automatically in the send instruction only.
- **PIPEDREAM MESSAGE ID SOURCING**: Thread reply message IDs MUST come from Pipedream's own available message list, NOT from Gmail MCP search results. If the target message has cycled out of Pipedream's list, send as a new email instead of attempting a broken thread reply.
- **EMAIL OPT-OUT SCOPE**: Zoho contact Email_Opt_Out only blocks Zoho CRM Mail sends (Tier 2). It does NOT affect Pipedream (Tier 1) or Zapier (Tier 4) sends. No action needed to send via Pipedream when contact has opt-out enabled.
- **TOOL UUID IDENTIFICATION TABLE**: Pipedream UUID `4804cd9a` uses `instruction` (SINGULAR), zero credits, always Tier 1. Zapier UUID `91a221c4` uses `instructions` (PLURAL), burns credits, Tier 4 only.
- **STRENGTHENED SPACING**: Explicit blank-line-between-every-paragraph enforcement with validation checklist before every draft presentation.
- **UPDATED COMPANION SKILLS**: References zoho-crm-v27, fu30-followup-automation-v1-3
- All v3.4 Pipedream threading, 4-tier routing, style guide, and error handling retained

## What's New in v3.4

- **Pipedream Tier 1 for EVERYTHING**: Pipedream gmail-send-email is now the primary send path for both new emails AND thread replies across all environments. Thread replies confirmed working with proper In-Reply-To header threading (tested 2/27/2026).
- **4-Tier Routing**: Pipedream (Tier 1) > Zoho CRM Mail (Tier 2, chat only) > Gmail compose link (Tier 3) > Zapier (Tier 4, credit-limited fallback)
- **CRITICAL: Pipedream Parameter Bug**: Pipedream MCP schema advertises `instructions` (plural) but backend requires `instruction` (singular). ALWAYS use `instruction` (singular) for all Pipedream Gmail tool calls.
- **Zapier Demoted to Tier 4**: Zapier credits are limited. Only use Zapier when all other tiers fail or are unavailable.
- **Updated Companion Skills**: References zoho-crm-v26, fu30-followup-automation-v1-2
- All v3.3 cascade prevention, style guide, spacing enforcement, and error handling retained

---

## CRITICAL: Tool UUID Identification (NEW IN V3.5)

### MCP Tool Reference Table

| Tool | UUID Prefix | Parameter Name | Credits | Tier |
|------|-------------|---------------|---------|------|
| Pipedream Gmail | `4804cd9a` | `instruction` (SINGULAR) | Zero | Tier 1 (ALWAYS) |
| Zapier Gmail | `91a221c4` | `instructions` (PLURAL) | Burns credits | Tier 4 (LAST RESORT) |

**How to identify which tool you're calling:**
- Look at the MCP tool name: `mcp__4804cd9a-...` = Pipedream, `mcp__91a221c4-...` = Zapier
- Pipedream tools start with `mcp__4804cd9a-4d6c-47aa-a787-a6c57d5daf6f__gmail-`
- Zapier tools start with `mcp__91a221c4-ef99-4b89-96f3-ef7396e59fa2__gmail_`

**NEVER confuse these two.** Using `instructions` (plural) on Pipedream will fail. Using `instruction` (singular) on Zapier will fail.

## CRITICAL: Pipedream Parameter Name Bug

**The Pipedream MCP schema is wrong.** All Pipedream Gmail tools (gmail-send-email, gmail-create-draft, etc.) advertise the parameter name as `instructions` (plural) in their schema, but the backend ONLY accepts `instruction` (singular, no 's').

If you use `instructions` (plural), you will get this error every time:
```
Error parsing arguments: "instruction" Required
```

**ALWAYS use `instruction` (singular) for ALL Pipedream tool calls. No exceptions.**

## CRITICAL: Pipedream Message ID Sourcing (NEW IN V3.5)

When composing thread replies via Pipedream:

```
Thread reply message IDs MUST come from Pipedream's own available message list.
DO NOT use message IDs obtained from Gmail MCP search results (gmail_search_messages).

WHY: Pipedream's sub-agent can only reference messages it can see in its own context.
     Gmail MCP message IDs are from a different system and may not be accessible to Pipedream.

IF the target message has cycled out of Pipedream's available list:
  -> Send as a NEW email instead of attempting a broken thread reply
  -> Include context from the original thread in the body for continuity
```

## Email Opt-Out Scope (NEW IN V3.5)

Zoho contact `Email_Opt_Out = true` ONLY blocks emails sent via **Zoho CRM Mail (Tier 2)**.

| Send Path | Affected by Opt-Out? | Action Needed |
|-----------|---------------------|---------------|
| Pipedream (Tier 1) | NO | Send normally, no opt-out handling needed |
| Zoho CRM Mail (Tier 2) | YES | Must temporarily disable opt-out, send, re-enable |
| Gmail Compose (Tier 3) | NO | Send normally |
| Zapier (Tier 4) | NO | Send normally |

**Implication:** Since Pipedream is Tier 1 and not affected by opt-out, the opt-out toggle workflow (disable -> send -> re-enable) is only needed when falling back to Tier 2 Zoho CRM Mail.

---

## Environment Detection

### How to Detect

```
IF current working directory contains "/sessions/"
   OR filesystem path matches /sessions/*/mnt/*
   -> MODE = COWORK

ELSE (no VM context, no /sessions/ paths)
   -> MODE = CHAT
```

### Why It Matters

| Feature | Chat Mode | Cowork Mode |
|---------|-----------|-------------|
| Pipedream Gmail (Tier 1) | Available (PRIMARY) | Available (PRIMARY) |
| Zoho CRM Send Mail (Tier 2) | Available | May have connector issues |
| Gmail compose link (Tier 3) | Available | Available |
| Zapier MCP (Tier 4) | Available (credit-limited) | Available (credit-limited) |
| Gmail MCP (search/read) | Available | Available |

---

## 4-Tier Email Routing (ALL Environments)

### Tier Overview

```
TIER 1 - PIPEDREAM gmail-send-email     (Free, works everywhere, supports threading)
TIER 2 - ZOHO CRM Send Mail             (Free, chat mode only, no thread replies)
TIER 3 - GMAIL COMPOSE LINK             (Free, manual send required)
TIER 4 - ZAPIER gmail_send_email /      (Limited credits, last resort)
         gmail_reply_to_email
```

### New Outbound Emails (No Existing Thread)

```
BOTH MODES:
  1. TIER 1:  Pipedream gmail-send-email (instruction singular!)
  2. TIER 2:  ZohoCRM_Send_Mail (chat mode only; skip in cowork)
  3. TIER 3:  Gmail compose link (manual send)
  4. TIER 4:  Zapier gmail_send_email (only if user requests or all above fail)
```

### Thread Replies (Existing Thread with thread_id)

```
BOTH MODES:
  1. TIER 1:  Pipedream gmail-send-email with In-Reply-To threading
  2. TIER 3:  Gmail compose link (manual send, skip Tier 2 since Zoho can't thread)
  3. TIER 4:  Zapier gmail_reply_to_email (only if Pipedream fails)
```

### Quick Decision Tree

```
Is this a REPLY to an existing thread?
  YES -> TIER 1: Pipedream gmail-send-email (with thread context in instruction)
         -> If fails: TIER 3: Gmail compose link
         -> If fails: TIER 4: Zapier gmail_reply_to_email
  NO  -> TIER 1: Pipedream gmail-send-email
         -> If fails: TIER 2: ZohoCRM_Send_Mail (chat only)
         -> If fails: TIER 3: Gmail compose link
         -> If fails: TIER 4: Zapier gmail_send_email
```

---

## Pipedream Thread Reply Format (TIER 1 - PROVEN WORKING)

Thread replies via Pipedream were confirmed working on 2/27/2026. The key is providing the Gmail message ID and thread ID in the `instruction` parameter so Pipedream's sub-agent sets the In-Reply-To and References headers correctly.

### Required Information for Thread Replies

Before composing a Pipedream thread reply, you MUST have:

1. **Message ID** - The Gmail message ID of the email being replied to (from gmail_search_messages or gmail_read_message)
2. **Thread ID** - The Gmail thread ID (from the same search/read)
3. **Recipient email** - The person you're replying to
4. **Exact subject line** - Must match the original thread subject (prepend "Re: " only if not already present)

### Pipedream Thread Reply Format

```json
{
  "instruction": "Reply to the email with message ID [MESSAGE_ID] in thread [THREAD_ID], sending to [NAME] at [EMAIL] with subject '[Re: Exact Subject]' and body '[Full plain text body with proper spacing]'. This must be sent as a reply within the existing email thread, not as a new standalone email. Use the In-Reply-To and References headers to ensure proper threading. Send from chrisg@stratusinfosystems.com.",
  "output_hint": "Return the sent message ID, thread ID, and confirmation of whether it was sent as an in-thread reply."
}
```

### Pipedream Thread Reply Example (Actual Working Call)

```json
{
  "instruction": "Reply to the email with message ID 19c4959db66edd8b in thread 19c49580d479caf0, sending to cjgraves1119@gmail.com with subject 'Re: Thread testing' and body 'Testing Pipedream MCP thread reply - did this land in the same conversation?'. This must be sent as a reply within the existing email thread, not as a new standalone email. Use the In-Reply-To and References headers to ensure proper threading. Send from chrisg@stratusinfosystems.com.",
  "output_hint": "Return the sent message ID, thread ID, and confirmation of whether it was sent as an in-thread reply."
}
```

### Important Notes on Pipedream Threading

- Pipedream's sub-agent LLM interprets the instruction text and maps it to Gmail API parameters
- Be explicit about "reply within existing thread" and "use In-Reply-To headers" in the instruction
- The sub-agent may ask for confirmation before sending. If so, repeat the instruction with "Yes, send the email now." prepended
- Confirm the returned thread ID matches the original thread to verify proper threading
- If Pipedream's sub-agent misinterprets the instruction, retry with clearer phrasing before falling to Tier 3/4

---

## Pipedream New Email Format (TIER 1)

```json
{
  "instruction": "Send a new email to [Name] at [email@example.com] with subject '[Subject Line]' and body '[Full email body with proper spacing]'. Send from chrisg@stratusinfosystems.com.",
  "output_hint": "Return the sent message ID and confirmation."
}
```

**CRITICAL REMINDER: Use `instruction` (singular). Using `instructions` (plural) will fail every time.**

---

## Zoho CRM Send Mail (TIER 2 - Chat Mode Only)

Zoho CRM Mail works as Tier 2 in chat mode for new outbound emails. It does NOT support thread replies and may have connector issues in Cowork mode.

```json
{
  "body": {
    "data": [{
      "from": {"user_name": "Chris Graves", "email": "chrisg@stratusinfosystems.com"},
      "to": [{"user_name": "[Name]", "email": "[email]"}],
      "cc": [{"user_name": "[Name]", "email": "[cc_email]"}],
      "subject": "[Subject]",
      "content": "[HTML body with <p> tags]",
      "mail_format": "html"
    }]
  },
  "path_variables": {
    "moduleName": "[Module]",
    "id": "[Record_ID]"
  }
}
```

Supported modules (priority order): Contacts > Leads > Deals > Accounts > Quotes

---

## Gmail Compose Link (TIER 3)

When Pipedream and Zoho both fail, generate a pre-filled Gmail compose URL for manual send.

```
https://mail.google.com/mail/?view=cm&to=[email]&cc=[cc_email]&su=[URL_encoded_subject]&body=[URL_encoded_body]
```

Encode blank lines as %0A%0A between paragraphs. For thread replies via Gmail compose, warn user: "This will create a new email, not a threaded reply."

---

## Zapier (TIER 4 - Limited Credits, Last Resort)

Zapier has limited credits. Only use when Tiers 1-3 all fail or are unavailable.

### New Email via Zapier

```json
{
  "instructions": "Send a new email to [Name] at [email] with subject '[Subject]' and body:\n\n[Full body]\n\nCC: [if applicable]",
  "output_hint": "confirmation that email was sent, message id"
}
```

### Thread Reply via Zapier

```json
{
  "instructions": "Reply to thread [thread_id] to [Name] at [email] with subject '[exact subject]' and body:\n\n[Full reply body]",
  "output_hint": "confirmation that reply was sent, message id"
}
```

Note: Zapier uses `instructions` (plural) correctly. Only Pipedream has the singular/plural bug.

---

## Trigger Patterns

Use this skill when:

- "send email to [customer]"
- "email [contact] about [topic]"
- "draft email for [deal/quote]"
- "reply to [email/thread]"
- "follow up email"
- "send quote to customer"
- "batch emails" or multiple email sends
- User requests email communication from CRM context

---

## Chris Graves Style Guide (Reference for All Drafts)

Apply this guide every time an email is composed. The goal is to sound like a knowledgeable colleague, not a formal report.

### Voice Principles

- Friendly and confident, never stiff
- Clear and skimmable first, detailed second
- Assume good intent in every follow-up
- Use contractions: I'll, you're, that's, we've
- Ask for a specific next step in nearly every email
- **Hard rule: never use em dashes. Use commas, parentheses, or periods instead.**

### Tone Anchors

- "For your convenience..." as a transition into links, steps, or details
- "How does everything look?" as a closing prompt
- "Let me know what you think" or "Upon review..." to invite a reply without pressure
- "What has feedback been so far?" for soft follow-ups
- Anchor urgency to real deadlines (promo end, renewal window, price increase)

### Email Structure (Default Anatomy)

1. Greeting (first name, exclamation if warm)
2. 1 to 2 sentences of context (why you're writing now)
3. The payload: answer, options, quote links, or bullets
4. A single decision question (two short questions max)
5. Close with full signature on external emails (unless user says "no sig")

### Format Rules

- Keep paragraphs to 1 to 3 lines
- Use bullets for any list of more than 2 items
- Use labeled options (Option A, Option B) when presenting choices
- Put links on their own line when possible
- Avoid giant pasted blocks unless it solves a problem
- Add a blank line between every paragraph for readability

### Subject Line Rules

- Reply threads: keep the existing subject exactly, including ref tags and case numbers
- New outreach: short and outcome-based ("Meraki renewal options for [Org]", "Quote options for [Model] and [Term]")

### What to Avoid

- Em dashes (never, under any circumstance)
- Stiff or overly formal language
- Long unbroken paragraphs
- Starting with "I hope this email finds you well" or similar filler
- Closing without asking for a next step

### Signature (External Emails)

```
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### Signature Toggle

If user says "remove the signature", "no sig", "without signature", or similar:
- Omit the full signature block
- End with just "Best,\nChris" or closing line only
- Still maintain all other style rules

---

## Mandatory Line Spacing Rules

Every email drafted by this skill MUST have proper spacing. This is enforced before every draft review.

### Plain Text (Pipedream, Zapier, and Gmail compose link)

- One blank line between EVERY paragraph
- One blank line before and after bullet lists
- One blank line before the signature block
- No two content lines should ever be adjacent without a blank line between them

### HTML (Zoho CRM Mail)

- Every paragraph wrapped in <p> tags (never use <br><br> between paragraphs)
- Bullet lists wrapped in <ul><li> tags with <p> before and after the list
- Signature uses <br> for line breaks within the signature block only

### Gmail Compose URL Encoding

Encode blank lines as %0A%0A (double newline) between paragraphs.

### Pre-Send Spacing Check (MANDATORY)

Before presenting any draft for review, verify:

```
[ ] Blank line between every paragraph
[ ] Blank line before and after bullet lists
[ ] Blank line before signature block
[ ] No two content paragraphs touching without a blank line
[ ] HTML uses <p> tags (not <br><br>)
[ ] Gmail URL uses %0A%0A between paragraphs
[ ] Pipedream instruction body has proper spacing
[ ] Zapier instructions body has \n\n between paragraphs
```

If any check fails, fix the spacing before showing the draft.

---

## Core Workflow: New Email

### Step 1: Detect Environment

```
Check for /sessions/ in current paths:
  Found    -> COWORK mode
  Not found -> CHAT mode
```

### Step 2: Identify CRM Record (if customer referenced)

Search for the recipient in priority order: Contact > Lead > Deal > Account

### Step 3: Search Gmail for Thread Context (if replying)

Use search_gmail_messages to find the thread. Extract:
1. Exact subject line (including ref tags, case numbers, brackets)
2. Thread ID
3. Message ID (of the specific email being replied to)
4. All recipients (To and CC from the most recent message)
5. Thread context to inform the reply

### Step 4: Compose the Draft

Apply the Chris Graves style guide. Enforce mandatory line spacing rules.

### Step 5: MANDATORY Draft Review (Never Skip)

**DRAFT PRESENTATION RULES (NEW IN V3.5):**
- Body ends at the closing line ("Best," or "Thanks," or similar)
- Signature is NOT shown in draft preview (reduces clutter, signature is auto-included in send instruction)
- Blank line between EVERY paragraph in preview (verify before showing)

```
DRAFT EMAIL READY FOR REVIEW

Mode:    [CHAT / COWORK]
Path:    [Pipedream (Tier 1) / Zoho CRM Mail (Tier 2) / Gmail Compose (Tier 3) / Zapier (Tier 4)]
From:    chrisg@stratusinfosystems.com
To:      [recipient_email]
CC:      [if any]
Subject: [subject_line]
Thread:  [thread_id if reply, "New" if outbound]

----------------------------------------
[Email body preview - ends at closing line]
[Signature NOT shown - auto-included in send]
----------------------------------------

Reply with:
  "send"           -> Send via [determined path]
  "edit [note]"    -> Modify before sending
  "add cc [email]" -> Add a CC recipient
  "no sig"         -> Remove signature entirely
  "cancel"         -> Discard draft
```

### Step 6: Execute Send (4-Tier Routing)

See tier-specific format sections above.

### Step 7: Failover Handling

```
NEW EMAIL:
  IF Pipedream (Tier 1) fails:
    -> IF Chat mode: Try Zoho CRM Send Mail (Tier 2)
    -> IF Zoho fails or Cowork mode: Gmail compose link (Tier 3)
    -> Last resort: Zapier (Tier 4, limited credits)

THREAD REPLY:
  IF Pipedream (Tier 1) fails:
    -> Skip Tier 2 (Zoho can't thread)
    -> Offer choice: Gmail compose (Tier 3, won't thread) or Zapier (Tier 4, uses credits)
```

### Step 8: Confirm Success

```
Email sent via [Pipedream (Tier 1) / Zoho CRM Mail (Tier 2) / Gmail compose (Tier 3) / Zapier (Tier 4)]
Mode:    [CHAT / COWORK]
To:      [recipient_email]
Subject: [subject]
Thread:  [thread_id or "New"]
```

---

## Threaded Reply Workflow (Detailed)

### Step 1: Search Gmail (MANDATORY for all replies)

### Step 2: Read Full Thread (extract subject, thread ID, message ID, recipients)

### Step 3: Build the Reply (style guide, spacing, exact subject)

### Step 4: Present Draft

```
THREADED REPLY DRAFT

Mode:    [CHAT / COWORK]
Path:    Pipedream (Tier 1)

Replying to: [Brief thread description]
From:    chrisg@stratusinfosystems.com
To:      [extracted recipients]
CC:      [extracted CC]
Subject: [exact subject from thread]
Thread:  [thread_id]
Message: [message_id being replied to]

----------------------------------------
[Reply body with proper spacing enforced]
----------------------------------------
```

### Step 5: Execute via Pipedream with threading instruction. Failover to Tier 3/4 if needed.

---

## Batch Email Workflow

Send approved emails one at a time, reporting success/failure per email with tier used.

---

## Email Templates (Chris Graves Voice)

All templates follow the style guide. Blank lines between every paragraph are mandatory.

### Warm Intro (Cisco AE or Partner Referral)

```
Hey [Name]!

Thank you for the introduction, [Referrer].

[Name], it's a pleasure to meet you and to be working with you on [project].

To keep things moving, could you confirm a few quick details?

- Qty and models (or a screenshot of your License Info page)
- Preferred term (1, 3, or 5 year)
- Any deadlines (expiration date, install window)

Once I have that, I'll send over options right away.

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### Quote Delivery (Two Options)

```
Hey [Name]!

For your convenience, here are two options based on what we discussed:

Option A: [Model], [Term]
[Order link]

Option B: [Model], [Term]
[Order link]

Quantities and terms can be adjusted anytime. Just let me know what you'd like changed.

How does everything look?

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### Renewal Links

```
Sounds good!

For your convenience, here are links to purchase [qty] x [license or model] whenever the time is right:

1 Year: [link]

3 Year: [link]

5 Year: [link]

Let me know if you'd like to adjust the term or quantities.

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### License Key Delivery Help

```
Hey [Name]!

I see Cisco already sent the license key email on [date].

For your convenience, here's the copy below so you can claim it right away.

[Key details]

If you want, reply with a screenshot of what you see under Organization > Licensing and I'll confirm everything looks right.

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### Soft Follow-Up

```
Hey [Name], hope all has been well!

Just following up to see if you had a chance to review the quote options.

What has feedback been so far?

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### Approval/Finance Follow-Up

```
Hi [Name],

Following up to see if you had a chance to review this with your finance team.

Do you have any updates on the approval, or is this something you'd like to move forward with?

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### Ordering Workflow (Set Expectations)

```
You got it!

I just sent over the contract via ZohoSign to initiate the order.

Once completed, you'll automatically receive an invoice via email to pay online. After payment clears, the order goes to Cisco for processing and you should receive the license key or tracking within 24 to 48 hours.

Let me know once you've completed everything so I can help put it on the fast track.

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

### Deal Gone Quiet (Close-Out)

```
Hey [Name], hope you've been well!

I wanted to check in one more time on [project/quote]. If the timing isn't right or priorities have shifted, no worries at all. I'll close this out for now and we can always pick it back up down the road.

Just say the word if anything changes.

Best,
Chris Graves
Regional Sales Director
Stratus Information Systems
415-326-3661
chrisg@stratusinfosystems.com
Sales & Logistics | Project Consulting | IT Management | Install & Config | Purchase Financing
```

---

## Cascade Prevention (CRITICAL)

### Rule: Never Batch Zoho + External Send in Parallel

Zoho CRM MCP calls and external send calls (Pipedream, Zapier) must NEVER execute in the same parallel block.

### Rule: Email Must Confirm Before CRM Updates

Email must be confirmed sent before any CRM record updates (close task, change deal stage, etc.).

### Rule: One Email at a Time in Task Workflows

Process sequentially: send email -> confirm -> close task -> verify -> next task.

---

## Important Rules

### Never Auto-Send

Always present the full draft for review before sending. Never call any send tool without explicit "send" approval.

### Gmail MCP = Search and Read Only

search_gmail_messages and read_gmail_thread are for finding threads and extracting context only. Never attempt to send via native Gmail MCP tools.

### Threading Rules

- ALWAYS search Gmail for original thread before composing a reply
- Use exact subject line from original thread
- Match all recipients from the most recent message
- For Pipedream: include message ID AND thread ID in instruction
- For Zapier: pass thread_id in instructions text

### Failover Behavior

```
NEW EMAIL:
  TIER 1: Pipedream (instruction singular!)
    -> TIER 2: ZohoCRM_Send_Mail (chat only)
    -> TIER 3: Gmail compose link
    -> TIER 4: Zapier (limited credits)

THREAD REPLY:
  TIER 1: Pipedream (with In-Reply-To threading)
    -> TIER 3: Gmail compose link (won't thread)
    -> TIER 4: Zapier gmail_reply_to_email (uses credits)
```

---

## Error Handling

### Pipedream Send Failure (Tier 1)

1. Check error: if parameter error, verify using "instruction" (singular), retry
2. If sub-agent confusion: rephrase instruction more clearly, retry once
3. If service outage: fall to Tier 2 (chat) or Tier 3

### Pipedream Sub-Agent Asks for Confirmation

Normal behavior. Resend instruction with "Yes, send the email now." prepended.

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Pipedream "instruction Required" | Used instructions (plural) | Use instruction (singular) |
| Pipedream sub-agent asks to confirm | Normal behavior | Resend with "Yes, send now" prepended |
| Pipedream timeout | Service issue | Fall to Tier 2/3 |
| Zapier timeout | Network/API issue | Fall to Gmail compose link |
| Zoho invalid module | Wrong module name | Check API name spelling |
| Zoho record not found | Bad record ID | Re-search for correct ID |
| Thread not found | No Gmail match | Broaden search or send as new |

---

## Quick Reference Checklist

```
REPLY WORKFLOW (BOTH MODES):
[ ] Search Gmail for original thread (MANDATORY)
[ ] Read full thread for context, subject, message ID, and recipients
[ ] Compose reply using Chris Graves style guide
[ ] Enforce mandatory line spacing
[ ] Present draft with tier indicator for approval
[ ] Send via Pipedream with threading (Tier 1) - USE "instruction" SINGULAR
  -> If fails: Gmail compose link (Tier 3) or Zapier (Tier 4)

NEW EMAIL WORKFLOW (BOTH MODES):
[ ] Find CRM record if customer referenced
[ ] Compose using Chris Graves style guide
[ ] Enforce mandatory line spacing
[ ] Present draft with "Path: Pipedream (Tier 1)" for approval
[ ] Send via Pipedream (Tier 1) - USE "instruction" SINGULAR
  -> If fails (Chat): Zoho CRM Send Mail (Tier 2)
  -> If fails: Gmail compose link (Tier 3)
  -> Last resort: Zapier (Tier 4)

NEVER:
x Auto-send without approval
x Use "instructions" (plural) for Pipedream (MUST be "instruction" singular)
x Use "instruction" (singular) for Zapier (MUST be "instructions" plural)
x Confuse Pipedream (UUID 4804cd9a) with Zapier (UUID 91a221c4)
x Use Zapier as first choice (Tier 4 only, limited credits)
x Use native Gmail MCP to send (search/read only)
x Use Gmail MCP message IDs for Pipedream thread replies (use Pipedream's own list)
x Skip Gmail thread search for replies
x Skip the draft review step
x Show signature in draft preview (signature auto-included in send instruction)
x Use em dashes
x Batch Zoho CRM + Pipedream/Zapier calls in same parallel block
x Close a CRM task before confirming email was sent
x Present draft with two paragraphs touching without a blank line between them
```

---

## Integration Points

**Email Send Tools (4-Tier Priority):**
- Tier 1: Pipedream gmail-send-email (all modes, new + replies, instruction singular)
- Tier 2: ZohoCRM_Send_Mail (chat mode only, new emails only)
- Tier 3: Gmail compose URL (all modes, manual send, no threading)
- Tier 4: Zapier gmail_send_email / gmail_reply_to_email (limited credits)

**Search and Read Tools (Gmail MCP only, never send):**
- search_gmail_messages (find thread)
- read_gmail_thread (extract context, subject, message ID, recipients)

**Companion Skills:**
- zoho-crm-v27 (CRM operations, task lifecycle, cascade prevention, never-close-won)
- license-renewal-email-v1-1 (renewal-specific workflows)
- fu30-followup-automation-v1-3 (30-day follow-ups with atomic lifecycle, Pipedream-first)

---

## Changelog

### v3.5 (Current)

- **DRAFT PRESENTATION RULES**: Body ends at closing line, no signature in draft preview, signature auto-included in send instruction
- **PIPEDREAM MESSAGE ID SOURCING**: Thread reply message IDs must come from Pipedream's own list, not Gmail MCP
- **EMAIL OPT-OUT SCOPE**: Clarified that opt-out only affects Zoho CRM Mail (Tier 2), not Pipedream or Zapier
- **TOOL UUID IDENTIFICATION TABLE**: Embedded UUID and parameter reference for Pipedream vs Zapier
- **STRENGTHENED SPACING**: Explicit blank-line-between-every-paragraph enforcement with validation checklist
- **UPDATED COMPANION SKILLS**: References zoho-crm-v27, fu30-followup-automation-v1-3
- All v3.4 Pipedream threading, 4-tier routing, style guide retained

### v3.4

- **Pipedream Tier 1 for ALL emails**: Primary send path for new emails AND thread replies in all environments
- **Proven thread reply support**: Pipedream threading confirmed working 2/27/2026 with In-Reply-To headers
- **CRITICAL parameter bug documented**: Pipedream uses instruction (singular), not instructions (plural) despite schema
- **4-Tier routing**: Pipedream > Zoho (chat) > Gmail compose > Zapier (limited credits)
- **Zapier demoted to Tier 4**: Only used as last resort due to credit limitations
- All v3.3 cascade prevention, style guide, spacing enforcement retained

### v3.3

- Cowork Mode: Pipedream Primary Send for new outbound emails
- Zoho CRM Mail Fallback, Instructions-Only Format Documentation
- Signature Toggle, Three-Tier Cowork Failover

### v3.2

- Cascade Prevention, Atomic Lifecycle Integration, One-at-a-Time Task Emails

### v3.1

- Environment-Aware Routing, Mandatory Line Spacing Enforcement

### v3.0

- Zapier Primary Send, Three-Tier Failover, Chris Graves Style Guide

### v2.0

- Threaded Reply Support, Dual Send Path, Batch Email Support

### v1.0

- Initial release with core ZohoCRM_Send_Mail documentation
