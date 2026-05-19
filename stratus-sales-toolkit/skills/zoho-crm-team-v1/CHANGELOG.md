# Zoho CRM Changelog

### team-v1 (2026-05-19, new branch — coexists with v35)

- **TEAM-DISTRIBUTABLE FORK OF v35**: Identical operational scope to v35; only difference is identity handling. Created so any Stratus rep (Tim, Jay, Lauren, etc.) can install via the stratus-sales-toolkit plugin and have records attributed to themselves instead of Chris Graves.
- **MANDATORY IDENTITY RESOLUTION (first-step section at top of SKILL.md)**: Before any Zoho write, the skill checks `memory/user_zoho_identity.md` for the caller's full name, work email, and Zoho user ID. If missing, prompts the user once, auto-looks-up the Zoho ID via `/users?type=ActiveUsers` if needed, confirms, then writes the memory file and indexes it in `memory/MEMORY.md`.
- **`/zoho-identity` OVERRIDE TRIGGER**: User can type `/zoho-identity`, "update my zoho identity", "change my zoho identity", or "reset zoho identity" to re-prompt and overwrite the saved identity file.
- **TEMPLATE VARIABLES THROUGHOUT**: All Chris-Graves-specific hardcodes replaced with `{{USER_ZOHO_ID}}`, `{{USER_FULL_NAME}}`, `{{USER_EMAIL}}` placeholders. The skill resolves these from the identity file at session start.
- **STRATUS SALES CATCH-ALL PRESERVED**: `Stratus Sales` user (id `2570562000027286729`) is the team-wide `Meraki_ISR` fallback for non-ISR-referral deals. Explicitly NOT replaced with `{{USER_ZOHO_ID}}` — added a "do NOT replace" callout in the identity-resolution block.
- **ALL v35 FEATURES RETAINED**: Embedded prices.json hot cache, auto velocity hub deal approval, mandatory follow-up task on every new deal, master quote workflow, send-quote-to-customer pipeline, gmail thread read pre-step, delinquency gate, CCW approval shortcut, margin update routing.

---

### v35 (Personal — Chris Graves, retained alongside)


- **EMBEDDED PRICES.JSON HOT CACHE**: Bundled `data/prices.json` (1,042 SKUs) provides both `zoho_product_id` and ecomm pricing in a single file read. Eliminates 2-3 API calls per quote (Products module search + WooProducts pricing lookup). Cache refreshed bi-weekly by `bot-price-refresh-v1-0` scheduled task
- **UNIFIED PRODUCT ID + PRICING RESOLUTION**: New `PRODUCT ID + PRICING LOOKUP` section replaces the old "LIVE BATCH ONLY, NO HOT CACHE" approach. Cache is primary (98.5% coverage), live API is fallback only for cache misses
- **COMBINED QUOTE CREATION STEP**: Workflow Steps 11 (SKU lookup) and 12 (ecomm discount) merged into a single unified step. Product IDs and pricing loaded together from cache before the validation checkpoint
- **PRICE SOURCE HIERARCHY UPDATED**: Embedded cache is now Priority 1 (zero API calls), WooProducts is Priority 2 (fallback only), list price is Priority 3 (flag for review)
- **VALIDATION CHECKPOINT ENHANCED**: Pre-creation table now shows cache hit rate for product IDs and pricing
- **CACHE MAINTENANCE**: `bot-price-refresh-v1-0` scheduled task syncs prices.json to this skill's `data/` directory after each bi-weekly refresh
- All v34 features retained

### v34

- **STRATUS PRICING DEFAULT**: All quotes now priced at Stratus ecomm rates by default — no longer "explicit request only." Primary source is WooProducts `Stratus_Price` field (live, authoritative, no rounding needed). Fallback to prices.json `price` field for SKUs not in WooProducts. Discounts applied inline at quote creation time (no separate update step)
- **WOOPRODUCTS BATCH LOOKUP**: OR-criteria batch search for all SKUs in a single call (max 10/call). Post-filters bundle records (`WooProduct_Code` contains `+`) and deduplicates. Confirmed via live testing that Zoho's `equals`, `word`, and `starts_with` operators all behave as contains matches on this field — post-filter is the only reliable approach
- **INLINE DISCOUNT AT CREATION**: `Discount` (dollar amount) and `Description` ("Stratus price $X/unit (Y% off list)") included directly in the CREATE payload. Eliminates the separate Phase B update call for new quotes
- **PHASE B SIMPLIFIED**: Send Quote Phase B now references STRATUS PRICING DEFAULT section instead of its own prices.json-only logic. Phase B is only needed to update pre-existing list-price quotes
- **1% ROUNDING REMOVED**: WooProducts `Stratus_Price` is the exact live price — no staleness buffer needed
- **"ONLY INCLUDE WHEN EXPLICITLY REQUESTED" UPDATED**: Removed Discount and Description from that table — they are now always applied
- All v33 features retained

