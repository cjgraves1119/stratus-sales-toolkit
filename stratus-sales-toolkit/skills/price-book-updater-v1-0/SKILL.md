---
name: price-book-updater-v1-0
description: "converts stratus meraki price book xlsx files into a cleaned excel and updated prices.json. applies exclusion filters to remove non-sellable skus (true-forward, bounded, xcat, wpa, msp, cog, beta, international variants, 7y/10y/1d licenses), transforms cfg/rtg/rf sku variants to their correct form, calculates ecomm pricing at 13% margin, and flags new skus not in the previous price book for manual review. outputs a cleaned xlsx with yellow-highlighted new products and a structured json matching the stratus prices.json format. triggers: update price book, new price book, refresh prices, price book update, convert price book, update prices json, process price book, meraki price book, new price list."
---

# Price Book Updater v1-0

Converts a raw Meraki price book XLSX into a cleaned Excel file and updated `prices.json` ready for the Stratus website. Handles all exclusion filtering, SKU transformations, ecomm pricing, and new product flagging in one pass.

## Inputs

- **New price book**: Raw Meraki XLSX (e.g. `US - Meraki Price Books (MM-DD-YYYY).xlsx`)
- **Previous prices.json** (optional): Used to detect new products for flagging. If not provided, all SKUs are treated as confirmed.
- **Margin override** (optional): Default is 13% (divide by 0.87). User can specify a different margin.

The new price book must have at minimum these columns:
- `Short Description`
- `Manufacturer Part Number`
- `List Price (MSRP)`
- `Promotion Price`
- `Normal Price`
- `Hardware/Software`

## Output

1. **Cleaned Excel** (`Price List MM-DD-YYYY (Cleaned).xlsx`) — same 8-column format as the working price list, with new/unconfirmed products highlighted yellow
2. **prices.json** — structured JSON matching the existing Stratus format with `prices`, `_meta`, and `_new_products_flagged` sections

---

## Workflow

### Step 1 — Detect date from filename

Extract the date from the uploaded filename (e.g. `03-14-2026`) to use in output filenames and `_meta.last_updated`. If not parseable, ask the user.

### Step 2 — Apply SKU transformations (BEFORE filtering)

Run these in order. Transformations modify the part number in place before any rows are removed.

#### CFG++ → RTG rename

For any SKU containing `-CFG++`:
- Derive the RTG equivalent: replace `-CFG++` with `-RTG`
- If the RTG equivalent **already exists** in the file → delete the CFG++ row (duplicate)
- If no RTG equivalent exists → rename the CFG++ row to the RTG SKU

#### RTG-RF → RTG (strip suffix)

For any SKU containing `-RTG-RF`:
- Derive the clean RTG: replace `-RTG-RF` with `-RTG`
- If a `-RTG` version already exists in the file → delete the RTG-RF row (duplicate)
- If no RTG exists yet → rename by stripping `-RF` suffix

#### CFG-RF → delete

Any SKU containing `-CFG-RF`: check if a corresponding `-RTG-RF` or `-RTG` already exists (or was just created above). If yes, delete the CFG-RF row. If somehow no RTG equivalent exists at all, rename to `-RTG` as a fallback.

### Step 3 — Apply exclusion filters

Remove entire rows matching ANY of these conditions:

| Filter | Rule |
|--------|------|
| **Prefix exclusions** | SKU starts with: `TF-`, `BOUND-`, `XCAT-`, `WPA-`, `MSP-`, `COG-`, `B-` |
| **LIC term length** | SKU starts with `LIC` AND contains `7Y`, `10Y`, `7YR`, `10YR`, or `1D` |
| **MA international** | SKU starts with `MA-` AND contains any of: `-UK`, `-EU`, `-AU`, `-CN`, `-IN`, `-TW`, `-AR`, `-BR`, `-FR`, or `SIMTRAY` |
| **Description: BETA** | Short Description contains `BETA` |
| **Description: UK Plug** | Short Description contains `(UK Plug)` (case-insensitive) |
| **Suffix: BUN** | SKU contains `BUN` |
| **Suffix: plain -RF** | SKU ends with `-RF` and does NOT contain `RTG` or `CFG` (remanufactured — no RTG equivalent) |

### Step 4 — Calculate ecomm pricing

For each remaining row:

```
Ecomm Price = CEILING(Promotion Price / 0.87)
```

- Round up to the nearest whole dollar (no cents)
- If Promotion Price is missing or zero, leave Ecomm Price blank
- Default margin divisor is 0.87 (13% margin). Adjust if user specifies a different margin.

### Step 5 — Flag new products

Before filtering, preserve each row's **original SKU** (pre-transformation) in a `_original_sku` column. This is critical for matching transformed SKUs back to the old JSON.

Compare remaining SKUs against the previous `prices.json` (if provided). A SKU is **confirmed** if EITHER:
- The current (post-transform) SKU exists in the old JSON, OR
- The original pre-transform SKU exists in the old JSON

This ensures renamed SKUs (e.g. `CW9176I-CFG-RF` → `CW9176I-RTG`) are correctly recognized as existing products rather than flagged as new.

- **Confirmed** → include in `prices` dict
- **New** (neither current nor original SKU in old JSON) → flag for review, include in `_new_products_flagged` only

If no previous JSON is provided, treat all SKUs as confirmed.

### Step 6 — Build outputs

#### Excel output

Columns (in order):
1. Short Description
2. Manufacturer Part Number
3. List Price (MSRP)
4. Promotion Price
5. Normal Price
6. SKU ETA
7. Ecomm Price
8. Hardware/Software

Formatting:
- Header row: dark blue fill (`1F4E79`), white bold Arial 10pt
- New/flagged product rows: yellow fill (`FFF2CC`), dark gold font (`7F6000`)
- All other rows: Arial 10pt
- Freeze row 1
- Column widths: 55, 28, 18, 18, 18, 14, 14, 18

Save as: `Price List {MM-DD-YYYY} (Cleaned).xlsx`

#### JSON output

```json
{
  "prices": {
    "LIC-MV-CA30-1Y": { "list": 221, "price": 149, "discount": 42 },
    ...
  },
  "_meta": {
    "source": "Meraki Price Book {Mon DD, YYYY}",
    "last_updated": "YYYY-MM-DD",
    "total_skus": 1013,
    "structure": "list=MSRP, price=ecomm price, discount=percent off",
    "note": "Use 'price' field directly - no calculation needed. Duplicate base SKUs removed where -HW version exists.",
    "new_products_pending_review": 12
  },
  "_new_products_flagged": [
    {
      "sku": "MV52-HW",
      "description": "Meraki Varifocal MV52 Outdoor Bullet Camera With 1TB Storage",
      "type": "HW",
      "list_price": 1299
    }
  ]
}
```

Field definitions:
- `list` — `List Price (MSRP)` rounded to nearest whole dollar
- `price` — Ecomm Price (calculated in Step 4)
- `discount` — `round((1 - promo_price / list_price) * 100)` as integer percent
- `_new_products_flagged` — SKUs that passed all filters but weren't in the previous JSON

Save as: `prices.json`

### Step 7 — Present results and flag summary

After generating both files, present:
1. Links to both output files via `computer://` links
2. A brief summary: total SKUs, excluded count, confirmed count, new/flagged count
3. If there are flagged new products, list them grouped by category (Licenses, Cameras, Switches, etc.) and ask the user which ones to add to the confirmed `prices` dict

If the user approves specific flagged products, add them to the `prices` dict and regenerate the JSON.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Missing `Promotion Price` column | Fall back to `Normal Price` for ecomm calculation |
| Both promo and normal price missing | Leave Ecomm Price blank, exclude from JSON |
| Duplicate SKUs after transformation | Keep the row with a valid price; flag duplicates in console output |
| `$0` list price items | Include in Excel, exclude from JSON (can't calculate meaningful discount) |
| Previous JSON not provided | Skip new-product flagging; treat all as confirmed |
| Unrecognized column names | Report columns found and ask user to map them |

---

## Python Implementation Notes

Use `pandas` for data loading and filtering, `openpyxl` for Excel formatting, `math.ceil` for ecomm rounding, and `json` for output. All logic should be implemented in a single Python script run via Bash.

Key import pattern:
```python
import pandas as pd, math, json, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
```

Suppress the openpyxl default style warning with `warnings.filterwarnings('ignore')`.

When reading the price book, always use `header=0` and strip whitespace from the `Manufacturer Part Number` column immediately after loading.
