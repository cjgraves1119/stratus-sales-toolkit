# Zoho CRM Changelog

### v28 (Current)

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
