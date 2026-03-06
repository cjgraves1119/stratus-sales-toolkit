---
name: plugin-setup-guide
description: automatic user detection and mcp connection health check for stratus sales toolkit. detects who the user is, what connections are active, and guides setup of any missing mcp integrations required for skill operations. triggers: setup, plugin setup, check connections, check my setup, am i set up, whats missing, configure plugin, onboarding, getting started, help me set up.
---

# Plugin Setup Guide

Automatically detects the current user's identity, checks which MCP connections are active, and guides them through setting up any missing integrations required by the Stratus Sales Toolkit skills.

## When to Run

- First time a user installs the plugin
- When any skill fails due to a missing MCP connection
- When user asks "setup", "check connections", "am I set up?", "what's missing?"
- Proactively on first interaction if user identity is unknown

## Phase 1: User Identification

### Step 1: Detect User Identity

Try these methods in order. Stop at the first success:

**Method A: Gmail Profile (fastest)**
```
Call: gmail_get_profile (MCP tool: 28661f0e)
Extract: emailAddress, messagesTotal
```
If this returns successfully, the user has Gmail connected and you have their email.

**Method B: Google Calendar Profile**
```
Call: gcal_list_calendars (MCP tool: f9e93729)
Look for: primary calendar → id (this is the user's email)
```

**Method C: Zoho CRM Current User**
```
Call: ZohoCRM_Get_Records (module: "Users", type: "CurrentUser")
Extract: email, full_name, id
```

**Method D: Ask the User**
If all automated methods fail:
```
"I wasn't able to detect your identity automatically. What's your email address?
This helps me configure the toolkit for your Zoho CRM records and email routing."
```

### Step 2: Display User Profile

Once identified, display:

```
DETECTED USER PROFILE:
| Field | Value |
|-------|-------|
| Name | {name} |
| Email | {email} |
| Zoho Owner ID | {id or "needs lookup"} |
```

If the user is Chris Graves (chrisg@stratusinfosystems.com), set Zoho Owner ID = 2570562000141711002 (from preferences).

For any other user, look up their Zoho Owner ID:
```
ZohoCRM_Search_Records → module: "Users", email: "{detected_email}"
```

---

## Phase 2: Connection Health Check

Test each required MCP connection by making a lightweight probe call. Categorize results as CONNECTED, MISSING, or ERROR.

### Connection Test Matrix

Run ALL tests in parallel for speed:

| Connection | Test Call | Success Indicator | Required By |
|------------|----------|-------------------|-------------|
| Zoho CRM MCP | `ZohoCRM_Get_Records(module: "Deals", per_page: 1)` | Returns data array | All CRM skills |
| Gmail (Native) | `gmail_get_profile()` | Returns emailAddress | Email search, deal context |
| Google Calendar (Native) | `gcal_list_calendars()` | Returns calendars array | Daily briefing, scheduling |
| Pipedream Gmail | `gmail-find-email(instruction: "find most recent email")` | Returns result | Email sending (Tier 1) |
| Webex | `cisco_webex-list-messages(instruction: "list messages in most recent room, max 1")` | Returns messages | Bot messaging, rep comms |
| Gmail Reply (Zapier) | `gmail_create_draft_reply(instructions: "test connection", output_hint: "connection status")` | Returns result (cancel draft after) | Direct email replies |
| Firecrawl | `firecrawl_search(query: "test", limit: 1)` | Returns results | E-Rate bid scanning |

### Important Notes on Testing

- **Gmail Native vs Pipedream Gmail vs Zapier Gmail**: These are THREE separate connections serving different purposes:
  - Gmail Native (28661f0e prefix: `gmail_search_messages`, `gmail_read_message`, `gmail_get_profile`) = Search and read only
  - Pipedream Gmail (4804cd9a prefix: `gmail-send-email`, `gmail-find-email`) = Sending emails (Tier 1)
  - Zapier Gmail (91a221c4 prefix: `gmail_reply_to_email`, `gmail_send_email`) = Reply threading, last resort sending (Tier 4)

- **Do NOT test destructive actions.** Use read-only probes only.

### Connection Results Display

After all tests complete, display:

```
MCP CONNECTION HEALTH CHECK:
| # | Connection | Status | Required For |
|---|-----------|--------|-------------|
| 1 | Zoho CRM | ✅ Connected | All CRM operations |
| 2 | Gmail (Native) | ✅ Connected | Email search, deal context |
| 3 | Google Calendar | ✅ Connected | Daily briefing, scheduling |
| 4 | Pipedream Gmail | ❌ Missing | Email sending (Tier 1) |
| 5 | Webex | ✅ Connected | Bot messaging, rep comms |
| 6 | Gmail Reply (Zapier) | ⚠️ Optional | Direct email replies (Tier 4) |
| 7 | Firecrawl | ⚠️ Optional | E-Rate bid scanning |

SUMMARY: 4/5 required connections active. 1 setup needed.
```

Status icons:
- ✅ = Connected and working
- ❌ = Missing (required) — needs setup
- ⚠️ = Missing (optional) — works without it but some features limited
- 🔴 = Error (connected but failing) — needs troubleshooting

