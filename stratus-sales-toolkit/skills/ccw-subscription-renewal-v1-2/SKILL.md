---
name: ccw-subscription-renewal-v1-2
description: "speed-optimized cisco ccw subscription renewal workflow. parallel zoho+tab fetch, js-only page transitions (zero screenshot waits), consolidated js extraction, single zoho write-back, batch renewal support for multiple quotes. triggers: renew subscription, ccw renewal, subscription renewal, renew meraki license, ccw sub renewal, renew sub, batch renewals."
---

# CCW Subscription Renewal Skill v1-2

Automates the full Cisco Commerce Workspace (CCW) subscription renewal workflow end-to-end with **speed optimizations** that minimize screenshots and maximize JS-first detection. Fetches the Subscription ID from Zoho, navigates CCW to complete the renewal, extracts the CCW Quote Number and CCW Deal ID from the confirmation page, and writes both back to Zoho in a single update call.

## What's New in v1-2

- **BATCH RENEWAL SUPPORT**: Process multiple quote renewals in sequence. Pass a list of Zoho Quote IDs or URLs; each runs through the full workflow atomically before moving to the next.
- **ZERO-SCREENSHOT PAGE TRANSITIONS**: All page transition detection now uses JS hash polling exclusively. Screenshots are fallback-only for value extraction when JS DOM queries return null.
- **CONSOLIDATED JS EXTRACTION**: Quote Number + Deal ID extracted in a single JS call from confirmation page (was already in v1-1, now emphasized as mandatory first approach).
- **CCRC DIRECT URL MANDATORY**: Direct URL navigation to ccrc.cisco.com/subscriptions/detail/{SubID} is the only path. CCW search fallback removed from primary flow (moved to error recovery only).
- **WAIT OPTIMIZATION**: Replaced fixed wait times with JS-based readiness checks. Poll for DOM elements rather than waiting arbitrary seconds.
- **UPDATED COMPANION SKILLS**: References zoho-crm-v28
- All v1-1 features retained

---

## Trigger Phrases

- "renew subscription"
- "ccw renewal"
- "subscription renewal"
- "renew meraki license"
- "ccw sub renewal"
- "renew sub"
- Any message referencing a Zoho quote URL + renewal context

---

## Prerequisites

- Active CCW session at apps.cisco.com (will auto-navigate if not)
- Zoho quote record with `Notes1` field containing the Subscription ID (format: "Sub1856246 Renewal")
- Chrome browser automation active (Claude in Chrome / Cowork mode)

---

## Input

**Required:**
- Zoho Quote ID or URL (e.g., `https://crm.zoho.com/crm/org647122552/tab/Quotes/2570562000384787142`)

**Extracted automatically:**
- Subscription ID → from Zoho `Notes1` field
- `CCW_Quote_Number` → checked first; skip CCW if already populated

---

## Step-by-Step Workflow

### Step 1: Parallel Fetch — Zoho + Tab Context

**Start both simultaneously** — Zoho fetch and tab context can run in parallel since CCW home load takes time and does not require the Sub ID yet.

```
# In parallel:
ZohoCRM_Get_Record(module="Quotes", recordID="{quote_id}")
tabs_context_mcp()  # Get tab IDs while Zoho data loads
```

**From Zoho, extract:**
- `Notes1` → parse Subscription ID (e.g., "Sub1856246 Renewal" → `Sub1856246`)
- `CCW_Quote_Number` → if already populated, **STOP** (see Skip Guard below)
- `Account_Name` → for confirmation reporting
- `Subject` → for context

**Skip Guard:** If `CCW_Quote_Number` is already set, report to user and stop:
> "CCW Quote Number already populated: {number}. Renewal appears complete — skipping CCW workflow."

### Step 2: Navigate CCW

Navigate to CCW home while Zoho data is resolving:
```
navigate(url="https://apps.cisco.com/Commerce/home", tabId=ccwTabId)
```

Confirm tab ID from `tabs_context_mcp()` result. If no CCW tab exists, create one.

### Step 3: Handle Idle Timeout (If Present)