### v33

- **AUTO VELOCITY HUB DEAL APPROVAL**: After `LIVE_CiscoQuote_Deal` successfully generates a CCW Deal Number (DID), Claude automatically submits it to Cisco's Velocity Hub for deal approval via Pipedream webhook (`https://eo44ez435h7vzp2.m.pipedream.net`). Non-blocking: if submission fails, workflow continues and user can retry manually
- **BOTH FLOWS COVERED**: Auto-submit integrated into both the standard Quote-to-PO flow and the Ecomm-to-PO flow
- **DID VALIDATION**: Only submits if CCW_Deal_Number matches `^[0-9]{8}$` (exactly 8 digits). Skips with warning if format is unexpected
- **UPDATED REP PROMPT**: Post-DID prompt now says "Deal ID generated and submitted for approval" instead of just "Deal ID generated"
- **2 NEW NEVER DO RULES**: Don't block workflow on Velocity Hub failure; don't submit without validating 8-digit format
- All v32 features retained

### v32

- **MANDATORY FOLLOW-UP TASK ON QUOTE CREATION**: Every new Deal created via standard quote workflow MUST have a follow-up task as the final step
- All v31 features retained

### v31

- **ENFORCED COMPLETE PAYLOAD TEMPLATES**: COMPLETE DEAL/QUOTE CREATION PAYLOAD templates mandatory for every create call
- **BILLING ADDRESS MANDATORY**: Street, City, 2-letter State, Code, Country required on every Quote
- **Valid_Till, Cisco_Billing_Term, Shipping_Country MANDATORY** on every Quote
- **Closing_Date MANDATORY** on every Deal
- All v30 features retained

### v30

- **HOT CACHE REMOVED**: Eliminated `hot-cache.json` entirely. All product ID lookups now use live batch Zoho Products search via `(Product_Code:equals:SKU1)OR(Product_Code:equals:SKU2)...` (max 10 per call). Eliminates stale ID issues that caused "inactive product" errors on MX67-SEC, MX85-SEC, and other frequently-updated license SKUs
- **MASTER QUOTE WORKFLOW**: For multi-variant quotes (customer wants 1Y + 3Y options), create a single Master Quote containing ALL SKUs across all terms, submit for DID via LIVE_CiscoQuote_Deal, then create separate term-specific quotes with the DID passed through. Master Quote naming: `{Account} - {Description} (Master)`. Avoids submitting multiple CCW deals for the same opportunity
- **DID PASS-THROUGH**: Term-specific quotes include `CCW_Deal_Number` in the create payload so all variants are linked to the same Cisco estimate
- All v29 features retained

### v29

- **SEND QUOTE TO CUSTOMER WORKFLOW**: Full end-to-end pipeline: Deal → Quote → Ecomm Pricing → CCW → PO → E-Sign → Email → CCW Approval → Follow-up Task. Single command to go from request to contract-in-customer-hands
- **ECOMM DISCOUNT PROMPT**: After creating a quote at list price, prompts whether to apply ecomm discounts. Uses stratus-quoting-bot prices.json with 1% rounding reduction: `floor(ecomm_price * 0.99)`
- **GMAIL THREAD READ MANDATORY**: When request references an email thread, sender, or subject, reading the full Gmail thread is now a mandatory Step 0 before any pre-creation validation. Extracts exact SKUs, quantities, terms, payment method, and contacts
- **LIVE_SENDTOESIGN FIX**: Must target Sales_Orders module (PO record ID), not Quotes module. Running on Quotes returns __NotFound. Added Sales_Orders search by Deal_Name to get PO ID
- **DELINQUENCY GATE**: After LIVE_ConvertQuoteToSO, checks Delinquency_Score. Non-green scores trigger Manager Approval Request that blocks PO creation. Auto-switches Net_Terms to "Cash" and re-runs conversion
- **1% ECOMM PRICE ROUNDING**: All ecomm prices from cache get 1% reduction via `math.floor(ecomm_price * 0.99)` to compensate for cache staleness vs live pricing
- **CCW APPROVAL SHORTCUT ENHANCEMENT**: Pass Deal ID in prompt message to skip Zoho page extraction. Navigate to Quote page first before executing. Native browser automation fallback documented
- **6 NEW CRITICAL RULES**: Rules 43-47 (LIVE_SendToEsign on Sales_Orders, Delinquency Gate, Ecomm 1% rounding, Gmail thread read, CCW shortcut Deal ID)
- **5 NEW NEVER DO RULES**: E-sign on Quotes, Net_Terms with non-green delinquency, raw ecomm prices, skip Gmail thread read
- **6 NEW ERROR RECOVERY ENTRIES**: LIVE_SendToEsign__NotFound, Delinquency blocks PO, Ecomm price off, CCW shortcut failures
- All v28 features retained

