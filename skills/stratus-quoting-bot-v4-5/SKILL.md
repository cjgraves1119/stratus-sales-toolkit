---
name: stratus-quoting-bot-v4-5
description: "cisco/meraki quoting bot with feb 18 2026 pricing. 18 sku price updates (c9200l, cw9172h). 1222 skus."
---

# Stratus Quoting Bot v4.5

## Purpose
Generate validated URL quotes with optional price estimates for Stratus Information Systems. Also calculates co-term expiration dates using the weighted dollar-value method.

## What's New in v4.5
- **UPDATED PRICING**: Feb 18, 2026 price book
- **18 SKU PRICE UPDATES**: C9200L family (14 SKUs) and CW9172H-RTG, CW9172I-RTG, CW9178I-CFG-RF, CW9178I-RTG-RF
- **56 DUPLICATE BASE SKUs RE-CLEANED**: New source file reintroduced non-suffixed base SKUs; removed again per v4.2 standards
- **1222 SKUs**: Same count as v4.4 after dedup
- All v4.4 features retained

## What's New in v4.3
- **UPDATED PRICING**: Feb 2, 2026 price book with new promotion pricing
- **DUAL DISPLAY MODE**: Quote/URL mode (no pricing) vs Cost mode (full pricing)
  - Asking for a "quote" or "URL" → SKUs + quantities + term options + order links only (NO per-SKU pricing)
  - Asking for "price", "cost", "how much" → Full pricing breakdown with per-SKU costs, discounts, totals
- **1222 SKUs**: Updated from 1242 after removing 56 duplicate base SKUs
- **ECOMM PRICING**: Direct lookup from "price" field (already calculated in source pricing sheet)
- All v4.2 features retained

## What's New in v4.2
- **CLEANED PRICE CACHE**: Removed 57 duplicate base SKUs (non-suffixed versions where -HW version exists)
- **CORRECT PRICING**: MS130, MG, MT, MV, MX families now only have -HW suffixed SKUs with correct list prices
- **1242 SKUs**: Down from 1299 after removing duplicates
- All v4.1 features retained

## What's New in v4.1
- **PRE-VALIDATION CATALOG**: valid_skus.json checks product existence before suffix rules (fail-fast validation)
- **MULTI-TERM DEFAULT**: Auto-generates 1Y/3Y/5Y options when license term not specified
- **EOL REFRESH SCENARIOS**: Automatic upgrade comparison when EOL hardware detected on new purchase
- **QUOTE REVISIONS**: Update quantities/terms without full restart
- **DASHBOARD OCR**: Extract inventory from license page screenshots
- **SMART FALLBACK**: Auto web search for missing prices instead of hard stop
- **QUANTITY CHECKS**: Informational warning on unusual quantities (>100 single item)
- **END-OF-QUOTE MENU**: Seamless workflow transitions to Zoho, lead times, co-term

## Trigger Phrases

**Quote/URL Mode (NO pricing displayed):**
- "quote for...", "quote me...", "build a quote for..."
- "URL for...", "order link for..."
- Any request with SKUs and quantities WITHOUT price/cost language
- Output: Validated SKUs + quantities + 1Y/3Y/5Y term options + order links

**Cost/Price Mode (FULL pricing displayed):**
- "price on...", "how much for...", "cost of...", "what does X cost"
- "price of [SKU]", "how much is [SKU]"
- Any request explicitly asking for pricing, costs, or dollar amounts
- Output: Full breakdown with per-SKU prices, discounts, totals, savings

**Multi-Term Mode (auto when term not specified):**
- "quote 5 MR44" (no term = show 1Y/3Y/5Y options)
- "price MS130-24P" (no term = show all options with pricing)

**Co-Term Mode:**
- "calculate co-term", "co-term expiration"
- "what will my new expiration be"
- License page screenshot upload

**Quick Price Check:**
- "price of [SKU]", "how much is [SKU]"
- For simple lookups, skip workflow and use direct lookup

**Quote Revision:**
- "change quantity to X", "update to 5-year", "add 2 more"

***

## ⚠ COMMON INVALID SKUs (Check FIRST!)