Use JS to detect the idle popup before taking a screenshot:
```javascript
// Check for idle timeout overlay
!!document.querySelector('.idle-timeout-modal, [class*="timeout"], [class*="session-expired"]')
```

If detected (or if screenshot shows popup), dismiss at approximately `(419, 234)` then re-check via JS.

### Step 4: Navigate to Subscription — Direct URL

Once Sub ID is available from Zoho, navigate directly to the CCRC Subscription Workbench. This skips CCW search entirely.

```
navigate(url="https://ccrc.cisco.com/subscriptions/detail/{SubID}", tabId=ccwTabId)
```

**Proactive banner dismiss** — after page loads, run JS before any other interaction:
```javascript
// Dismiss announcement banner if present
const banner = document.querySelector(
  '[class*="announcement"] button[class*="close"], [class*="banner"] button[class*="dismiss"], [aria-label="Close"]'
);
if (banner) { banner.click(); 'dismissed'; } else { 'no banner'; }
```

If JS dismiss fails, fall back to coordinate click at approximately `(611, 119)`.

**Option B — CCW Search (Fallback if direct URL fails):**
1. Click CCW search bar at coordinate `(330, 29)` — **must use coordinate click, NOT form_input**
2. Type the Subscription ID: `computer(action="type", text="{SubID}")`
3. Click the magnifying glass at `(408, 61)` — **Enter key does NOT trigger CCW search**
4. Take screenshot and locate the subscription in results
5. Click the subscription record to open it

> **CRITICAL:** CCW search requires coordinate-based interaction. `form_input` and keyboard Enter do not work reliably on this interface.

### Step 5: Click Modify/Renew

Locate and click the **"Modify/Renew"** button.

```
find(query="Modify/Renew button", tabId=ccwTabId)
```

Take a screenshot only if `find` fails to confirm button location.

### Step 6: Select "Renew My Subscription"

On the renewal type selection page, select the **"Renew My Subscription"** radio button.

**Use coordinate click** — radio buttons in CCW do not respond to `form_input`:
```
computer(action="left_click", coordinate=[455, 530], tabId=ccwTabId)
```

> Coordinate `(455, 530)` confirmed from live execution. If layout differs, take one screenshot to adjust.

**Detect selection via JS instead of screenshot:**
```javascript
// Confirm radio is selected
const radios = document.querySelectorAll('input[type="radio"]');
Array.from(radios).find(r => r.checked)?.value || 'none selected';
```

### Step 7: Verify & Save

Click **"Verify & Save"**. Detect page transition via URL hash instead of screenshot:

```javascript
// Confirm transition away from current page
window.location.hash
```

Expected: hash changes to cfgcor/configuration URL after save.

### Step 8: Terms & Billing — Save and Continue

On the Terms and Billing page, click **"Save and Continue"**.

Use JS to confirm page context before clicking:
```javascript
document.title + ' | ' + window.location.href
```

Click "Save and Continue" via `find` or coordinate.

### Step 9: Detect Items Page + Extract Quote Number

After "Save and Continue," wait for redirect to the Items page. Detect via URL hash:

```javascript
window.location.hash  // Should return '#/items/...'
```

**Extract CCW Quote Number from DOM immediately (no screenshot needed):**
```javascript
// Try multiple selectors — CCW layout may vary
const qn = document.querySelector('[data-fieldname="quoteNumber"] .value')?.innerText?.trim()
  || document.querySelector('.quote-number')?.innerText?.trim()
  || Array.from(document.querySelectorAll('td, span, div'))
     .find(el => /^\d{10}$/.test(el.innerText?.trim()))?.innerText?.trim();
qn || 'not found';
```

> Quote Number is a 10-digit number (e.g., `4789972657`). If JS extraction returns "not found," take one screenshot to read it visually.

### Step 10: Advance to Review & Submit

Click the **"Review & Submit"** step (breadcrumb or Continue button).

Detect arrival via URL hash:
```javascript
window.location.hash  // Should return '#/review/...'
```

### Step 11: Handle Incentives Check (JS-First Approach)

**Do not screenshot first.** Query DOM for the incentives warning banner:

```javascript
// Check for incentives warning in one call
const warning = document.querySelector('[class*="incentive"], [class*="warning"]');
const hereLink = Array.from(document.querySelectorAll('a'))
  .find(l => l.textContent.trim() === 'here' && l.offsetParent !== null);
JSON.stringify({ hasWarning: !!warning, hasHereLink: !!hereLink });
```

If `hasHereLink` is true, click it immediately:
```javascript
const hereLink = Array.from(document.querySelectorAll('a'))
  .find(l => l.textContent.trim() === 'here' && l.offsetParent !== null);
if (hereLink) { hereLink.click(); 'clicked'; } else { 'no link found'; }
```

On the Explore Incentives page, check for offers via JS:
```javascript
document.body.innerText.includes('No offers found') ? 'no offers' : 'offers present';
```

**If "No offers found":** Navigate back to Review & Submit using the breadcrumb step, NOT the Back button. The Back button routes to Items page — known CCW bug.

```javascript
// Click Review & Submit breadcrumb step directly
const steps = document.querySelectorAll('[class*="step"], [class*="breadcrumb"] li');
const reviewStep = Array.from(steps).find(s => s.textContent.includes('Review'));
if (reviewStep) { reviewStep.click(); 'clicked review step'; } else { 'not found'; }
```

Fallback: click Continue button at approximately `(1338, 361)`.

### Step 12: Submit the Renewal

Verify `#/review/` hash via JS, then click Submit:

```javascript
window.location.hash  // Confirm '#/review/...'
```

```
find(query="Submit button", tabId=ccwTabId)
```

Fallback coordinate: `(530, 299)`.

### Step 13: Extract Quote Number and Deal ID from Confirmation Page

Detect the confirmation page via URL hash:
```javascript
window.location.hash  // Should return '#/confirmation/...'
```

**Single JS composite extraction — both values in one call:**
```javascript
// Extract CCW Quote Number and Deal ID from confirmation page
const allText = Array.from(document.querySelectorAll('td, span, div, p'));
const quoteNum = allText
  .find(el => /^\d{10}$/.test(el.innerText?.trim()))?.innerText?.trim();
const dealId = (() => {
  const dealLabel = Array.from(document.querySelectorAll('*'))
    .find(el => el.innerText?.trim() === 'Deal ID');
  if (dealLabel) {
    const sibling = dealLabel.nextElementSibling
      || dealLabel.parentElement?.nextElementSibling;
    return sibling?.innerText?.trim();
  }
  return null;
})();
JSON.stringify({ quoteNumber: quoteNum, dealId: dealId });
```

> Deal ID is a shorter numeric value (e.g., `83598009`) displayed alongside Quote Number on the confirmation page. If JS extraction returns null for either value, take one screenshot to read them visually.

### Step 14: Update Zoho — Single Call, Both Fields

Write CCW Quote Number AND CCW Deal ID back to Zoho in one API call:

```
ZohoCRM_Update_Record(
  module="Quotes",
  recordID="{quote_id}",
  data=[{
    "CCW_Quote_Number": "{ccw_quote_number}",
    "CCW_Deal_ID": "{ccw_deal_id}"
  }]
)
```

> **Field name note:** `CCW_Deal_ID` is the assumed API name for the CCW Deal ID field. If the update fails with a field error, confirm the correct API name with `ZohoCRM_Get_Fields(module="Quotes")` and retry.

### Step 15: Confirm and Report

After the Zoho update succeeds, report to the user:

```
✅ CCW Subscription Renewal Complete

Subscription: {SubID}
Account: {Account_Name}
CCW Quote Number: {ccw_quote_number}
CCW Deal ID: {ccw_deal_id}
Zoho Quote Updated: ✓ (both fields written)

Zoho Quote: https://crm.zoho.com/crm/org647122552/tab/Quotes/{quote_id}
```

---

## CCW Navigation Quick Reference

