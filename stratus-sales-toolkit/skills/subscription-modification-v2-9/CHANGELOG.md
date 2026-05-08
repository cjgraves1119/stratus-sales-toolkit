# Subscription Modification & True Forward Skill — Changelog

## v2.9.1 (2026-05-08) — Codex merge: SOAP-correct + in-place updates

Hardening pass after comparing v2.9 first cut against the Codex prototype
(`ccw_subscription_addon_quote.rb` + `submod_quote_pricing.py`). Codex's
prototype was production-correct in three places this skill was wrong.

### Fixed
- **Real Cisco API endpoints.** Previous v2.9 cut shipped fictional JSON paths
  (`api.cisco.com/commerce/QUOTE/v3/sync/...`). Real Manage Quote API is SOAP/XML
  at `apix.cisco.com/commerce/QUOTING/v1/{ListQuoteService,AcquireQuoteService}`.
  `pull_sub_mod_api.py` is now a Python port of the validated Ruby reference:
  OAGIS SOAP envelopes, XML response parsing, NameValue + CiscoLine extraction.
- **Decimal arithmetic with `ROUND_HALF_UP`** in `build_quote_payloads.py`
  (replaced floats). Penny-bump heuristic added so rounded `List_Price × Qty`
  always >= target sell amount before discount is subtracted.
- **Default `margin_mode = "gross"`** — matches Codex + sales-team practice for
  true-margin reporting. `markup` mode remains available.

### Added
- `scripts/submod_quote_pricing.py` (from Codex, with one cosmetic fix to
  quantity rendering — replaced `Decimal.normalize()` with a non-scientific
  helper). This is the **preferred Fast Path A path** when the Zoho deal
  already has a quote attached: it patches Quoted_Items in place and preserves
  subform line ids, dodging the subform-id-invalidation bug noted in the
  feedback memory.

### Changed
- `pull_sub_mod_api.py` output schema now includes `ccw_net_addon_cost` and a
  full `api.*` block per line so both `submod_quote_pricing.py` (update path)
  and `build_quote_payloads.py` (create path) can consume the same parsed JSON.
- SKILL.md: Fast Path A split into A-update (existing quote, preferred) and
  A-create (new quote from scratch). Scripts table reflects all four scripts.
  API endpoints documented inline.

---

## v2.9 (2026-05-08) — API-First Sub Mod

**Core goal:** When Chris has a CCW DID, pull quote economics directly from Cisco
instead of waiting on a downloaded XLS export. Bill add-on net change with a
configurable margin while showing the full subscription on the quote.

### New

1. **`scripts/pull_sub_mod_api.py`** — stdlib-only client for Cisco's Manage Quote
   API. OAuth2 client_credentials (id.cisco.com), then ListQuoteService → quoteId,
   then AcquireQuoteService → full quote with `QuantityChange`,
   `BillingAmountNetChange`, `ContractAmountNetChange`, `RemainingTerm`, and
   `BillingFrequency` per line. Output schema is a superset of `parse_sub_mod.py`
   so `build_quote_payloads.py` consumes either source unchanged.

2. **`pricing_source = "ccw_api_net"`** in `build_quote_payloads.py`. Add-on lines
   are billed at `cisco_net_change × (1 + margin)` (markup mode, default 20%) or
   `cisco_net_change / (1 - margin)` (gross mode). No-change lines display the
   full term list price with a 100% discount → $0 net. Customer and OP quotes
   are identical: full subscription transparency, only the delta is invoiced.

3. **Configurable margin** — `margin_percent` + `margin_mode` in config.json.
   Default is `20% markup`. `gross` mode mirrors true-forward math.

4. **Workflow Selection Decision** updated for the API-first path. If Chris
   provides a DID, use `pull_sub_mod_api.py`; if only an XLS, fall back to
   `parse_sub_mod.py`.

5. **Sample math anchored to verified DID `84410290`** (LIC-ACCSMGR-A: 35 qty,
   $933.92 add-on list, $542.79 Cisco net cost, $651.35 customer invoice at
   20% markup, $282.57 line discount). Built-in test reproduces these numbers.