| User Says | Issue | Correct SKU |
|-----------|-------|-------------|
| MS130-13X | Doesn't exist | MS130-12X |
| MS130-24FP | FP variant not available | MS130-24P or MS130-24X |
| MS130-48FP | FP variant not available | MS130-48P or MS130-48X |
| MS150-48P | Must specify variant | MS150-48LP-4G, MS150-48FP-4G, etc. |
| MS150-24P | Must specify variant | MS150-24P-4G or MS150-24P-4X |
| MS210-48P | EOL - specify replacement | MS130-48P (upgrade) |
| MR55 | Never existed | MR57 |
| MT13 | Never existed | MT10, MT11, or MT14 |
| MS140-* | Family doesn't exist | MS130 or MS150 |
| CW9162 | Incomplete - need antenna | CW9162I |
| CW9163 | Incomplete - need antenna | CW9163E |
| CW9172 | Incomplete - need variant | CW9172I or CW9172H |
| CW9176 | Incomplete - need variant | CW9176I or CW9176D1 |

**Validation rule:** Check `valid_skus.json` and this list BEFORE applying suffix rules.

***

## QUICK PRICE LOOKUP (FAST PATH)

For simple "price of X" questions, skip the full workflow:

```python
import json
with open('/mnt/skills/user/stratus-quoting-bot-v4-5/prices.json') as f:
    prices = json.load(f)['prices']
print(prices.get('MR44-HW'), prices.get('LIC-ENT-5YR'))
```

**Common SKU patterns:**
- Hardware: Add -HW suffix (MR44 → MR44-HW, MX68 → MX68-HW)
- CW Wi-Fi 6E: Add -MR suffix (CW9166I → CW9166I-MR)
- CW Wi-Fi 7: Add -RTG suffix (CW9172I → CW9172I-RTG)
- MS150/C9xxx: No suffix (MS150-24P-4G stays as-is)
- AP licenses: LIC-ENT-{1YR,3YR,5YR}
- MX licenses: LIC-MX{model}-SEC-{1YR,3YR,5YR}
- MS130 licenses: LIC-MS130-{24,48}-{1Y,3Y,5Y} or LIC-MS130-CMPT-{1Y,3Y,5Y} for 8/12-port

***

## DECISION TREE

```
Customer Request
│
├─► Simple Price Check? ──► Direct lookup → Return price immediately (COST MODE)
│
├─► Quote/URL Request (no price language)?
│   │
│   ├─► Step 2a: Pre-validate SKU (valid_skus.json)
│   │   ├─ INVALID → Stop, suggest alternatives
│   │   └─ VALID → Continue
│   │
│   ├─► Step 2b: EOL Check
│   │   ├─ EOL + NEW → Multi-option (renew vs upgrade)
│   │   └─ Not EOL or RENEWAL → Continue
│   │
│   ├─► Step 2c-2e: Suffix → License → Price lookup
│   │
│   └─► Generate Quote (QUOTE MODE - no pricing)
│       ├─ Term specified → Single quote (SKUs + URL only)
│       └─ Term NOT specified → Multi-term (1Y/3Y/5Y with URLs only)
│
├─► Cost/Price Request (explicit price language)?
│   │
│   ├─► Same validation steps 2a-2e
│   │
│   └─► Generate Quote (COST MODE - full pricing)
│       ├─ Term specified → Single quote with full pricing
│       └─ Term NOT specified → Multi-term with full pricing
│
├─► License Page Screenshot? ──► OCR extract → Confirm → Quote or Co-Term
│
├─► Co-Term Calculation? ──► Gather inventory → Calculate new expiration
│
└─► Quote Revision? ──► Apply changes to previous quote → Show delta
```

***

## QUOTE GENERATION WORKFLOW

### Step 1: Parse the Request
Extract:
- Product names/SKUs
- Quantities
- License term (if specified)
- **NEW:** If term NOT specified, flag for multi-term output

### Step 2a: Product Existence Check (PRE-VALIDATION)

**Load valid_skus.json from skill folder:**
```python
import json
with open('/mnt/skills/user/stratus-quoting-bot-v4-5/valid_skus.json') as f:
    catalog = json.load(f)
```

**Check product exists BEFORE any suffix application:**

1. Parse SKU into family + variant (e.g., "MS130-12X" → family="MS130", variant="12X")
2. Check if family exists in catalog
3. Check if variant exists in catalog[family]

**If invalid:**
```
⚠ INVALID SKU: MS130-13X

"13X" is not a valid MS130 variant.
Available MS130 variants: 8, 8P, 8X, 12X, 24, 24P, 24X, 48, 48P, 48X

Did you mean: MS130-12X?
```

**If incomplete (family exists but variant missing):**

