---
description: Generate a Cisco/Meraki quote (URL or Zoho CRM)
argument-hint: "<SKUs and quantities> [customer name]"
---

# /quote

Generate a Cisco/Meraki quote. Arguments: $ARGUMENTS

## Routing
- No customer mentioned → use `stratus-quoting-bot-v4-5` (URL quote)
- Customer mentioned → use `zoho-crm-v28` (Zoho Deal + Quote)
- Subscription file uploaded or "sub mod/add-on" → use `subscription-modification-v2-6`

## SKU Validation (always run before quoting)
- MR access points: `-HW` suffix
- MS switches: NO suffix
- MX/MV/MG/MT: `-HW` suffix
- CW (Wi-Fi 6E): `-MR` suffix
- Wi-Fi 7: `-RTG` suffix
- Validate license pairings match hardware and requested term
- Display validation table: Requested → Validated SKU → Status
- STOP and clarify if any SKU is invalid or ambiguous
