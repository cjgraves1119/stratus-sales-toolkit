# Margin Update Workflow

## When to Use

- "set X% margin" / "X% margin" / "apply X% margin"
- "update margin to X%" / "change margin to X%" / "price at X% margin"
- "set this to X%" / "make this X%" / "margin update"
- Any phrase combining "margin" with a percentage on an existing quote

## Critical: Use Disti_Price_Total, Not Net_Price

**Cost basis MUST be `Disti_Price_Total`** (pre-rebate) from `Vendor_Lines`. NOT `Net_Price`.

Why: Zoho's `Extended_Margin` rollup field is calculated against `Disti_Price`. Using `Net_Price` (post-rebate) produces math that looks correct (e.g., 17.5% off Net) but renders ~3 percentage points lower in the Zoho UI. A 17.5% margin off Net = ~14.36% off Disti, which is what the customer-facing rollup shows.

## Prerequisites

Quote must have `CCW_Deal_Number` populated (Cisco pricing approved). If empty, run `LIVE_CiscoQuote_Deal` first.

## Step-by-Step Process

### 1. Fetch Quote with CCW Deal Number
```
Module: Quotes
ID: {quote_id}
Fields: id,Subject,Grand_Total,Quoted_Items,CCW_Deal_Number,Extended_Disti_Price,Extended_Net_Price
```

If `CCW_Deal_Number` is empty, user needs to submit for Cisco approval first.

### 2. Get Vendor_Lines (Cost Data)

Use ZohoCRM_searchRecords (NOT getRelatedRecords — that returns INVALID_DATA on the Vendor_Lines relation):
```
Module: Vendor_Lines
Criteria: (Quote.id:equals:{quote_id})
Fields: id,Name,Product_Code,Quantity,List_Price,Disti_Price,Disti_Price_Total,Net_Price,Net_Price_Total,Sequence_Number
per_page: 200
```

### 3. Calculate Target Pricing

**Formula (per line, per unit):**
```
Target_Sell_Per_Unit = Disti_Price / (1 - margin_decimal)
Discount_Percent = round((List_Price - Target_Sell_Per_Unit) / List_Price × 100, 2)
Discount_Field = f"{Discount_Percent}%"
```

For lines where vendor has split quantity (Disti_Price_Total = Disti_Price × Qty), the per-unit Disti_Price is the basis.

**Common Margins:**

| Margin | Divisor | Use Case |
|--------|---------|----------|
| 13% | 0.87 | Standard/online pricing |
| 15% | 0.85 | Competitive deals |
| 17.5% | 0.825 | Mid-range deals |
| 20% | 0.80 | Default margin |

### 4. Match Vendor_Lines to Quoted_Items

Match by per-unit `List_Price` (vendor `List_Price` should equal quoted item `List_Price`). When two vendor lines share the same list price (Cisco substitution edge case), match by `Name` sequence — vendor line names are sequential and correspond to quoted item creation order.

### 5. Update Quote with Discounts

**Use percentage strings (not numbers):**
```json
{
  "data": [{
    "id": "{quote_id}",
    "Quoted_Items": [
      {
        "id": "{line_item_id}",
        "Discount": "45.5%",
        "Description": "{Product Name} (45.5% off list, 17.5% margin)"
      }
    ]
  }]
}
```

**CRITICAL:** Use percentage strings (`"45.5%"`), not decimals or dollar amounts. This is consistent with Critical Rule #42 in the main SKILL.md.

### 6. Verify Update

Re-fetch quote and confirm:
- `Sub_Total` (with tax) reflects new discounts
- Sum of `Total_After_Discount` per line matches expected pre-tax sell
- `Extended_Margin` displays correctly (may have a brief delay; if stale, re-run `LIVE_GetQuoteData` to force refresh)
- No duplicate items created

**Margin verification:**
```
actual_margin = (Sub_Total_pretax - Extended_Disti_Price) / Sub_Total_pretax × 100
where Sub_Total_pretax = Sub_Total - All_Taxes_Total
```

## Worked Example

**Given:**
- List Price: $1,000 (per unit)
- Quantity: 2
- Disti_Price (per unit): $400
- Disti_Price_Total: $800
- Target Margin: 20%

**Calculate:**
```
Target_Sell_Per_Unit = $400 / 0.80 = $500
Discount_Percent = round(($1,000 - $500) / $1,000 × 100, 2) = 50%
```

**Apply:** `"Discount": "50%"`

**Verify:**
```
Total_After_Discount = $1,000 × (1 - 0.50) × 2 = $1,000
Margin = ($1,000 - $800) / $1,000 = 20% ✓
```

## Troubleshooting

**Discount not applying correctly:**
- Confirm percentage string format (`"45.5%"`), not number (`45.5`) or dollar amount (`455.00`)
- Verify line item ID is correct
- Verify Vendor_Lines data is populated (Cisco must have approved the deal)

**Grand_Total doesn't match expected:**
- Re-fetch and verify all line items
- Check for rounding differences (round to 2 decimal places)
- Confirm quantity matches between Vendor_Lines and Quoted_Items

**Extended_Margin shows old value after update:**
- Zoho rollup fields can lag. Check actual `Sub_Total` and line `Total_After_Discount` first — those reflect the new discounts immediately
- If rollup still wrong after page refresh, trigger `LIVE_GetQuoteData` admin action to force recalculation

**Two vendor lines have same List_Price:**
- This happens when Cisco substitutes a SKU at the same list price (common with newer-gen replacements)
- Match by vendor `Name` sequence (lower name = earlier quoted item)
- Total cost is unchanged regardless of which line gets which cost — total margin will still hit target

## Why Disti_Price (Not Net_Price)

`Disti_Price` is what Cisco shows the disti as the price BEFORE rebates/incentives. `Net_Price` is the cost AFTER disti rebates pass through to Stratus.

Zoho's `Extended_Margin` and `Extended_Markup_Percent` rollups use `Disti_Price` because that's the Cisco-facing benchmark. Using `Net_Price` undercuts the customer-facing margin number.

When a customer says "I need 17.5% margin", they mean the displayed Zoho margin — which is calculated against Disti_Price. Always price off Disti_Price_Total for margin updates.

## Reference: Production Bug This Workflow Prevents

A Miniso quote was set to 17.5% margin using `Net_Price` as cost basis. The math was internally consistent (Sub_Total / Net_Price ratio = 17.5%), but Zoho's UI showed 14.36% margin because the rollup uses `Disti_Price`. Required a redo using `Disti_Price` to fix.

This workflow exists to prevent that.