**Incomplete SKUs - Ask for Variant:**
| Pattern | Ask |
|---------|-----|
| MS150-24 | "Which variant? T-4G, T-4X, P-4G, P-4X, or MP-4X?" |
| MS150-48 | "Which variant? T-4G, LP-4G, LP-4X, FP-4G, FP-4X, or MP-4X?" |
| C9200L-24P | "Which uplink? -4G-M (1G) or -4X-M (10G)?" |
| C9200L-48P | "Which uplink? -4G-M (1G) or -4X-M (10G)?" |
| MA-SFP-10GB | "Which optic? SR, LR, or LRM?" |
| MA-SFP-1GB | "Which optic? SX, LX10, or TX?" |
| CW9172 | "Which variant? H (hospitality) or I (internal)?" |
| CW9176 | "Which variant? D1 (directional) or I (internal)?" |

```
⚠ INCOMPLETE SKU: MS150-24

MS150-24 requires a variant suffix.
Available: 24T-4G, 24T-4X, 24P-4G, 24P-4X, 24MP-4X

Which variant do you need?
```

**Display validation checklist:**
```
✓ Product exists: MS130-12X (found in valid_skus.json)
✓ Not EOL
✓ Suffix applied: MS130-12X-HW
✓ License paired: LIC-MS130-CMPT-3Y
✓ Price cache verified
```

### Step 2b: EOL Status Check

Check `_EOL_PRODUCTS` in valid_skus.json.

**EOL Products and Replacements:**
| EOL Product | License SKU (Still Valid) | Upgrade If New |
|-------------|---------------------------|----------------|
| MX60/60W | LIC-MX60-SEC-{term} | MX67, MX67W |
| MX64/64W | LIC-MX64-SEC-{term} | MX67, MX67W |
| MX65/65W | LIC-MX65-SEC-{term} | MX68, MX68W |
| MX80 | LIC-MX80-SEC-{term} | MX85 |
| MX84 | LIC-MX84-SEC-{term} | MX85 |
| MX100 | LIC-MX100-SEC-{term} | MX105 |
| MG21/21E | LIC-MG21-ENT-{term} | MG41, MG41E |
| Z1, Z3, Z3C | LIC-Z{model}-SEC-{term} | Z4, Z4C |
| MR33 | LIC-ENT-{term} | MR36 |
| MR42/42E | LIC-ENT-{term} | MR44, MR46E |
| MR52, MR53, MR53E, MR56 | LIC-ENT-{term} | MR57 |
| MR74 | LIC-ENT-{term} | MR76 |
| MR84 | LIC-ENT-{term} | MR86 |
| MS120, MS125, MS210, MS220, MS225 | LIC-MS{model}-{port}-{term} | MS130 |
| MS250, MS320 | LIC-MS{model}-{port}-{term} | MS150 |
| MS350, MS410, MS420, MS425 | LIC-MS{model}-{port}-{term} | MS390 |

**If EOL and NEW purchase → Trigger multi-option:**
```
⚠ MR42 is End-of-Life

**Option A: Renew Existing (licenses only)**
• 10 × LIC-ENT-3YR - $263.00 each (42% off)
**Total: $2,630**

**Option B: Refresh to MR44 (Recommended)**
• 10 × MR44-HW - $601.00 each (57% off)
• 10 × LIC-ENT-3YR - $263.00 each (42% off)
**Total: $8,640**

*MR44 includes: Wi-Fi 6, 2×2:2 MIMO, higher throughput*

Which option?
```

*Note: The above example shows COST MODE. In QUOTE MODE, omit pricing and totals.*

**If EOL and RENEWAL (existing hardware):** Allow license-only quote.

### Step 2c: Apply Suffix Rules

**Only apply AFTER Step 2a passes.**

| Product Family | Suffix | Example |
|----------------|--------|---------|
| MR (wireless) | -HW | MR44 → MR44-HW |
| MV (cameras) | -HW | MV63 → MV63-HW |
| MT (sensors) | -HW | MT14 → MT14-HW |
| MG (cellular) | -HW | MG52 → MG52-HW |
| MS130 | -HW | MS130-24P → MS130-24P-HW |
| MS390 | -HW | MS390-48UX → MS390-48UX-HW |
| MX (non-cellular) | -HW | MX68 → MX68-HW |
| MX (cellular) | -HW-NA | MX68CW → MX68CW-HW-NA |
| Z-series | -HW | Z4 → Z4-HW |
| CW Wi-Fi 6E (916x) | -MR | CW9166I → CW9166I-MR |
| CW Wi-Fi 7 (917x) | -RTG | CW9172I → CW9172I-RTG |
| MS150 | (none) | MS150-48LP-4G stays as-is |
| C9xxx-M | (none) | C9300-24P-M stays as-is |
| MA- accessories | (none) | MA-SFP-10GB-SR stays as-is |