### Connection Priority Classification

**Required (skills will fail without these):**
1. Zoho CRM MCP — needed by ALL deal/quote/task skills
2. Gmail (Native) — needed for email search, deal context, task evaluation
3. Pipedream Gmail — needed for email sending (Tier 1 routing)
4. Webex — needed for Commerce Bot, rep messaging, internal chat

**Recommended (significant features depend on these):**
5. Google Calendar — daily briefing, meeting scheduling

**Optional (specific workflows only):**
6. Gmail Reply (Zapier) — email reply threading (Tier 4 fallback)
7. Firecrawl — E-Rate USAC SODA API scanning, web scraping

---

## Phase 3: Setup Guidance for Missing Connections

For each MISSING or ERROR connection, provide step-by-step setup instructions. Present ONLY the ones that need setup (skip already-connected ones).

### 3A: Zoho CRM MCP Setup

```
ZOHO CRM CONNECTION SETUP:

1. Go to https://www.zoho.com/mcp/ in your browser
2. Sign in with your Zoho CRM credentials
3. Click "Connect to Claude" or "Generate MCP Configuration"
4. In Claude Cowork, go to Settings → MCP Servers
5. Add the Zoho CRM MCP connection using the configuration provided

REQUIRED TOOLS TO ENABLE (check ALL of these in MCP settings):
  ☐ ZohoCRM_Get_Record
  ☐ ZohoCRM_Get_Records
  ☐ ZohoCRM_Search_Records
  ☐ ZohoCRM_Create_Records
  ☐ ZohoCRM_Update_Record
  ☐ ZohoCRM_Update_Records
  ☐ ZohoCRM_Delete_Record
  ☐ ZohoCRM_Get_Fields
  ☐ ZohoCRM_Get_Field
  ☐ ZohoCRM_Get_Module
  ☐ ZohoCRM_Get_Modules
  ☐ ZohoCRM_getRelatedRecords
  ☐ ZohoCRM_getRelatedRecord
  ☐ ZohoCRM_Create_Notes
  ☐ ZohoCRM_Send_Mail
  ☐ ZohoCRM_Clone_Record

After connecting, re-run this setup check to verify.
```

### 3B: Gmail (Native) Setup

```
GMAIL (NATIVE) CONNECTION SETUP:

This is the built-in Gmail integration in Claude Cowork (not Pipedream or Zapier).

1. In Claude Cowork, go to Settings → Connectors
2. Find "Gmail" under Google integrations
3. Click "Connect" and authorize with your Google account
4. Grant read access to Gmail

This enables: gmail_search_messages, gmail_read_message, gmail_get_profile
Used for: Searching email history, reading deal context, identifying contacts
```

### 3C: Google Calendar (Native) Setup

```
GOOGLE CALENDAR CONNECTION SETUP:

1. In Claude Cowork, go to Settings → Connectors
2. Find "Google Calendar" under Google integrations
3. Click "Connect" and authorize with your Google account
4. Grant calendar read/write access

This enables: gcal_list_events, gcal_create_event, gcal_find_meeting_times, etc.
Used for: Daily briefing, meeting scheduling, availability checks
```

### 3D: Pipedream Gmail (Email Sending) Setup

```
PIPEDREAM GMAIL CONNECTION SETUP (Tier 1 Email Sending):

This is the PRIMARY email sending method. Must be set up for email workflows.

1. Create a Pipedream account at https://pipedream.com/ if you don't have one
2. In Claude Cowork, go to Settings → Connectors
3. Search for "Pipedream" and click Connect
4. Authorize Pipedream with your Google/Gmail account
5. Ensure the Gmail actions are enabled in Pipedream

CRITICAL: The Pipedream Gmail tool uses "instruction" (SINGULAR) as its parameter.
Do NOT confuse with Zapier Gmail which uses "instructions" (PLURAL).

Tool prefix: 4804cd9a
Key tools: gmail-send-email, gmail-find-email, gmail-create-draft
Used for: All outbound email sending, draft creation
```

### 3E: Webex Setup

```
WEBEX CONNECTION SETUP:

1. In Claude Cowork, go to Settings → Connectors
2. Search for "Webex" or "Cisco Webex"
3. Click "Connect" and sign in with your Webex credentials
4. Authorize Claude to send and read messages

Key tools: cisco_webex-create-message, cisco_webex-list-messages
Used for: Commerce Bot lead times, Stratus Chatbot pricing, rep messaging
```

### 3F: Gmail Reply (Zapier) Setup

```
GMAIL REPLY CONNECTION SETUP (Optional — Tier 4):

This is a FALLBACK email tool. Only needed if Pipedream threading doesn't work.
Uses Zapier credits, so use sparingly.

1. In Claude Cowork, go to Settings → Connectors
2. Search for "Zapier" and connect your account
3. Enable Gmail actions in your Zapier integration
4. Authorize Gmail access through Zapier

Tool prefix: 91a221c4
CRITICAL: Uses "instructions" (PLURAL) — different from Pipedream's "instruction" (SINGULAR)
Key tools: gmail_reply_to_email, gmail_send_email, gmail_create_draft_reply
Used for: Email reply threading when Pipedream can't thread
```

