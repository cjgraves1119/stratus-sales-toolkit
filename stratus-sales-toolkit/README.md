# Stratus Sales Toolkit

Sales operations plugin for Stratus Information Systems. Covers the full Cisco/Meraki deal lifecycle: quoting, CRM automation, task management, subscription processing, and customer communications.

## Skills

| Skill | Description |
|-------|-------------|
| **zoho-crm-v32** | Core CRM operations: deals, quotes, tasks, admin actions, send-quote-to-customer pipeline, mandatory follow-up task on quote creation |
| **zoho-crm-email-v3-6** | Email composition and sending with Pipedream-first routing and dynamic companion skill version resolution |
| **daily-task-engine-v2-1** | Token-optimized architecture with pre-built dashboard injector, file-piped sub-agent results, deferred companion skill loading. Interactive HTML dashboard output with card/compact/kanban views, inline email editing, batch approve/skip/reject, Send to Claude integration, dark mode, and chat table fallback. Adds Phase 1c orphaned deal check (open active deals with zero linked tasks) and dynamic companion skill version resolution |
| **fu30-followup-automation-v1-4** | 30-day post-sale follow-up email automation — always searches Gmail for context (no dollar threshold), dynamic companion skill version resolution, banned not_equals Zoho query fix |
| **stratus-quoting-bot-v4-6** | Cisco/Meraki URL quote generation with 1,222 SKU pricing catalog |
| **stratus-quote-pdf-v2-0** | Stratus-branded PDF quote generation from Zoho CRM data |
| **subscription-modification-v2-6** | Cisco subscription add-on and modification quote processing |
| **ccw-subscription-renewal-v1-2** | CCW subscription renewal workflow with browser automation |
| **coterm-calculator-v1-0** | Meraki co-term expiration date calculator (weighted dollar-value method) |
| **webex-bots-v1-7** | Commerce Bot (lead times) and Stratus Chatbot (pricing) via Webex |
| **weborder-to-deal-automation-v1-1** | Closed-won deal creation from Cisco/Meraki weborders |
| **erate-proposal-workflow-v1-2** | E-Rate Form 470 competitive bid workflow with Firecrawl-powered USAC SODA API, weekly bid scanner, and parallel agent evaluation |
| **pharos-iq-automation** | PharosIQ lead-to-deal conversion with Zoho CRM |
| **skill-creator-v10** | Skill authoring with eval/benchmark framework, plugin-aware mode, GitHub auto-sync, and description optimization |
| **plugin-setup-guide** | Automatic user detection and MCP connection health check — guides setup of missing integrations required for skill operations |
| **skill-downloader-v1-0** | Bulk export all plugin skills as .skill files for one-click install into standard Claude desktop sessions |

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
- "/UpdateSkills" or "download skills" → skill-downloader