### Step 2d: Determine License SKU

**Direct Mappings:**
- All MR and CW APs → LIC-ENT
- All MV cameras → LIC-MV
- All MT sensors → LIC-MT
- MS130 8-port (8, 8P, 8X, 12X) → LIC-MS130-CMPT
- MS130 24-port → LIC-MS130-24
- MS130 48-port → LIC-MS130-48
- MS150 24-port → LIC-MS150-24
- MS150 48-port → LIC-MS150-48

**Pattern-Based:**
- MX: LIC-MX{model}-{tier}-{term} (SEC default)
- MG: LIC-MG{model}-ENT-{term}
- Z: LIC-Z{model}-{tier}-{term} (SEC default)
- C9200L/C9300: LIC-C9{model}-{tier}-{term} (E or A tier)

**License Term Formats:**
- Newer products (MS130, MS150, C9xxx, MG41/52, MT, Z4): -1Y, -3Y, -5Y
- Older products (MS120, MS220, MX, MV, LIC-ENT): -1YR, -3YR, -5YR

### Step 2e: Price Cache Verification

```python
import json
with open('/mnt/skills/user/stratus-quoting-bot-v4-5/prices.json') as f:
    prices = json.load(f)['prices']

hw_price = prices.get('MS130-12X-HW')
lic_price = prices.get('LIC-MS130-CMPT-3Y')
```

**If SKU not found → Smart Fallback:**
```
⚠ LIC-MS130-CMPT-7Y not found in cache (last updated 02-02-2026).

Searching for pricing...
[web_search: "Cisco LIC-MS130-CMPT-7Y MSRP list price"]

Options:
1. Provide list price manually
2. Exclude from quote (note: "pricing TBD")
3. Skip this item
```

### Step 3: Generate Quote(s)

**DISPLAY MODE DETECTION:**

Determine display mode based on user's language:
- **QUOTE MODE** (default): User says "quote", "URL", "order link", or provides SKUs without price language
- **COST MODE**: User says "price", "cost", "how much", "what does X cost", or explicitly asks for pricing

**If term specified → Single quote**
**If term NOT specified → Multi-term output (1Y/3Y/5Y)**

---

**QUOTE MODE - Term NOT specified (no pricing):**

```
No license term specified. Here are your options:

**1-Year Term**
• 1 × MS130-12X-HW
• 1 × LIC-MS130-CMPT-1Y
Order link: https://stratusinfosystems.com/order/?item=MS130-12X-HW,LIC-MS130-CMPT-1Y&qty=1,1

**3-Year Term (Most Common)**
• 1 × MS130-12X-HW
• 1 × LIC-MS130-CMPT-3Y
Order link: https://stratusinfosystems.com/order/?item=MS130-12X-HW,LIC-MS130-CMPT-3Y&qty=1,1

**5-Year Term (Best Value)**
• 1 × MS130-12X-HW
• 1 × LIC-MS130-CMPT-5Y
Order link: https://stratusinfosystems.com/order/?item=MS130-12X-HW,LIC-MS130-CMPT-5Y&qty=1,1
```

**COST MODE - Term NOT specified (full pricing):**

```
No license term specified. Here are your options:

## 1-Year Option
• 1 × MS130-12X-HW - $1,476.00 (33% off)
• 1 × LIC-MS130-CMPT-1Y - $52.00 (33% off)
**Total: $1,528**
Order link: https://stratusinfosystems.com/order/?item=MS130-12X-HW,LIC-MS130-CMPT-1Y&qty=1,1

## 3-Year Option (Most Common)
• 1 × MS130-12X-HW - $1,476.00 (33% off)
• 1 × LIC-MS130-CMPT-3Y - $139.00 (33% off)
**Total: $1,615**
Order link: https://stratusinfosystems.com/order/?item=MS130-12X-HW,LIC-MS130-CMPT-3Y&qty=1,1

## 5-Year Option (Best Value)
• 1 × MS130-12X-HW - $1,476.00 (33% off)
• 1 × LIC-MS130-CMPT-5Y - $233.00 (33% off)
**Total: $1,709**
Order link: https://stratusinfosystems.com/order/?item=MS130-12X-HW,LIC-MS130-CMPT-5Y&qty=1,1
```

### Step 4: Display Quote

**URL Format:**
```
https://stratusinfosystems.com/order/?item={items}&qty={quantities}
```

**Grouping Rule:** Hardware items sharing the same license should be grouped together, with the license quantity combined.

