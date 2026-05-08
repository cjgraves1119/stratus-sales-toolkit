---
name: subscription-modification-v2-9
description: "cisco subscription modification AND true forward quote generator. API-first sub mod workflow pulls quote/line economics from CCW DID via ListQuoteService + AcquireQuoteService, avoiding downloaded CCW XLS when API access works; bills only add-on net change with configurable 20% markup/margin while showing full subscription at $0 for no-change lines. retains XLS fallback parser and true forward workflow from cisco TF reports. triggers: subscription modification, sub mod, sub-mod, ccw subscription, add licenses, license modification, did add-on quote, true forward, tf report, tf quote, ea anniversary, value shift."
---

# Subscription Modification & True Forward Skill v2.9

Two distinct workflows in one skill:

1. **Subscription Modification** (Fast Paths A/B) — adds/modifies licenses on an existing sub. API-first when Chris provides a CCW DID/deal ID; fallback to CCW xls file if API access is unavailable.
2. **True Forward** (Fast Path C) — bills customer for mid-EA consumption variance via a Cisco-generated TF report (xlsx). 20% true margin applied to already-discounted Cisco net cost per line. Uses Drive read + live Zoho lookups.

**Pick the right workflow first** — the file format differs, the math differs, and the line structure differs. See `workflows/true_forward.md` for the full TF playbook.

## Workflow Selection Decision

```
Request from Chris arrives. What is it?

  IF filename matches "TrueForward*Report*" OR "TF*Report*"
  OR Chris says "true forward" / "TF" / "value shift" / "TF for [customer]"
      → True Forward workflow (Fast Path C, see workflows/true_forward.md)

  IF Chris provides a CCW DID / deal ID for a subscription modification
  OR says "pull the add-on costs from DID #######"
      → API-first Subscription Modification workflow (Fast Path A/B with pull_sub_mod_api.py)

  IF file is a CCW xls quote (with "Pricing Term in months" column, "Ext. List Price" column)
  OR Chris says "sub mod" / "subscription modification" / "add-on" / "modify subscription"
      → Subscription Modification workflow. Prefer API if a DID is available; otherwise use XLS fallback.

  AMBIGUOUS → ask Chris before proceeding.
```

## DANGER ZONE (READ BEFORE ANY QUOTE WORK)

These traps have caused wrong quotes in past runs. The scripts below handle them, but if you deviate from the scripts, remember:

### Sub Mod Traps

1. **API path is source of truth when DID is available.** Use `pull_sub_mod_api.py` first. It reads Cisco's own `QuantityChange`, `RemainingTerm`, and `BillingAmountNetChange`, avoiding XLS download/export drift.

2. **Show full quantity, bill only add-on delta.** If the CCW line shows 12 total AP licenses and `QuantityChange=2`, the Zoho quote line quantity should be 12, but the discount should drive the invoice amount to the two-license add-on economics plus margin.

3. **Non-add-on lines are transparency only.** Keep them on the quote, but discount them 100% to $0. They are already covered under the existing subscription.

4. **In API net mode, do not apply old 30%/45% list discounts.** Use Cisco `BillingAmountNetChange` / `ContractAmountNetChange` as Stratus cost, then apply configured margin. Default is `20% gross` (`sell = cost / (1 - 0.20)` = `cost / 0.80`). For markup mode, set `margin_mode="markup"` (`sell = cost * 1.20`).

5. **XLS fallback traps still apply.** If API cannot pull the DID, the old downloaded-Excel path is allowed. In that path, "Pricing Term in months" column = 1 is NOT remaining term, and "Ext. List Price" already equals qty × unit × term.

### True Forward Traps

6. **TF margin is on the NET cost (post-credits), per line.** Each charge line gets `cost / 0.80`. Each credit line gets `credit / 0.80`. The credits are NOT absorbed by Stratus — they flow through to the customer. If you only mark up the charge lines, the customer total will be wrong (too high).

7. **Value Shift Credits are positive list + oversized discount, NOT negative list.** Zoho accepts negative List_Price but the printed PDF formatting is awkward. Use positive `List_Price = (credit / 0.80) / qty`, `Discount = 2 × List × Qty` to drive a negative line net.

8. **Show the FULL EA on the quote, not just the changed lines.** Fully Consumed SKUs go on the quote at 100% discount ($0 net) for transparency. Customers expect to see their full subscription, not just the delta.

