---
name: zoho-crm-v28
description: "zoho crm with product_name field fix for inactive inventory bypass, never-manually-close-won rule, weborder association logic, strengthened successor enforcement on all actions, gmail-as-source-of-truth for deal context, pipedream/zapier tool identification, and updated companion skill references. triggers: create quote, new deal, update deal, close task, task review, daily tasks, task clean up, help me complete todays tasks, close out my tasks, what tasks are due, review my tasks, submit to ccw, admin action, clone quote, cancel po. org id: org647122552."
---

# Zoho CRM v28 (Product_Name Fix + Never Close Won + Weborder Check + Gmail Source of Truth)

See CHANGELOG.md for what changed in each version.

## LIVE DEAL STAGE VALIDATION (CRITICAL - NEW IN V20)

### Why Live Validation?

Zoho CRM **silently accepts** invalid picklist values and creates new dropdown options instead of rejecting them. This means:
- Typos like "Closed Lost" (vs "Closed (Lost)") create duplicate stage options
- Reporting breaks because deals are split across invalid stages
- No error is returned, so the problem is invisible until data is audited

### Validation Workflow (REPLACES hardcoded Stage list for create/update)

**Before ANY Deal create or update that includes Stage:**

```
1. CALL ZohoCRM_Get_Fields for Deals module, field "Stage"
2. EXTRACT pick_list_values from response
3. BUILD valid_stages list from actual_value fields
4. CHECK if requested Stage value is in valid_stages
   - If exact match → proceed
   - If in auto-correction map → correct and proceed
   - If neither → STOP and show user the valid options from the live list
```

### API Call for Live Stage Check
```
ZohoCRM_Get_Field:
  path_variables: { field: "Stage" }
  query_params: { module: "Deals" }
```

### When to Use Live vs Cached
| Scenario | Method |
|----------|--------|
| Creating a Deal | LIVE check (always) |
| Updating Deal Stage | LIVE check (always) |
| Lead_Source validation | Use cached list (stable values) |
| Reason validation | Use cached list (stable values) |

**Note:** Lead_Source and Reason values are stable and controlled by Stratus admins, so the hardcoded lists remain valid for those fields. Only Stage requires live validation because Zoho auto-creates invalid values silently.

## NEVER MANUALLY CLOSE WON (CRITICAL - NEW IN V27)

### Rule

**Claude must NEVER manually set a Deal's Stage to "Closed Won".** Deals auto-close to Closed Won when a completed PO (Sales_Order) is properly attached. This is a Zoho workflow automation, not a manual step.

### When a Deal Appears Fulfilled But Is Not Closed Won

If a deal looks like it shipped or was fulfilled (customer received equipment, license activated, etc.) but the Stage is still active:

```
1. DO NOT manually change Stage to Closed Won
2. CHECK: Does this deal have a PO (Sales_Order) attached?
   - Search Sales_Orders: (Deal_Name:equals:{Deal_Id}) or check Related Lists
3. IF PO exists and is completed → Deal should auto-close. If it hasn't, flag for manual review
4. IF NO PO exists → Check if order was placed as a weborder:
   a. Search Gmail for weborder confirmation (customer email, order number)
   b. Search Sales_Orders for weborder number if known
   c. If weborder found → Use weborder-to-deal-automation-v1-1 skill to:
      - Associate the weborder PO to the existing deal
      - Update Account_Name if mismatched
      - This association triggers the auto-close workflow
   d. If no weborder found → Ask user for clarification
```

### Weborder Association Workflow

When routing to weborder-to-deal-automation-v1-1:
- The skill handles PO creation, deal linking, and account matching
- Do NOT change the deal Stage manually before or after
- Do NOT change Lead_Source unless instructed
- The weborder association itself triggers the Closed Won automation

## GMAIL AS SOURCE OF TRUTH (CRITICAL - NEW IN V27)

### Rule

**Never rely solely on Zoho Last_Activity_Time for evaluating deal status or customer engagement.** Always search Gmail for actual last contact before proposing actions.

### When to Search Gmail

```
BEFORE proposing any action on a deal-linked task:
1. Search Gmail: from:{contact_email} OR to:{contact_email}
2. Check for most recent conversation date and content
3. Use Gmail findings to inform proposed action:
   - Recent contact (< 7 days): Note in proposal, may not need follow-up
   - Stale contact (7-14 days): Recommend follow-up
   - Very stale (14+ days): Flag for urgent attention
4. Include Gmail context in batch approval table notes
```

### Why This Matters

Zoho Last_Activity_Time can be misleading (updates on internal changes, not just customer contact). Gmail provides the real picture of when you last actually communicated with the customer.

## PRE-CLOSE DEAL VALIDATION (CRITICAL - NEW IN V26)

### Purpose

Before closing ANY task that is linked to a Deal (via What_Id), validate the deal's current state. This prevents blind task closure that orphans active deals without follow-up coverage.

### Validation Workflow

```
BEFORE closing a task where What_Id links to a Deal:

1. FETCH DEAL: ZohoCRM_Get_Record(module="Deals", recordID={What_Id})
   Fields: id,Deal_Name,Stage,Amount,Account_Name,Last_Activity_Time

2. SEARCH GMAIL for last actual contact with customer (see GMAIL AS SOURCE OF TRUTH)

3. EVALUATE DEAL STATE:
   - Closed Won → OK to close task (deal complete)
   - Closed (Lost) → OK to close task (deal dead)
   - Active stage (Qualification, Proposal/Negotiation, Verbal Commit/Invoicing)
     → MUST run successor task check before closing (see below)
   - Deal appears fulfilled but NOT Closed Won → Check for weborder (see NEVER MANUALLY CLOSE WON)

4. IF ACTIVE DEAL: Check for successor task
   Search Tasks: (What_Id:equals:{Deal_Id}) and (Status:not_equals:Completed)
                  and (id:not_equals:{current_task_id})
   - IF other open tasks exist → OK to close (successor exists)
   - IF no other open tasks → MUST create successor before closing
```

### Successor Task Creation (STRENGTHENED IN V27)

**ALL open/ongoing deals require a follow-up task after any action.** This applies to every task closure, email send, or quote creation on an active deal. Only skip successor creation when engagement should genuinely end (deal Closed Lost, purely informational FU30 with no ask, customer explicitly declined further contact).

When no other open tasks exist on an active deal, create a successor BEFORE closing the current task:

```json
{
  "data": [{
    "Subject": "Follow Up: {Contact_Name} - {Company}",
    "Due_Date": "{today + 3 business days}",
    "Status": "Not Started",
    "Priority": "Normal",
    "Owner": {"id": "2570562000141711002"},
    "What_Id": "{Deal_Id}",
    "$se_module": "Deals",
    "Who_Id": "{Contact_Id}",
    "Description": "Successor task created during task cleanup on {today}. Original task: {original_subject}. Deal is active in {Stage} stage."
  }]
}
```

### Business Day Calculator

```python
from datetime import datetime, timedelta

def add_business_days(start_date, days):
    """Add business days to a date, skipping weekends."""
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday=0, Friday=4
            added += 1
    return current
```

## PICKLIST PROTECTION (STRENGTHENED IN V26)

### Banned Values (NEVER Use These)

| Banned Value | Correct Value | Why |
|-------------|---------------|-----|
| Closed Lost | Closed (Lost) | Missing parentheses creates duplicate stage |
| Referral | Referal | Double R creates duplicate lead source |
| Closed-Won | Closed Won | Hyphen creates duplicate stage |
| closed won | Closed Won | Case mismatch creates duplicate |

### Protection Rules

1. **LIVE validation required** for ALL Deal Stage writes (create and update)
2. **Cached validation acceptable** for Lead_Source and Reason (stable values)
3. **If value not in picklist**: STOP and show user the valid options
4. **NEVER create new picklist values**: Zoho silently accepts invalid values
5. **Auto-correction map**: Only use for known typos (e.g., "Closed Lost" → "Closed (Lost)")

### Evaluation Gate Integration

Task closure now requires passing through the per-task-type evaluation gate defined in daily-task-engine-v1-8. The gate determines the correct action for each task type BEFORE any status change.

```
TASK CLOSURE SEQUENCE:
1. Identify task type from Subject pattern
2. Run evaluation gate (per daily-task-engine-v1-8)
3. If gate says "close": run pre-close deal validation
4. If active deal: check/create successor task
5. Close task
6. Verify closure via re-fetch
```

## CCW INCENTIVE AUTO-SUBMIT (UPDATED IN V24 — PRODUCTION-VALIDATED)

### Overview

Automates the Cisco Commerce (CCW) incentive justification submission directly from a Zoho CRM Purchase Order page. Can be triggered via:
1. **Cowork / Chrome Extension shortcut**: `submit-deal-incentive` (fully automated)
2. **Manual Claude request**: "Submit this deal to CCW", "submit to ccw", "ccw incentive", or "run deal incentive"

### Fixed Inputs (Never Ask User)
| Field | Value |
|-------|-------|
| Business Problem | Cloud Networking |
| Postal Code | 60606 |
| RFQ/RFP/RFI or E-Rate 470 | No |
| Deal ID Source | CCW_Deal_Number field on current Zoho CRM Purchase Order page |

