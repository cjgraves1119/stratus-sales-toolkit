# True Forward Workflow

## What a True Forward Is

A **True Forward** is a periodic Cisco-generated mid-EA consumption check, distinct from a Subscription Modification:

| | True Forward | Subscription Mod |
|---|---|---|
| Trigger | Annual EA anniversary (mid-term) | Customer adds licenses |
| Source file | Cisco TF report (xlsx, named like `TrueForwardReport_{Customer}_{SubID}_{Date}_Detailed.xlsx`) | CCW xls quote |
| Math basis | Cisco-calculated cost per line, already discounted | Pricing term × line totals, raw |
| Purpose | Bill for overconsumed licenses, credit for underconsumed | Add or modify licenses on existing sub |
| Margin formula | `customer_price = cisco_net_cost / 0.80` (true 20%) | `discount = list_price × 30%` (Meraki) or `× 45%` (EA 3.0) per line |

## Trigger Phrases

- "True Forward"
- "TF report"
- "true forward quote"
- "create an invoice for their true forward"
- "TF for [customer]"
- File names matching `TrueForward*Report*` or `TF*Report*`

If the file is the standard CCW sub mod xls (not a Cisco-generated TF report), use the regular sub mod workflow instead.

## TF Report Structure

The Cisco TF report contains:

1. **Header section** (top of sheet):
   - Customer name
   - Buying Program ID (`EA####`)
   - Subscription ID (`SR######`)
   - EA Start Date / End Date
   - Remaining term in months
   - Report generation date
   - Next True Forward date

2. **Per-SKU detail lines**, each marked with one of:
   - **Fully Consumed** — purchased qty matches deployed qty, no charge
   - **Overconsumed** — deployed > purchased, charged for the delta
   - **Underconsumed** — deployed < purchased, generates a Value Shift credit

3. **Per-line columns** include:
   - SKU
   - Description
   - Purchased Quantity
   - Consumed Quantity
   - Status
   - Unit Cost (Net) — already at customer's negotiated EA discount
   - Total Cost — for charge lines
   - Adjustment for Returned Licenses — for credit lines (negative)

4. **Rollup totals** at bottom:
   - Cost of Added Licenses (sum of overconsumed)
   - Adjustment for Returned Licenses (sum of underconsumed credits)
   - **Net True Forward Cost** = Added - Adjustment

## Pricing Logic

Apply the markup **per-line, on every charge AND credit line**, not on the rollup.

```
For each charge line:    customer_unit_price = (cisco_total_cost / 0.80) / qty
For each credit line:    customer_unit_credit = (cisco_credit_amount / 0.80) / qty
```

This way the value shift flows through to the customer at the same 20% margin. Stratus margin = `Net TF Cost × 0.25` (because cost / 0.80 = cost × 1.25, so margin = cost × 0.25).

### Worked Example (Andy Mohr Automotive, SR111313, Apr 2026)

Net TF Cost from Cisco: $3,906.30
- Charges total (Cisco): $11,581.50 → Customer: $14,476.94
- Credits total (Cisco): -$7,675.20 → Customer: -$9,594.00
- Net pre-tax to customer: $4,882.94 (Cisco $3,906.30 / 0.80)
- Stratus margin: $976.64

## Quote Line Structure (matches Cisco TF report visually)

The quote should mirror what the customer sees on Cisco's report. Three line groups:

### Group 1: Charges (one line per Overconsumed SKU)

| Field | Value |
|---|---|
| Product_Name.id | Zoho ID for the SKU |
| Quantity | Overconsumed delta from report |
| List_Price | `(cisco_net_cost / 0.80) / qty` rounded to 2 decimals |
| Discount | 0 |
| Description | "True Forward EA charge - {qty} overconsumed licenses (per {SubID} {month year} report)" |

### Group 2: Value Shift Credits (one line per Underconsumed SKU with balance > 0)

Use **positive List_Price + oversized Discount** to drive the line net negative. Do NOT use negative List_Price (Zoho accepts it but the printed quote PDF formatting is awkward).

| Field | Value |
|---|---|
| Product_Name.id | Zoho ID for the SKU |
| Quantity | Underconsumed balance (positive integer from report) |
| List_Price | `(cisco_credit_amount / 0.80) / qty` rounded to 2 decimals (POSITIVE) |
| Discount | `2 × (List_Price × Quantity)` to drive net negative equal to `-(List_Price × Quantity)` |
| Description | "Value Shift Credit - {qty} unused licenses (Underconsumed per {SubID} {month year} report)" |