### v28

- **PRODUCT_NAME FIELD FIX**: Always use `Product_Name: {"id": "..."}` for line items, never `product: {"id": "..."}`. The `product` field triggers Zoho inventory active check and fails on products with negative stock quantities (even when Product_Active = true). `Product_Name` bypasses this check while correctly linking the product record. Applies to ALL quote/SO line item operations
- **DISCOUNT IS DOLLAR AMOUNT**: The `Discount` field on Quoted_Items accepts dollar amounts, not percentages. Formula: `Discount = (List_Price x Quantity) - Target_Sell_Price`. Example: List $201, target $138 -> `Discount: 63`
- **HOT CACHE PATH UPDATED**: References updated to `/mnt/skills/user/zoho-crm-v28/data/hot-cache.json`
- **2 NEW CRITICAL RULES**: Rules 41 (Product_Name not product) and 42 (Discount is dollar amount) added
- All v27 features retained

### v27

- **NEVER MANUALLY CLOSE WON**: Deals auto-close when completed PO (Sales_Order) is attached. Claude never sets Stage to Closed Won manually
- **WEBORDER CHECK**: When deal appears fulfilled but not Closed Won, search for weborder and route through weborder-to-deal-automation-v1-1 for proper association
- **SUCCESSOR AFTER EVERY ACTION**: All open/ongoing deals require follow-up task after any action. Only skip if engagement should genuinely end
- **GMAIL AS SOURCE OF TRUTH**: Always search Gmail for actual last contact before proposing actions on deal-linked tasks. Zoho Last_Activity_Time is supplementary only
- **PIPEDREAM/ZAPIER TOOL ID**: Embedded UUID and parameter name reference to prevent tool confusion
- **6 NEW CRITICAL RULES**: Never close won, Gmail before actions, successor after every action, Pipedream vs Zapier, weborder check (rules 36-40)
- **UPDATED COMPANION SKILLS**: References daily-task-engine-v1-3, zoho-crm-email-v3-5, fu30-followup-automation-v1-3
- All v26 features retained

### v26

- **PRE-CLOSE DEAL VALIDATION**: Fetch deal stage before closing any deal-linked task. Active deals require successor check
- **SUCCESSOR TASK ENFORCEMENT**: Active deals must have at least one open task. Create successor before closing if none exist
- **PICKLIST PROTECTION STRENGTHENED**: Explicit banned-value list with correct alternatives. "Closed Lost" -> "Closed (Lost)", "Referral" -> "Referal"
- **EVALUATION GATE INTEGRATION**: Task closure requires passing through type-specific evaluation gate from daily-task-engine-v1-2
- **BUSINESS DAY CALCULATOR**: Embedded Python function for weekend-skipping date math
- **5 NEW CRITICAL RULES**: Pre-close deal check, successor enforcement, evaluation gates, banned picklist values (rules 32-35)
- **UPDATED COMPANION SKILLS**: References daily-task-engine-v1-2, zoho-crm-email-v3-3, fu30-followup-automation-v1-2
- All v25 features retained

### v25

- **STAGE LOCK**: Never update Deal Stage mid-workflow. Only allowed change is closing (uses live-validated "Closed (Lost)" value only)
- **NO NEW STAGE OPTIONS**: Always run ZohoCRM_Get_Field live lookup before any stage change. Never hardcode or create new values
- **LEAD SOURCE DEFAULT**: Stratus Referal is the default for 99.9% of deals. No pre-creation prompt needed
- **MERAKI_ISR DEFAULT**: Stratus Sales by default. Only change if Cisco rep explicitly in prompt
- **PROCEED-FIRST WORKFLOW**: Create deal/quote immediately with defaults, then ask about Cisco rep post-creation
- **POST-CREATION REP PROMPT**: After every deal/quote creation, ask: "Is there a Cisco rep involved? I can update the record with their info."
- All v24 features retained