These are hard-coded. Do not ask the user for any of these values.

### Step 1 — Get Tab Context + Extract Deal ID

**Get tabs first:**
```
Use tabs_context_mcp to get current tab IDs.
Store the tabId for all subsequent steps.
If multiple tabs, identify the one showing Zoho CRM (crm.zoho.com).
```

**JS-first extraction (fastest — skip read_page if this succeeds):**
```javascript
document.querySelector('[data-fieldname="CCW_Deal_Number"] .field-value')?.innerText?.trim()
|| document.querySelector('.zcrmfield[data-fieldname="CCW_Deal_Number"] span')?.innerText?.trim()
```

If JS extraction fails, use `find` tool with query "CCW Deal Number" to locate field visually.

Store the result as DEAL_ID. If not found, take a screenshot and report to user.

**Performance note:** JS extraction is instant. Skip read_page entirely if JS succeeds.

### Step 2 — Navigate to Cisco Commerce

```
Navigate to https://apps.cisco.com/Commerce/home on the active tab (or open a new tab if needed).
Wait for page load — CCW home page header should be visible before proceeding.
```

Do NOT use find/read_page until the page is confirmed loaded.

### Step 3 — Search for the Deal

**CRITICAL: Coordinate clicks only for CCW search. Do NOT use form_input or refs here.**

```
1. Click the search bar at coordinate (330, 29) — do NOT use form_input
2. Type the DEAL_ID (e.g. "83551548")
3. Click the magnifying glass icon at coordinate (408, 61)
   IMPORTANT: Do NOT press Enter — Enter does NOT trigger search in CCW. Must click the icon.
4. Wait 1 second for results.
```

If search bar text doesn't land: click (330, 29), Ctrl+A to clear, retype DEAL_ID, then click (408, 61).

### Step 4 — Open the Deal

```
After search results load:
1. Use find tool: query = "Deal ID [DEAL_ID]" or the deal number link in results
2. Click the Deal ID link to open the Deal Summary page
3. Wait for Deal Summary to load — confirm by looking for the Incentive section (shown in red if action required)
```

### Step 5 — Navigate to Incentive Justification

```
On the Deal Summary page:
1. Use find tool: query = "Incentive" to locate the incentive icon/button (typically highlighted red)
2. Click it to navigate to the Incentive tab
3. URL should change to a path containing "#/justification/"
4. Wait for the Justification form to load
```

Do not take a screenshot here unless the page fails to load. Proceed directly to Step 6.

### Step 6 — Fill Justification Form

Fill all 3 fields before clicking any navigation button.

**FIELD 1 — Business Problem (textarea):**
```
Use find: query = "Business Problem" or "business problem textarea"
Use form_input with the found ref to set value: "Cloud Networking"
form_input is reliable for text/textarea fields.
```

**FIELD 2 — Postal Code (text input):**
```
Use find: query = "Postal Code" or "postal code input"
Use form_input with the found ref to set value: "60606"
```

**FIELD 3 — RFQ/RFP/RFI Radio Button (CRITICAL — DO NOT USE form_input OR ref):**
```
Radio buttons in CCW do NOT respond reliably to form_input or element ref clicks.
REQUIRED METHOD:
1. Use find: query = "No" radio button near RFQ/RFP/RFI
2. Take a screenshot to visually confirm position of the "No" radio button
3. Click "No" using coordinate click based on its visual position
   Typical coordinate: (148, 630) — verify via screenshot if layout differs
```

| Field | Value | Method |
|-------|-------|--------|
| Business Problem textarea | Cloud Networking | form_input with ref |
| Postal Code input | 60606 | form_input with ref |
| RFQ/RFP/RFI "No" radio | No | **Coordinate click only** (~148, 630) |

### Step 7 — Proceed to Review

```
1. Use find: query = "Proceed to Review" button
2. Click it using the found ref or coordinate
3. Wait for navigation — URL should change to "#/review/"
4. Confirm review page shows "Deal is ready for submission." before proceeding
```

"Proceed to Review" saves the form and advances in one action. No separate Save button needed.

### Step 8 — Submit for Approval

```
1. Use find: query = "Submit Quote for Approval" button
2. Click it. If the first click doesn't advance the page:
   - Scroll down slightly
   - Click again at coordinate (530, 299) — button may shift after initial render
3. Wait 2-3 seconds for submission processing
4. Confirm URL changes to "#/confirmation/"
5. Take a screenshot to capture confirmation details
6. Report to user: confirmation message, Next Approver, Next Partner Action, and date
```

**Typical confirmation:**
- Message: "Thank you for submitting your Quote."
- Next Approver: Pps-amer-qualification
- Next Partner Action: Wait for Approval

### Performance Optimizations
- **JS-first extraction**: Use `javascript_tool` for CCW_Deal_Number before any screenshot or read_page
- **Coordinate clicks for CCW search**: (330, 29) for search bar, (408, 61) for magnifying glass — more reliable than refs in CCW
- **Skip intermediate screenshots**: Only screenshot to confirm radio button position and at final confirmation
- **Fill all fields before advancing**: Complete all 3 fields before "Proceed to Review" — reduces page transitions
- **Text = form_input + ref, Radio = coordinate click**: form_input works for text/textarea; radio buttons in CCW REQUIRE coordinate clicks
- **Minimal waits**: 1 second after search, 2-3 seconds after Submit; no other explicit waits needed

### Manual Trigger (Without Browser Extension)

If user asks Claude directly to submit a deal to CCW:
1. User should be on the Zoho PO page with CCW Deal ID visible
2. Follow Steps 1-8 above — same workflow applies
3. Extract CCW Deal ID via JS or `find` before navigating to CCW

### Error Recovery
| Error | Recovery |
|-------|----------|
| Search bar text doesn't land | Click (330, 29), Ctrl+A to clear, retype DEAL_ID |
| Magnifying glass not in accessibility tree | Click coordinate (408, 61) directly |
| Deal ID not found on Zoho page | Ask user to confirm they're on a PO page; check CCW_Deal_Number field |
| CCW search returns no results | Verify DEAL_ID from Zoho CRM; re-extract and retry |
| "No" radio button doesn't register via ref | Take screenshot, confirm position, click by coordinate (~148, 630) |
| "Proceed to Review" doesn't advance | Scroll up, use find again, then retry with coordinates |
| "Submit" button missed on first click | Scroll down, use find again, then click coordinate (530, 299) |
| Incentive section not visible on Deal Summary | Scroll down; look for red-highlighted section |
| Confirmation page doesn't load | Wait 5 seconds, take screenshot, report status to user |

## PICKLIST VALIDATION (CRITICAL - ALWAYS ENFORCE)

### DEAL STAGE RULES (v27 — STRICT)

**NEVER update Deal Stage during create or update unless the user EXPLICITLY says to close the deal.**
**NEVER manually set a Deal to Closed Won. Deals auto-close when a completed PO is attached.**

| Scenario | Stage Behavior |
|----------|----------------|
| New deal creation | Default to `Qualification`. Set once. Done. |
| Quote created / updated | Do NOT change Stage. Leave as-is. |
| User says "close this deal" / "mark as lost" | Use live API to get exact picklist value, use ONLY the "Closed (Lost)" option |
| Deal appears fulfilled / shipped | Do NOT manually close won. Check for weborder, use weborder-to-deal-automation skill |
| User says "mark as closed won" | Explain that deals auto-close when PO is attached. Offer to check for weborder instead |
| Any other mid-workflow update | Do NOT touch Stage unless user specifically requests it |

**Closing a Deal as Lost (ONLY allowed manual stage change besides creation):**
1. Run `ZohoCRM_Get_Field` for "Stage" on Deals module
2. From the live picklist, identify the option that represents Closed/Lost
3. Use that exact string value, no variations, no new options created
4. Do NOT use "Closed Lost", "Closed-Lost", "closed lost" — get the exact live value
5. If the live picklist doesn't have a matching option, STOP and show user the options

**Closing a Deal as Won (NEVER manual, ALWAYS automatic):**
1. Deals close won automatically when a completed PO (Sales_Order) is linked
2. If deal should be Closed Won but isn't, check for missing weborder association
3. Use weborder-to-deal-automation-v1-1 to properly link PO → triggers auto-close
4. NEVER use ZohoCRM_Update_Record to set Stage = "Closed Won"

### Valid Lead Sources (USE EXACTLY AS SHOWN)

| Lead_Source Value | When to Use |
|-------------------|-------------|
| `Stratus Referal` | **DEFAULT for 99.9% of deals** — use unless Cisco rep is clearly involved |
| `Meraki ISR Referal` | Cisco rep explicitly named or clearly implied in the prompt |
| `Meraki ADR Referal` | ADR referral explicitly mentioned |
| `VDC` | Virtual Data Center lead explicitly mentioned |
| `Website` | Website inquiry explicitly mentioned |
| `-None-` | FORBIDDEN — never use, it is a required field |