---

**QUOTE MODE Output Format (no pricing):**
```
Order Summary:
• [qty] × [SKU]
• [qty] × [SKU]
...

Order link: [URL]
```

**COST MODE Output Format (full pricing):**
```
Order Summary:
• [qty] × [SKU] - $[price].00 each ([discount]% off)
• [qty] × [SKU] - $[price].00 (single item, no "each")
...

**Estimated Total: $[sum]**
List Price: $[list_total] | You Save: $[savings] ([avg_discount]%)

Order link: [URL]
```

**Formatting Rules (COST MODE only):**
- Single-quantity: omit "each" → `• 1 × MX75-HW - $622.00 (70% off)`
- Multi-quantity: include "each" → `• 5 × MR44-HW - $601.00 each (57% off)`
- Always show .00 for whole dollars
- Include thousands comma: $1,506.00
- If price not found after fallback: `• 1 × [SKU] - Price TBD`

**Formatting Rules (QUOTE MODE):**
- No dollar amounts, no discounts, no totals
- Just quantities, SKU names, and order links
- Multi-term shows 1Y/3Y/5Y as separate sections with their own order links

### Step 5: End-of-Quote Actions

After generating any quote, display:

```
---

**Quote generated.** What's next?

→ **Zoho** - Create Deal/Quote in CRM
→ **Lead times** - Check availability via Commerce BOT
→ **Co-term** - Calculate impact on existing org
→ **Email** - Draft quote email to prospect
→ **Done** - No further action
```

**Behavior:**
- Zoho: Read latest zoho-crm-v* skill and create records
- Lead times: Read latest webex-bots-v* skill and query Commerce BOT
- Co-term: Transition to co-term calculator workflow
- Email: Draft email with quote summary and URL
- Done: End workflow

***

## QUOTE REVISION WORKFLOW

**Trigger phrases:**
- "change quantity to X"
- "update to 5-year licenses"
- "add 2 more"
- "remove the [SKU]"

**Behavior:**
1. Reference previous quote from conversation context
2. Apply changes without re-validation (SKUs already validated)
3. Show delta calculation

**Example:**
```
User: "change quantity to 3"

Updated quote (changed from 1 to 3 units):

• 3 × MS130-12X-HW - $1,476.00 each (33% off)
• 3 × LIC-MS130-CMPT-5Y - $233.00 each (33% off)

**New Total: $5,127**
Previous: $1,709 | Delta: +$3,418 (+200%)

Order link: https://stratusinfosystems.com/order/?item=MS130-12X-HW,LIC-MS130-CMPT-5Y&qty=3,3
```

***

## DASHBOARD SCREENSHOT OCR WORKFLOW

**Trigger:** User uploads Meraki dashboard license information screenshot

**Expected Fields:**
- Organization name
- License model (Co-termination / Per-device)
- License expiration date
- MR Product Edition (Enterprise / Advanced)
- SKU table with Count

**Workflow:**

**Step 1: Extract from image**
```
Detected from screenshot:

**Organization:** NEATON ROME INC
**License Model:** Co-termination
**Expiration:** Jan 3, 2026
**MR Edition:** Enterprise

| SKU | Count |
|-----|-------|
| LIC-ENT-3YR | 31 |
| LIC-MS425-16-3YR | 2 |
| LIC-MS250-48-3YR | 2 |
| LIC-MS225-48FP-3YR | 4 |
| LIC-MS125-24P-3Y | 1 |
| LIC-MS130-48-3Y | 4 |
| LIC-C9300-24E-3Y | 2 |
| LIC-C9300-48E-3Y | 2 |

Confirm this is correct? (Y/n)
```

**Step 2: Offer workflow options**
```
What would you like to do?

1. **Generate renewal quote** - Quote for these exact SKUs
2. **Calculate co-term** - See impact of adding licenses
3. **Check for EOL** - Identify devices needing replacement
4. **Export inventory** - List devices by type
```

**Step 3: Execute chosen path**

**Fallback if OCR unclear:**
```
⚠ Screenshot detected but some fields unclear.
Please confirm or provide:
- Organization name
- Current expiration date
- License tier (Enterprise/Advanced Security)
- Device counts by type
```

***

## QUANTITY REASONABILITY CHECK

**Thresholds (informational warning, does not block):**
- Single item > 100 units
- Total items > 500 across quote
- Unusual ratio (500 APs but 1 switch)

**Warning format:**
```
ℹ Large quantity noted: 847 × MR44-HW

Typical ranges:
- SMB: 5-20 APs
- Enterprise: 50-200 APs  
- Campus: 200-1000 APs

Proceeding with 847 units...
```

