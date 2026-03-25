# Subscription Quote Workflow

## When to Use

- User says "subscription quote" or "convert to subscription"
- User requests subscription licenses (LIC-MR-E, LIC-MS-xxx-E, etc.)
- User requests Secure Access (SA-SIA-*, SA-SPA-*, SA-DNS-*)
- Subscription modification from Cisco file

## Subscription vs Co-Term Detection

**Subscription License Patterns:**
- `LIC-MR-E`, `LIC-MR-A` (MR subscription)
- `LIC-MX-S-E/A`, `LIC-MX-M-E/A`, `LIC-MX-L-E/A`, `LIC-MX-XL-E/A` (MX subscription)
- `LIC-MS-100-*`, `LIC-MS-200-*`, `LIC-MS-300-*`, `LIC-MS-400-*` (MS subscription)
- `LIC-MV-E`, `LIC-MT-E`, `LIC-MG-E`, `LIC-Z-E/A` (Other subscription)
- `LIC-CW-E`, `LIC-CW-A` (CW subscription)
- `SA-SIA-*`, `SA-SPA-*`, `SA-DNS-*` (Secure Access subscription)
- `UMB-*` (Umbrella subscription)
- `ETD-*` (Email Threat Defense subscription)

**Co-Term License Patterns:**
- `LIC-ENT-xYR` (MR co-term)
- `LIC-MS130-xx-xY` (MS130 co-term)
- `LIC-MXxx-SEC-xYR` (MX co-term)
- Any SKU ending in `-1YR`, `-3YR`, `-5YR`, `-7YR`, `-10YR`

## Parent SKU Requirements

Subscription quotes MUST include parent SKU (listed FIRST):

| Parent SKU | Zoho Product ID | Use Case | Price |
|------------|-----------------|----------|-------|
| CISCO-NETWORK-SUB | 2570562000292110371 | Meraki network subscriptions | $0 |
| SECURE-ACCESS-SUB | 2570562000240080110 | Secure Access (SA-*) | $0 |
| UMB-SEC-SUB | 2570562000024580783 | Umbrella subscriptions | $0 |
| ETD-SEC-SUB | 2570562000186369660 | Email Threat Defense | $0 |

## Auto-Add Parent SKU Logic

| Detected License Pattern | Auto-Add Parent SKU |
|-------------------------|---------------------|
| LIC-MR-*, LIC-MX-*, LIC-MS-*, LIC-CW-*, LIC-MV-E, LIC-MT-E, LIC-MG-E, LIC-Z-* | CISCO-NETWORK-SUB |
| SA-SIA-*, SA-SPA-*, SA-DNS-* | SECURE-ACCESS-SUB |
| UMB-* | UMB-SEC-SUB |
| ETD-* | ETD-SEC-SUB |

## Size Class Mapping

**MR Access Points:** All use `LIC-MR-E` or `LIC-MR-A`

**MX Security Appliances:**
| Hardware | Size | License |
|----------|------|---------|
| MX67, MX68, Z-series | Small | LIC-MX-S-E |
| MX75, MX85, MX95 | Medium | LIC-MX-M-E |
| MX105, MX250 | Large | LIC-MX-L-E |
| MX450 | X-Large | LIC-MX-XL-E |

**MS Switches:**
| Hardware | Size | License |
|----------|------|---------|
| MS120-8, MS130-8, MS130-CMPT | Small (100-S) | LIC-MS-100-S-E |
| MS125-24, MS130-24 | Medium (100-M) | LIC-MS-100-M-E |
| MS125-48, MS130-48 | Large (100-L) | LIC-MS-100-L-E |
| MS150-24 | Medium (200-M) | LIC-MS-200-M-E |
| MS150-48 | Large (200-L) | LIC-MS-200-L-E |
| C9300-24 | Medium (300-M) | LIC-MS-300-M-E |
| C9300-48 | Large (300-L) | LIC-MS-300-L-E |

**Default to Essentials (E) unless user specifies Advantage (A).**

## CCW CSV Generation (CORRECT FORMAT)

When subscription licenses detected, auto-generate CCW import CSV.

### CSV Column Headers (REQUIRED - 8 columns)
```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
```

### Default Subscription Terms
| Field | Default Value |
|-------|---------------|
| Initial Term(Months) | 36 |
| Auto Renew Term(Months) | 12 |
| Billing Model | Prepaid Term |
| Requested Start Date | Current date (YYYY-MM-DD) |

### CSV Generation Rules
1. **Parent SKU FIRST** - Always list parent SKU as first line (qty 1)
2. **Co-term items** - Leave term fields blank (columns 4-7 empty)
3. **Subscription items** - Include all term fields
4. **Filename format** - `CCW_Import_{Quote_Number}_{Account_Name}.csv`