## Scripts (Sub Mod only)

Located in `scripts/`. True Forward uses live Zoho lookups + per-line math, not these scripts.

| Script | Input | Output |
|---|---|---|
| `pull_sub_mod_api.py` | CCW DID | SOAP OAuth2 + ListQuoteService + AcquireQuoteService against `apix.cisco.com/commerce/QUOTING/v1`. Outputs the parsed schema below with `ccw_net_addon_cost` and full `api.*` block per line. |
| `parse_sub_mod.py` | CCW xls file path | Fallback clean JSON from downloaded XLS |
| `submod_quote_pricing.py` | parsed JSON + fetched Zoho quote JSON (with subform ids) | Ready-to-PUT Zoho update body that updates lines IN PLACE: preserves subform ids, Decimal precision, penny-bump heuristic. **Preferred path when the DID already has a Zoho quote.** |
| `build_quote_payloads.py` | parsed JSON + config JSON | Ready-to-POST Customer + OP Zoho payloads (CREATE from scratch). Supports `ccw_api_net` (default `gross` margin mode) and `xls_list_discount`. Decimal precision + penny-bump. |
| `verify_quotes.py` | expected JSON + actual (fetched) JSON | Pass/fail report with line-level diff |

`pull_sub_mod_api.py` and `submod_quote_pricing.py` use only Python stdlib. `pull_sub_mod_api.py` requires `CISCO_CLIENT_ID` and `CISCO_CLIENT_SECRET` in the environment. `parse_sub_mod.py` auto-installs `xlrd` for XLS fallback.

**API endpoints baked in** (override via env if Cisco rotates):
- OAuth: `https://id.cisco.com/oauth2/default/v1/token`
- List:  `https://apix.cisco.com/commerce/QUOTING/v1/ListQuoteService`
- Acquire: `https://apix.cisco.com/commerce/QUOTING/v1/AcquireQuoteService`

## Fast Paths

### FAST PATH A: Sub Mod, attach to existing deal (most common sub mod case)

Chris provides a Zoho deal URL plus either a CCW DID or a sub mod CCW xls file.

**A-update (preferred when Zoho deal already has a Quote attached, e.g. auto-created
by Velocity Hub from the CCW DID):** patch the existing quote in place via
`submod_quote_pricing.py`. Keeps subform line ids stable.

```
1. Parse URL -> extract deal_id
2. Fetch deal -> Account_Name.id, Contact_Name.id, related Quotes
3. If a Quote already exists on this deal that maps to the CCW DID:
     a. Fetch that Quote with full Quoted_Items (each line id required)
     b. Run pull_sub_mod_api.py {did} > /tmp/parsed.json   (or parse_sub_mod.py for xls)
     c. Run submod_quote_pricing.py --ccw-parsed /tmp/parsed.json                                     --zoho-quote /tmp/zoho_fetch.json                                     --quote-id {quote_id}                                     --margin 20 --margin-mode gross                                     --output /tmp/quote_update.json
     d. Show consolidated validation table. Ask Chris to proceed.
     e. ZohoCRM_updateRecord module=Quotes recordID={quote_id}
          body=$(jq .zoho_update_body /tmp/quote_update.json)
     f. Re-fetch quote, compare Sub_Total to expected_pre_tax_total ($0.02 tolerance)
     g. Create follow-up task (+7 business days)
4. Else (no existing quote on deal): fall through to A-create below.
```

**A-create (no existing quote — build new Customer + OP quotes):**

```
1. Parse URL -> extract deal_id
2. Fetch deal -> Account_Name.id, Contact_Name.id (if set)
3. Fetch account -> billing/shipping address fields
4. If CCW DID available: pull_sub_mod_api.py {did} > /tmp/parsed.json
   Else: parse_sub_mod.py on XLS > /tmp/parsed.json
5. Build config.json. For API path set pricing_source=ccw_api_net, margin_percent=20,
   margin_mode=gross (default). Use markup only when explicitly requested.
6. Run build_quote_payloads.py -> verify totals match in stdout before POST
7. Show ONE consolidated validation table. Ask Chris to proceed.
8. POST both quotes, then run verify_quotes.py
9. Create follow-up task (+7 business days)
10. Report summary with quote URLs
```

### FAST PATH B: Sub Mod, new deal from scratch

Chris only provides the sub mod file.

