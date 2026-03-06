---
name: subscription-modification-v2-6
description: "optimized cisco subscription quote processor. embedded sku cache eliminates lookups, enforced parent sku with term months, correct Description field, pre-validation of product status. meraki 30%, ea 45%."
---

# Subscription Modification Skill v2.6

Optimized workflow for processing Cisco subscription modifications. Creates customer quote first, then OP quote with consolidated quantities.

See CHANGELOG.md for what changed in each version.


## REQUIRED FIELDS (MUST ENFORCE)

### Deal Required Fields
| Field | Required | Default for Sub Mods | Notes |
|-------|----------|---------------------|-------|
| Deal_Name | YES | {Account} - {SubID} Add-On (CCW {DealID}) | Auto-generate from file |
| Account_Name | YES | - | Lookup from file customer name |
| Lead_Source | YES | **"Stratus Referal"** | Always default for sub mods |
| Stage | YES | "Proposal/Negotiation" | Default for sub mods |
| Closing_Date | YES | Deal Expiration from file | Extract from CCW quote |
| Meraki_ISR | YES | **"Stratus Sales"** | ID: 2570562000027286729 |
| CCW_Deal_Number | YES | - | Extract from file |
| Cisco_Billing_Term | YES | "Prepay" | Extract from file or default |

### Quote Required Fields
| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| Subject | YES | {Account} - {SubID} Add-On (CCW {DealID}) | Match deal name |
| Deal_Name | YES | - | Link to created deal |
| Account_Name | YES | - | From deal |
| Contact_Name | YES | - | Lookup from Account (auto-assign if only one) |
| Valid_Till | YES | Deal Expiration from file | Match deal closing date |
| Cisco_Billing_Term | YES | "Prepaid Term" | Always set |
| Billing_Street | YES | From Account | Copy from Account |
| Billing_City | YES | From Account | Copy from Account |
| Billing_State | YES | From Account | Copy from Account |
| Billing_Code | YES | From Account | Copy from Account |
| Billing_Country | YES | "US" | Default if not specified |
| Shipping_Street | YES | From Account | Copy from Account |
| Shipping_City | YES | From Account | Copy from Account |
| Shipping_State | YES | From Account | Copy from Account |
| Shipping_Code | YES | From Account | Copy from Account |
| Shipping_Country | YES | "US" | Default if not specified |

### Task Required Fields
| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| Subject | YES | "Follow up - {Account} {SubID} Add-On" | Auto-generate |
| What_Id | YES | {deal_id} | Link to deal |
| $se_module | YES | "Deals" | **CRITICAL - must include** |
| Due_Date | YES | Today + 7 days | Default follow-up |
| Status | YES | "Not Started" | Default |
| Owner | YES | Chris Graves | ID: 2570562000141711002 |

## Pre-Creation Validation (MANDATORY)

### Before Creating Deal
```
PRE-CREATION VALIDATION - DEAL:
| Field | Value | Status |
|-------|-------|--------|
| Deal_Name | VGM Forbin - Sub2106615 Add-On (CCW 82958762) | ✓ |
| Account_Name | VGM Forbin (ID: 2570562000136604115) | ✓ |
| Lead_Source | Stratus Referal | ✓ |
| Stage | Proposal/Negotiation | ✓ |
| Closing_Date | 2026-04-15 | ✓ |
| Meraki_ISR | Stratus Sales (ID: 2570562000027286729) | ✓ |
| CCW_Deal_Number | 82958762 | ✓ |
| Cisco_Billing_Term | Prepay | ✓ |
```

### Before Creating Quote
```
PRE-CREATION VALIDATION - QUOTE:
| Field | Value | Status |
|-------|-------|--------|
| Subject | VGM Forbin - Sub2106615 Add-On (CCW 82958762) | ✓ |
| Deal_Name | (ID: {deal_id}) | ✓ |
| Account_Name | VGM Forbin | ✓ |
| Contact_Name | Nick Gerrans (ID: 2570562000153534111) | ✓ |
| Valid_Till | 2026-04-15 | ✓ |
| Cisco_Billing_Term | Prepaid Term | ✓ |
| Billing Address | PO Box 2817, Waterloo, IA 50704, US | ✓ |
| Shipping Address | 1111 W San Marnan Dr, Waterloo, IA 50701, US | ✓ |
| Parent SKU | MERAKI-SUB (ID: 2570562000214328410) | ✓ |
| Products Validated | 7 SKUs - all active | ✓ |
```