### Example: Meraki Subscription CSV
```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
CISCO-NETWORK-SUB,1,,36,12,Prepaid Term,2026-01-13,
LIC-MR-E,36,,36,12,Prepaid Term,2026-01-13,
LIC-MS-100-M-E,15,,36,12,Prepaid Term,2026-01-13,
LIC-MS-100-S-E,6,,36,12,Prepaid Term,2026-01-13,
LIC-MX-XL-E,1,,36,12,Prepaid Term,2026-01-13,
LIC-MS-300-M-A,2,,36,12,Prepaid Term,2026-01-13,
```

### Example: Secure Access CSV
```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
SECURE-ACCESS-SUB,1,,36,12,Prepaid Term,2026-01-13,
SA-SIA-ESS-K9,100,,36,12,Prepaid Term,2026-01-13,
```

### Example: Mixed Co-Term + Subscription
```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
LIC-ENT-3YR,36,,,,,,
LIC-MX250-SEC-3YR,1,,,,,,
LIC-MS120-8-3YR,4,,,,,,
CISCO-NETWORK-SUB,1,,36,12,Prepaid Term,2026-01-13,
LIC-MR-E,36,,36,12,Prepaid Term,2026-01-13,
LIC-MS-100-M-E,15,,36,12,Prepaid Term,2026-01-13,
```

## Secure Access Product Reference

| SKU | Zoho Product ID | Description | Unit Price |
|-----|-----------------|-------------|------------|
| SA-SIA-ESS-K9 | 2570562000241504854 | Secure Internet Access Essentials | $118.80/user/yr |
| SA-SIA-ADV-K9 | 2570562000277901036 | Secure Internet Access Advantage | $155.02/user/yr |
| SA-SPA-ESS-K9 | 2570562000240080179 | Secure Private Access Essentials | $123.86/user/yr |
| SA-SPA-ADV-K9 | 2570562000342428559 | Secure Private Access Advantage | $329.69/user/yr |
| SA-DNS-ESS-K9 | 2570562000342404656 | DNS Defense Essentials | $54/user/yr |
| SA-DNS-ADV-K9 | 2570562000342449402 | DNS Defense Advantage | $81/user/yr |
| SVS-SECA-SUP-E | 2570562000240080133 | Enhanced Support | % of product |

## Subscription Modification (Two Quotes Required)

When processing Cisco subscription modification files:

### OP Quote (Order Processing)
- Contains ALL line items
- NOCHANGE items discounted to $0 (use `Qty × List_Price` as discount)
- ADDED items at full price
- Subject: "{Account} - OP Quote"

### Customer Quote
- Contains ONLY added items
- No NOCHANGE items
- Subject: "{Account} - Customer Quote"

**NOCHANGE Item Handling:**
```json
{
  "id": "{line_item_id}",
  "Discount": "{Qty × List_Price}",
  "Description": "NOCHANGE - {SKU}"
}
```

## Co-Term to Subscription Conversion

### Step 1: Identify Current Licenses
Map co-term to subscription equivalent using size class rules above.

### Step 2: Apply Default Discounts
- Meraki subscriptions: 30% default
- EA (Advantage): 45% default

### Step 3: Create Both Quotes
If subscription modification, create both OP and Customer quotes.

## Example Conversion

**Co-Term:**
- 5x LIC-MS130-48-3Y (MS130-48 switches)
- 10x LIC-ENT-3YR (MR access points)

**Subscription Equivalent:**
- 1x CISCO-NETWORK-SUB ($0)
- 5x LIC-MS-100-L-E (48-port = Large = 100-L)
- 10x LIC-MR-E

## CSV Generation Workflow

```
1. DETECT subscription licenses in quote
2. IDENTIFY correct parent SKU (or auto-add if missing)
3. SORT items: Parent SKU first, then co-term, then subscriptions
4. GENERATE CSV with CORRECT 8-column format
5. SAVE as CCW_Import_{Quote_Number}_{Account_Name}.csv
6. PRESENT file for download alongside quote confirmation
```

## Quick Reference

```
CORRECT CSV HEADER (8 columns):
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name

WRONG CSV HEADER (DO NOT USE):
SKU,Quantity,Term,Billing

PARENT SKU MAPPING:
- CISCO-NETWORK-SUB → Meraki (LIC-MR-*, LIC-MX-*, LIC-MS-*, etc.)
- SECURE-ACCESS-SUB → Secure Access (SA-SIA-*, SA-SPA-*, SA-DNS-*)
- UMB-SEC-SUB → Umbrella (UMB-*)
- ETD-SEC-SUB → Email Threat Defense (ETD-*)

DEFAULT TERMS:
- Initial: 36 months
- Auto Renew: 12 months
- Billing: Prepaid Term
- Start Date: Today (YYYY-MM-DD)
```