```
1. If Chris provided a DID: run pull_sub_mod_api.py {did}; otherwise run parse_sub_mod.py
2. Lookup account by end_customer_name via Zoho search
3. Check for existing deal with same CCW_Deal_Number (criteria: CCW_Deal_Number:equals:{ccw_did})
4. If existing deal found: switch to FAST PATH A with that deal_id
5. Else: create new deal with Stratus Referal defaults, THEN run FAST PATH A
```

### FAST PATH C: True Forward (EA mid-term consumption variance)

Chris provides a Cisco-generated TF report (xlsx, often via Google Drive URL).

```
1. Read TF report (Drive read_file_content if URL, or local read if uploaded)
2. Extract: customer name, EA ID, SubID, term, per-SKU lines (charges/credits/unchanged)
3. Lookup account in Zoho (skip delinquency check — Net_Terms always Cash for EA TFs)
4. Lookup or create deal
5. Lookup contact (single = use, multiple = ask)
6. Live Zoho Products search for ALL distinct SKUs (E3N-* not in cache)
7. Build line groups: charges (cost/0.80) + credits (credit/0.80, positive+discount) + unchanged ($0)
8. Show validation table, confirm with Chris
9. Create Deal + Quote, force Net_Terms = Cash if Zoho reverted it
10. Update Deal Amount, add Notes (deal + quote), create follow-up task
```

Full TF playbook in `workflows/true_forward.md` — read it on every TF run.

## API Net Pricing Logic (Preferred Sub Mod Path)

Use this when `parsed.source == "ccw_api"` or config has `"pricing_source": "ccw_api_net"`.

For each line:

```
If is_addon (QuantityChange > 0 OR BillingAmountNetChange > 0 OR ContractAmountNetChange > 0
             OR LineChangeType == "Added"):
  quantity shown = full New Qty from CCW
  cost          = BillingAmountNetChange OR ContractAmountNetChange OR ccw_net_addon_cost
  customer invoice = cost × (1 + margin/100)              # markup mode
                  OR cost / (1 - margin/100)              # gross mode (DEFAULT)
  discount = full visible line list amount - customer invoice amount

Else:
  quantity shown = full New Qty from CCW
  customer invoice amount = 0
  discount = full visible line list amount                # 100% discount
```

Decimal arithmetic with `ROUND_HALF_UP` plus a penny-bump heuristic ensures the
line total reaches the target before the discount is subtracted, so the customer
invoice amount lands on the expected dollar+cent.

Example from verified DID `84410290`, SKU `LIC-ACCSMGR-A` (qty 35, list $933.92,
Cisco net $542.79):

| Mode | Customer invoice | Discount on $933.92 list |
|---|---|---|
| 20% markup | `542.79 × 1.20 = $651.35` | `$282.57` |
| 20% gross  | `542.79 / 0.80 = $678.49` | `$255.43` |

Default is `gross`. `markup` exists for the legacy 20%-markup-on-cost mental model.
For sub mod work, `gross` matches the sales practice for true-margin reporting.

## XLS Discount % Decision Tree (Fallback Sub Mod Path)

Only use this when working from the old CCW XLS export path.

| Parent SKU | Child SKU Prefix | Discount % | Notes |
|---|---|---|---|
| MERAKI-SUB | LIC-* | **30** | Classic Meraki co-term |
| CISCO-NETWORK-SUB | LIC-* | **30** | New umbrella but children are still Meraki co-term |
| CISCO-NETWORK-SUB | E3N-* | **45** | EA 3.0 Networking |
| SECURE-ACCESS-SUB | SA-*, E3S-SA-* | **45** | EA 3.0 Security / Secure Access |

If mixed children (rare), prompt Chris. Do not guess.

## True Forward Margin (separate logic, not a discount %)

For TFs only:

```
For each charge line:    list_price = (cisco_net_cost / 0.80) / qty,    discount = 0
For each credit line:    list_price = (cisco_credit / 0.80) / qty,      discount = 2 × list × qty
For each unchanged line: list_price = zoho_default_unit_price,           discount = list × qty (drives $0)
```

Stratus margin = `Net TF Cost × 0.25` (since `cost / 0.80 = cost × 1.25`).

## Config JSON Template (Sub Mod only)