## Quick Reference IDs

```
Chris Graves User ID: 2570562000141711002
Stratus Sales ID: 2570562000027286729
Org ID: org647122552

DEFAULT FOR ALL SUBSCRIPTION MODIFICATIONS:
- Lead_Source: "Stratus Referal"
- Meraki_ISR: {"id": "2570562000027286729"} (Stratus Sales)
- Stage: "Proposal/Negotiation"
- Cisco_Billing_Term (Deal): "Prepay"
- Cisco_Billing_Term (Quote): "Prepaid Term"
```

## Existing Deal Detection (from v2.5)

### Before Creating Any Records

```python
# Search for existing deal by CCW Deal Number
criteria = "(CCW_Deal_Number:equals:{ccw_deal_id})"
```

**If Deal Found:**
```
Found existing deal: {Deal_Name}
URL: https://crm.zoho.com/crm/org647122552/tab/Deals/{id}

Would you like to:
1. Add quotes to existing deal
2. Create new deal from scratch

Also found {N} existing quote(s):
- {Quote_Subject} - ${Grand_Total}

Would you like to:
A. Modify existing quote with new items/discounts
B. Create new quote(s)
```

**Wait for user confirmation before proceeding.**

## Customer Quote First (from v2.5)

### Why Customer Quote First?
1. Contains only changed items (simpler)
2. No NOCHANGE items to complicate math
3. Straightforward: List_Price × Qty × 0.70
4. Once verified, OP quote target is locked

### Customer Quote Line Items

| Action | Include? | Quantity | List_Price | Discount (30%) |
|--------|----------|----------|------------|----------------|
| NOCHANGE | NO | - | - | - |
| MODIFIED | YES | Net Change Qty | From file (for net change) | List × Qty × 0.30 |
| ADDED | YES | Net Change Qty | From file | List × Qty × 0.30 |

### Pre-Creation Calculation
```python
customer_total = 0
for item in changed_items:  # MODIFIED + ADDED only
    net_qty = item['net_change_qty']
    list_price = item['ext_list_price']  # From file (already for net change qty)
    discount = list_price * 0.30
    net = list_price - discount
    customer_total += net

print(f"Expected Customer Total: ${customer_total:.2f}")
```

## OP Quote with Consolidated Quantities (from v2.5)

### OP Quote = Full Subscription State

For MODIFIED items, show the FULL NEW QUANTITY (not net change), with discount calculated so customer only pays for new licenses.

### MODIFIED Item Calculation

**Example: LIC-MS-100-L-E**
- Existing qty: 1
- New qty: 4
- Net change: +3
- Unit price: $17/month
- Term: 24.42 months
- List price per license: $17 × 24.42 = $415.14
- Total list (4 licenses): $415.14 × 4 = $1,660.56

**Customer pays for 3 new @ 70%:**
- Customer cost: $415.14 × 3 × 0.70 = $871.79

**OP Quote Discount:**
- Discount = Total List - Customer Cost
- Discount = $1,660.56 - $871.79 = $788.77

## Complete OP Quote Math

### For Each Line Item:

**NOCHANGE:**
```
Qty = existing_qty
List_Price = ext_list_price / qty (unit price × term)
Discount = List_Price × Qty (100%)
Net = $0.00
```

**MODIFIED:**
```
Qty = new_qty (full amount)
List_Price = unit_price × term (per license)
Total_List = List_Price × Qty
Customer_Pays = List_Price × net_change_qty × 0.70
Discount = Total_List - Customer_Pays
Net = Customer_Pays
```

**ADDED:**
```
Qty = net_change_qty
List_Price = ext_list_price / qty
Discount = List_Price × Qty × 0.30
Net = List_Price × Qty × 0.70
```

### Verification Gate
```
IF OP_Quote_Grand_Total ≠ Customer_Quote_Grand_Total:
  → STOP
  → Identify which line item has incorrect discount
  → Recalculate and update
  → Re-verify
```

