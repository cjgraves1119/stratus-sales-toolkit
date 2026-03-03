# Error Solutions Reference

## Common Errors and Fixes

### "Product not found in hot cache"

**Cause:** SKU not in product-ids.json

**Fix:** 
1. Search Zoho Products module: `word = "{SKU}"`
2. Get the product ID from results
3. Use that ID for the quote

### "Duplicate line items after update"

**Cause:** Added items instead of updating existing

**Fix:**
1. Re-fetch quote with `Quoted_Items` field
2. Use existing line item IDs when updating
3. Never create new items when modifying existing

### "Grand_Total doesn't match expected"

**Cause:** Usually discount format issue

**Fix:**
1. Confirm using percentage string format: `"Discount": "45%"`
2. Not decimal: `"Discount": 0.45` (wrong)
3. Not dollar without calculation (wrong for qty > 1)

### "Discount not applying correctly"

**Cause:** Dollar vs percentage confusion

**Fix:**
- For "apply X% discount" → Use `"Discount": "X%"`
- For "price at $X" → Calculate discount amount from list price

### "Quote creation failed - no Deal"

**Cause:** Attempting to create quote without associated deal

**Fix:**
1. Create deal first
2. Use deal ID in quote's `Deal_Name` field

### "Task not linked to Deal"

**Cause:** Missing `$se_module` field

**Fix:**
```json
{
  "What_Id": {"id": "{deal_id}"},
  "$se_module": "Deals"
}
```

### "Country code invalid"

**Cause:** Using full country name

**Fix:**
- Use `"US"` not `"United States"`
- Use `"CA"` not `"Canada"`

### "New dropdown value created"

**Cause:** Passed value not in existing picklist

**Fix:**
- Check valid Lead Source options in SKILL.md
- Use exact spelling including typos (e.g., "Referal")

### "Vendor_Lines empty"

**Cause:** CCW pricing not yet retrieved

**Fix:**
1. Check if `CCW_Deal_Number` is populated
2. If yes, trigger `LIVE_GetQuoteData`
3. Wait 5-10 seconds, retry
4. If still empty after 5 retries, pricing may not be approved yet

### "Line item delete not working"

**Cause:** Wrong delete syntax

**Fix:**
```json
{
  "Quoted_Items": [
    {"id": "LINE_ID", "_delete": true}
  ]
}
```

Note: `_delete` not `delete`

### "Search returns no results"

**Cause:** Criteria too specific or wrong field

**Fix:**
1. Try `word` search first (most flexible)
2. Simplify search terms
3. Check field API names match exactly
4. After 2 failed attempts, ask user for clarification

### "Quote stage not updating"

**Cause:** Using wrong field name

**Fix:**
- Field is `Quote_Stage` not `Stage`
- Valid values: "Draft", "Delivered", "Sent", "Invoiced", "Accepted", "On Hold"