```json
{
  "deal_id": "2570562000xxxxxxxxx",
  "account_id": "2570562000xxxxxxxxx",
  "contact_id": "2570562000xxxxxxxxx",
  "billing": {
    "street": "...",
    "city": "...",
    "state": "XX",
    "code": "xxxxx",
    "country": "US"
  },
  "shipping": {
    "street": "...",
    "city": "...",
    "state": "XX",
    "code": "xxxxx",
    "country": "US"
  },
  "pricing_source": "ccw_api_net",
  "margin_percent": 20,
  "margin_mode": "gross",
  "valid_till": "YYYY-MM-DD",
  "discount_percent": 30,
  "subject_prefix": "Short customer name",
  "owner_id": "2570562000141711002",
  "skip_ea3_prompt": false,
  "zoho_fallback_ids": {
    "RARE-SKU-NOT-IN-CACHE": "zoho_id_from_live_search"
  }
}
```

For XLS fallback use `"pricing_source": "xls_list_discount"` and set `discount_percent` from the decision tree. For API path, `discount_percent` is ignored.

## Consolidated Validation Table — Sub Mod

Display this once. If any row is red, stop and fix.

```
| Field                    | Value                                          | Status |
|--------------------------|------------------------------------------------|--------|
| Customer                 | {end_customer_name}                            | ✓      |
| CCW DID                  | {ccw_deal_id}                                  | ✓      |
| CCW_Deal_ID (on Deal)    | {deal.CCW_Deal_ID or "WILL BACKFILL"}          | ✓      |
| Subscription ID          | {subscription_id}                              | ✓      |
| Term                     | {term_months} months ({start} -> {end})        | ✓      |
| Parent SKU               | {parent_sku}                                   | ✓      |
| Pricing Source           | API net change / XLS fallback                  | ✓      |
| Margin                   | {margin_percent}% {markup/gross}               | ✓      |
| Deal                     | {deal_name} [{deal_id}]                        | ✓      |
| Account                  | {account_name} [{account_id}]                  | ✓      |
| Contact                  | {contact_name} [{contact_id}]                  | ✓      |
| Billing Address          | {full address}                                 | ✓      |
| Shipping Address         | {full address}                                 | ✓      |
| Delinquency Score        | {score} (gate: <= 5)                           | ✓      |
| Line Items               | {total_skus} SKUs (+{added}/~{modified}/={nochange}) | ✓  |
| Expected Customer Total  | ${customer_total}                              | ✓      |
| Expected OP Total        | ${op_total} (must match customer)              | ✓      |
| Unresolved SKUs          | {list or "none"}                               | ✓      |
| Warnings                 | {from builder script}                          | ✓      |
```

## Consolidated Validation Table — True Forward

```
| Field                    | Value                                          | Status |
|--------------------------|------------------------------------------------|--------|
| Customer                 | {customer_name}                                | ✓      |
| EA ID                    | {ea_id}                                        | ✓      |
| Subscription ID          | {sub_id}                                       | ✓      |
| Remaining Term           | {months} months                                | ✓      |
| Report Date              | {report_date}                                  | ✓      |
| Account                  | {account_name} [{account_id}]                  | ✓      |
| Contact                  | {contact_name} [{contact_id}]                  | ✓      |
| Billing Address          | {full address}                                 | ✓      |
| Charge Lines             | {n} SKUs, total $charges_customer              | ✓      |
| Credit Lines             | {n} SKUs, total -$credits_customer             | ✓      |
| Unchanged Lines          | {n} SKUs at $0                                 | ✓      |
| Cisco Net TF Cost        | ${cisco_net}                                   | ✓      |
| Customer Pre-tax         | ${customer_pretax} (= Cisco net / 0.80)        | ✓      |
| Expected Tax             | ${expected_tax} ({state_pct}% {state})         | ✓      |
| Customer Grand Total     | ${grand_total}                                 | ✓      |
| Net_Terms                | Cash (always for EA TFs)                       | ✓      |
| Stratus Margin           | ${margin}                                      | ✓      |
| Unresolved SKUs          | {list or "none"}                               | ✓      |
```

## Sub Mod Workflow Step-by-Step (Fast Path A, most common)