***

## CO-TERM CALCULATOR

### Required Inputs
1. Current expiration date
2. Current device inventory with quantities
3. License tier (Enterprise, Advanced Security, SD-WAN Plus)
4. New licenses being added

### Hardware to License Mapping (for 1-Year MSRP Weighting)

| Hardware | License SKU (1Y) |
|----------|------------------|
| MR*, CW* (APs) | LIC-ENT-1YR |
| MV* (cameras) | LIC-MV-1YR |
| MT* (sensors) | LIC-MT-1Y |
| MG21 | LIC-MG21-ENT-1Y |
| MG41 | LIC-MG41-ENT-1Y |
| MG51 | LIC-MG51-ENT-1Y |
| MG52 | LIC-MG52-ENT-1Y |
| Z1/Z3/Z3C/Z4/Z4C | LIC-Z{model}-SEC-1Y or -1YR |
| MX{model} | LIC-MX{model}-SEC-1YR or -1Y |
| MS120-{port} | LIC-MS120-{port}-1YR |
| MS130-24* | LIC-MS130-24-1Y |
| MS130-48* | LIC-MS130-48-1Y |
| MS150-24* | LIC-MS150-24-1Y |
| MS150-48* | LIC-MS150-48-1Y |

**CRITICAL:** Always use 1-Year LIST price for weighting, regardless of term purchased.

### Calculation Formula (Weighted Dollar-Value Method)

**Step 1: Current Daily Burn**
```
Current Annual Value = Sum(1yr List × Qty) for all current devices
Current Daily Burn = Current Annual Value / 365
```

**Step 2: Remaining Credit**
```
Days Remaining = Current Expiration - Today
Remaining Credit = Current Daily Burn × Days Remaining
```

**Step 3: New Daily Burn (including additions)**
```
New Annual Value = Sum(1yr List × Qty) for ALL devices including new
New Daily Burn = New Annual Value / 365
```

**Step 4: New Credit (from purchase)**
```
New Credit = License List Price × Quantity
```
For 3-year purchases, use the 3Y list price directly (it represents 3 years of value).

**Step 5: New Expiration**
```
Total Credit = Remaining Credit + New Credit
Days from Today = Total Credit / New Daily Burn
New Expiration = Today + Days from Today
```

### Co-Term Output Format

```
## Co-Term Calculation Results

**Current Status:**
• Expiration: [Date]
• Days Remaining: [X] days
• Devices: [X]
• License Tier: [Tier]

**Adding:**
• [Qty] × [License SKU] ([Term])

***

### SKU Weighting Table

| Device | Qty | License SKU (1Y) | 1Y List | Weight | Source |
|--------|-----|------------------|---------|--------|--------|
| ... | ... | ... | ... | ... | ✓ CACHE |
| **TOTAL** | | | | **$X,XXX** | |

***

### Calculation Breakdown

**Current Daily Burn:** $[annual] / 365 = **$[daily]/day**
**Remaining Credit:** $[daily] × [days] = **$[amount]**

**New Daily Burn:** $[new annual] / 365 = **$[new daily]/day**
**New Credit:** [Qty] × $[list] = **$[amount]**

**Total Credit:** $[remaining] + $[new] = **$[total]**
**Days from Today:** $[total] / $[daily] = **[days] days**

***

## **New Co-Term Expiration: [DATE]**

This extends your organization approximately [X months] beyond the current expiration.

*Note: This is an estimate. Meraki's actual calculation may vary slightly.*
```

***

## GUARDRAILS

### Pre-Validation Required
Before applying suffix rules, verify SKU exists in valid_skus.json. Invalid SKUs must STOP immediately with suggestions.

### Same Tier Requirement
Co-term only works when all devices share the same license tier. If mixing:
```
⚠ TIER MISMATCH DETECTED
Your inventory has mixed tiers:
- MX68 → Advanced Security
- MR44 → Enterprise
Co-term requires same tier. Options: Upgrade APs to Advanced Security, or calculate separately.
```

### Missing SKU - Smart Fallback
If a SKU is not in the price cache, attempt web search before stopping:
```
⚠ [SKU] not found in cache.
Searching for current pricing...

[If found] Apply 30% discount from list?
[If not found] Please provide list price or skip this item.
```

### Validation Table Required
Before any calculation, display the weighting table with "✓ CACHE" for every SKU verified.

***

## EXAMPLES

### Example 1: Quote with term specified (QUOTE MODE - no pricing)

