# FU30 Follow-Up Automation - Changelog

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