```
STEP 1 - PARSE FILE
  Preferred:
    Run: CISCO_CLIENT_ID=... CISCO_CLIENT_SECRET=... python3 scripts/pull_sub_mod_api.py {ccw_did} > /tmp/parsed.json
  Fallback:
    Run: python3 scripts/parse_sub_mod.py <uploaded_file> > /tmp/parsed.json
  Check: parsed.json has header + term + consolidated_line_items
  Fail -> STOP, print stderr, ask for re-upload

STEP 2 - FETCH DEAL + ACCOUNT
  ZohoCRM_getRecord module=Deals recordID={deal_id}
    -> Account_Name.id, Contact_Name.id (if present), CCW_Deal_ID
  ZohoCRM_getRecord module=Accounts recordID={account_id}
    -> Billing_* + Shipping_* fields, Delinquency_Score

  CCW_Deal_ID gate:
    - If deal.CCW_Deal_ID is null AND parsed.header.ccw_deal_id exists:
        ZohoCRM_updateRecord module=Deals recordID={deal_id}
          body={"data": [{"CCW_Deal_ID": "{parsed.header.ccw_deal_id}"}]}
        Log: "Backfilled CCW_Deal_ID with {ccw_did}"
    - If deal.CCW_Deal_ID exists AND matches parsed.header.ccw_deal_id: ok, proceed
    - If deal.CCW_Deal_ID exists AND DIFFERS from parsed.header.ccw_deal_id:
        STOP, prompt Chris: "Existing deal has DID X, this sub mod is for DID Y. Combined deal? Wrong deal? Override?"

STEP 3 - FETCH/PICK CONTACT
  If Deal.Contact_Name populated: use it.
  Else: ZohoCRM_getRelatedRecords parent=Accounts/{account_id} related=Contacts
    - If 1 contact: use it.
    - If >1: prompt Chris.

STEP 4 - DETERMINE PRICING MODE
  If parsed.source == "ccw_api":
    Use pricing_source=ccw_api_net, margin_percent=20, margin_mode=gross (default). Switch to markup only on explicit request.
  Else:
    Use XLS Discount Decision Tree above. If ambiguous, prompt.

STEP 5 - BUILD PAYLOADS
  Write config.json with deal_id, account_id, contact_id, address, pricing_source, margin/discount settings.
  Run: python3 scripts/build_quote_payloads.py /tmp/parsed.json /tmp/config.json > /tmp/payloads.json
  Check exit code:
    0 -> proceed (totals verified)
    2 -> unresolved SKU. Look up in Zoho, add to config.zoho_fallback_ids, retry.
    3 -> math error. STOP, do not POST.

STEP 6 - CONSOLIDATED VALIDATION TABLE
  Display one table (see format above). Ask Chris: "Proceed?"

STEP 7 - POST QUOTES (sequential, not parallel)
  ZohoCRM_createRecords module=Quotes body={ "data": [customer_quote_from_payloads] }
    -> capture customer_quote_id
  ZohoCRM_getRecord module=Quotes recordID=customer_quote_id
    -> capture for verify

  ZohoCRM_createRecords module=Quotes body={ "data": [op_quote_from_payloads] }
    -> capture op_quote_id
  ZohoCRM_getRecord module=Quotes recordID=op_quote_id
    -> capture for verify

STEP 8 - VERIFY
  Write actual.json with both fetched quote responses.
  Run: python3 scripts/verify_quotes.py /tmp/payloads.json /tmp/actual.json
  PASS -> proceed to step 9
  FAIL -> report diff to Chris, DO NOT create task, ask how to proceed

STEP 9 - CREATE TASK
  ZohoCRM_createRecords module=Tasks body={
    "data": [{
      "Subject": "Follow up - {Account} {SubID} Add-On",
      "What_Id": {"id": "{deal_id}"},
      "$se_module": "Deals",
      "Due_Date": "{today + 7 business days}",
      "Status": "Not Started",
      "Priority": "Normal",
      "Owner": {"id": "{owner_id}"},
      "Description": "Follow up on {SubID} add-on. Customer quote: ${customer_total}. CCW DID {ccw_did} expires {deal_expiration}."
    }]
  }

STEP 10 - REPORT
  Print summary table with:
    - Customer Quote URL
    - OP Quote URL
    - Follow-up Task URL
    - Deal URL
    - Customer total
    - Term
    - Any warnings from builder
```

## True Forward Workflow Step-by-Step (Fast Path C)

See `workflows/true_forward.md` for the full playbook. Quick reference:

```
1. READ TF REPORT (Drive or local upload)
2. PARSE: customer, EA ID, SubID, term, per-SKU lines (status: Fully Consumed/Overconsumed/Underconsumed)
3. LOOKUP ACCOUNT (no delinquency gate — Net_Terms = Cash always for EA TFs)
4. LOOKUP/CREATE DEAL (Lead_Source = Stratus Referal, Meraki_ISR = Stratus Sales)
5. LOOKUP CONTACT
6. LIVE ZOHO PRODUCTS SEARCH for all distinct SKUs (E3N-* not cached)
7. BUILD LINE GROUPS:
   - Charges: List = (cost / 0.80) / qty, Discount = 0
   - Credits: List = (credit / 0.80) / qty, Discount = 2 × List × Qty (drives net negative)
   - Unchanged: List = zoho_default, Discount = List × Qty (drives $0)
8. SHOW VALIDATION TABLE, confirm with Chris
9. CREATE DEAL + QUOTE
10. VERIFY Sub_Total within $0.10. Force Net_Terms = Cash if reverted.
11. UPDATE DEAL AMOUNT to Grand_Total
12. ADD DEAL NOTE + QUOTE NOTE + FOLLOW-UP TASK
13. REPORT with URLs and Stratus margin
```

## Required Fields Reference

### Deal — Sub Mod (Fast Path B)

| Field | Value |
|---|---|
| Deal_Name | `{Account} - {SubID} Add-On (CCW {DealID})` |
| Account_Name | from lookup |
| Contact_Name | from account or prompt |
| Lead_Source | `Stratus Referal` (default for sub mods) |
| Stage | `Proposal/Negotiation` |
| Closing_Date | `{deal_expiration}` |
| Amount | `{customer_total}` |
| **CCW_Deal_ID** | **`{ccw_did}` from parsed file (string field, REQUIRED)** |
| Cisco_Billing_Term | `Prepay` |
| Meraki_ISR | `{"id": "2570562000027286729"}` (Stratus Sales) |

### Deal — True Forward (Fast Path C, when creating new)

| Field | Value |
|---|---|
| Deal_Name | `{Account} - True Forward {Year} ({SubID})` |
| Account_Name | from lookup |
| Contact_Name | from account |
| Lead_Source | `Stratus Referal` |
| Stage | `Qualification` |
| Closing_Date | `today + 30 days` |
| Amount | `{grand_total_with_tax}` |
| Cisco_Billing_Term | `Prepaid Term` |
| Meraki_ISR | `{"id": "2570562000027286729"}` (Stratus Sales) |
| Owner | `{"id": "2570562000141711002"}` (Chris Graves) |

**CCW_Deal_ID rules (Sub Mod only):**
- Single sub mod → populate with `parsed.header.ccw_deal_id`
- Multiple sub mods combined into one deal → populate with the FIRST DID, list secondaries in Description
- Field is a string (NOT a number). Pass as `"84335446"` not `84335446`.
- For Fast Path A (existing deal): always check `CCW_Deal_ID` on the deal. If null, BACKFILL via `ZohoCRM_updateRecord`. If different from parsed DID, prompt Chris.
- TFs do NOT have a CCW_Deal_ID — leave that field null.

### Quote — Sub Mod

All handled by `build_quote_payloads.py`. Required fields are hardcoded. The model only provides the config.json values.

### Quote — True Forward

| Field | Value |
|---|---|
| Subject | `{Account} - True Forward {Year} ({SubID})` |
| Account_Name | `{"id": account_id}` |
| Deal_Name | `{"id": deal_id}` |
| Contact_Name | `{"id": contact_id}` |
| Owner | `{"id": "2570562000141711002"}` |
| Cisco_Billing_Term | `Prepaid Term` |
| **Net_Terms** | **`Cash`** (ALWAYS for EA TFs — no delinquency check needed) |
| Valid_Till | today + 30 days |
| Billing_Street/City/State/Code/Country | from account |
| Shipping_Country | `US` |
| Description | TF summary text |
| Quoted_Items | charges + credits + unchanged lines |

### Task

```
{
  "Subject": "Send TF quote - {Account} ({SubID})"  // for TFs
            OR "Follow up - {Account} {SubID} Add-On"  // for sub mods
  "What_Id": {"id": deal_id},
  "$se_module": "Deals",
  "Due_Date": today + 5-7 business days,
  "Status": "Not Started",
  "Priority": "High" (TF) or "Normal" (sub mod),
  "Owner": {"id": owner_id},
  "Description": context-specific
}
```

