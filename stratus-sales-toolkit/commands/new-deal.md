---
description: Create a new deal in Zoho CRM with full validation
argument-hint: "<company name> [amount] [stage]"
---

# /new-deal

Create a new deal in Zoho CRM. Arguments: $ARGUMENTS

Follow the `zoho-crm-v28` skill. Required fields: Deal Name, Account, Stage, Lead Source, Meraki ISR, Close Date, Amount.

## Rules
- NEVER use Lead_Source = "-None-" — ask if not clear
- Default Lead_Source = "Stratus Referal", Meraki_ISR = "Stratus Sales"
- Display a pre-creation validation table before any API call
- Create successor follow-up task after deal creation (3 business days, skip weekends)
- NEVER manually set Stage to "Closed Won"
