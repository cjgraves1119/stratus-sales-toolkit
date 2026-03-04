---
description: Draft or send an email to a customer or Cisco contact
argument-hint: "<contact or deal name> [subject or context]"
---

# /email

Draft or send an email. Arguments: $ARGUMENTS

Follow the `zoho-crm-email-v3-5` skill. Use this routing order:

1. **Pipedream** (UUID 4804cd9a, param: `instruction` SINGULAR) — Tier 1, always try first
2. **Zoho CRM Mail** — Tier 2, new emails only (no thread replies)
3. **Gmail compose link** — Tier 3, manual send
4. **Zapier** (UUID 91a221c4, param: `instructions` PLURAL) — Tier 4, last resort only

## Voice Rules
- No em dashes ever
- Contractions natural (I'll, you're, we've)
- End every customer email with a question or CTA
- Blank line between every paragraph
- Never start with "I hope this email finds you well"
- Always show draft for approval before sending