### 3G: Firecrawl Setup

```
FIRECRAWL CONNECTION SETUP (Optional — E-Rate workflows):

Only needed if you work with E-Rate proposals and bid scanning.

1. In Claude Cowork, go to Settings → Connectors
2. Search for "Firecrawl" and click Connect
3. Follow the authorization flow

Setup details are also documented in the erate-proposal-workflow skill.

Key tools: firecrawl_search, firecrawl_scrape, firecrawl_agent
Used for: USAC SODA API bid scanning, Form 470 lookups, web research
```

---

## Phase 4: Skill-to-Connection Dependency Map

After checking connections, show the user which skills are fully operational and which have gaps:

```
SKILL READINESS:
| Skill | Required Connections | Status |
|-------|---------------------|--------|
| zoho-crm-v30 | Zoho CRM, Gmail Native | ✅ Ready |
| zoho-crm-email-v3-5 | Zoho CRM, Pipedream Gmail | ❌ Missing Pipedream |
| daily-task-engine-v1-8 | Zoho CRM, Gmail Native, Pipedream Gmail, Calendar | ✅ Ready |
| fu30-followup-automation-v1-3 | Zoho CRM, Gmail Native, Pipedream Gmail | ❌ Missing Pipedream |
| stratus-quoting-bot-v4-6 | None (embedded catalog) | ✅ Ready |
| stratus-quote-pdf-v2-0 | Zoho CRM | ✅ Ready |
| subscription-modification-v2-6 | Zoho CRM | ✅ Ready |
| ccw-subscription-renewal-v1-2 | Zoho CRM, Chrome Browser | ✅ Ready |
| coterm-calculator-v1-0 | None (embedded cache) | ✅ Ready |
| webex-bots-v1-7 | Webex | ✅ Ready |
| weborder-to-deal-automation-v1-1 | Zoho CRM, Gmail Native | ✅ Ready |
| erate-proposal-workflow-v1-2 | Zoho CRM, Firecrawl | ⚠️ Missing Firecrawl |
| pharos-iq-automation | Zoho CRM | ✅ Ready |
| skill-creator-v9 | GitHub PAT (in preferences) | ✅ Ready |
```

### Skill Dependency Details

| Skill | Zoho CRM | Gmail Native | Pipedream | Webex | Calendar | Zapier Gmail | Firecrawl |
|-------|----------|-------------|-----------|-------|----------|-------------|-----------|
| zoho-crm-v30 | REQ | REQ | — | — | — | — | — |
| zoho-crm-email-v3-5 | REQ | REQ | REQ | — | — | OPT | — |
| daily-task-engine-v1-8 | REQ | REQ | REQ | — | OPT | OPT | — |
| fu30-followup-automation-v1-3 | REQ | REQ | REQ | — | — | OPT | — |
| stratus-quoting-bot-v4-6 | — | — | — | — | — | — | — |
| stratus-quote-pdf-v2-0 | REQ | — | — | — | — | — | — |
| subscription-modification-v2-6 | REQ | — | — | — | — | — | — |
| ccw-subscription-renewal-v1-2 | REQ | — | — | — | — | — | — |
| coterm-calculator-v1-0 | — | — | — | — | — | — | — |
| webex-bots-v1-7 | — | — | — | REQ | — | — | — |
| weborder-to-deal-automation-v1-1 | REQ | REQ | — | — | — | — | — |
| erate-proposal-workflow-v1-2 | REQ | — | — | — | — | — | REQ |
| pharos-iq-automation | REQ | — | — | — | — | — | — |
| skill-creator-v9 | — | — | — | — | — | — | — |

Legend: REQ = Required, OPT = Optional, — = Not needed

---

## Phase 5: Summary and Next Steps

After presenting all results, provide a clear action summary:

```
SETUP SUMMARY:
✅ {X} connections active
❌ {Y} required connections missing
⚠️ {Z} optional connections missing

{X}/{total} skills fully operational

NEXT STEPS:
1. [If missing required] Set up {connection name} — instructions above
2. [If all required present] You're all set! All core skills are operational.
3. [If optional missing] Optional: Set up {connection} to enable {skill features}

Run "check my setup" anytime to re-verify connections.
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| MCP call times out | Mark connection as "⚠️ Slow — may be temporarily unavailable" |
| MCP call returns auth error | Mark as "🔴 Auth Error — reconnect needed" + show setup steps |
| User identity not detected | Ask for email, proceed with manual setup |
| Zoho Owner ID not found | Ask user for their Zoho CRM profile link |
| Connection test returns unexpected format | Mark as "⚠️ Unknown — test manually" |

---

## Changelog

### v1.0 (Current)
- Initial release
- 4-phase workflow: user detection, connection health check, setup guidance, skill readiness
- 7 MCP connection tests with parallel execution
- Skill-to-connection dependency matrix (14 skills x 7 connections)
- Step-by-step setup instructions for all connections
- Tool UUID identification to prevent Pipedream/Zapier confusion
- User identity auto-detection via Gmail, Calendar, or Zoho
