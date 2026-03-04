---
description: Create a Closed Won deal from a Cisco/Meraki weborder
argument-hint: "<weborder number or paste weborder details>"
---

# /weborder

Convert a Cisco/Meraki weborder into a Closed Won deal in Zoho CRM. Arguments: $ARGUMENTS

Follow the `weborder-to-deal-automation-v1-1` skill.

1. Parse weborder details (PO number, account, products, amount)
2. Look up or create the Account in Zoho CRM
3. Search Gmail for deal approval email to identify the Cisco rep
4. Create the Deal with Stage = "Closed Won" and link the PO/Sales Order
5. Assign Meraki ISR from the Gmail-identified Cisco rep
6. Create a FU30 follow-up task (30 days out)

NEVER manually set Stage = "Closed Won" without a linked Sales Order/PO.