Math check: net = `(List × Qty) - Discount = (List × Qty) - 2×(List × Qty) = -(List × Qty)` ✓

### Group 3: Unchanged EA Inventory (one line per Fully Consumed SKU)

These show the rest of the customer's EA at $0 net for full subscription transparency. They're informational only.

| Field | Value |
|---|---|
| Product_Name.id | Zoho ID for the SKU |
| Quantity | Purchased qty (from EA inventory, NOT from TF report) |
| List_Price | Default Zoho `Unit_Price` for the SKU (1-month rate) |
| Discount | `List_Price × Quantity` (drives net to $0) |
| Description | "Fully Consumed - covered under existing EA, no additional charge" |

## EA SKU Family (E3N-*)

EA 3.0 license SKUs use the `E3N-` prefix. Common ones encountered on TF reports:

| SKU | Product |
|---|---|
| E3N-MR-E | Meraki MR Essentials EA 3.0 |
| E3N-MR-A | Meraki MR Advanced EA 3.0 |
| E3N-MS-100-S-E | Meraki MS100 Small Essentials EA 3.0 |
| E3N-MS-100-M-E | Meraki MS100 Medium Essentials EA 3.0 |
| E3N-MS-100-L-E | Meraki MS100 Large Essentials EA 3.0 |
| E3N-MS-200-S-E | Meraki MS200 Small Essentials EA 3.0 |
| E3N-MS-200-M-E | Meraki MS200 Medium Essentials EA 3.0 |
| E3N-MS-200-L-E | Meraki MS200 Large Essentials EA 3.0 |
| E3N-MX-S-E | Meraki MX Small Essentials EA 3.0 |
| E3N-MX-M-E | Meraki MX Medium Essentials EA 3.0 |
| E3N-MX-L-E | Meraki MX Large Essentials EA 3.0 |
| E3N-MX-XL-E | Meraki MX X-Large Essentials EA 3.0 |

These are NOT in the prices.json hot cache — always look them up live via `ZohoCRM_searchRecords module=Products criteria=Product_Code:equals:E3N-*`.

## Workflow Step-by-Step

