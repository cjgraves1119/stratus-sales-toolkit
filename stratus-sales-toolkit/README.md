# Stratus Sales Toolkit

Sales operations plugin for Stratus Information Systems. Covers the full Cisco/Meraki deal lifecycle: quoting, CRM automation, task management, subscription processing, and customer communications.

## Skills

| Skill | Description |
|-------|-------------|
| **zoho-crm-v28** | Core CRM operations: deals, quotes, tasks, admin actions |
| **zoho-crm-email-v3-5** | Email composition and sending with Pipedream-first routing |
| **daily-task-engine-v1-8** | Task review with canonical Zoho query, IR01 batch pre-filter, sub-agent verbosity cap, DR01 closed-won auto-close, embedded Chris Graves voice/style guide, and Phase 3 spacing+style gate |
| **fu30-followup-automation-v1-3** | 30-day post-sale follow-up email automation |
| **stratus-quoting-bot-v4-5** | Cisco/Meraki URL quote generation with 1,222 SKU pricing catalog |
| **stratus-quote-pdf-v2-0** | Stratus-branded PDF quote generation from Zoho CRM data |
| **subscription-modification-v2-6** | Cisco subscription add-on and modification quote processing |
| **ccw-subscription-renewal-v1-2** | CCW subscription renewal workflow with browser automation |
| **coterm-calculator-v1-0** | Meraki co-term expiration date calculator (weighted dollar-value method) |
| **webex-bots-v1-6** | Commerce Bot (lead times) and Stratus Chatbot (pricing) via Webex |
| **weborder-to-deal-automation-v1-1** | Closed-won deal creation from Cisco/Meraki weborders |
| **erate-proposal-workflow-v1-1** | E-Rate Form 470 competitive bid workflow |
| **pharos-iq-automation** | PharosIQ lead-to-deal conversion with Zoho CRM |
| **skill-creator-v9** | Skill authoring with plugin-aware mode — auto-updates plugin.json and README when skill folder names change |

## Required Connectors

This plugin works with the following MCP integrations:

- **Zoho CRM** (required)
- **Gmail** (required for email and deal context)
- **Webex** (required for bot messaging and rep communication)
- **Google Calendar** (optional, for scheduling)

## Setup

1. Install this plugin in Claude Cowork
2. Ensure Zoho CRM, Gmail, and Webex MCP connectors are configured
3. Skills will trigger automatically based on natural language requests

## Usage

Skills activate on natural language triggers. Examples:

- "Create a quote for 10 MR46-HW" → stratus-quoting-bot
- "New deal for Acme Corp" → zoho-crm
- "Run my tasks" → daily-task-engine
- "Send fu30 emails" → fu30-followup-automation
- "Renew subscription" → ccw-subscription-renewal
- "Lead time on MS425-32" → webex-bots (Commerce Bot)
- "Process this sub mod file" → subscription-modification