### Retained from v2.8

- `scripts/parse_sub_mod.py` for XLS fallback (downloaded CCW exports).
- `scripts/verify_quotes.py` Sub_Total compare with $0.02 tolerance — works
  unchanged for both pricing modes.
- 300+ SKU embedded cache (`data/sku_cache.json`).
- True Forward Fast Path C and `workflows/true_forward.md`.
- Discount Decision Tree for the XLS fallback (Meraki 30%, EA 45%).
- Net_Terms = Cash always for EA TFs.
- All v2.7/v2.8 danger-zone callouts.

### Why This Update

XLS exports lag the CCW edit experience by minutes and cost a manual download
step. The API path collapses pull → parse → cost basis into a single 1-2s
script call, gives Stratus access to Cisco's authoritative `BillingAmountNetChange`
(no margin guesswork), and removes the largest source of "wait until I have the
xls" lag in the workflow. XLS path stays as a tested fallback for reps without
DID access.

---

## v2.8 (2026-04-29) — True Forward Workflow Added

(Retained verbatim from prior release.)

**Core goal:** Add a separate, dedicated workflow for Cisco True Forward reports
without disturbing the existing sub mod logic. TFs are mathematically and
structurally distinct from sub mods (post-discount net cost vs raw list, three
line groups vs one, no CCW DID, no parent SKU decision).

### New

1. **Fast Path C: True Forward.** Handles Cisco-generated TF reports (xlsx) for
   EA mid-term consumption variance. Pulls customer name, EA ID, SubID, term,
   and per-SKU lines (Fully Consumed / Overconsumed / Underconsumed) from the
   report.

2. **Per-line 20% true margin on Cisco net cost.** Each charge line:
   `customer_unit = (cisco_net_cost / 0.80) / qty`. Each credit line:
   `customer_unit_credit = (cisco_credit / 0.80) / qty`. Credits flow through to
   customer at the same margin (NOT absorbed by Stratus).

3. **Three-group quote line structure for full subscription transparency:**
   - Charges (positive list, no discount) for Overconsumed SKUs
   - Value Shift Credits (positive list + oversized discount = negative net) for
     Underconsumed SKUs
   - Unchanged EA Inventory (default unit price + 100% discount = $0 net) for
     Fully Consumed SKUs

4. **`workflows/true_forward.md`** — full TF playbook with worked example.

5. **Workflow Selection Decision** at top of SKILL.md to disambiguate TF vs sub
   mod based on filename pattern and Chris's wording.

6. **Net_Terms = Cash policy for EA TFs.**

7. **TF-specific validation table.**

8. **TF-specific danger zone callouts.**

9. **New error recovery entries.**

---

## v2.7 (2026-04-24) — Deterministic Scripts

**Core goal:** Make this skill work on weaker models by shifting math and parsing
off the model and onto scripts. Eliminate the trap that caused the
"Pricing Term in months = 1" math errors.

### Added

- `scripts/parse_sub_mod.py` — Deterministic xls parser.
- `scripts/build_quote_payloads.py` — Math pre-verified payload builder.
- `scripts/verify_quotes.py` — Post-creation verification.
- `data/sku_cache.json` — 300+ embedded SKUs.
- Attach-to-existing-deal fast path.
- Discount Decision Tree.

### Fixed

- "Pricing Term in months = 1" trap.
- Ext List double-multiplication.
- Same-SKU split rows.

---

## v2.6 (previous)

- Embedded SKU cache (~30 SKUs)
- Enforced parent SKU with term months in description
- Fixed "Description" field name
- Pre-validation of product active status
- Logging when falling back to Zoho search
- Deal validation, default Lead_Source = Stratus Referal
- Contact auto-assign if single contact on account
- Task $se_module enforcement

---

## v2.5

- Customer quote first workflow
- Consolidated OP items
- Dollar-based discounts
- Existing deal detection

## v2.4

- Address lookup integration
- Deal Notes on creation
- Required fields enforcement
