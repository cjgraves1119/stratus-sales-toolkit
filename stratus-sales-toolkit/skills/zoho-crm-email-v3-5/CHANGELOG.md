# Zoho CRM Email - Changelog

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
