# Margin Update Workflow

## When to Use

- User says "update margin to X%"
- User says "apply X% margin"
- User says "price at X% margin"

## Prerequisites

Quote must have `CCW_Deal_Number` populated (Cisco pricing approved).

## Step-by-Step Process

### 1. Fetch Quote with CCW Deal Number
```
Module: Quotes
ID: {quote_id}
Fields: id,Subject,Grand_Total,Quoted_Items,CCW_Deal_Number
```

If `CCW_Deal_Number` is empty, user needs to submit for Cisco approval first.

### 2. Get Vendor_Lines (Cost Data)
```
Module: Vendor_Lines
Criteria: (Quote.id:equals:{quote_id})
Fields: Name,Product_Code,Quantity,List_Price,Disti_Price,Disti_Price_Total
```

### 3. Calculate Target Pricing

**Formula:**
```
Target_Sell = Disti_Price_Total / (1 - margin_decimal)
Discount_Amount = (List_Price * Quantity) - Target_Sell
Discount_Percent = Discount_Amount / (List_Price * Quantity) * 100
```

**Common Margins:**
| Margin | Divisor | Use Case |
|--------|---------|----------|
| 13% | 0.87 | Standard/online pricing |
| 15% | 0.85 | Competitive deals |
| 20% | 0.80 | Default margin |

### 4. Match Vendor_Lines to Quoted_Items

Match by `List_Price` (per unit) since SKU formats may differ.

### 5. Update Quote with Discounts

**Use percentage format for discounts:**
```json
{
  "Quoted_Items": [
    {
      "id": "{line_item_id}",
      "Discount": "45.5%",
      "Description": "{Product Name} (45.5% discount)"
    }
  ]
}
```

**CRITICAL:** Use percentage strings ("45.5%"), not decimals.

### 6. Verify Update

Re-fetch quote and confirm:
- Grand_Total matches expected
- All line items updated
- No duplicate items created

## Example Calculation

**Given:**
- List Price: $1,000
- Quantity: 2
- Disti Cost Total: $800
- Target Margin: 20%

**Calculate:**
```
Target_Sell = $800 / 0.80 = $1,000
Total_List = $1,000 × 2 = $2,000
Discount_Amount = $2,000 - $1,000 = $1,000
Discount_Percent = $1,000 / $2,000 × 100 = 50%
```

Apply: `"Discount": "50%"`

## Troubleshooting

**Discount not applying correctly:**
- Ensure using percentage string, not number
- Check that line item ID is correct
- Verify Vendor_Lines data is populated

**Grand_Total doesn't match:**
- Re-fetch and verify all line items
- Check for rounding differences
- Confirm quantity matches between Vendor_Lines and Quoted_Items