**Lead Source Decision Logic (v25):**
```
Is a Cisco/Meraki rep explicitly named or clearly referenced in the prompt?
├── YES → Lead_Source = "Meraki ISR Referal", Meraki_ISR = [look up rep], Reason = "Meraki ISR recommended"
└── NO (default) → Lead_Source = "Stratus Referal", Meraki_ISR = "Stratus Sales" (ID: 2570562000027286729)

THEN after deal/quote created:
→ ALWAYS ask: "Is there a Cisco rep involved with this deal? I can update the record with their info."
```

**This means:** Don't wait for Lead Source confirmation before proceeding. Default to Stratus Referal, build the deal, then ask about a rep afterward. Only interrupt pre-creation if a rep is obviously in the prompt (e.g., "Joey referred this" or "Cisco ISR sent this over").

### Auto-Correction Map

Before any create/update, check input against this map and auto-correct:

| Invalid Input | Corrected To |
|---------------|--------------|
| `closed lost` | → run live picklist lookup, use exact "Closed (Lost)" value |
| `Closed Lost` | → run live picklist lookup, use exact "Closed (Lost)" value |
| `quoting` | `Qualification` |
| `quote sent` | `Proposal` |
| `Quote Sent to Customer` | `Proposal` |
| `verbal commit` | `Pending` |
| `Verbal Commit/Invoicing` | `Pending` |
| `Proposal/Negotiation` | `Negotiation` |
| `referral` | `Stratus Referal` |
| `Referral` | `Stratus Referal` |
| `ISR Referral` | `Meraki ISR Referal` |
| `ADR Referral` | `Meraki ADR Referal` |

### Validation Workflow (MANDATORY)

**Before ANY Deal create or update:**

```
1. STAGE: Only set during initial creation (Qualification default). 
   For updates, only change if user explicitly said to close.
   If closing → live picklist lookup → use "Closed (Lost)" exact value only.

2. LEAD_SOURCE: Default Stratus Referal unless Cisco rep clearly involved.
   Do not prompt for Lead_Source before creation — proceed with default.

3. DISPLAY validation in pre-creation checkpoint:
   | Field | Resolved Value | Basis |
   |-------|---------------|-------|
   | Stage | Qualification | Default |
   | Lead_Source | Stratus Referal | Default (no rep mentioned) |
   | Meraki_ISR | Stratus Sales | Matches Lead_Source default |
```

### NEVER DO (Picklist Rules)

- **NEVER** update Stage mid-workflow without explicit user instruction to close
- **NEVER** create new picklist options (Zoho silently accepts them but breaks reporting)
- **NEVER** use Lead_Source = "-None-"
- **NEVER** block deal creation to ask about Lead_Source when the default (Stratus Referal) applies
- **NEVER** use Stage variations like "Closed-Lost", "closed_lost", "CLOSED LOST", "Closed Lost" — always get live value for closures

### Error Recovery

If Zoho returns an error about invalid picklist value:
1. Check the value against the valid list
2. Check the auto-correction map
3. For Stage: run ZohoCRM_Get_Field live lookup and show user the actual options
4. If no match, prompt user: "The stage '{value}' isn't a valid Zoho option. Here are the current options: [live list]"

## What's New in v18
- **CCW CSV GENERATION**: Auto-generate CCW import CSV with correct 8-column format for hardware and subscription quotes
- **CLAUDE CHAT SUBJECT**: Note includes searchable chat subject (e.g., "RAE Products quote for MX75, CW9172, and MV84X")
- **QUOTE NOTE FORMAT**: Standardized note format with products list for easy reference
- All v17 features retained (ecomm-to-po, pre-conversion checkpoint, hot cache fallback)

## What's New in v17
- **ECOMM-TO-PO WORKFLOW**: Automate converting ecomm quotes to POs for customers needing net terms or formal invoicing
- **PRE-CONVERSION CHECKPOINT**: Mandatory validation before LIVE_ConvertQuoteToSO (Net_Terms CANNOT change after conversion)
- **HOT CACHE FALLBACK**: When product creation fails with "inactive product", auto-search Products module by Product_Code
- **CANCEL PENDING PO FIRST**: When deal has existing PO and new one needed, cancel pending PO before creating new quote
- All v16 features retained (clone quotes, auto-pricing, admin actions)

## CLONE QUOTES FOR VARIANTS (NEW)

### When to Use Clone
- Creating a modified version of an existing quote
- Changing quantities or line items on a similar quote
- Testing different configurations for same customer

### Clone Workflow
```
1. Fetch original quote to get structure
2. Call ZohoCRM_Clone_Record with:
   - Override Subject (new name)
   - Override Quoted_Items (new line items)
   - DO NOT include Tax fields (causes validation errors)
3. Zoho auto-populates: prices, taxes, totals
4. Add Claude Reference note to cloned quote
```

### Clone Payload Example
```json
{
  "data": [{
    "Subject": "Customer - Quote Variant v2",
    "Quoted_Items": [
      {"Quantity": 5, "Discount": 1500.00, "Description": "67% discount applied", "Product_Name": {"id": "product_zoho_id"}},
      {"Quantity": 10, "Product_Name": {"id": "another_product_id"}}
    ]
  }]
}
```

### Clone Rules
| DO | DON'T |
|----|-------|
| Override Subject | Include Tax field |
| Override Quoted_Items | Include List_Price (auto from product) |
| Include Discount if applying | Include Unit_Price |
| Include Description | Include Net_Total, Total |

## ADMIN ACTION WORKFLOW (Quote-to-PO)

### Overview
Admin Actions are Zoho CRM automations that interact with Cisco CCW and distribution systems. They are triggered by writing the action name to the `Admin_Action` field on the Quote record via `ZohoCRM_Update_Record`. **Claude executes these directly via API. Never tell the user to click a button or do it manually.**

### HOW TO TRIGGER ANY ADMIN ACTION (API Method)

**Step 1: Set the Admin_Action field**
```json
ZohoCRM_Update_Record
Module: Quotes
RecordID: {quote_id}
Body: {"data": [{"id": "{quote_id}", "Admin_Action": "LIVE_CiscoQuote_Deal"}]}
```

**Step 2: Wait for processing**
- Wait 5 seconds, then re-fetch the quote record
- Check `Admin_Action` field: when it shows `{ACTION_NAME}__Done`, it completed successfully

**Step 3: Verify results**
| Action Triggered | Confirm By Checking |
|---|---|
| LIVE_CiscoQuote_Deal | `CCW_Deal_Number` populated, `Cisco_Estimate_Status` = "Success.VALID" |
| LIVE_GetQuoteData | `Vendor_Lines` related list populated with disti pricing |
| LIVE_ConvertQuoteToSO | New Sales_Orders record linked to Quote |
| LIVE_SendToEsign | Quote Stage updates, customer receives ZohoSign email |

**If still blank after 5s:** Wait another 5s and re-fetch once more before reporting an error.

### NEVER DO
- Tell the user to click Admin Action buttons in the UI
- Say "I can't trigger Admin Actions via API"
- Say "you'll need to do this manually in Zoho"
- Leave Admin Actions unexecuted when the user asks to run them

### Admin Action Sequence (Typical Flow)

| Step | Admin Action | Purpose | When to Use |
|------|-------------|---------|-------------|
| 1 | `LIVE_CiscoQuote_Deal` | Submit quote to Cisco CCW | After quote created, need Deal ID for discount approvals |
| 2 | `LIVE_GetQuoteData` | Retrieve approved disti pricing from Cisco | After DID approved, to get cost data for margin calc |
| 3 | `LIVE_ConvertQuoteToSO` | Convert quote to Purchase Order | After pricing finalized, ready to order |
| 4 | `LIVE_SendToEsign` | Send PO to customer via ZohoSign | After PO created, need customer signature |

### Step 1: LIVE_CiscoQuote_Deal (Submit to CCW)

**Trigger:** Quote ready for Cisco pricing approval
**Result:** Generates CCW Deal ID (DID), triggers discount approval workflow
**Status Check:** 
- `CCW_Deal_Number` field populated with DID
- `Cisco_Quote_Status` field updates to Approved/Pending

**After Completion:**
- If Meraki_ISR = "Stratus Sales", prompt: "Deal ID generated. Want me to look up the Cisco rep from the approval email?"

### Step 2: LIVE_GetQuoteData (Get Disti Pricing)

**Trigger:** CCW Deal ID approved, need cost data
**Result:** Populates `Vendor_Lines` related list with disti pricing
**Use for:** Margin calculations, applying discount to hit target margin

**Check Vendor_Lines:**
```
Module: Vendor_Lines
Criteria: (Quote.id:equals:{quote_id})
Fields: Name,Product_Code,Quantity,List_Price,Disti_Price,Disti_Price_Total
```

### Step 3: LIVE_ConvertQuoteToSO (Create Purchase Order)

**Trigger:** Pricing finalized, ready to place order
**Result:** Creates PO record linked to Quote
**Note:** Run on the Quote record

**⚠️ CRITICAL: PRE-CONVERSION CHECKPOINT (MANDATORY)**

Before running LIVE_ConvertQuoteToSO, display this validation:

```
PRE-CONVERSION VALIDATION (Net_Terms CANNOT change after conversion):
| Field | Value | Status |
|-------|-------|--------|
| Net_Terms | Net 30 | ⚠ FINAL - verify before proceeding |
| Contact for e-sign | Matt Estep | ✓ |
| Tax Exempt | No | ✓ |
| Grand Total | $6,267.59 | ✓ |
```

**Rules:**
- Net_Terms must be set on Quote BEFORE conversion
- Once PO is created, Net_Terms on the contract cannot be changed
- If customer requests specific terms (Net 30, Net 15), update Quote first

### Step 4: LIVE_SendToEsign (Customer Signature)

**Trigger:** PO created, need customer signature
**Result:** Sends PO via ZohoSign to customer contact
**Note:** Run on the most recent PO for the account

### Admin Action Workflow Summary

```
TYPICAL QUOTE-TO-PO FLOW:

1. Create Quote in Zoho (this skill)
2. Run LIVE_CiscoQuote_Deal → Gets Deal ID, submits for approval
3. Wait for Cisco approval (check email or CCW portal)
4. Run LIVE_GetQuoteData → Pulls disti pricing into Vendor_Lines
5. Apply margin (use margin-update workflow if needed)
6. Run LIVE_ConvertQuoteToSO → Creates PO from Quote
7. Run LIVE_SendToEsign → Sends PO for customer signature
8. Customer signs → Order placed with distribution
```

## ECOMM-TO-PO WORKFLOW (NEW IN V17)

### When to Use
Customer needs a formal Purchase Order instead of ecomm checkout, typically because:
- They require Net 30/Net 15 payment terms
- Their billing process requires a formal invoice
- They need a signed contract for their records

### Workflow
When converting ecomm pricing to a PO, margins are already validated by the ecomm system. The Deal ID (DID) is still required, but you don't need to wait for cost data before proceeding.

```
ECOMM-TO-PO FLOW:
1. Match Quote line items exactly to ecomm cart prices (apply same discounts)
2. Set Net_Terms on Quote BEFORE conversion (customer's requested terms)
3. Run LIVE_CiscoQuote_Deal → Get Deal ID (REQUIRED)
4. Run LIVE_GetQuoteData → Pull disti pricing (OPTIONAL - empty results OK)
5. Run LIVE_ConvertQuoteToSO → Create PO
6. Run LIVE_SendToEsign → Send contract to customer
```

**Key Points:**
- DID is still REQUIRED (LIVE_CiscoQuote_Deal must run)
- LIVE_GetQuoteData can be run but empty/incomplete cost data is OK (ecomm margins pre-validated)
- Can proceed to PO conversion immediately after DID is generated
- Ensure Net_Terms is correct before Step 5 (cannot change after)

## CANCEL PENDING PO BEFORE NEW QUOTE (NEW IN V17)

### When a Deal Has an Existing PO

If a deal already has a Sales Order (PO) and a new one needs to be sent:

1. **Cancel the pending PO first** - Update Status to "Cancelled" on the existing Sales Order
2. **Create new Quote** - Build fresh quote with correct pricing/terms
3. **Convert and send** - Follow normal PO workflow

**Why:** Multiple active POs on the same deal causes confusion and potential duplicate orders.

```
REPLACE PO WORKFLOW:
1. Search Sales_Orders for existing PO on deal
2. If Status = "Pending" or "Not Proceed" → Update Status to "Cancelled"
3. Create new Quote with correct specs
4. Run Admin Actions as normal
```

## HOT CACHE FALLBACK (UPDATED IN V28)

### When Product Creation Fails

If quote creation fails with error: `"can't add inactive product in the inventory"`

**Root Cause:** Zoho's `product: {"id": "..."}` field triggers an inventory active check. Products with negative stock (Qty_in_Stock < 0) fail this check even when `Product_Active = true`.

**Fix (v28): Always use `Product_Name` field, never `product` field**
```json
// CORRECT - bypasses inventory check
{"Quoted_Items": [{"Product_Name": {"id": "2570562000205715303"}, "Quantity": 1}]}

// WRONG - triggers inventory check, fails on negative stock
{"Quoted_Items": [{"product": {"id": "2570562000205715303"}, "Quantity": 1}]}
```

**If error still occurs after using Product_Name:**
1. Extract the Product_Code from the failed SKU
2. Search Products module for active product with same code:
   ```
   Module: Products
   Search: word = "{product_code}"
   Fields: id,Product_Name,Product_Code,Product_Active
   Filter: Product_Active = true
   ```
3. Use the active product ID and retry with Product_Name field
4. Flag hot-cache.json for update (stale ID detected)

**Common Stale SKUs:** License SKUs get replaced when Cisco updates pricing. Hardware SKUs are usually stable.

## CISCO REP LOOKUP (Post-DID)

### When to Prompt

After `LIVE_CiscoQuote_Deal` completes (DID generated):
- If `Meraki_ISR` = "Stratus Sales" (ID: 2570562000027286729)
- AND `CCW_Deal_Number` is now populated

**Prompt:**
> "Deal ID {DID} generated. Want me to look up the Cisco rep from the approval email and update the deal?"

### Rep Lookup Method 1: DID Approval Email (Primary)

**Best method when DID exists.** Cisco reps are CC'd on deal approval emails.

**Process:**
1. Search Gmail for DID approval email:
   ```
   search_gmail_messages with q = "{DID}"
   ```
2. Read the thread to get full email headers
3. Extract email addresses from To/CC fields
4. Match against cisco-rep-locator skill cache
5. If match found, update both Deal and Quote `Meraki_ISR` field

**Example:**
```
Gmail search: "83071521"
Found: eweichel@cisco.com, jberline@cisco.com
Match: jberline@cisco.com → Joey Berliner (ID: 2570562000275341406)
Update: Meraki_ISR = Joey Berliner on Deal and Quote
```

### Rep Lookup Method 2: Customer Email Thread (Secondary)

**Use when:** No DID exists yet, or DID email search returns no matches.

**Process:**
1. Search Gmail for customer/account email threads:
   ```
   search_gmail_messages with q = "from:{customer_email}" OR "to:{customer_email}"
   ```
2. Look for Cisco rep emails in CC or thread participants
3. Evaluate context: Did rep introduce the deal, or did customer reach out first?
4. If rep introduced → Lead_Source should be "Meraki ISR Referal"
5. If customer reached out first → Keep Lead_Source as is, but can still assign rep

**Context Evaluation:**
- Rep forwarded lead to Chris → Lead_Source = "Meraki ISR Referal", assign rep
- Customer emailed Chris, rep joined later → Keep original Lead_Source, optionally assign rep
- No rep involvement found → Keep Stratus Sales

### Rep Lookup Decision Tree

```
DID Generated?
├── YES → Search Gmail for DID
│   ├── Found Cisco rep emails → Match against cisco-rep-locator
│   │   ├── Match found → Update Meraki_ISR (prompt first)
│   │   └── No match → Keep Stratus Sales
│   └── No rep emails found → Try customer thread search
│
└── NO → Search customer email threads
    ├── Found rep who introduced deal → Update Lead_Source + Meraki_ISR
    ├── Found rep who joined later → Optionally assign (prompt)
    └── No rep found → Keep Stratus Sales
```

### Important: Always Prompt Before Updating

**Never auto-update Lead_Source or Meraki_ISR.** Always prompt:
- "Found Joey Berliner on the DID approval email. Update Meraki_ISR from Stratus Sales to Joey Berliner?"
- "Found Mike Smith introduced this deal. Update Lead_Source to 'Meraki ISR Referal' and assign Mike Smith?"

## CLAUDE THREAD URL IN QUOTE NOTES

### When Creating Any Quote

After quote is successfully created, add a Note to the Quote record with the Claude conversation reference.

**⚠️ IMPORTANT: Claude does NOT have programmatic access to the current chat ID.**

Include BOTH the **Chat Subject** (always) and the **URL** (when user provides it).

### Note Format (REQUIRED)
```
Note_Title: "Quote Created via Claude"
Note_Content: 
"Quote created via Claude:
Chat: {Chat Subject Title}
URL: {https://claude.ai/chat/uuid OR [pending]}

Products:
- {qty}x {SKU}
- {qty}x {SKU}
..."
```

**Chat Subject Format:** Use the conversation topic/title. This appears in Claude's sidebar and search.
- Pattern: `{Account} quote for {products}`
- Example: `RAE Products quote for MX75, CW9172, and MV84X`

**URL:** Include if user provides the chat URL from their browser. Otherwise use `[pending]`.

**Example Note Content (with URL):**
```
Quote created via Claude:
Chat: RAE Products quote for MX75, CW9172, and MV84X
URL: https://claude.ai/chat/caf187c3-7bf1-4430-9834-b77cacf9cfc9

Products:
- 1x MX75-HW
- 2x CW9172I-RTG
- 6x MV84X
```

**Example Note Content (without URL):**
```
Quote created via Claude:
Chat: RAE Products quote for MX75, CW9172, and MV84X
URL: [pending]

Products:
- 1x MX75-HW
- 2x CW9172I-RTG
- 6x MV84X
```