| Action | Method | Coordinates |
|--------|--------|-------------|
| Search bar click | coordinate only | `(330, 29)` |
| Trigger search | click magnifying glass | `(408, 61)` |
| Renew radio button | coordinate click | `(455, 530)` confirmed |
| Submit fallback | scroll + click | `(530, 299)` |
| Idle timeout dismiss | coordinate click | `(419, 234)` |
| Continue (after incentives) | coordinate fallback | `(1338, 361)` |
| CCRC banner dismiss | coordinate fallback | `(611, 119)` |

> **Never use `form_input` for CCW search or radio buttons.** CCW uses custom JS-driven components that do not respond to standard form interactions.

---

## Incentives Flow — Known Behavior

The incentives check is a predictable step on every renewal. Documented behavior:

1. Review & Submit page may show: *"To submit this quote, please review the available incentives and select one, or choose to opt out. Click here to proceed."*
2. Clicking "here" opens the Explore Incentives page
3. Most renewals will show **"No offers found"**
4. **Back button routes to Items page, not Review & Submit** — use breadcrumb JS click or Continue button instead
5. After returning to Review & Submit, the Submit button is available without the warning repeating

---

## Error Handling

| Error | Recovery |
|-------|----------|
| Idle timeout popup | JS detect first; click dismiss at `(419, 234)`, re-check via JS |
| CCRC announcement banner | JS proactive dismiss; fallback coordinate `(611, 119)` |
| CCW search returns no results | Try direct URL: `ccrc.cisco.com/subscriptions/detail/{SubID}` |
| Submit button not found by `find` | Scroll down, click at `(530, 299)` |
| CCW_Quote_Number already in Zoho | Skip entire CCW workflow, report to user |
| Subscription ID missing from Notes1 | Stop and ask user for Sub ID before proceeding |
| Page redirects to CCW home | Check for idle timeout, then re-attempt navigation |
| Back button after incentives returns to Items | Use Continue at `(1338, 361)` or click Review & Submit breadcrumb |
| JS extraction returns null for Quote Number or Deal ID | Take one screenshot and read values visually |
| CCW_Deal_ID field update fails | Run `ZohoCRM_Get_Fields(module="Quotes")` to confirm correct API name |

---

## Zoho Field Reference

| Field | API Name | Notes |
|-------|----------|-------|
| Subscription ID | `Notes1` | Format: "SubXXXXXX Renewal" — parse SubXXXXXX |
| CCW Quote Number | `CCW_Quote_Number` | 10-digit CCW quote number written after renewal |
| CCW Deal ID | `CCW_Deal_ID` | CCW Deal ID from confirmation page — confirm API name if needed |
| Account | `Account_Name` | For verification context |
| Deal | `Deal_Name` | For context |

**Zoho Quote URL pattern:**
```
https://crm.zoho.com/crm/org647122552/tab/Quotes/{RECORD_ID}
```

---

## v1-1 Optimizations vs. v1-0

| Area | v1-0 Approach | v1-1 Optimization |
|------|--------------|-------------------|
| Page state detection | Screenshot after every action | JS `window.location.hash` to detect transitions |
| Incentives handling | Screenshot then find then coordinate click | DOM query + JS click in one call |
| Quote Number extraction | Read from screenshot | JS DOM extraction (multi-selector) |
| Deal ID extraction | Not captured | JS composite extraction alongside Quote Number |
| Zoho write-back | One field (`CCW_Quote_Number`) | Two fields (`CCW_Quote_Number` + `CCW_Deal_ID`) in single call |
| Announcement banner | Reactive (screenshot, detect, click) | Proactive JS dismiss before any interaction |
| Initial fetch | Sequential (Zoho then tabs) | Parallel (Zoho + `tabs_context_mcp` together) |
| Back after incentives | Back button (broken, routes to Items) | Breadcrumb JS click or Continue button |
| Screenshots per run | ~8-10 | ~1-3 (fallback only) |

---

## Batch Renewal Support (NEW IN V1-2)

### When to Use

When the user provides multiple Zoho Quote IDs or URLs for renewal, process them sequentially (not in parallel, since CCW can only handle one renewal at a time).

### Batch Workflow