### v24

- **CCW INCENTIVE OVERHAUL**: Section rewritten with production-validated coordinate patterns from live submission (Deal 83551548)
- **JS-FIRST DEAL ID EXTRACTION**: `javascript_tool` query for CCW_Deal_Number before any screenshot or read_page
- **COORDINATE-BASED CCW SEARCH**: Search bar (330, 29), magnifying glass (408, 61). Enter key confirmed non-functional in CCW
- **RADIO BUTTON FIX**: Removed incorrect guidance to use form_input/refs for radio buttons. "No" radio now uses coordinate click (~148, 630) with screenshot confirmation
- **SUBMIT FALLBACK**: Added coordinate (530, 299) as fallback if "Submit Quote for Approval" misses on first click
- **PERFORMANCE SECTION UPDATED**: Clarified text/textarea = form_input + ref, radio buttons = coordinate clicks (required distinction)
- **EXPANDED ERROR RECOVERY**: 9-row error table with confirmed recovery patterns for all known CCW failure modes
- All v23 features retained

### v23

- **CRM TASK MANAGEMENT**: Full task lifecycle rules folded in from daily-task-engine orchestrator
- **ATOMIC TASK LIFECYCLE**: Send -> complete -> verify -> follow-up in guaranteed sequence
- **CASCADE PREVENTION**: Never batch Zoho + Zapier in same parallel block
- **ZOHO SEARCH GOTCHAS**: starts_with for Subject, no Due_Date sort, no word search
- **TRIAGE CATEGORIES**: AUTO_CLOSE, FU30_EMAIL, DEAL_FOLLOWUP, ISR_CHECKIN, QUOTE_ACTION, NEEDS_REVIEW
- **DATE SCOPE**: Daily review/close = today + past due only; FU30 = 7-day lookahead
- **FOLLOW-UP RULES**: 3 business days, weekend skip, conditional on email content
- **TRIGGER PHRASES**: Expanded description for better natural language matching
- All v22 features retained

### v22

- **ADMIN ACTIONS VIA API**: Admin_Action is a writable trigger field on Quotes. Set value = action name, wait 5s, verify __Done suffix. All 4 actions executable by Claude directly. NEVER defer to UI.
- All v21 features retained

### v21

- **HOT CACHE REMOVED**: Product IDs now resolved via live batched Zoho Products search instead of local cache
- **SHELL-FIRST QUOTE CREATION**: Deal and Quote shell created BEFORE SKU lookup; ensures a recoverable Zoho record exists if lookup fails
- **BATCH SKU SEARCH**: All SKUs in a single OR-criteria API call regardless of line item count
- **VARIANT FALLBACK**: Auto-retry with alternate suffix (-3Y vs -3YR) if initial SKU search returns empty
- **SKU PATCH STEP**: Line items added via Update call after shell confirmed created
- All v20 features retained

### v20

- **LIVE STAGE VALIDATION**: Deal Stage values verified via ZohoCRM_Get_Fields API before any create/update (replaces hardcoded list)
- **CCW INCENTIVE AUTO-SUBMIT**: Full workflow for submitting deal incentive justification in Cisco Commerce
- **CHROME EXTENSION INTEGRATION**: Documents submit-deal-incentive shortcut for automated CCW submissions
- **SILENT PICKLIST FIX**: Prevents Zoho from silently creating invalid dropdown options
- All v19 features retained

### v19

- **MANDATORY PICKLIST VALIDATION**: All Deal Stage and Lead_Source values must match exact valid options before create/update
- **AUTO-CORRECTION MAP**: Common typos auto-corrected
- **VALIDATION GATE**: Claude must verify picklist values against whitelist before any Zoho API call

### v18

- **CCW CSV GENERATION**: Auto-generate CCW import CSV with correct 8-column format
- **CLAUDE CHAT SUBJECT**: Note instructions updated to include searchable chat subject
- **QUOTE NOTE FORMAT**: Standardized with products list
- All v17 features retained

### v17

- **ECOMM-TO-PO WORKFLOW**: Full automation for converting ecomm quotes to POs
- **PRE-CONVERSION CHECKPOINT**: Mandatory validation before LIVE_ConvertQuoteToSO
- **HOT CACHE FALLBACK**: Auto-search Products module when "inactive product" error occurs
- **CANCEL PENDING PO**: Cancel pending PO before creating new one
- All v16 features retained

### v16 - v11

- Clone for variants, admin actions, hot cache restructure, required fields enforcement, address auto-lookup, Gmail thread integration