### API Call Example
```json
{
  "data": [{
    "Note_Title": "Quote Created via Claude",
    "Note_Content": "Quote created via Claude:\nChat: RAE Products quote for MX75, CW9172, and MV84X\nURL: https://claude.ai/chat/caf187c3-7bf1-4430-9834-b77cacf9cfc9\n\nProducts:\n- 1x MX75-HW\n- 2x CW9172I-RTG\n- 6x MV84X",
    "Parent_Id": {
      "id": "{quote_id}",
      "module": {"api_name": "Quotes"}
    }
  }]
}
```

### Chat Subject Guidelines
| Quote Type | Chat Subject Pattern |
|------------|---------------------|
| Hardware quote | `{Account} quote for {product list}` |
| Subscription mod | `{Account} subscription modification` |
| Renewal | `{Account} license renewal` |
| Multiple products | `{Account} quote for {main product}, {other products}` |

### DO NOT USE
- `https://claude.ai/chat/current` - This is NOT a valid URL
- `https://claude.ai/chat/current-conversation` - This is NOT a valid URL
- Fake UUIDs or placeholders in the URL field (use `[pending]` instead)

**Purpose:** Easy traceability back to the conversation where quote was created. Chat Subject is searchable in Claude's sidebar. URL provides direct link when available.

## PRODUCT ID LOOKUP (SIMPLIFIED)

**Key Insight:** Only the Product ID is needed. Zoho auto-populates List_Price, Unit_Price from the product record. Never lookup or include prices unless explicitly requested.

### Step 1: Query Hot Cache via Python
```bash
python3 -c "import json; cache=json.load(open('/mnt/skills/user/zoho-crm-v28/data/hot-cache.json')); print(cache.get('SKU-NAME', 'NOT FOUND'))"

# Example: MR36-HW lookup
python3 -c "import json; cache=json.load(open('/mnt/skills/user/zoho-crm-v28/data/hot-cache.json')); print(cache.get('MR36-HW'))"
# Returns: 2570562000028753805

# Multiple SKUs
python3 -c "import json; cache=json.load(open('/mnt/skills/user/zoho-crm-v28/data/hot-cache.json')); skus=['MR36-HW','LIC-ENT-3YR']; [print(f'{s}: {cache.get(s)}') for s in skus]"
```

### What to Lookup
| Lookup | Skip |
|--------|------|
| Product ID (Zoho ID) | List_Price |
| Product_Code (for validation) | Unit_Price |
| | Net_Total |
| | Tax |

**Hot Cache Contains (182 SKUs):**
- Parent SKUs: CISCO-NETWORK-SUB, SECURE-ACCESS-SUB, DUO-SUB
- Access Points: MR (Wi-Fi 6), CW (Wi-Fi 6E -MR suffix), CW (Wi-Fi 7 -RTG suffix)
- AP Licenses: LIC-ENT-{1,3,5}YR
- Switches: MS130-HW, MS150 (no suffix), C9200L-M, C9300-M, C9300X-M, C9300L-M
- Switch Licenses: LIC-MS130-*, LIC-MS150-*, LIC-C9200L-*, LIC-C9300-*
- Security: MX-HW, LIC-MX*-SEC-*
- Teleworker: Z4-HW, Z4C-HW, LIC-Z4-ENT-*
- Cellular: MG41-HW, MG41E-HW, MG52-HW, MG52E-HW, LIC-MG41-ENT-*
- Sensors: MT10-MT40-HW, LIC-MT-*
- Cameras: MV2/MV12N/MV13/MV22X/MV33/MV63/MV93-HW, LIC-MV-*
- Secure Access: SA-SIA-*, SA-SPA-*, SA-DNS-*, SA-INSIGHTS
- Subscription: LIC-MR-E, LIC-CW-E, LIC-MX-S/M/L-E, LIC-MV-E, LIC-MT-E

### Step 2: If Not in Hot Cache → Query Unified Product Catalog
Reference the latest `unified-product-catalog-v*` skill (check /mnt/skills/user/ for current version).

```bash
# Find latest unified catalog version
ls -d /mnt/skills/user/unified-product-catalog-v* | sort -V | tail -1

# Hardware lookup (replace {CATALOG_PATH} with result above)
jq '.hardware.{FAMILY}.models["{SKU}"].zoho_id' {CATALOG_PATH}/data/products.json

# License lookup (co-term with term)
jq '.co_term_licenses["{BASE}"].terms["{TERM}"].zoho_id' {CATALOG_PATH}/data/licenses.json
```

### Step 3: EOL Product Check
If product not found in either cache:
```bash
jq '.eol_products.{FAMILY}["{MODEL}"]' {CATALOG_PATH}/data/upgrade-paths.json
```
If EOL: Ask if renewal (use original license) or new deployment (recommend replacement).

## OPTIMIZED QUOTE CREATION (v16)

**Key Insight:** Zoho auto-populates ALL pricing and tax fields. Only provide Product_Name.id and Quantity. Never include List_Price, Unit_Price, Tax, Net_Total, or Total unless explicitly requested.

### Quoted_Items Minimal Payload
```json
{
  "Quoted_Items": [
    {"Quantity": 10, "Product_Name": {"id": "2570562000297110189"}},
    {"Quantity": 10, "Product_Name": {"id": "2570562000001098895"}}
  ]
}
```

### With Discount Applied (v28: Discount = Dollar Amount)
```json
{
  "Quoted_Items": [
    {"Quantity": 5, "Discount": 7574.98, "Description": "67.7% discount applied", "Product_Name": {"id": "2570562000034080533"}},
    {"Quantity": 1, "Discount": 1856.78, "Description": "59.7% discount applied", "Product_Name": {"id": "2570562000348083785"}}
  ]
}
```

**v28 CRITICAL**: `Discount` is a **dollar amount**, not a percentage. Formula: `Discount = (List_Price × Quantity) - Target_Sell_Price`
Example: List $201, target $138, Qty 1 → `Discount: 63`

Zoho will automatically fill in:
- List_Price (from product record)
- Unit_Price (from product record)
- Tax (based on tax settings)
- Net_Total (calculated)
- Total (calculated)

### ALWAYS Skip These Fields
| Field | Reason |
|-------|--------|
| List_Price | Auto from product record |
| Unit_Price | Auto from product record |
| Tax | Auto-calculated, causes clone errors if included |
| Net_Total | Auto-calculated |
| Total | Auto-calculated |
| Line_Tax | Auto-calculated |

### Only Include When EXPLICITLY Requested
| Field | When to Include |
|-------|-----------------|
| List_Price | User says "override list price" or "custom pricing" |
| Tax | User says "modify tax" or "tax exempt" |
| Discount | User wants discount applied (calculate $ amount) |
| Description | User wants discount % shown on line item |

## REQUIRED FIELDS (MUST ENFORCE)

### Deal Required Fields
| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| Deal_Name | YES | {Account} - {Description} | Auto-generate |
| Account_Name | YES | - | Must lookup/create first |
| Lead_Source | YES | **Stratus Referal** | Default unless Cisco rep explicitly involved |
| Stage | YES | Qualification | Set once at creation. Do NOT update unless user says to close. |
| Closing_Date | YES | Today + 30 days | Calculate dynamically |
| Reason | CONDITIONAL | Meraki ISR recommended | Required ONLY when Lead_Source = "Meraki ISR Referal" |
| Meraki_ISR | CONDITIONAL | **Stratus Sales** (ID: 2570562000027286729) | Stratus Sales by default; only change if ISR referral |

### Quote Required Fields
| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| Subject | YES | {Account} - {Description} | Auto-generate |
| Deal_Name | YES | - | Must exist or create first |
| Account_Name | YES | - | Must lookup/create first |
| Contact_Name | YES | - | Lookup from Account contacts (auto-assign if only one) |
| Valid_Till | YES | Today + 30 days | Calculate dynamically |
| Cisco_Billing_Term | YES | "Prepaid Term" | Always default to Prepaid Term |
| Billing_Street | YES | From Account | Copy from Account or lookup |
| Billing_City | YES | From Account | Copy from Account or lookup |
| Billing_State | YES | From Account | Copy from Account or lookup |
| Billing_Code | YES | From Account | Copy from Account or lookup |
| Billing_Country | YES | "US" | Default to US if not specified |
| Shipping_Country | YES | "US" | Mirror Billing_Country, default to US |

## ADDRESS LOOKUP SEQUENCE

When Account is missing billing address:

1. **Check Account in Zoho** - Fields: id,Account_Name,Billing_Street,Billing_City,Billing_State,Billing_Code,Billing_Country
2. **If Screenshot/Email Referenced** → Search Gmail for thread, check signature for address
3. **Web Search** - `"{Company Name} headquarters address"` or `"{email domain} company headquarters"`
4. **Note Address Source** - Always inform user where address was sourced
5. **Offer Account Update** - If Account had no address and we found one, offer to update record

## GMAIL THREAD INTEGRATION

When to use: User shares screenshot of email, references "this email", or mentions customer request without full context.