## File Parsing

### Header Section (Rows 1-25)
Extract:
- End Customer name/address
- CCW Deal ID
- Subscription ID
- Quote Name
- Deal Expiration
- Term dates (calculate months remaining)
- Cisco AM email

### Line Items Section (Starting ~Row 64)
Extract columns:
- # (line number)
- Action (NOCHANGE/MODIFIED/NEW/ADDED)
- SKU
- Description
- Unit List Price
- Pricing Term
- New Qty
- Existing Qty
- Net Change Qty
- Ext. List Price

## CCW CSV Generation (ON REQUEST ONLY)

Only generate when user explicitly asks. Format:
```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
```

## Error Recovery

### Pricing Mismatch
```
IF OP_Total ≠ Customer_Total:
  1. List each line item's expected vs actual net
  2. Identify discrepancy
  3. Recalculate discount using formula
  4. Update quote
  5. Re-verify
```

### SKU Not in Catalog
```
IF SKU not in embedded cache AND not in hot-cache AND not in unified catalog:
  1. Search Zoho Products module
  2. Log: "SKU {sku} not in cache, falling back to Zoho search"
  3. If found: Use Zoho ID, FLAG FOR SKILL UPDATE
  4. If not found: Flag for manual review
```

### Existing Deal Found
```
IF deal with matching CCW_Deal_Number exists:
  1. Display deal info and existing quotes
  2. Ask user preference (modify existing vs create new)
  3. Wait for confirmation
  4. Proceed based on user choice
```

### "Can't add inactive product" Error
```
1. Identify which product ID triggered error
2. Check Zoho: Products module → find by ID → verify Product_Active field
3. If inactive: 
   - Option A: Activate product in Zoho
   - Option B: Find alternate active product with same SKU
   - Option C: Skip parent SKU if that's the issue
4. Re-attempt quote creation
```

### SKU Not in Embedded Cache
```
1. Log: "SKU {sku} not in embedded cache"
2. Try external files (hot-cache, catalog)
3. If still not found, search Zoho Products
4. If found in Zoho: FLAG FOR SKILL UPDATE
   - Add SKU + Zoho ID to embedded cache for future quotes
5. If not found anywhere: STOP and request manual SKU verification
```

## Critical Field Names (MUST USE EXACTLY)

```
Quoted_Items array fields:
- Product_Name: {"id": "zoho_product_id"}
- Quantity: integer
- List_Price: decimal
- Discount: decimal (DOLLAR AMOUNT, not percentage)
- Description: string   <-- CORRECT (not "Product_Description")
```

## Embedded SKU Cache (USE FIRST - NO LOOKUPS NEEDED)

```json
{
  "parent_skus": {
    "MERAKI-SUB": "2570562000214328410",
    "CISCO-NETWORK-SUB": "2570562000292110371",
    "SECURE-ACCESS-SUB": "2570562000240080110"
  },
  "meraki_subscription": {
    "LIC-MR-E": "2570562000209856181",
    "LIC-MR-A": "2570562000218306162",
    "LIC-MX-S-E": "2570562000207919032",
    "LIC-MX-S-A": "2570562000214328464",
    "LIC-MX-M-E": "2570562000209974109",
    "LIC-MX-M-A": "2570562000214328433",
    "LIC-MX-L-E": "2570562000218271173",
    "LIC-MX-L-A": "2570562000214328495",
    "LIC-MX-XL-E": "2570562000218306247",
    "LIC-MX-XL-A": "2570562000218306278",
    "LIC-Z-E": "2570562000211962229",
    "LIC-Z-A": "2570562000218306315",
    "LIC-MS-100-S-E": "2570562000215863602",
    "LIC-MS-100-S-A": "2570562000218296781",
    "LIC-MS-100-M-E": "2570562000218271099",
    "LIC-MS-100-M-A": "2570562000218296818",
    "LIC-MS-100-L-E": "2570562000211962001",
    "LIC-MS-100-L-A": "2570562000218271130",
    "LIC-MS-200-M-E": "2570562000215863633",
    "LIC-MS-200-M-A": "2570562000218296861",
    "LIC-MS-200-L-E": "2570562000214343629",
    "LIC-MS-200-L-A": "2570562000218296892",
    "LIC-MS-300-M-E": "2570562000218139487",
    "LIC-MS-300-M-A": "2570562000218296929",
    "LIC-MS-300-L-A": "2570562000218296966",
    "LIC-MS-400-M-E": "2570562000214343660",
    "LIC-MS-400-M-A": "2570562000218306063",
    "LIC-MS-400-L-E": "2570562000218306094",
    "LIC-MS-400-L-A": "2570562000218306125",
    "LIC-MV-E": "2570562000218306377",
    "LIC-MG-E": "2570562000218306346",
    "LIC-MT-E": "2570562000216815413",
    "LIC-SM-E": "2570562000214343691"
  }
}
```

