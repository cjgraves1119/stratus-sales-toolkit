---
description: Renew a Meraki/Cisco subscription in CCW
argument-hint: "<deal name or subscription ID>"
---

# /renew-sub

Renew a Cisco/Meraki subscription via CCW browser automation. Arguments: $ARGUMENTS

Follow the `ccw-subscription-renewal-v1-2` skill exactly.

1. Fetch Subscription ID from Zoho CRM Notes field
2. Navigate CCW and execute the renewal flow (JS-only page transitions, no screenshot waits)
3. Extract the new CCW quote number
4. Write CCW quote number and deal ID back to Zoho CRM
5. Confirm completion and display results

Supports batch renewals — specify multiple deals in arguments.