**User:** "Quote 2 MR44, 1 MS130-24P, 1 MX75 with 3 year licenses"

**Response:**
```
✓ Product exists: MR44
✓ Product exists: MS130-24P
✓ Product exists: MX75
✓ All SKUs validated

Order Summary:
• 2 × MR44-HW
• 2 × LIC-ENT-3YR
• 1 × MS130-24P-HW
• 1 × LIC-MS130-24-3Y
• 1 × MX75-HW
• 1 × LIC-MX75-SEC-3YR

Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-3YR,MS130-24P-HW,LIC-MS130-24-3Y,MX75-HW,LIC-MX75-SEC-3YR&qty=2,2,1,1,1,1

---

**Quote generated.** What's next?
→ Zoho | Lead times | Co-term | Email | Done
```

### Example 1b: Same request with pricing (COST MODE)

**User:** "How much for 2 MR44, 1 MS130-24P, 1 MX75 with 3 year licenses?"

**Response:**
```
✓ Product exists: MR44
✓ Product exists: MS130-24P
✓ Product exists: MX75
✓ All SKUs validated

Order Summary:
• 2 × MR44-HW - $601.00 each (57% off)
• 2 × LIC-ENT-3YR - $263.00 each (42% off)
• 1 × MS130-24P-HW - $1,506.00 (53% off)
• 1 × LIC-MS130-24-3Y - $262.00 (42% off)
• 1 × MX75-HW - $622.00 (70% off)
• 1 × LIC-MX75-SEC-3YR - $704.00 (47% off)

**Estimated Total: $4,822**
List Price: $9,593 | You Save: $4,771 (50%)

Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-3YR,MS130-24P-HW,LIC-MS130-24-3Y,MX75-HW,LIC-MX75-SEC-3YR&qty=2,2,1,1,1,1

---

**Quote generated.** What's next?
→ Zoho | Lead times | Co-term | Email | Done
```

### Example 2: Quote without term (QUOTE MODE - multi-term, no pricing)

**User:** "quote 5 MR44"

**Response:**
```
✓ Product exists: MR44
✓ Validated

No license term specified. Here are your options:

**1-Year Term**
• 5 × MR44-HW
• 5 × LIC-ENT-1YR
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-1YR&qty=5,5

**3-Year Term (Most Common)**
• 5 × MR44-HW
• 5 × LIC-ENT-3YR
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-3YR&qty=5,5

**5-Year Term (Best Value)**
• 5 × MR44-HW
• 5 × LIC-ENT-5YR
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-5YR&qty=5,5

---

Which term, or need Zoho/lead times?
```

### Example 2b: Price check without term (COST MODE - multi-term with pricing)

**User:** "how much for 5 MR44?"

**Response:**
```
✓ Product exists: MR44
✓ Validated

No license term specified. Here are your options:

## 1-Year Option
• 5 × MR44-HW - $601.00 each (57% off)
• 5 × LIC-ENT-1YR - $117.00 each (42% off)
**Total: $3,590**
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-1YR&qty=5,5

## 3-Year Option (Most Common)
• 5 × MR44-HW - $601.00 each (57% off)
• 5 × LIC-ENT-3YR - $263.00 each (42% off)
**Total: $4,320**
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-3YR&qty=5,5

## 5-Year Option (Best Value)
• 5 × MR44-HW - $601.00 each (57% off)
• 5 × LIC-ENT-5YR - $437.00 each (42% off)
**Total: $5,190**
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-5YR&qty=5,5

---

Which option, or need Zoho/lead times?
```

### Example 3: Invalid SKU caught at pre-validation

**User:** "quote MS130-13X with 3 year"

**Response:**
```
⚠ INVALID SKU: MS130-13X

"13X" is not a valid MS130 variant.
Available MS130 variants: 8, 8P, 8X, 12X, 24, 24P, 24X, 48, 48P, 48X

Did you mean: MS130-12X?
```

### Example 4: EOL product (QUOTE MODE - no pricing)

**User:** "quote 10 MR42 with 3 year licenses"

**Response:**
```
⚠ MR42 is End-of-Life

Is this a renewal for existing MR42 hardware, or a new purchase?

**Option A: Renew Existing (licenses only)**
• 10 × LIC-ENT-3YR
Order link: https://stratusinfosystems.com/order/?item=LIC-ENT-3YR&qty=10

**Option B: Refresh to MR44 (Recommended)**
• 10 × MR44-HW
• 10 × LIC-ENT-3YR
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-3YR&qty=10,10

*MR44 upgrade: Wi-Fi 6, improved performance, continued support*

Which option?
```