## SKU Lookup Order (ENFORCED)

### Step 1: Check Embedded Cache (MANDATORY FIRST)
```python
# ALWAYS check embedded cache first - covers 90%+ of subscription SKUs
EMBEDDED_CACHE = {
    "LIC-MR-E": "2570562000209856181",
    "LIC-MS-100-L-E": "2570562000211962001",
    # ... (full list above)
}

zoho_id = EMBEDDED_CACHE.get(sku)
if zoho_id:
    print(f"{sku} -> {zoho_id} (embedded cache)")
    # DONE - no further lookups needed
```

### Step 2: Query External Files (ONLY if not in embedded cache)
```bash
# Hot cache
jq -r --arg s "$sku" '.[$s] // empty' /mnt/skills/user/zoho-crm-v14/data/hot-cache.json

# Unified catalog
jq -r --arg s "$sku" '.licenses.subscription.licenses[$s].zoho_id // empty' \
  /mnt/skills/user/unified-product-catalog-v2-0/data/catalog.json
```

### Step 3: Zoho Search (LAST RESORT ONLY)
```
Only if Steps 1-2 return nothing:
- Search Zoho Products module
- Log: "SKU {sku} not in embedded cache or catalog, falling back to Zoho search"
- Flag for potential skill update
```

## Parent SKU Enforcement (MANDATORY)

### Always Include Parent SKU as First Line Item

**Determine Parent SKU:**
- Meraki licenses (LIC-*) → MERAKI-SUB
- EA 3.0 licenses (E3N-*, E3S-*) → CISCO-NETWORK-SUB
- Secure Access (SA-*) → SECURE-ACCESS-SUB

**Parent SKU Line Item Format:**
```json
{
  "Product_Name": {"id": "2570562000214328410"},
  "Quantity": 1,
  "List_Price": 0,
  "Discount": 0,
  "Description": "Meraki Subscription - 24.42 months remaining (Jan 18, 2026 → Jan 30, 2028)"
}
```

**Description Template:**
```
{Subscription Type} - {term_months} months remaining ({start_date} → {end_date})
```

## Pre-Validation Gate (NEW v2.6)

### Before Creating Any Quote

```python
# 1. Verify all product IDs resolve
for item in line_items:
    zoho_id = lookup_sku(item['sku'])
    if not zoho_id:
        STOP - "Cannot find Zoho ID for {sku}"
    
    # 2. Check product is active (prevents "can't add inactive product" error)
    product = get_zoho_product(zoho_id, fields="Product_Active")
    if not product.get('Product_Active', False):
        WARN - "{sku} (ID: {zoho_id}) is INACTIVE in Zoho"
        # Options: activate product, use alternate SKU, or flag for manual review

# 3. Only proceed when ALL products validated
print("PRE-VALIDATION PASSED - All {n} products active and ready")
```

## Complete Workflow (v2.6)

