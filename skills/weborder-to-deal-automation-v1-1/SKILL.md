---
name: weborder-to-deal-automation-v1-1
description: automate closed-won deal creation from cisco/meraki weborders with account lookup, deal naming, po linking, and automatic cisco rep assignment via gmail search. searches deal approval emails to identify cisco reps and assigns them to meraki_isr field.
---

# WebOrder to Deal Automation

Streamlines the process of converting WebOrders/Purchase Orders into closed deals with automatic account lookup, standardized configurations, and Cisco rep assignment.

## When to Use

Prompt this skill when you have one or more WebOrder numbers (e.g., N68645, N68708, etc.) and need to:

- Create deals for each WebOrder
- Automatically look up the associated account
- Link deals and POs bidirectionally
- Identify and assign Cisco reps from deal approval emails
- Apply standard settings (Closed Won, Stratus Referral)

**Trigger phrases:**
- "Create deals for these WebOrders"
- "Assign WebOrder N68645, N68708, etc. to new deals"
- "Process these POs and create corresponding deals"

## Core Workflow

For each WebOrder provided:

1. **Search Sales_Orders module** for the WebOrder number
2. **Extract Account Name** (lookup field ID) and Grand_Total for Amount
3. **Generate Deal Name** using pattern: `[Account Name] [Context] (N[ORDER_NUMBER])`
4. **Create Deal** with standardized fields (initially with Stratus Sales as Meraki_ISR)
5. **Link PO to Deal** by updating Sales_Orders with the Deal_Name ID
6. **Search Gmail for Cisco rep** using deal approval emails
7. **Update Meraki_ISR** with identified Cisco rep (if found)

## Cisco Rep Assignment Workflow

After deals are created and POs linked, identify Cisco reps:

### Step 1: Search Gmail
For each WebOrder, search Gmail:
```
Query: "N[ORDER_NUMBER] Cisco deal approval"
```

### Step 2: Extract Cisco Rep Emails
Look for pattern in email content:
- "Cisco Reps Involved:" followed by email addresses
- Format: `alexisma@cisco.com, jbermeop@cisco.com, tydoll@cisco.com`

### Step 3: Look Up Reps in Meraki_ISRs Module
For each extracted email, search:
```
Module: Meraki_ISRs
email: "[cisco_rep_email]"
fields: "id,Name,Email"
```

### Step 4: Assignment Logic

| Scenario | Action |
|----------|--------|
| **0 reps found in Meraki_ISRs** | Keep Stratus Sales (ID: 2570562000027286729) |
| **1 rep found in Meraki_ISRs** | Update deal with that rep's ID |
| **2+ reps found in Meraki_ISRs** | Flag for user clarification before assigning |
| **No approval email found** | Keep Stratus Sales (standard/auto-approved deals) |

### Step 5: Update Deal
```python
Module: Deals
Record ID: [deal_id]
Update: {"data": [{"Meraki_ISR": {"id": "[cisco_rep_id]"}}]}
```

## Field Mappings & Constants

**Stratus Sales ISR ID (default fallback):**
```
2570562000027286729
```

**Deal Creation Fields:**
```
Stage = "Closed Won"
Lead_Source = "Stratus Referral"
Meraki_ISR = {"id": "2570562000027286729"}  # Updated after Cisco rep lookup
Reason = "Needs a specialist"
Closing_Date = Today (format: YYYY-MM-DD)
Amount = Grand_Total from Sales_Order
```

**Deal Name Format:**
```
[Account Name] [Auto-Generated Context] (N[ORDER_NUMBER])
```

Examples:
- "Keating Tractor Network Upgrade (N68645)"
- "CapCom Technology Solutions Network Infrastructure (N69775)"

Context suggestions: Network Upgrade, Wireless Refresh, Network Deployment, IT Infrastructure, Platform Migration, Enterprise Security Suite, Network Consolidation, Connectivity Expansion, IT Solutions, Network Expansion.

## Search Syntax

**Find WebOrder Account:**
```
Module: Sales_Orders
criteria: "(Subject:equals:Weborder N[ORDER_NUMBER])"
fields: "id,Subject,Account_Name,Grand_Total"
```

**Find Cisco Rep by Email:**
```
Module: Meraki_ISRs
email: "[cisco_rep_email]@cisco.com"
fields: "id,Name,Email"
```

## Create Multiple Deals in Batch

When processing multiple WebOrders, batch create deals in a single API call:

```python
{
  "data": [
    {
      "Stage": "Closed Won",
      "Amount": 18149.53,
      "Reason": "Needs a specialist",
      "Deal_Name": "[Generated Name 1]",
      "Meraki_ISR": {"id": "2570562000027286729"},
      "Lead_Source": "Stratus Referral",
      "Account_Name": {"id": "[account_id_1]"},
      "Closing_Date": "2025-12-10"
    }
  ]
}
```

Batch create returns array of deal IDs in same order as request.

## Link POs to Deals

After deal creation, update each Sales_Orders record:
```python
Module: Sales_Orders
Record ID: [po_id]
Update: {"data": [{"Deal_Name": {"id": "[deal_id]"}}]}
```

## URL Output

Generate shareable URLs:
```
https://crm.zoho.com/crm/org647122552/tab/Deals/[DEAL_ID]
```

## Summary Output

After processing all WebOrders, provide a summary table:

| WebOrder | Account | Amount | Cisco Rep | Deal URL |
|----------|---------|--------|-----------|----------|
| N69775 | CapCom Technology Solutions | $18,149.53 | Alex Martinez | [URL] |
| N69828 | FSI Strategies | $2,351.00 | Stratus Sales (default) | [URL] |

## Error Handling

| Scenario | Action |
|----------|--------|
| WebOrder not found | Alert user, skip that order, continue with others |
| Account not found | Alert user with order number, skip linking |
| Deal creation fails | Log error, stop batch, report which orders failed |
| Gmail search returns no results | Use Stratus Sales as default ISR |
| Multiple Cisco reps in Meraki_ISRs | Ask user which rep to assign |

## Best Practices

1. Batch create deals when possible (multiple orders at once)
2. Link POs immediately after successful deal creation
3. Search Gmail for Cisco reps after all deals are created
4. Only update Meraki_ISR when a single matching rep is found
5. Flag ambiguous cases (2+ reps found) for user decision
6. Include Amount from Sales_Order Grand_Total
7. Output summary table with Cisco rep assignments for verification