Process:
1. Extract identifiers (sender, subject, date, unique phrases)
2. `search_gmail_messages` with q = "from:{sender} {keywords}"
3. `read_gmail_thread` with found thread_id
4. Extract: request details, products, timeline, address from signature
5. Store Gmail thread link for Deal Note

## DEAL NOTES (NEW DEALS ONLY)

### Note Format
```
Source: {Email from sender@domain.com (MM/DD/YY) | Phone call | Website inquiry | ISR referral from Rep Name}
Request: {Brief description of products/services requested, quantities, terms}
Context: {Customer's stated need, competitive situation, timeline, any special requirements}
Address Source: {Account record | Email signature | Web search (HQ) | User provided}
Gmail Thread: {link if available}
```

### Note Creation API
```json
{
  "Note_Title": "Deal Summary - {Deal_Name}",
  "Note_Content": "{formatted note content}",
  "Parent_Id": {"id": "{deal_id}", "module": {"api_name": "Deals"}}
}
```

## Pre-Creation Validation (MANDATORY)

Before ANY record creation, display validation table:
```
PRE-CREATION VALIDATION:
| Field | Value | Status |
|-------|-------|--------|
| Deal_Name | Bison Equities - Secure Access | ✓ |
| Lead_Source | Meraki ISR Referal | ✓ |
| Reason | Meraki ISR recommended | ✓ |
| Meraki_ISR | [Pending - need rep name] | ⚠ PROMPT |
| Address | 123 Main St, Chicago IL | ✓ (via web search) |
```

**If ANY field shows ⚠ PROMPT, ask user before proceeding.**

## Lead Source Conditional Logic

```
IF Lead_Source = "Meraki ISR Referal":
    → Reason = "Meraki ISR recommended" (auto-set)
    → Meraki_ISR = REQUIRED (prompt for Cisco rep name, use cisco-rep-locator skill)
    
IF Lead_Source = "Meraki ADR Referal":
    → Meraki_ADR = REQUIRED (prompt for ADR name)
    
IF Lead_Source = "Cisco ISR":
    → Meraki_ISR = REQUIRED (prompt for Cisco rep name)

IF Lead_Source = "Stratus Referal", "VDC", or "Website":
    → Meraki_ISR = "Stratus Sales" (ID: 2570562000027286729)
    → After DID generated, PROMPT for rep lookup
```

## Valid Lead Source Options (NEVER CREATE NEW)

- `-None-`
- `Meraki ISR Referal` (note: one R in "Referal")
- `Meraki ADR Referal`
- `VDC`
- `Stratus Referal`
- `Website`
- `Cisco ISR`

## Valid Reason Options (NEVER CREATE NEW)

- `-None-`
- `Does not have reseller`
- `Needs new reseller`
- `Needs competitive quote`
- `Needs faster response`
- `Needs a specialist`
- `MSP Consultant needs reseller`
- `Meraki ISR recommended`

## Workflow Router

| User Request Pattern | Load Module |
|---------------------|-------------|
| "Create quote for...", "quote for X" | `workflows/quote-creation.md` |
| "Update margin to...", "apply X% margin" | `workflows/margin-update.md` |
| "Create deal for...", "new deal" | `workflows/deal-creation.md` |
| "Subscription quote...", "convert to subscription" | `workflows/subscription.md` |
| "Secure Access", "SA-SIA", "SA-SPA", "SA-DNS" | `workflows/subscription.md` |
| Error occurred, validation failed | `references/error-solutions.md` |

## HANDOFF TO DEDICATED SKILLS

### Subscription Modification Files → USE subscription-modification-v2-4+

**When user uploads Cisco subscription files or says trigger phrases, STOP and use the dedicated skill instead.**

| Trigger | Action |
|---------|--------|
| Cisco subscription quote file uploaded (.xls/.xlsx) | → **USE subscription-modification-v2-4+** |
| TD Synnex CPO file uploaded | → **USE subscription-modification-v2-4+** |
| "sub mod", "sub add-on", "subscription modification" | → **USE subscription-modification-v2-4+** |
| "true forward", "TF quote" | → **USE subscription-modification-v2-4+** |
| "CPO quote", "process this subscription" | → **USE subscription-modification-v2-4+** |

## CCW CSV GENERATION (NEW IN V18)

### When to Generate CCW CSV
- **ONLY when user explicitly requests it** — e.g., "generate CCW CSV", "make the import file", "CCW import"
- Do NOT auto-generate after quote creation
- Do NOT generate proactively or as a default step

### CSV Column Headers (REQUIRED - 8 columns)
```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
```

### Co-Term Hardware/License CSV (Term columns BLANK)
For traditional co-term quotes (hardware + LIC-ENT, LIC-MX*-SEC, etc.), leave term columns empty:

```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
MX75-HW,1,,,,,,
CW9172I-RTG,2,,,,,,
MV84X,6,,,,,,
```

**Rules for Co-Term:**
- Columns 3-8 are empty (just commas)
- No parent SKU needed
- Hardware SKUs use full format (MX75-HW, CW9172I-RTG, etc.)

### Subscription License CSV (Term columns POPULATED)
For subscription quotes (LIC-MR-E, LIC-MX-*-E, etc.), include term information:

```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
CISCO-NETWORK-SUB,1,,36,12,Prepaid Term,2026-01-30,
LIC-MR-E,36,,36,12,Prepaid Term,2026-01-30,
LIC-MS-100-M-E,15,,36,12,Prepaid Term,2026-01-30,
LIC-MX-M-E,2,,36,12,Prepaid Term,2026-01-30,
```

**Rules for Subscription:**
- Parent SKU FIRST (CISCO-NETWORK-SUB, SECURE-ACCESS-SUB, etc.)
- Initial Term: 36 months default (3 year minimum for new)
- Auto Renew: 12 months default
- Billing Model: "Prepaid Term"
- Start Date: Current date (YYYY-MM-DD format)

### Parent SKU Mapping
| License Pattern | Parent SKU |
|-----------------|------------|
| LIC-MR-*, LIC-MX-*, LIC-MS-*, LIC-CW-*, LIC-MV-E, LIC-MT-E | CISCO-NETWORK-SUB |
| SA-SIA-*, SA-SPA-*, SA-DNS-* | SECURE-ACCESS-SUB |
| UMB-* | UMB-SEC-SUB |
| ETD-* | ETD-SEC-SUB |

### Mixed Co-Term + Subscription CSV
When quote has both types, co-term items have blank term fields, subscription items have populated fields:

```csv
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
LIC-ENT-3YR,36,,,,,,
LIC-MX250-SEC-3YR,1,,,,,,
CISCO-NETWORK-SUB,1,,36,12,Prepaid Term,2026-01-30,
LIC-MR-E,36,,36,12,Prepaid Term,2026-01-30,
```

### Filename Format
`CCW_Import_{Quote_Number}_{Account_Name_Sanitized}.csv`

Example: `CCW_Import_2570562000379811039_RAE_Products.csv`

### CSV Generation Workflow
```
1. DETECT license type (co-term vs subscription)
2. IF subscription → add parent SKU as first line
3. FORMAT each line item with correct columns
4. GENERATE CSV file with 8-column header
5. SAVE with proper filename
6. PRESENT file for download
```

## CRM TASK MANAGEMENT (NEW IN V23)

### Task Search

```
ZohoCRM_Search_Records
Module: Tasks
criteria: (Status:equals:Not Started)and(Owner:equals:2570562000141711002)
fields: id,Subject,Due_Date,What_Id,Who_Id,Status,Priority,Description
per_page: 200
```

**Pagination:** If `info.more_records` = true, fetch next page until all tasks retrieved.

### Zoho Search Gotchas (Production-Learned)

| Issue | Fix |
|-------|-----|
| `contains` invalid for Subject field | Use `starts_with` instead |
| Sort by `Due_Date` not supported | Only id, Created_Time, Modified_Time are valid sort fields. Sort client-side after retrieval |
| `Who_Id` returns no results for task owner | Use `Owner` field for task owner queries |
| `word` search returns irrelevant results | Use criteria-based search, not word search |
| Zoho silently accepts invalid picklist values | Always validate against whitelist before create/update |

### Date Scope Enforcement (CRITICAL)

**Task review and close operations NEVER include future-dated tasks.** Only tasks due today or past due are in scope.

```python
# Client-side filtering (MANDATORY after task pull)
today = date.today()

# /DailyTasks and /CloseTasks scope: today + past due ONLY
actionable = [t for t in tasks if t['Due_Date'] and t['Due_Date'] <= today]

# /FU30s scope: FU30 tasks get a 7-day lookahead (proactive outreach)
fu30_scope = [t for t in tasks if 'FU30' in t['Subject'] and t['Due_Date'] <= today + 7]

# DISCARD: Any task with Due_Date > today is excluded from daily review and close operations
```

| Scope | Date Rule |
|-------|-----------|
| Daily task review | Due_Date <= today (strictly enforced) |
| Task close/cleanup | Due_Date <= today (strictly enforced) |
| FU30 follow-ups | Due_Date <= today + 7 days (lookahead) |
| NEVER | Include future-dated tasks in daily review or close |

### Task Triage Categories

Categorize each task by subject pattern matching and deal stage lookup:

| Category | Pattern Match | Additional Check |
|----------|--------------|-----------------|
| `AUTO_CLOSE` | Subject contains "PO Signed", "Contract Signed", "Order Placed" | Deal Stage = "Closed Won" or "Closed Lost" |
| `FU30_EMAIL` | Subject starts with "FU30" or "30 Day" | — |
| `DEAL_FOLLOWUP` | What_Id links to Deal in active stage | Gmail thread exists for contact |
| `ISR_CHECKIN` | Subject contains "EOQ", "ISR Check", "Rep Follow" | — |
| `QUOTE_ACTION` | Subject contains "Quote", "Approval", "eComm" | — |
| `NEEDS_REVIEW` | No pattern match | Present for manual categorization |

### Atomic Task Lifecycle (CRITICAL - SEQUENTIAL ONLY)

After an email is sent for a task, execute these steps in guaranteed sequence. **Never parallelize these steps.**

```
Step 1: SEND EMAIL (via appropriate send path)
  ↓
Step 2: COMPLETE TASK
  ZohoCRM_Update_Record → Module: Tasks, Status: "Completed"
  ↓
Step 3: VERIFY TASK COMPLETION (MANDATORY)
  ZohoCRM_Get_Record → Module: Tasks, fields: id,Subject,Status,Modified_Time
  Confirm Status = "Completed". If not, retry once.
  ↓
Step 4: CREATE FOLLOW-UP TASK (conditional - see rules below)
  ZohoCRM_Create_Records → Module: Tasks
```

**All 4 steps are atomic. Never skip step 3 (verify). Never batch steps across tasks.**

### Follow-Up Task Creation Rules

**Create a follow-up when the email:**
- Asked for next steps or a decision
- Requested pricing review or approval
- Asked customer to "let me know" or "send over" something
- Was a first outreach (no prior reply from customer)

**Skip follow-up when the email:**
- Was purely informational (FU30 check-in with no ask)
- Was a thank-you or confirmation only
- Customer already confirmed next steps in prior thread

**Follow-up task payload:**
```json
{
  "data": [{
    "Subject": "Follow up - {Original Task Context}",
    "Due_Date": "{today + 3 business days}",
    "Status": "Not Started",
    "Owner": {"id": "2570562000141711002"},
    "What_Id": "{deal_id}",
    "Who_Id": "{contact_id}",
    "$se_module": "Deals",
    "Description": "Follow up on email sent {today}: {brief email summary}"
  }]
}
```

**Business day calculation:** Skip Saturday and Sunday. If due date lands on weekend, push to Monday.

### Cascade Prevention (CRITICAL)

**Never batch Zoho CRM and Zapier MCP calls in the same parallel block.** If one MCP provider errors, all sibling calls in the same parallel block fail.

```
CORRECT:
  Batch 1 (parallel): All Zoho task updates
  Batch 2 (sequential): Zapier email sends

INCORRECT:
  Single batch: Zoho update + Zapier send together (cascade risk)
```

This applies to any mixed-provider parallel calls, not just Zoho + Zapier.

### Auto-Close Verification

A task is auto-closable when:
```
IF deal.Stage IN ["Closed Won", "Closed Lost"]
   AND task.Subject matches closing pattern ("PO Signed", "Contract Signed", "Order Placed")
   → Category = AUTO_CLOSE (present for user approval before closing)
```

**Always present auto-closable tasks for user approval.** Never auto-close without confirmation.

After closing, always verify via re-fetch (`ZohoCRM_Get_Record` with Status check).

### Task-Related Minimal Field Sets

**Task fetch:** `id,Subject,Due_Date,What_Id,Who_Id,Status,Priority,Description`
**Task verify:** `id,Subject,Status,Modified_Time`

## Critical Rules (Always Apply)

1. **QUERY HOT CACHE VIA JQ** - Don't load entire cache; query specific SKUs via jq
2. **VALIDATE REQUIRED FIELDS** - Check all required fields before creating any record
3. **PROMPT IF UNKNOWN** - Never leave required fields blank; ask user
4. **LOOKUP ADDRESS** - Use Gmail/web search sequence if Account missing address
5. **CREATE DEAL NOTE** - Add summary note on new deal creation
6. **CREATE QUOTE NOTE** - Add Claude thread URL to Quote Notes (with products list)
7. **NEVER CREATE DROPDOWN OPTIONS** - Use only existing values; creating new options breaks workflows
8. **NEVER fetch all fields** - Always specify `fields` parameter with only needed fields
9. **ALL Quotes REQUIRE a Deal** - Never create Quote without Deal
10. **Task is REQUIRED** - Create follow-up task on every new deal (`$se_module: "Deals"`)
11. **Generate URLs after creation** - Format: `https://crm.zoho.com/crm/org647122552/tab/{MODULE}/{ID}`
12. **2-LETTER COUNTRY CODES** - Use "US" not "United States", "CA" not "Canada"
13. **Valid_Till = Today + 30 days** - Calculate dynamically, never hardcode
14. **CCW CSV** - Generate ONLY if user explicitly requests it
15. **Contact_Name REQUIRED** - Every Quote must have Contact_Name; if Account has only one contact, auto-assign
16. **Cisco_Billing_Term = "Prepaid Term"** - Always default to "Prepaid Term" on quotes
17. **Shipping_Country = "US"** - Always populate Shipping_Country, default to "US"
18. **PROMPT BEFORE REP UPDATE** - Never auto-update Lead_Source or Meraki_ISR; always ask first
19. **NET_TERMS BEFORE PO CONVERSION** - Set Net_Terms on Quote BEFORE running LIVE_ConvertQuoteToSO; cannot change after
20. **CANCEL PENDING PO FIRST** - If deal has existing PO and new one needed, cancel pending PO before creating new quote
21. **HOT CACHE FALLBACK** - If "inactive product" error, search Products module for active product by Product_Code
22. **CLAUDE CHAT SUBJECT** - Include searchable chat subject in notes: "Chat: {Account} quote for {products}"
23. **QUOTE NOTE FORMAT** - Include products list in note (- Qty x SKU format)
24. **ATOMIC TASK LIFECYCLE** - Send email → complete task → verify → create follow-up. Always sequential, never parallel
25. **VERIFY TASK CLOSURE** - Always re-fetch task after updating Status to confirm completion
26. **CASCADE PREVENTION** - Never batch Zoho and Zapier MCP calls in the same parallel block
27. **DATE SCOPE** - Daily task review and close use Due_Date <= today only. FU30 gets 7-day lookahead. Never include future tasks in daily review
28. **FOLLOW-UP 3 BUSINESS DAYS** - Default follow-up task due date is 3 business days out, skip weekends
29. **TASK SEARCH: NO CONTAINS** - Use `starts_with` for Subject field searches, not `contains`
30. **TASK SEARCH: NO DUE_DATE SORT** - Sort tasks client-side after retrieval; Zoho only supports id, Created_Time, Modified_Time
31. **APPROVAL BEFORE CLOSE** - Present auto-closable tasks for user approval before closing. Never auto-close silently
32. **PRE-CLOSE DEAL CHECK** - Before closing any deal-linked task, fetch the deal and check its stage. Active deals require successor task enforcement
33. **SUCCESSOR TASK ENFORCEMENT** - Never close a task on an active deal without confirming or creating a successor open task
34. **EVALUATION GATE REQUIRED** - Every task must pass its type-specific evaluation gate (per daily-task-engine-v1-8) before any status change
35. **BANNED PICKLIST VALUES** - "Closed Lost" (no parens), "Referral" (double R), "Closed-Won" (hyphen) are banned. Live validate before writing
36. **NEVER MANUALLY CLOSE WON** - Deals auto-close when completed PO is attached. If deal appears fulfilled but not Closed Won, check for weborder and use weborder-to-deal-automation skill
37. **GMAIL BEFORE ACTIONS** - Always search Gmail for actual last contact with customer before proposing actions on deal-linked tasks. Zoho Last_Activity_Time is not reliable for customer engagement
38. **SUCCESSOR AFTER EVERY ACTION** - ALL open/ongoing deals require a follow-up task after any action. Only skip if engagement should genuinely end (Closed Lost, informational FU30 with no ask)
39. **PIPEDREAM vs ZAPIER** - Pipedream (UUID 4804cd9a) uses `instruction` (singular), zero credits, Tier 1. Zapier (UUID 91a221c4) uses `instructions` (plural), burns credits, Tier 4. Never confuse
40. **WEBORDER CHECK** - When deal shows shipped/fulfilled but not Closed Won, search for weborder PO and route through weborder-to-deal-automation-v1-1
41. **PRODUCT_NAME NOT PRODUCT** - Always use `Product_Name: {"id": "..."}` for line items, NEVER `product: {"id": "..."}`. The `product` field triggers Zoho inventory active check and fails on products with negative stock (even when Product_Active = true). `Product_Name` bypasses this check
42. **DISCOUNT IS DOLLAR AMOUNT** - The `Discount` field on Quoted_Items accepts dollar amounts, not percentages. Formula: `Discount = (List_Price × Quantity) - Target_Sell_Price`. Example: List $201, target $138, Qty 1 → `Discount: 63`