```
1. Parse file (targeted rows only)
2. Extract header data + line items + TERM MONTHS
3. CHECK FOR EXISTING DEAL (by CCW Deal ID)
4. DETERMINE PARENT SKU from license types
5. SKU LOOKUP: Embedded cache → External files → Zoho (last resort)
6. PRE-VALIDATE all product IDs are active
7. Lookup Account in Zoho
8. Lookup Contact (auto-assign if single contact on account)
9. Validate address (all 5 billing + 5 shipping fields required)
10. PRE-CREATION VALIDATION TABLE - DEAL
11. Create Deal with DEFAULTS:
    - Lead_Source: "Stratus Referal"
    - Meraki_ISR: {"id": "2570562000027286729"} (Stratus Sales)
    - Stage: "Proposal/Negotiation"
    - Cisco_Billing_Term: "Prepay"
12. Create Deal Note (CCW details, Cisco AM, line item summary)
13. CALCULATE expected customer total
14. PRE-CREATION VALIDATION TABLE - CUSTOMER QUOTE
15. CREATE CUSTOMER QUOTE (changed items only, with parent SKU)
    - Contact_Name: REQUIRED
    - Cisco_Billing_Term: "Prepaid Term"
    - All address fields: REQUIRED
16. VERIFY customer quote matches calculation
17. CALCULATE OP quote discounts (consolidated quantities)
18. PRE-CREATION VALIDATION TABLE - OP QUOTE
19. CREATE OP QUOTE (all items, with parent SKU showing term)
20. VERIFY OP total = Customer total
21. Create follow-up task ($se_module: "Deals" REQUIRED)
22. Output summary with URLs
```

## Deal Creation Payload (with defaults)

```json
{
  "Deal_Name": "{Account} - {SubID} Add-On (CCW {DealID})",
  "Account_Name": {"id": "{account_id}"},
  "Contact_Name": {"id": "{contact_id}"},
  "Lead_Source": "Stratus Referal",
  "Stage": "Proposal/Negotiation",
  "Closing_Date": "{deal_expiration_from_file}",
  "Amount": "{calculated_customer_total}",
  "CCW_Deal_Number": "{ccw_deal_id}",
  "Cisco_Billing_Term": "Prepay",
  "Meraki_ISR": {"id": "2570562000027286729"},
  "Description": "Subscription modification for {SubID}\n\nChanges:\n{line_item_summary}\n\nTerm: {months} months ({start} → {end})\nCisco AM: {am_name} ({am_email})"
}
```

## Quote Creation Payload (with required fields)

```json
{
  "Subject": "{Account} - {SubID} Add-On (CCW {DealID})",
  "Deal_Name": {"id": "{deal_id}"},
  "Account_Name": {"id": "{account_id}"},
  "Contact_Name": {"id": "{contact_id}"},
  "Valid_Till": "{deal_expiration}",
  "Cisco_Billing_Term": "Prepaid Term",
  "Billing_Street": "{from_account}",
  "Billing_City": "{from_account}",
  "Billing_State": "{from_account}",
  "Billing_Code": "{from_account}",
  "Billing_Country": "US",
  "Shipping_Street": "{from_account}",
  "Shipping_City": "{from_account}",
  "Shipping_State": "{from_account}",
  "Shipping_Code": "{from_account}",
  "Shipping_Country": "US",
  "Quoted_Items": [...]
}
```

## Task Creation Payload (CRITICAL: include $se_module)

```json
{
  "Subject": "Follow up - {Account} {SubID} Add-On",
  "What_Id": {"id": "{deal_id}"},
  "$se_module": "Deals",
  "Due_Date": "{today + 7 days}",
  "Status": "Not Started",
  "Priority": "Normal",
  "Owner": {"id": "2570562000141711002"},
  "Description": "Follow up on {SubID} subscription modification. CCW Deal {ccw_id} expires {expiration}."
}
```

## Quoted_Items Structure (CORRECT FIELD NAMES)

```json
{
  "Quoted_Items": [
    {
      "Product_Name": {"id": "2570562000214328410"},
      "Quantity": 1,
      "List_Price": 0,
      "Discount": 0,
      "Description": "Meraki Subscription - 24.42 months remaining (Jan 18, 2026 → Jan 30, 2028)"
    },
    {
      "Product_Name": {"id": "2570562000209856181"},
      "Quantity": 17,
      "List_Price": 317.45,
      "Discount": 5396.65,
      "Description": "NOCHANGE - 17 licenses (no charge)"
    }
  ]
}
```

**CRITICAL: Field is "Description" not "Product_Description"**

## Customer Quote Structure (v2.6)

### Line Items (MODIFIED + ADDED only, plus Parent SKU)