```
STEP 1 - PARSE TF REPORT
  If the file is in /mnt/user-data/uploads or already attached, read it directly.
  If only a Drive URL was provided, use Google Drive:read_file_content with the file ID.
  Extract:
    - Customer name
    - Subscription ID (SR######)
    - EA ID (EA####)
    - EA Start/End dates, remaining months
    - Per-SKU lines with status (Fully Consumed / Overconsumed / Underconsumed)
    - For each line: SKU, qty (purchased + consumed/overconsumed/balance), Cisco net cost or credit

STEP 2 - LOOKUP ACCOUNT IN ZOHO
  ZohoCRM_searchRecords module=Accounts criteria=(Account_Name:starts_with:{customer})
  Capture: id, billing/shipping address, Owner, Delinquency_Score
  No delinquency gate — Net_Terms always defaults to Cash for EA TF quotes (per Chris policy).

STEP 3 - LOOKUP / CREATE DEAL
  Search for an existing open deal with this Account + matching subject. If none, create:
    Deal_Name: "{Account} - True Forward {Year} ({SubID})"
    Stage: Qualification
    Amount: estimated grand total (will update after quote builds)
    Closing_Date: today + 30 days
    Lead_Source: Stratus Referal (default for TFs)
    Meraki_ISR: Stratus Sales (id 2570562000027286729)
    Owner: Chris Graves (id 2570562000141711002)

STEP 4 - LOOKUP CONTACTS
  ZohoCRM_searchRecords module=Contacts criteria=(Account_Name:equals:{account_id})
  If 1: use it. If >1: prompt Chris.

STEP 5 - LOOKUP ALL DISTINCT SKU PRODUCT IDs
  Build OR criteria with all unique SKUs from the TF report (charges + credits + fully consumed):
    ((Product_Code:equals:E3N-XXX-1)or(Product_Code:equals:E3N-XXX-2)or...)
  Capture: id, Unit_Price for each.
  If any SKU not found: STOP, prompt Chris (likely a new variant — needs Zoho product creation).

STEP 6 - BUILD VALIDATION TABLE
  Show 3 line groups (charges / credits / unchanged) with quantities and per-unit prices.
  Show: Pre-tax, expected tax (state %), Grand Total, Net_Terms = Cash.
  Confirm Lead_Source, Meraki_ISR, Contact selection.
  Ask Chris: "Proceed?"

STEP 7 - CREATE DEAL (if not existing)
  ZohoCRM_createRecords module=Deals body=...
  Capture deal_id.

STEP 8 - CREATE QUOTE
  ZohoCRM_createRecords module=Quotes body={
    "data": [{
      "Deal_Name": {"id": deal_id},
      "Account_Name": {"id": account_id},
      "Contact_Name": {"id": contact_id},
      "Subject": "{Account} - True Forward {Year} ({SubID})",
      "Owner": {"id": owner_id},
      "Cisco_Billing_Term": "Prepaid Term",
      "Net_Terms": "Cash",                     // ALWAYS Cash for EA TFs
      "Valid_Till": "{today + 30}",
      "Billing_Street/City/State/Code/Country": from account,
      "Shipping_Country": "US",
      "Description": "{summary}",
      "Quoted_Items": [
        ...charge_lines (positive list_price, no discount),
        ...credit_lines (positive list_price, oversized discount),
        ...unchanged_lines (default unit price, 100% discount)
      ]
    }]
  }
  Capture quote_id.

STEP 9 - VERIFY
  ZohoCRM_getRecord module=Quotes recordID={quote_id}
  Check: Sub_Total within $0.10 of expected, line count matches plan, Net_Terms = Cash.
  If Net_Terms reverted to Net 15: ZohoCRM_updateRecord to force Cash.

STEP 10 - UPDATE DEAL AMOUNT
  ZohoCRM_updateRecord module=Deals recordID={deal_id}
  body={"data":[{"Amount": {grand_total}}]}

STEP 11 - ADD NOTES + TASK
  Deal Note: Source = Cisco TF report, breakdown of charges/credits, math summary.
  Quote Note: Same content, attached to quote.
  Task: "Send TF quote to {contact}", due +5 business days, Priority High.

STEP 12 - REPORT
  Print summary with Deal URL, Quote URL, Task URL, totals, Stratus margin.
```

## Key Defaults (no need to ask Chris)

| Field | Default | Reason |
|---|---|---|
| Lead_Source | Stratus Referal | TFs are recurring billing on existing EA, not net-new ISR-sourced |
| Meraki_ISR | Stratus Sales (2570562000027286729) | Same reason as above |
| Net_Terms | **Cash** | Always Cash for EA TF quotes per Chris policy (skips delinquency check entirely) |
| Cisco_Billing_Term | Prepaid Term | Standard for EA |
| Valid_Till | today + 30 days | Standard quote validity |
| Closing_Date | today + 30 days | Standard for new deals |
| Stage | Qualification | Default for new deals; Chris moves through pipeline manually |

## Auto-Tax Behavior

Zoho's auto-tax workflow fires on save and adds the billing state's sales tax rate to the Sub_Total. This is expected for taxable accounts (Tax_Type = Regular). The Sub_Total field on the quote record represents pre-tax line totals, while Grand_Total includes tax. Verifier should compare Sub_Total, not Grand_Total.

## Common Pitfalls

1. **Don't ignore credits.** The customer-facing total must include the value shift, otherwise you're charging for the gross overconsumption rather than the net TF cost.

2. **Don't allocate the net cost across charge lines.** Apply markup per line, not on the rollup. Allocating distorts the per-SKU pricing and the customer can't reconcile against Cisco's report.

3. **Don't use negative List_Price for credits.** Zoho accepts it but the printed PDF formatting is bad. Use positive List + oversized Discount.

4. **Don't skip the unchanged inventory.** Showing only the changed lines makes the quote feel incomplete. Customers expect to see their full subscription with $0 lines for the unchanged stuff.

5. **Don't use the prices.json hot cache for E3N-* SKUs.** They're not in it. Always do a live Zoho Products search.

6. **Don't conflate "sub mod discount %" with the TF margin.** Sub mods use 30% (Meraki) or 45% (EA) discount on raw list price. TFs use 20% true margin on already-discounted Cisco net cost. Different math entirely.