## Critical Field Names (exact spelling required)

```
Quoted_Items[].Product_Name.id      NOT Product.id
Quoted_Items[].Description          NOT Product_Description (saves as null)
Quoted_Items[].List_Price           decimal
Quoted_Items[].Discount             decimal DOLLAR AMOUNT (not %)
Task.$se_module                     "Deals" (literally "$se_module", dollar-prefixed)
Task.What_Id                        {"id": deal_id}
```

## Known IDs

```
Chris Graves User:    2570562000141711002
Stratus Sales (ISR):  2570562000027286729
Org ID:               org647122552

Parent SKUs (Sub Mod):
  MERAKI-SUB:         2570562000214328410
  CISCO-NETWORK-SUB:  2570562000292110371
  SECURE-ACCESS-SUB:  2570562000240080110
```

## Error Recovery Playbook

### Script error: "xlrd not installed"
Scripts auto-install on first run. If blocked, manually: `pip install xlrd --break-system-packages`

### Script error: "Parent SKU X not in cache"
Add to `config.json.zoho_fallback_ids` with ID from `ZohoCRM_searchRecords module=Products criteria=(Product_Code:equals:X)`. Retry.

### Script error: "Unresolved SKUs"
Same as above. Then flag the SKU for cache update (add to `data/sku_cache.json` and bump version).

### Script error: "Math error: customer != op total"
Indicates a bug in the builder. Do NOT POST. Inspect the raw parsed JSON and manually validate line-by-line. Report to Chris.

### TF error: "E3N-* SKU not found in Products"
The SKU may be a new variant. STOP. Prompt Chris: "{SKU} not in Zoho Products — needs to be created in CRM before quote can be built. Should I create it?" Do NOT proceed without resolution.

### TF error: "Net_Terms reverted to Net 15 after save"
Zoho's auto-fill workflow can override Net_Terms. After Quote create, re-fetch and check. If reverted, force Cash:
```
ZohoCRM_updateRecord module=Quotes recordID={quote_id}
  body={"data":[{"Net_Terms": "Cash"}]}
```

### Zoho error: "Can't add inactive product"
One of the resolved Zoho IDs points to `Product_Active=false`. Re-search Zoho for that SKU, may need to activate product or find alternate ID.

### Quote total mismatch after POST
Run `verify_quotes.py` (sub mod) or manually check Sub_Total against expected (TF). Most common cause: Zoho silently rounded a list price. Delete the wrong quote, fix the List_Price precision, re-POST.

### Taxable accounts (Tax_Type: Regular) show Grand_Total > expected
This is expected behavior. Zoho auto-applies sales tax based on billing state for taxable accounts (common for IL, CA, NY, IN, etc). Compare `Sub_Total` (pre-tax) rather than `Grand_Total`. The tax amount appears in `All_Taxes_Total` on the quote record. No action needed — the underlying pricing is correct.

## What Changed from v2.8

- **NEW: SOAP-based API client** — `scripts/pull_sub_mod_api.py` is a Python port of a
  Cisco-validated Ruby reference. Hits the real Manage Quote API endpoints
  (`apix.cisco.com/commerce/QUOTING/v1` SOAP/XML), parses OAGIS QuoteLine + CiscoLine
  blocks, and surfaces `ccw_net_addon_cost` per line.
- **NEW: In-place quote update path** — `scripts/submod_quote_pricing.py` patches an
  existing Zoho quote line-by-line by matching subform ids. Decimal precision with a
  penny-bump heuristic. Preserves line ids (avoids the subform-id-invalidation bug).
- **NEW: CCW net-change pricing mode** — both `submod_quote_pricing.py` and
  `build_quote_payloads.py` produce identical math; the former updates, the latter creates.
- **NEW: Default margin_mode = `gross`** — matches sales-team practice. `markup` mode
  remains available via `--margin-mode markup` or `"margin_mode": "markup"` in config.
- **NEW: Decimal arithmetic with ROUND_HALF_UP** in `build_quote_payloads.py`, replacing
  v2.8 floats.
- **Retained: XLS fallback** — `parse_sub_mod.py` path unchanged.
- **Retained: True Forward workflow** — no TF logic changed.

See CHANGELOG.md for per-version history.