```json
{
  "Quoted_Items": [
    {
      "Product_Name": {"id": "{PARENT_SKU_ID}"},
      "Quantity": 1,
      "List_Price": 0,
      "Discount": 0,
      "Description": "{Type} Subscription - {months} months remaining ({start} → {end})"
    },
    {
      "Product_Name": {"id": "{modified_sku_id}"},
      "Quantity": 3,
      "List_Price": 415.14,
      "Discount": 373.63,
      "Description": "MODIFIED - +3 added (4 total)"
    },
    {
      "Product_Name": {"id": "{added_sku_id}"},
      "Quantity": 1,
      "List_Price": 268.61,
      "Discount": 80.58,
      "Description": "ADDED - 1 new license"
    }
  ]
}
```

## OP Quote Structure (v2.6)

### Line Items (ALL items, consolidated quantities, plus Parent SKU)

```json
{
  "Quoted_Items": [
    {
      "Product_Name": {"id": "{PARENT_SKU_ID}"},
      "Quantity": 1,
      "List_Price": 0,
      "Discount": 0,
      "Description": "{Type} Subscription - {months} months remaining ({start} → {end})"
    },
    {
      "Product_Name": {"id": "{nochange_sku_id}"},
      "Quantity": 17,
      "List_Price": 317.45,
      "Discount": 5396.65,
      "Description": "NOCHANGE - 17 licenses (no charge)"
    },
    {
      "Product_Name": {"id": "{modified_sku_id}"},
      "Quantity": 4,
      "List_Price": 415.14,
      "Discount": 788.77,
      "Description": "MODIFIED - 4 total (+3 added)"
    },
    {
      "Product_Name": {"id": "{added_sku_id}"},
      "Quantity": 1,
      "List_Price": 268.61,
      "Discount": 80.58,
      "Description": "ADDED - 1 new license"
    }
  ]
}
```

## Dollar-Based Discounting (CRITICAL)

### Zoho Discount Field = DOLLAR AMOUNT

| Goal | Formula | Example |
|------|---------|---------|
| 100% discount (net $0) | `Discount = List_Price × Quantity` | $317.45 × 17 = $5,396.65 |
| 30% discount (Meraki) | `Discount = List_Price × Quantity × 0.30` | $415.14 × 3 × 0.30 = $373.63 |
| 45% discount (EA 3.0) | `Discount = List_Price × Quantity × 0.45` | $500 × 2 × 0.45 = $450 |

### MODIFIED Item OP Quote Discount
```
Total_List = List_Price × New_Qty
Customer_Pays = List_Price × Net_Change_Qty × 0.70
Discount = Total_List - Customer_Pays
```

## Description Notation Format

| Action | Description Template |
|--------|---------------------|
| PARENT | `"{Type} Subscription - {months} months remaining ({start} → {end})"` |
| NOCHANGE | `"NOCHANGE - {qty} licenses (no charge)"` |
| MODIFIED | `"MODIFIED - {new_qty} total (+{net_change} added)"` |
| ADDED | `"ADDED - {qty} new license(s)"` |

## Quick Reference