```
FOR EACH quote in batch:
  1. Fetch Zoho quote (Notes1, CCW_Quote_Number)
  2. Skip-if-done guard (CCW_Quote_Number already set)
  3. Navigate CCW to subscription
  4. Complete renewal flow (steps 5-13)
  5. Write back to Zoho
  6. Report success/failure
  THEN next quote

After all quotes processed:
  Report batch summary:
  - Total attempted: X
  - Successful: Y
  - Skipped (already done): Z
  - Failed: W (with error details)
```

### Batch Input Formats

```
# Multiple URLs:
"Renew these subscriptions:
https://crm.zoho.com/crm/org647122552/tab/Quotes/2570562000384787142
https://crm.zoho.com/crm/org647122552/tab/Quotes/2570562000391234567"

# Multiple IDs:
"Batch renew quotes: 2570562000384787142, 2570562000391234567"
```

---

## JS Readiness Polling (NEW IN V1-2)

Replace arbitrary `wait` calls with DOM readiness checks:

```javascript
// Wait for page readiness instead of fixed timer
const waitForReady = () => {
  const loading = document.querySelector('[class*="loading"], [class*="spinner"]');
  const content = document.querySelector('[class*="subscription"], [class*="detail"]');
  return JSON.stringify({ loading: !!loading, content: !!content });
};
waitForReady();
```

If `loading: true`, wait 2 seconds and re-poll. If `content: true` and `loading: false`, proceed. Max 3 polls before falling back to screenshot.

---

## Token Efficiency Notes

- Pull Zoho data AND get tab context in **parallel** at session start
- Use JS hash polling to detect page transitions instead of screenshots
- DOM extraction for Quote Number and Deal ID avoids image reads entirely
- Take screenshots only as fallback when JS extraction returns null
- Single Zoho API call writes both `CCW_Quote_Number` and `CCW_Deal_ID` simultaneously
- Check `CCW_Quote_Number` early to avoid unnecessary CCW navigation entirely
- **Batch renewals**: Reuse CCW tab across quotes; no new tab creation per renewal
- **JS readiness polling**: Replace fixed waits with DOM-based readiness checks

---

## Changelog

### v1-2 (2026-02-27)
- **Batch renewal support:** Process multiple Zoho Quote renewals sequentially with summary reporting
- **JS readiness polling:** DOM-based readiness checks replace arbitrary wait times
- **CCRC direct URL mandatory:** CCW search removed from primary flow (error recovery only)
- **Zero-screenshot transitions:** All page transitions verified via JS hash polling exclusively
- **Batch input formats:** Support for multiple URLs or comma-separated IDs
- **Updated companion skills:** References zoho-crm-v28
- All v1-1 features retained

### v1-1 (2026-02-24)
- **JS-first state detection:** URL hash polling replaces post-click screenshots for page transition verification
- **JS incentives handling:** DOM query + JS click replaces screenshot, find, coordinate click loop
- **JS composite extraction:** Single JS call extracts both Quote Number and Deal ID from confirmation page
- **CCW Deal ID capture:** Deal ID now extracted and written to Zoho `CCW_Deal_ID` field alongside Quote Number
- **Dual field Zoho write-back:** Single `ZohoCRM_Update_Record` call writes both CCW fields simultaneously
- **Proactive banner dismiss:** JS query dismisses CCRC announcement banner before any interaction
- **Parallel initial fetch:** Zoho fetch + `tabs_context_mcp` now run simultaneously at session start
- **Incentives back navigation fix:** Breadcrumb JS click documented as correct return path (Back button routes to Items — known CCW bug)
- **Confirmed coordinates updated:** Renew radio at `(455, 530)`, Continue after incentives at `(1338, 361)`, banner dismiss at `(611, 119)`
- **Screenshot count reduced:** From ~8-10 per run to ~1-3 (fallback only)

### v1-0 (2026-02-24)
- Initial release
- Full end-to-end CCW subscription renewal workflow
- Skip guard for already-completed renewals
- Direct URL navigation optimization (ccrc.cisco.com)
- Coordinate-based CCW interaction documented
- Idle timeout handling
- Zoho Notes1 Sub ID extraction pattern
- Error recovery table