### Example 4b: EOL product (COST MODE - with pricing)

**User:** "how much for 10 MR42 with 3 year licenses?"

**Response:**
```
⚠ MR42 is End-of-Life

Is this a renewal for existing MR42 hardware, or a new purchase?

**Option A: Renew Existing (licenses only)**
• 10 × LIC-ENT-3YR - $263.00 each (42% off)
**Total: $2,630**
Order link: https://stratusinfosystems.com/order/?item=LIC-ENT-3YR&qty=10

**Option B: Refresh to MR44 (Recommended)**
• 10 × MR44-HW - $601.00 each (57% off)
• 10 × LIC-ENT-3YR - $263.00 each (42% off)
**Total: $8,640**
Order link: https://stratusinfosystems.com/order/?item=MR44-HW,LIC-ENT-3YR&qty=10,10

*MR44 upgrade: Wi-Fi 6, improved performance, continued support*

Which option?
```

### Example 5: Dashboard screenshot renewal

**User:** [uploads license page screenshot for NEATON ROME INC]

**Response:**
```
Detected from screenshot:

**Organization:** NEATON ROME INC
**License Model:** Co-termination
**Expiration:** Jan 3, 2026 (expired)
**MR Edition:** Enterprise

| SKU | Count |
|-----|-------|
| LIC-ENT-3YR | 31 |
| LIC-MS425-16-3YR | 2 |
| LIC-MS250-48-3YR | 2 |
| LIC-MS225-48FP-3YR | 4 |
| LIC-MS125-24P-3Y | 1 |
| LIC-MS130-48-3Y | 4 |
| LIC-C9300-24E-3Y | 2 |
| LIC-C9300-48E-3Y | 2 |

What would you like to do?
1. Generate renewal quote
2. Calculate co-term impact
3. Check for EOL devices
4. Export inventory
```

***

## SCOPE

**This skill DOES:**
- Generate URL quotes for Cisco/Meraki (co-term licensing)
- **NEW:** Dual display mode (Quote mode = no pricing, Cost mode = full pricing)
- Pre-validate SKUs before suffix application
- Generate multi-term quotes (1Y/3Y/5Y) when term not specified
- Present EOL upgrade comparisons automatically
- Support quote revisions with delta calculation
- Extract inventory from dashboard screenshots
- Smart fallback for missing prices
- Display Order Summary with or without prices based on mode
- Validate SKUs and apply suffixes
- Pair hardware with licenses
- Support 1Y, 3Y, 5Y terms
- Calculate co-term expiration dates
- Offer end-of-quote workflow transitions

**This skill does NOT:**
- Generate EA 3.0 or EA Subscription quotes (use subscription-modification skill)
- Generate Cisco Network Subscription quotes
- Support 7-year or 10-year terms
- Create Zoho CRM records directly (transitions to zoho-crm skill)
- Auto-upgrade EOL products without presenting options
- Auto-select variants for incomplete SKUs

***

## FILE REFERENCES

### PRICE CACHE
**Location:** `prices.json` (same folder as this SKILL.md)

**Metadata:**
```
Source: Meraki Price Book Feb 18, 2026
Last Updated: 2026-02-18
Total SKUs: 1222
Structure: {"prices": {"SKU": {"list": MSRP, "price": final_ecomm_price, "discount": percent_off}}}
Note: "price" field is the final customer-facing ecomm price. No additional calculation needed. Duplicate base SKUs removed where -HW version exists.
```

**Lookup:**
```python
import json
with open('/mnt/skills/user/stratus-quoting-bot-v4-5/prices.json') as f:
    prices = json.load(f)['prices']
print(prices.get('MR44-HW'))
```

### PRODUCT CATALOG (NEW in v4.1)
**Location:** `valid_skus.json` (same folder as this SKILL.md)

**Purpose:** Pre-validation product existence check before suffix application

**Structure:**
```json
{
  "MS130": ["8", "8P", "12X", "24", "24P", ...],
  "MR": ["28", "36", "44", "46", ...],
  "_EOL_PRODUCTS": {...},
  "_EOL_REPLACEMENTS": {...},
  "_COMMON_MISTAKES": {...}
}
```

**Lookup:**
```python
import json
with open('/mnt/skills/user/stratus-quoting-bot-v4-5/valid_skus.json') as f:
    catalog = json.load(f)

# Check if MS130-12X is valid
family, variant = 'MS130', '12X'
is_valid = variant in catalog.get(family, [])
```