```
WORKFLOW ORDER (v2.6):
1. Parse file + extract TERM MONTHS
2. CHECK FOR EXISTING DEAL
3. DETERMINE PARENT SKU
4. SKU lookup: Embedded → External → Zoho (log if fallback used)
5. PRE-VALIDATE all products active
6. Lookup Account
7. Lookup Contact (auto-assign if single)
8. Validate address (all 10 fields)
9. PRE-VALIDATION TABLE - DEAL
10. Create Deal (with defaults below)
11. Create Deal Note
12. CALCULATE customer total
13. PRE-VALIDATION TABLE - CUSTOMER QUOTE
14. CREATE CUSTOMER QUOTE (with parent SKU + term)
15. VERIFY customer quote
16. CALCULATE OP discounts
17. PRE-VALIDATION TABLE - OP QUOTE
18. CREATE OP QUOTE (with parent SKU + term)
19. VERIFY OP = Customer total
20. Create task (with $se_module: "Deals")
21. Output summary

SUBSCRIPTION MODIFICATION DEFAULTS (ALWAYS APPLY):
• Lead_Source: "Stratus Referal"
• Meraki_ISR: {"id": "2570562000027286729"} (Stratus Sales)
• Stage: "Proposal/Negotiation"
• Cisco_Billing_Term (Deal): "Prepay"
• Cisco_Billing_Term (Quote): "Prepaid Term"

KEY IDS:
• Chris Graves: 2570562000141711002
• Stratus Sales: 2570562000027286729
• Org ID: org647122552

SKU LOOKUP ORDER (ENFORCED):
1. Embedded cache (in this skill) ← CHECK FIRST, NO API CALLS
2. Hot cache JSON file
3. Unified catalog JSON file  
4. Zoho Products search ← LAST RESORT, LOG IF USED

CORRECT FIELD NAMES:
✓ Description (for line item descriptions)
✗ Product_Description (WRONG - will save as null)

PARENT SKU (ALWAYS INCLUDE):
• MERAKI-SUB: 2570562000214328410
• CISCO-NETWORK-SUB: 2570562000292110371
• SECURE-ACCESS-SUB: 2570562000240080110

PARENT DESCRIPTION FORMAT:
"{Type} Subscription - {months} months remaining ({start} → {end})"

DISCOUNT FORMULAS (DOLLAR AMOUNTS):
• 100% off: Discount = List_Price × Quantity
• 30% off: Discount = List_Price × Quantity × 0.30
• 45% off: Discount = List_Price × Quantity × 0.45

DESCRIPTION NOTATION:
• PARENT: "{Type} Subscription - {months} months remaining ({start} → {end})"
• NOCHANGE: "NOCHANGE - {qty} licenses (no charge)"
• MODIFIED: "MODIFIED - {new_qty} total (+{net_change} added)"
• ADDED: "ADDED - {qty} new license(s)"

DEAL REQUIRED FIELDS:
✓ Deal_Name (auto-generate)
✓ Account_Name
✓ Contact_Name
✓ Lead_Source = "Stratus Referal"
✓ Stage = "Proposal/Negotiation"
✓ Closing_Date (from file)
✓ Meraki_ISR = Stratus Sales
✓ CCW_Deal_Number
✓ Cisco_Billing_Term = "Prepay"

QUOTE REQUIRED FIELDS:
✓ Subject
✓ Deal_Name
✓ Account_Name
✓ Contact_Name (auto-assign if single contact)
✓ Valid_Till
✓ Cisco_Billing_Term = "Prepaid Term"
✓ Billing_Street, City, State, Code, Country
✓ Shipping_Street, City, State, Code, Country

TASK REQUIRED FIELDS:
✓ Subject
✓ What_Id (deal)
✓ $se_module = "Deals" ← CRITICAL
✓ Due_Date
✓ Status
✓ Owner

PRE-VALIDATION (BEFORE EACH RECORD CREATION):
1. Display validation table with all fields
2. All SKUs resolved to Zoho IDs
3. All products are active (Product_Active: true)
4. Parent SKU determined and ID verified
5. Term months extracted from file
6. Contact assigned

ALWAYS DO:
✓ Check embedded cache FIRST for SKU lookups
✓ Include parent SKU with term months in description
✓ Use "Description" field (not "Product_Description")
✓ Pre-validate product active status
✓ Log when falling back to Zoho search
✓ Flag new SKUs for skill update
✓ Set Lead_Source = "Stratus Referal"
✓ Set Meraki_ISR = Stratus Sales
✓ Include $se_module: "Deals" on task creation
✓ Display pre-creation validation table
✓ Lookup Contact and auto-assign if single

NEVER DO:
✗ Skip embedded cache and go straight to Zoho search
✗ Omit parent SKU from quotes
✗ Use "Product_Description" field
✗ Create quote without pre-validating products
✗ Silently fail on SKU lookup - always log
✗ Use percentage values in Discount field
✗ Leave Lead_Source blank
✗ Leave Meraki_ISR blank
✗ Leave Contact_Name blank on quotes
✗ Leave Cisco_Billing_Term blank
✗ Omit $se_module from task creation
✗ Skip pre-creation validation tables
```


---

See CHANGELOG.md for version history.