## Minimal Field Sets

**Quote fetch (basic):** `id,Subject,Grand_Total,Quote_Stage`
**Quote fetch (with items):** `id,Subject,Grand_Total,Quoted_Items`
**Quote fetch (for margin):** `id,Subject,Grand_Total,Quoted_Items,CCW_Deal_Number`
**Quote fetch (for rep check):** `id,Subject,Meraki_ISR,CCW_Deal_Number`
**Deal fetch:** `id,Deal_Name,Account_Name,Stage,Amount,Lead_Source,Reason,Meraki_ISR`
**Account fetch:** `id,Account_Name,Billing_Street,Billing_City,Billing_State,Billing_Code,Billing_Country`
**Contact fetch:** `id,Full_Name,Email,Account_Name`
**Task fetch (full):** `id,Subject,Due_Date,What_Id,Who_Id,Status,Priority,Description`
**Task verify:** `id,Subject,Status,Modified_Time`
**Contact fetch (for email):** `id,First_Name,Last_Name,Email,Email_Opt_Out,Account_Name`

## Quick Reference IDs

**Chris Graves User ID:** `2570562000141711002`
**Org ID:** `org647122552`
**Stratus Sales ID:** `2570562000027286729`

## Quick Reference

```
CCW CSV GENERATION (v18, updated v25):
- ONLY generate when user explicitly requests it — never auto-generate
- 8-column header: ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
- Co-term: Leave columns 3-8 empty (just commas)
- Subscription: Parent SKU first, then 36/12/Prepaid Term/date
- Filename: CCW_Import_{Quote_Number}_{Account}.csv

CLAUDE REFERENCE FIX (v18):
- Include Chat Subject for searchability
- Format: "Chat: {Account} quote for {products}"
- Searchable in Claude's sidebar/history
- Include products list in note (- Qty x SKU)

ECOMM-TO-PO (v17):
- Match ecomm pricing → margins already validated
- DID still REQUIRED (LIVE_CiscoQuote_Deal must run)
- LIVE_GetQuoteData optional → empty cost data is OK
- Set Net_Terms on Quote BEFORE converting to PO
- Full automation: Deal → Quote → CCW → PO → Zoho Sign

PRE-CONVERSION CHECKPOINT (v17):
- MANDATORY before LIVE_ConvertQuoteToSO
- Net_Terms CANNOT be changed after PO conversion
- Verify: Net_Terms, Contact, Tax Exempt, Grand Total

CANCEL PENDING PO (v17):
- If deal has existing PO and new one needed
- Cancel pending PO first (Status = "Cancelled")
- Then create new Quote and convert

HOT CACHE FALLBACK (v17):
- If "inactive product" error → search Products module
- Find active product with same Product_Code
- Use active ID and retry

CLONE QUOTES FOR VARIANTS (v16):
- Use ZohoCRM_Clone_Record with overridden Subject + Quoted_Items
- NEVER include Tax fields (causes validation errors)
- Zoho auto-populates all pricing and taxes

IGNORE PRICES/TAXES (v16):
- Never lookup prices when getting Product IDs
- Never include List_Price, Unit_Price, Tax in payloads
- Only modify when user EXPLICITLY requests

ADMIN ACTION SEQUENCE (Quote-to-PO):
1. LIVE_CiscoQuote_Deal → Submit to CCW, get Deal ID
2. LIVE_GetQuoteData → Pull disti pricing (after approval)
3. LIVE_ConvertQuoteToSO → Create Purchase Order
4. LIVE_SendToEsign → Send PO for customer signature

REP LOOKUP (Post-DID):
- If Meraki_ISR = Stratus Sales AND DID generated → PROMPT for rep lookup
- Method 1: Search Gmail for DID → find Cisco reps on approval email
- Method 2: Search customer email threads → find rep involvement
- ALWAYS prompt before updating Lead_Source or Meraki_ISR

QUOTE NOTES:
- Add Claude reference to every Quote's Notes section
- Title: "Quote Created via Claude"
- Include Chat Subject: "Chat: {Account} quote for {products}"
- Include URL: direct link if provided, or "[pending]"
- Include products list: "- 1x MX75-HW\n- 2x CW9172I-RTG"
- Chat Subject is searchable in Claude's sidebar

PRODUCT ID LOOKUP ORDER (v21 - NO HOT CACHE):
1. Batch Zoho Products search: (Product_Code:equals:SKU1)OR(Product_Code:equals:SKU2)...
2. If SKU returns no result → retry with variant suffix (-3Y vs -3YR)
3. If still not found → report to user with quote URL for manual line item entry
NOTE: Hot cache removed. All lookups are live. SKU lookup happens AFTER quote shell created.

TASK MANAGEMENT (v23):
- Atomic lifecycle: send → close → verify → follow-up (sequential, never parallel)
- Date scope: Due_Date <= today for daily review/close. FU30 gets +7 day lookahead
- Triage: AUTO_CLOSE, FU30_EMAIL, DEAL_FOLLOWUP, ISR_CHECKIN, QUOTE_ACTION, NEEDS_REVIEW
- Follow-up: 3 business days default, skip weekends, conditional on email content
- Search: starts_with (not contains) for Subject, client-side sort (no Due_Date sort)
- Cascade: Never batch Zoho + Zapier in same parallel block

DEAL CREATION DEFAULTS (v25):
- Lead_Source = "Stratus Referal" (default, 99.9% of deals)
- Meraki_ISR = "Stratus Sales" (ID: 2570562000027286729) by default
- Stage = "Qualification" at creation — NEVER update stage mid-workflow
- Only switch to "Meraki ISR Referal" if Cisco rep explicitly named/implied in prompt
- AFTER deal/quote created, always ask: "Is there a Cisco rep involved? I can update the deal with their info."

STAGE LOCK RULES (v25):
- Creation: Stage = Qualification (set once, done)
- Updates: NEVER change Stage unless user explicitly says to close the deal
- Closing: Run live ZohoCRM_Get_Field lookup → use ONLY the exact "Closed (Lost)" value → never create a new option

ALWAYS DO:
✓ Default Lead_Source to "Stratus Referal" without prompting (unless rep is obvious in prompt)
✓ Proceed with deal/quote creation immediately using defaults
✓ After creation, ask if a Cisco rep should be added
✓ Use clone for quote variants (faster than recreate)
✓ Batch lookup all SKUs in single Zoho Products API call (after shell created)
✓ Validate all required fields before creation
✓ Lookup address if Account missing it
✓ Assign Contact_Name on every Quote
✓ Add Claude thread URL to Quote Notes (with products)
✓ Generate CCW CSV only when explicitly requested
✓ Prompt for rep lookup after DID generated (if Stratus Sales)
✓ Create Deal Note on new deals
✓ Verify task closure via re-fetch after every status update
✓ Present auto-closable tasks for user approval before closing
✓ Create follow-up tasks when email asked for next steps/decision
✓ Separate Zoho and Zapier calls into different batches
✓ Run live picklist lookup before setting "Closed (Lost)" stage

NEVER DO:
✗ Update Deal Stage mid-workflow without explicit "close this deal" instruction
✗ Create or invent a new Stage picklist value — always use exact live values
✗ Use Lead_Source = "-None-" (forbidden)
✗ Block deal creation to ask about Lead_Source when Stratus Referal default applies
✗ Auto-generate CCW CSV after every quote — only generate when explicitly asked
✗ Include Tax fields in clone/create payloads
✗ Lookup prices for SKUs (auto from product record)
✗ Include List_Price, Unit_Price, Net_Total, Total in payloads
✗ Auto-update Lead_Source or Meraki_ISR without prompting
✗ Look up SKUs before Deal and Quote shell are created
✗ Create records without validation checkpoint
✗ Use fake/placeholder URLs in Claude notes (use Chat Subject instead)
✗ Close tasks without verification re-fetch
✗ Include future-dated tasks in daily review or close operations
✗ Batch Zoho and Zapier MCP calls in the same parallel block
✗ Skip follow-up task creation when email asked for next steps
✗ Use `contains` for Subject field searches (use starts_with)
✗ Sort by Due_Date in Zoho search (sort client-side)
✗ Close tasks on active deals without checking for successor tasks
✗ Skip pre-close deal validation for deal-linked tasks
✗ Use banned picklist values ("Closed Lost", "Referral", "Closed-Won")
✗ Close tasks without running the evaluation gate first
✗ Manually set Deal Stage to "Closed Won" (deals auto-close when PO is attached)
✗ Rely solely on Zoho Last_Activity_Time without checking Gmail for actual contact
✗ Skip successor task creation on open/ongoing deals after any action
✗ Confuse Pipedream (instruction singular, UUID 4804cd9a) with Zapier (instructions plural, UUID 91a221c4)
✗ Take action on deal-linked tasks without first searching Gmail for last customer contact
✗ Use `product` field for line items — always use `Product_Name` field (product triggers inventory check)
✗ Use percentage string for Discount — always use dollar amount (List×Qty - Target)
```


---

See CHANGELOG.md for version history.
