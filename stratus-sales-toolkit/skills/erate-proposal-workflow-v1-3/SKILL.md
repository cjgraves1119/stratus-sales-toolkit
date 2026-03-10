---
name: erate-proposal-workflow-v1-3
description: e-rate form 470 proposal workflow with zero-credit python-requests-first usac soda api integration, dynamic funding year calculation, pre-scan filter prompt (state/days/score), automated weekly bid scanner with fit-scoring algorithm, excel export with hyperlinked rfp links, form 470 instant lookup, rfp pdf extraction, zoho-crm-v30 rule inheritance, mandatory sku validation against live catalog, proceed-first deal defaults, tiered installation estimates, multi-building quote splitting guidance, and sled optimization recommendations. covers rfp qualification, equivalence mapping, zoho crm setup, quote creation, cisco discount coordination, bid package generation, and post-submission actions.
---

# E-Rate / Form 470 Proposal Workflow v1.3

Complete workflow for analyzing E-Rate Form 470 RFPs, mapping competitor equipment to Cisco/Meraki equivalents, creating Zoho CRM records and quotes, coordinating Cisco discounts, and generating bid packages for K-12 school districts. Includes automated USAC data lookups, weekly bid scanning, and Excel bid digest export — all using Python requests by default (zero Firecrawl credits) with Firecrawl as fallback.

## What Changed in v1.3

| Change | v1.2 | v1.3 |
|--------|------|------|
| API fetch method | Firecrawl-only (1 credit/request) | Python requests (0 credits) — Firecrawl fallback only |
| Funding year | Hardcoded `2026` in queries | Dynamic `current_erate_fy()` — auto-calculates every year |
| Ad-hoc lookups | `$q=` with no year filter → old records returned | Always enforces `funding_year` + `f470_status` + deadline filter |
| Pre-scan prompt | Not available | Asks for state, days window, min score before scanning |
| Excel export | Separate manual step | Auto-generated 4-sheet workbook by `scan.py` |
| RFP hyperlinks | Not linked | Application numbers hyperlinked to Form 470 PDF/portal URL |
| SIRE flagging | Manual note only | Auto-flagged in Excel Hot Leads sheet for deals ≥ $200K |
| Pagination | Single-page results | Auto-pagination via offset loop, removes duplicates |
| Bundled script | Not available | `scripts/scan.py` — standalone CLI, no Firecrawl dependency |
| SLED optimizations | None | Urgency countdown, territory gap detection, batch qualification |

## When to Use

- User uploads or references a Form 470 / E-Rate RFP
- User mentions E-Rate, Form 470, school district network bid, or competitive displacement
- User asks to quote Meraki equipment against Aruba, Extreme, Ruckus, Ubiquiti, or Fortinet for a school district
- User references Healthcare Connect Fund (HCF/RHC) Form 461 opportunities
- User asks to scan for open E-Rate bids or check USAC for opportunities
- User provides a Form 470 application number for lookup
- Keywords: "E-Rate," "Form 470," "Form 461," "bid package," "USAC," "BEN," "Internal Connections," "bid scanner," "open bids," "erate scan," "sled"

## Company Details

- Company: Stratus Information Systems (Cisco-exclusive reseller, Meraki specialist)
- USAC SPIN: **143052656**
- Primary Contact: Chris Graves, Regional Sales Director, chrisg@stratusinfosystems.com, (888) 366-4911
- Installation SKU: SIS101 at $200/hour

---

## Pre-Scan Filter Prompt (NEW in v1.3)

**ALWAYS run this prompt before executing any bid scan.** This prevents national over-scans and ensures results are filtered to actionable opportunities.

```
Before scanning, ask the user:

1. STATE FILTER
   "Which states should I scan? (e.g., TX, CO, IA — or press Enter for national scan)"
   → Accept: comma-separated 2-letter codes, empty = national

2. DEADLINE WINDOW
   "How many days out should I look for bid deadlines? (default: 60)"
   → Accept: integer, default 60

3. MINIMUM FIT SCORE
   "Minimum fit score to include? (default: 20 — 40+ for hot/warm leads only)"
   → Accept: integer 0-100, default 20

4. EXPORT FORMAT
   "Export results as Excel? (yes/no, default: yes)"
   → Accept: yes/no
```

**After collecting filters**, display a confirmation summary before running:

```
📋 Scan Parameters:
   FY: [auto-calculated]
   States: [user input or "National"]
   Deadline window: [X] days (from today through [date])
   Min score: [X]/100
   Export: [Yes/No]

   Proceed? (yes/no)
```

---

## SODA API — Zero-Credit Access (NEW in v1.3)

### Why Python Requests, Not Firecrawl

The USAC SODA API returns standard JSON from a public REST endpoint. Firecrawl is a web scraping tool optimized for HTML/PDF — using it for a JSON API wastes credits unnecessarily. The Python `requests` library hits the same endpoint for $0.

| Method | Credits Used | Notes |
|--------|-------------|-------|
| Python requests | 0 | Primary for all JSON queries |
| Firecrawl scrape | 1 per 200 records | Fallback ONLY if requests fails |
| Firecrawl agent | 0 | For navigation-heavy district websites |

### Bundled Scanner Script

`scripts/scan.py` handles the complete scan workflow:

```bash
# Default: national scan, 60-day window, min score 20
python scan.py

# Filtered example
python scan.py --state TX,CO,IA --days 45 --min-score 40 --output /path/file.xlsx
```

**Arguments:**

| Flag | Default | Description |
|------|---------|-------------|
| `--state` | national | Comma-separated 2-letter state codes (e.g., TX,CO,IA) |
| `--days` | 60 | Deadline window (today through today + N days) |
| `--min-score` | 20 | Minimum fit score to include in output |
| `--output` | auto | Path for .xlsx output file |

**Firecrawl Fallback Signal:**

If Python requests fails (network error, timeout, etc.), the script exits with code 1 and prints:
```
FIRECRAWL_FALLBACK_REQUIRED
FALLBACK_URL: https://opendata.usac.org/resource/jp7a-89nd.json?...
```

When you see this signal, use `firecrawl_scrape` on the `FALLBACK_URL` printed.

### How to Run the Script

```python
# 1. Install dependencies (if not present)
pip install requests openpyxl --break-system-packages

# 2. Run with filters collected from pre-scan prompt
python /sessions/upbeat-zen-goldberg/erate-proposal-workflow-v1-3/scripts/scan.py \
  --state TX,CO \
  --days 60 \
  --min-score 20
```

The script outputs the Excel file path when complete.

---

## USAC SODA API Integration

### Overview

The USAC Open Data Platform provides public access to all E-Rate Form 470 filings via the Socrata SODA API. Data is updated daily, requires no authentication, and can be queried via Python requests for 0 credits.

### Datasets

| Dataset | Resource ID | Contents |
|---------|------------|----------|
| Form 470 Basic Info | `jp7a-89nd` | 56 fields: applicant, BEN, contact info, category descriptions, dates, status |
| Services Requested | `39tn-hjzv` | Service types, functions, quantities per Form 470 |

### Query Patterns — Python Requests (Primary, 0 Credits)

**Dynamic FY Calculation (CRITICAL — use this everywhere):**
```python
def current_erate_fy():
    today = datetime.date.today()
    if today.month >= 7:
        return today.year + 1
    return today.year

FY = current_erate_fy()  # e.g., 2026 when run Jan-June 2026
```

**Open Bid Scanner — Full Filter Set:**
```python
import requests, datetime

SODA_BASE = 'https://opendata.usac.org/resource/jp7a-89nd.json'
fy = current_erate_fy()
today = datetime.date.today().strftime('%Y-%m-%dT00:00:00.000')

params = {
    '$where': (
        f"funding_year='{fy}' "
        f"AND f470_status='Certified' "
        f"AND allowable_contract_date > '{today}' "
        "AND category_two_description IS NOT NULL"
    ),
    '$select': 'application_number,billed_entity_name,billed_entity_state,'
               'contact_name,contact_email,technical_contact_email,'
               'allowable_contract_date,category_two_description,'
               'rfp_identifier,f470_number,number_of_eligible_entities',
    '$order': 'allowable_contract_date ASC',
    '$limit': 200,
    '$offset': 0,
}
# Add optional state filter:
# params['$where'] += " AND billed_entity_state in('TX','CO')"

resp = requests.get(SODA_BASE, params=params, timeout=30)
records = resp.json()
```

**Single Form 470 Lookup:**
```python
params = {'application_number': '260024215'}
resp = requests.get(SODA_BASE, params=params, timeout=15)
```

**Keyword Search with MANDATORY Year Filter (fixed from v1.2):**
```python
# CORRECT — includes funding_year to prevent old records
params = {
    '$where': f"funding_year='{fy}' AND f470_status='Certified'",
    '$q': 'Meraki',  # Full-text search
    '$limit': 50,
}

# WRONG — never do this (returns FY2017, FY2020, FY2024+ records)
# params = {'$q': 'Meraki'}  # No year filter!
```

### Key Fields in SODA Response

| Field | Use |
|-------|-----|
| `application_number` | Form 470 ID (e.g., 260024215) |
| `billed_entity_name` | District/school name |
| `billed_entity_number` | BEN for Zoho Deal naming |
| `billed_entity_state` | State (2-letter code) |
| `contact_name` / `contact_email` | Primary contact |
| `technical_contact_email` | Tech contact for direct outreach |
| `category_two_description` | **CRITICAL** — Contains full RFP narrative including BOM, specs, bid requirements. ~60-70% of bids have complete data here. |
| `allowable_contract_date` | Bid deadline |
| `f470_status` | Certified = active, Expired = closed |
| `f470_number` | Object with `.url` key pointing to Form 470 PDF — use for Excel hyperlinks |
| `rfp_identifier` | Additional link to RFP document on USAC portal |
| `number_of_eligible_entities` | Building count (triggers multi-building quote logic) |

### Root Cause: Why Old Records Were Returned (FIXED in v1.3)

In v1.2, ad-hoc lookups using `$q=keyword` had NO `funding_year` filter. This caused searches like `$q=Genoa` to return records from FY2017, FY2020, and FY2024 alongside the current FY2026 records.

**Fix in v1.3:**
1. `scan.py` always includes `funding_year='{fy}'` in the `$where` clause, using the dynamic FY calculator
2. Keyword searches (when used outside scan.py) MUST include `funding_year` — never use bare `$q=` without it
3. Added `f470_status='Certified'` and `allowable_contract_date > today` filters to exclude expired records
4. Pagination via `$offset` loops ensures all current records are captured (not just first 50)

### Data Completeness

Approximately 60-70% of Form 470 filings include complete BOM details in the `category_two_description` field. The remaining 30-40% contain vague descriptions like "see RFP for details" and require PDF follow-up.

**Decision Logic:**
```
IF category_two_description contains specific SKUs, model numbers, or port counts:
  → Sufficient for fit-scoring AND equivalence mapping
  → Proceed to Phase 1 analysis

IF category_two_description is vague ("see attached RFP," "see RFP for details"):
  → Check f470_number.url or rfp_identifier for PDF link
  → Use Firecrawl scrape on PDF (~6 credits per document)
  → If no PDF available, flag for manual review
```

---

## Automated Weekly Bid Scanner (UPDATED in v1.3)

### Purpose

Scan all open E-Rate Form 470 bids to identify opportunities that are strong fits for Stratus (Cisco/Meraki-focused, equipment-only, low admin burden).

### Fit-Scoring Algorithm

Each bid is scored 0-100 across five dimensions:

| Dimension | Points | Trigger |
|-----------|--------|---------|
| CISCO_MERAKI | +40 | Keywords: meraki, cisco catalyst, c9300, c9200, cw916, cw917, ms120, ms125, ms130, ms225, ms250, ms350, ms390, ms425, mx4, mx6, mx8, mx9, mx1, mr , mr-, mr4, mr5, mr7, lic-ent, cw9, cisco |
| COMPETITIVE_SWAP | +25 | Keywords: fortinet, fortigate, fortiap, aruba, ruckus, extreme, sonicwall, palo alto, juniper, ubiquiti, unifi, aerohive, cambium, tp-link |
| NO_WALKTHROUGH | +15 | ABSENCE of: walkthrough, walk-through, walk through, site visit, mandatory visit |
| EQUIP_ONLY | +10 | ABSENCE of: mibs, managed internal broadband, managed services, managed wifi |
| SKU_SPECIFIC | +10 | Presence of specific model numbers (regex: alphanumeric-dash sequences like CW9176I, MS130-48P) |

**Score Interpretation:**

| Score | Rating | Action |
|-------|--------|--------|
| 70-100 | Hot Lead | Auto-create Zoho Deal + flag for immediate action |
| 40-69 | Warm Lead | Include in weekly digest, review manually |
| 20-39 | Cool | Include in digest as low-priority |
| 0-19 | Pass | Exclude from digest |

### Weekly Scanner Workflow (UPDATED — Zero-Credit Default)

```
0. Run Pre-Scan Filter Prompt (state, days, min score)

1. Run scripts/scan.py with collected filters:
   python scan.py --state [X] --days [N] --min-score [M]
   → 0 credits (Python requests)
   → Auto-paginates until all results fetched
   → Falls back to Firecrawl only if requests fails

2. Script runs fit-scoring on all fetched records

3. Script exports 4-sheet Excel workbook:
   → Sheet 1: Bid Digest (all records ≥ min-score, sorted by score desc)
   → Sheet 2: Hot Leads (70+) — SIRE flag for deals ≥ $200K est value
   → Sheet 3: Warm Leads (40-69)
   → Sheet 4: Legend, scoring reference, scan metadata

4. Present Excel file to user via present_files tool

5. For bids scoring 40+, optionally launch parallel sub-agents:
   → Pull full application details
   → Map equipment, estimate value, flag red flags
   → Return JSON results for consolidated review

6. Present digest for review:
   → Hot Leads (70+): recommend immediate Zoho Deal creation
   → Warm Leads (40-69): recommend manual review
   → Include deadline countdown (days remaining) for urgency

7. On approval: create Zoho Deals for selected opportunities
```

### Excel Export — 4-Sheet Workbook (NEW in v1.3)

The `scan.py` script generates a workbook with the following structure:

**Sheet 1: Bid Digest (All Scored)**

| Col | Field | Notes |
|-----|-------|-------|
| A | Application # | Hyperlinked to Form 470 PDF or USAC portal |
| B | District | billed_entity_name |
| C | State | billed_entity_state |
| D | Score | 0-100 |
| E | Rating | Hot/Warm/Cool/Pass |
| F | Deadline | allowable_contract_date |
| G | Days Left | Calculated from today |
| H | Contact | contact_name |
| I | Email | contact_email |
| J | Tech Email | technical_contact_email |
| K | Buildings | number_of_eligible_entities |
| L | MIBS Flag | Yes/No |
| M | Est Value | Rough dollar estimate from keyword counts |
| N | SIRE | Yes if est ≥ $200K |
| O | Fit Reasons | Comma-separated scoring reasons |
| P | Description Snippet | First 300 chars of category_two_description |

**Sheet 2: Hot Leads (Score ≥ 70)**
Same columns, filtered + sorted. Rows with SIRE=Yes are highlighted in yellow.

**Sheet 3: Warm Leads (Score 40-69)**
Same columns, filtered + sorted.

**Sheet 4: Legend & Notes**
Scoring algorithm reference, scan parameters used, generation timestamp, FY, total records pulled, records exported.

**Hyperlink Implementation:**
Application number cells in column A are hyperlinked using:
```python
# Primary: f470_number.url field from SODA response
link_cell.hyperlink = record.get('f470_number', {}).get('url', '')
# Fallback: USAC portal URL
# https://forms.universalservice.org/portal/form470/view/{application_number}
```

### Credit Budget (UPDATED)

| Step | Credits | Notes |
|------|---------|-------|
| Full scan (Python requests) | 0 | Primary method |
| Firecrawl fallback (if requests fails) | 1 per 200 records | Rare edge case |
| PDF extraction (when needed) | ~6 each | Only for vague descriptions |
| **Estimated weekly total** | **0-6** | vs. 15-30 in v1.2 |

---

## Firecrawl MCP Setup (For PDF Extraction and Fallback)

Firecrawl is no longer required for bid scanning. It is only needed for:
- PDF extraction when `category_two_description` is insufficient
- Firecrawl Agent fallback for district websites requiring navigation
- Edge cases where Python requests fails (network restrictions, proxy environments)

### Pre-Flight Check

```
IF firecrawl_scrape tool is available:
  → Firecrawl is connected. Use for PDFs/fallbacks only.

IF firecrawl_scrape tool is NOT available:
  → Bid scanning works fine via Python requests (scan.py)
  → PDF extraction will require manual upload if needed
  → Consider setting up Firecrawl for PDF workflows
```

### Setup Instructions

**Step 1: Create a Firecrawl Account**
1. Go to https://www.firecrawl.dev
2. Sign up for a free account (500 credits/month, no credit card required)

**Step 2: Get Your API Key**
1. In the Firecrawl dashboard, find the API Keys section
2. Copy your API key (starts with `fc-`)

**Step 3: Add to Claude**
```
For Cowork mode: Settings → MCP Servers → Add Server
Name: Firecrawl
URL: https://mcp.firecrawl.dev/{YOUR_API_KEY}/v2/mcp
```

### Credit Budget Awareness

| Tier | Credits/Month | Cost |
|------|--------------|------|
| Free | 500 | $0 |
| Hobby | 3,000 | $16/mo |
| Standard | 100,000 | $83/mo |

With v1.3's zero-credit scanning, **free tier is now more than sufficient** for all but heavy PDF extraction workflows.

### Graceful Degradation

| Workflow | With Firecrawl | Without Firecrawl |
|----------|---------------|-------------------|
| Bid scanning | scan.py (0 credits) | scan.py (0 credits) — no change |
| Form 470 lookup | Python requests (0 credits) | Python requests (0 credits) — no change |
| PDF extraction | Automated scrape | Manual upload |
| BOM verification | Web lookup | Training data / manual |
| Equivalence mapping | ✅ Works normally | ✅ Works normally |
| Zoho CRM records | ✅ Works normally | ✅ Works normally |

---

## Companion Skills (MANDATORY)

Before creating ANY Zoho CRM records or quotes, read the highest-version of each relevant companion skill:

| Skill | When Required |
|-------|--------------|
| **zoho-crm-v30** (or highest available) | ALL Zoho record creation (Deals, Quotes, Accounts, Contacts, Tasks) |
| **unified-product-catalog-v2-0** | SKU validation after equivalence mapping |
| **cisco-rep-locator-v1-1** | Cisco rep lookup for Meraki_ISR assignment |
| **stratus-quote-pdf-v2-0** | Bid package PDF generation |
| **zoho-crm-email-v3-5** | Any customer or Cisco rep email communication |
| **webex-bots-v1-6** (or highest) | SIRE network assessment requests to Jay Florendo |

### Zoho CRM v30 Rule Inheritance (MANDATORY)

ALL rules from the highest-version zoho-crm skill apply to E-Rate workflows. Critical rules to enforce:

1. **2-letter state abbreviation codes** — NEVER use full state names (e.g., "IA" not "Iowa")
2. **Contact_Name field** — Must be a lookup to an existing Contact record, not free text
3. **Cisco_Billing_Term** — Required on all quotes
4. **Shipping_Country** — Must be "United States" (not "US" or "USA")
5. **Product_Name format** — Use Zoho product lookup, never free text
6. **Quote note format** — Follow skill's standard note template
7. **Skip ecomm discount prompt** — E-Rate quotes are NEVER ecomm; skip the discount prompt entirely
8. **Pre-creation validation table** — Display for ALL Deals and Quotes before creating
9. **Picklist protection** — NEVER create new dropdown options
10. **Proceed-first deal defaults** — Create with Stratus Referal + Stratus Sales, ask about Cisco rep AFTER

---

## SLED Sales Optimization (NEW in v1.3)

### Urgency-Based Prioritization

When presenting the bid digest, always calculate and display days remaining:

```python
days_left = (deadline_date - today).days
urgency = "🔴 URGENT" if days_left <= 7 else \
          "🟡 Act Soon" if days_left <= 21 else \
          "🟢 Standard"
```

Sort Hot Leads by days_left ASC (most urgent first), not just score DESC.

### SIRE Flagging (Deals ≥ $200K)

When estimated deal value exceeds $200K list price, automatically flag for SIRE:

```
SIRE ELIGIBLE — Estimated list: $[X]K
Contact: Jay Florendo via Webex
Send: Customer Name, Country, State, Deal Size, Business Case (2-3 sentences),
      Competitive (Y/N), Competitor info, Cisco AM, Zoho Deal Link
```

The Hot Leads Excel sheet highlights SIRE-eligible rows in yellow.

### Territory Gap Detection

When scanning nationally (no state filter), identify state concentrations in the results:

```
After scan, group Hot Leads by state and display:
  TX: 12 hot leads  ← high-density territory
  IA: 8 hot leads
  CO: 3 hot leads
  ...

Suggest: "TX and IA are showing the most opportunity this cycle.
Run state-filtered scans to get more targeted lists?"
```

### Zoho Deal Deduplication Gate

Before creating any Deal from a scan result, check for existing records:

```python
# Search Zoho Deals for matching Form 470 number
criteria = f"(Description:contains:{application_number})"
existing = ZohoCRM_Search_Records(module='Deals', criteria=criteria)
if existing:
    → Show existing deal, ask user to confirm this is a duplicate or a new opportunity
    → Do NOT create duplicate deal
```

### Batch Qualification Workflow

For large scan results (15+ bids scoring 40+), use parallel sub-agents:

```
1. Run scan.py → get full scored list
2. Filter to 40+ scored bids
3. Launch parallel sub-agents (up to 10 at a time):
   - Each agent receives: application_number, billed_entity_name, state,
     category_two_description, allowable_contract_date, fit_score
   - Each agent parses equipment, maps to Cisco/Meraki, estimates value, flags risks
   - Returns JSON only (no prose)
4. Collect all results
5. Present consolidated approval table
6. Create Zoho Deals sequentially for approved bids
```

---

## Agent Workflows for Parallel Bid Evaluation

### When to Use Agent Workflows

| Scenario | Use Agent Workflows? | Reason |
|----------|---------------------|--------|
| Weekly bid scanner (15-20 bids to score) | YES | Evaluate all bids in parallel, 5-10x faster |
| Batch qualification (5-10 selected bids) | YES | Run Phase 0-1 on multiple bids simultaneously |
| Single bid deep-dive (one Form 470) | NO | Sequential by nature, no parallelism benefit |
| SODA API query | NO | Single script call returns all results |

### Sub-Agent Prompt Template

```
Evaluate this E-Rate Form 470 bid for Stratus Information Systems (Cisco/Meraki reseller).

Application: {application_number}
District: {billed_entity_name}
State: {billed_entity_state}
Deadline: {allowable_contract_date}
Fit Score: {fit_score}/100
Description: {category_two_description}

Tasks:
1. Parse equipment from the description (models, quantities, specs)
2. Map each competitor product to Cisco/Meraki equivalent
3. Estimate total list price using these approximate ranges:
   - APs: $800-1,500 each (depending on Wi-Fi 6E vs 7)
   - Switches 24-port: $2,000-4,500 each
   - Switches 48-port: $3,500-8,000 each
   - Firewalls: $1,500-15,000 each
   - Licenses: ~30% of hardware cost for 3-year, ~45% for 5-year
4. Identify red flags: MIBS, mandatory walkthrough, portal-only, BMIC
5. Recommend: pursue / review / pass

Return ONLY a JSON object (no markdown, no explanation):
{
  "district_name": "",
  "state": "",
  "application_number": "",
  "score": 0,
  "deadline": "",
  "competitor_products": [],
  "meraki_equivalents": [],
  "estimated_value": 0,
  "red_flags": [],
  "recommendation": "",
  "reasoning": ""
}
```

### Agent Workflow Rules

- **Verbosity cap**: Sub-agents must return JSON only, no prose (keeps context lean)
- **Parallel limits**: Launch up to 10 agents simultaneously. If more than 10 bids, batch in groups of 10.
- **No Zoho in sub-agents**: NEVER create CRM records inside sub-agents. Collect results first, then create records sequentially in the main thread after user approval.
- **Error handling**: If a sub-agent fails or times out, flag the bid for manual review.

---

## RFP PDF Extraction via Firecrawl

When `category_two_description` is insufficient (vague or "see attached"), extract full RFP details from the USAC portal PDF.

### PDF URL Pattern
```
https://publicdata.usac.org/EPC/Prd/Form470/{app_number}/{ben}/{doc_id}-{filename}
```

The `f470_number.url` field in the SODA response often contains the direct PDF URL.

### Extraction Workflow
```
1. Get PDF URL from f470_number.url or rfp_identifier field
2. firecrawl_scrape(url=PDF_URL, formats=["markdown"])
   → ~6 credits (1 per page, typical RFP is 4-8 pages)
3. Parse markdown output for: equipment specs, quantities, license terms,
   installation requirements, deadline, submission method
4. Feed parsed data into Phase 1 analysis
```

### Cost-Benefit Rule
- Only extract PDFs for bids scoring 40+ in fit-scoring
- For bids with complete `category_two_description`, skip PDF extraction entirely
- Maximum PDF budget: ~30 credits/week (5 PDFs at 6 credits each)

---

## BOM Swap Web Verification

Before mapping any competitor product to a Cisco/Meraki equivalent, verify the competitor's actual specifications via web lookup.

### Verification Workflow
```
1. Identify competitor product from RFP (e.g., "FortiAP 231F")
2. firecrawl_scrape the manufacturer's product page or datasheet:
   → https://www.fortinet.com/products/wireless/fortiap-231f (or similar)
   → 1 credit per product lookup
3. Extract: MIMO config, PoE requirements, port count, uplink speed, Wi-Fi standard
4. Map to Cisco/Meraki equivalent using verified specs (not assumed)
5. Document equivalence rationale with source URL
```

When to Verify: ALWAYS verify when the RFP lists specific competitor model numbers. Skip when the RFP uses generic descriptions ("Wi-Fi 6E access points, quantity 50").

---

## Phase 0: RFP Qualification

Determine viability before starting any work.

### Step 0a: USAC SODA Lookup

If the user provides a Form 470 application number, ALWAYS run a lookup first:

```python
import requests
params = {'application_number': '{APP_NUMBER}'}
resp = requests.get('https://opendata.usac.org/resource/jp7a-89nd.json', params=params, timeout=15)
record = resp.json()[0]
```

This provides: applicant name, BEN, state, contact info, category descriptions, deadline, and status — often enough to qualify without reading the full RFP.

### Step 0b: Viability Check

**Viable (Proceed):** Internal Connections (IC) = new equipment purchases. This is Stratus's focus.

**Non-Viable (Flag):** MIBS (Managed Internal Broadband Services) = managed services for existing equipment. Stratus cannot service non-Cisco gear.

**BMIC (Basic Maintenance):** License renewals for existing non-Cisco equipment. Not viable unless paired with IC.

**Mixed Form 470s:** Some RFPs combine IC and BMIC. Only quote the IC portion and document the exclusion in deal notes.

**Red Flags to Document:**
- Portal-only submission (extra admin burden, weigh against deal size)
- Notarized affidavit or bonding requirements
- Mandatory pre-bid site visits for small opportunities
- Very short deadlines with complex documentation
- Strong incumbent vendor relationships

**Decision Framework:**
- Under $15K with portal + complex requirements = likely pass (flag as "hail mary")
- Over $50K with email submission = pursue
- Over $200K = pursue aggressively, initiate SIRE network assessment via Jay Florendo

### Opportunity Fit Assessment

| Rating | Meaning | Action |
|--------|---------|--------|
| Strong Fit | IC-focused, clean displacement, email submission, $50K+ | Pursue aggressively |
| Partial Fit | Mixed IC/BMIC, can bid IC portion only, some exclusions | Pursue IC portion, document scope limitations |
| Marginal / Hail Mary | Small IC scope, high admin burden, submit anyway if low effort | Submit if convenient, don't invest significant time |
| Not a Fit / Pass | MIBS-only, BMIC-only, or deal-breaking requirements | Document reasoning, close or skip |

**Indicators of a Strong Fit:**
- District is requesting Cisco/Meraki by name
- Primarily IC (new equipment), minimal or no BMIC/MIBS components
- Email submission accepted
- Equipment value over $50K
- Wireless refresh or full network infrastructure (APs + switches)
- Standard license terms (3-5 year co-term)

**Indicators of a Poor Fit (flag or pass):**

1. **MIBS-Only RFP:** Managed services for existing non-Cisco gear. Stratus cannot service Fortinet, Aruba, Ruckus, or Ubiquiti. Example: Dodgeville SD was 100% MIBS for existing Fortinet/Extreme/Ruckus.

2. **BMIC-Only (License Renewals for Non-Cisco):** District renewing licenses on competitor hardware. Example: Sergeant Bluff-Luton had 145 Aruba APs as BMIC — only 6 new APs + 3 switches were quotable.

3. **Firewall-Only with High Admin Burden:** 1-3 firewalls ($10-15K total) with portal submission + notarized docs. Example: New Lisbon was 3x MX85 with notarized Noncollusion Affidavit.

4. **Mandatory Pre-Bid Site Visits:** Engineers require minimum $2,000 upfront for paid site visits. Example: Spirit Lake CSD required site visit for fiber routing.

5. **Strong Incumbent with Co-Term Language:** RFP using "co-term licenses on existing gear" language signals expansion within competitor ecosystem. Example: Interstate 35 CSD was a Fortinet shop expanding Fortinet gear.

6. **One-Person IT Department Seeking Managed Services:** Small districts wanting MSP relationship (monitoring, help desk) rather than equipment procurement. Stratus is not an MSP.

7. **Non-Cisco Products Required in BOM:** UPS units, structured cabling, racks not in Stratus catalog. Exclude and note for district to procure separately.

8. **Portal-Only Submission for Sub-$15K Deals:** Admin overhead of vendor portals may not justify small opportunities.

---

## Phase 1: RFP Analysis & Equivalence Mapping

Parse the Form 470 and RFP documents for:
1. Equipment specs (models, quantities, ports, PoE, MIMO)
2. License term preference (1, 3, 5, or 7 year). If "3-5 year preference," lean toward 5-year
3. Installation requirements
4. Submission deadline (exact date/time/timezone)
5. Work window dates (typically summer for K-12)
6. Contact info (direct contact AND E-Rate consultant if applicable)
7. Submission method (email, portal, mail)
8. Number of eligible entities/buildings

### Step 1a: Web Verification of Competitor Specs

For each competitor product in the RFP:
1. `firecrawl_scrape` manufacturer's product page (1 credit)
2. Extract: Wi-Fi standard, MIMO, PoE class, port count, uplink speed
3. Use VERIFIED specs for equivalence mapping
4. Document source URL in equivalence rationale

Skip web verification only when the RFP uses generic descriptions without specific model numbers.

### Equivalence Mapping Rules

**Switching:**
- Layer 2 edge/access → MS130 series (8/24/48-port, PoE variants)
- Layer 2 with 10G uplinks → MS150 series
- Layer 3 aggregation/distribution → **C9300-M series** (ALWAYS prefer over pure Meraki MS for L3)
- Core/aggregation 25G/mGig → C9300X series
- mGig access layer → C9300-48UXM-M or C9300-48UN-M

**Wireless:**
- Wi-Fi 6E indoor → CW9166I-MR
- Wi-Fi 7 indoor → CW9176I-RTG (standard) or CW9172I-RTG (lower cost)
- Wi-Fi 7 outdoor → CW9178I-RTG
- Indoor mesh/hard-to-cable → Use the SAME indoor AP model as the deployment (CW models support mesh). **MR86 is OUTDOOR ONLY, never use for indoor mesh.**
- Legacy indoor budget → MR36-HW

**Firewalls:**
- Small branch → MX67-HW or MX68-HW
- Medium → MX85-HW
- Large/main site → MX105-HW
- Enterprise → MX250-HW or MX450-HW

**Document equivalence rationale** for each mapping: port count/type, PoE budget, MIMO config, uplink speed, management platform. Include source URL from web verification.

### Known Gaps to Address

- Aruba CX 6300M 50G SFP56 uplinks vs C9300-M 10G SFP+: 10G is more than sufficient for K-12 environments. State this explicitly.
- If Wi-Fi 6E and Wi-Fi 7 price identically, always lead with Wi-Fi 7 (future-proof, matches district preference).

### Step 1b: SKU Validation (MANDATORY)

```
1. Parse mapped SKUs: separate hardware from licenses, note quantities
2. Validate each SKU against unified-product-catalog-v2-0 or Zoho Products module:
   - Confirm SKU exists and is active (not EOL)
   - Verify correct suffix per suffix rules below
   - Confirm license pairing matches hardware and requested term
3. Display validation table:
   | Requested SKU | Validated SKU | Status | Notes |
   |---------------|---------------|--------|-------|
   | CW9176I-RTG   | CW9176I-RTG   | ✓ Active | Wi-Fi 7 indoor |
   | LIC-ENT-5YR   | LIC-ENT-5YR   | ✓ Active | 5-year co-term |
   | MS130-48P     | MS130-48P     | ✓ Active | No suffix needed |
4. If ANY SKU is invalid, EOL, or ambiguous → STOP and clarify before proceeding
```

---

## Phase 2: Zoho CRM Setup

Read the **highest-version zoho-crm skill available** before creating any records.

### Account
- Search existing accounts first (avoid duplicates)
- If new: populate ALL address fields (Billing AND Shipping)
- **Set Tax_Type = "Tax Exempt"** at Account level
- **State fields: use 2-letter abbreviation codes only** (e.g., "IA" not "Iowa")
- **Shipping_Country: "United States"** (not "US" or "USA")

### Contact
- Link to Account via Contact_Name lookup (never free text)
- Include: first name, last name, email, phone, title
- Create records for BOTH tech contact AND E-Rate consultant if applicable

### Deal
- **Name format:** `[District Name] - E-Rate FY[XX] [Project Type] (Form 470 #[number])`
- Stage: "Qualification"
- Type: "E-Rate" (or "RHC" for Healthcare Connect Fund)
- **Lead_Source:** Default to **"Stratus Referal"** (one R, correct Zoho picklist value)
  - Change to "Meraki ISR Referal" only if a Cisco rep explicitly referred the deal
  - NEVER create new picklist options. If unsure, STOP and ask.
- **Meraki_ISR (Proceed-First Logic):**
  - DEFAULT: Set to "Stratus Sales" (ID: 2570562000027286729)
  - Create the deal first with this default
  - AFTER creation: ask if a Cisco rep is involved
  - If yes: use cisco-rep-locator-v1-1 skill to find the rep, then update
- Description: Form 470 number, BEN, entity count, scope summary, work window, deadline, submission contact
- **Deduplication gate**: Before creating, search Zoho for existing deals containing the Form 470 application number in Description

### Task
- Subject: "Submit E-Rate Bid - [District Name] (Form 470 #[number])"
- Due Date: **2 business days BEFORE actual deadline** (buffer)
- Priority: High
- Link to Deal

### Deal Notes
- After creating quote, add note with Claude chat thread link: `https://claude.ai/chat/{uri}`

### Pre-Creation Validation (MANDATORY)

| Field | Value | Status |
|-------|-------|--------|
| Account_Name | [value] | ✓ or ⚠️ |
| Tax_Type | Tax Exempt | ✓ |
| Billing_State / Shipping_State | [2-letter code] | ✓ or ⚠️ |
| Shipping_Country | United States | ✓ |
| Deal_Name | [format check] | ✓ |
| Lead_Source | Stratus Referal | ⚠️ Confirm |
| Meraki_ISR | Stratus Sales | ✓ (default) |
| Contact_Name | [lookup reference] | ✓ |

If ANY field is missing or ambiguous, STOP and ask.

---

## Phase 3: Quote Creation

### Equipment Quote(s)

**Tax Exemption (CRITICAL):**
- Set `Tax_Type` = "Tax Exempt" at the **quote level**
- NEVER modify taxes at line item level
- Also ensure Account has Tax_Type = "Tax Exempt"

**Licensing Rules (CRITICAL):**
- **ALWAYS use co-term licensing:** LIC-ENT-xYR
- **NEVER use CISCO-NETWORK-SUB** (subscription model) unless explicitly requested
- Wi-Fi 7 APs (CW9176I-RTG, CW9172I-RTG, CW9178I-RTG) ALL work with co-term LIC-ENT-xYR licenses
- Match license term to RFP preference. No preference stated → default 3-year

**License Pairing Reference:**

| Hardware Family | License Pattern | Example |
|----------------|----------------|---------|
| CW/MR APs (all) | LIC-ENT-{x}YR | LIC-ENT-5YR |
| MS130 8-port | LIC-MS130-CMPT-{x}Y | LIC-MS130-CMPT-5Y |
| MS130 24-port | LIC-MS130-24-{x}Y | LIC-MS130-24-3Y |
| MS130 48-port | LIC-MS130-48-{x}Y | LIC-MS130-48-5Y |
| MS150 24-port | LIC-MS150-24-{x}Y | LIC-MS150-24-3Y |
| MS150 48-port | LIC-MS150-48-{x}Y | LIC-MS150-48-5Y |
| C9300 24-port | LIC-C9300-24E-{x}Y | LIC-C9300-24E-5Y |
| C9300 48-port | LIC-C9300-48E-{x}Y | LIC-C9300-48E-3Y |
| C9300X 24-port | LIC-C9350-24E-{x}Y | LIC-C9350-24E-5Y |
| MX firewalls | LIC-MX{model}-SEC-{x}YR | LIC-MX105-SEC-5YR |

**SKU Suffix Rules:**

| Product Type | Suffix | Example |
|-------------|--------|---------|
| CW Wi-Fi 6E | -MR | CW9166I-MR |
| CW Wi-Fi 7 | -RTG | CW9176I-RTG |
| MR/MX/MV/MG/MT | -HW | MR36-HW, MX105-HW |
| MS switches | No suffix | MS130-48P |
| Z-series | -HW | Z4C-HW |

**Discounts:** NEVER auto-apply. Wait for Cisco approval. **Skip the ecomm discount prompt** — E-Rate quotes are never ecomm.

**Line Item Descriptions:** Include equivalence notes.
Format: `[SKU] | [Product Name] | Equivalent to: [Competitor] | [Key specs]`

### Multi-Building Quote Splitting

When the Form 470 covers multiple buildings (check `number_of_eligible_entities` from SODA data):
- **Create separate quotes per building** when the RFP itemizes equipment by location
- This simplifies Form 471 filing, where districts must allocate costs per eligible entity
- Name format: `[District Name] - E-Rate FY[XX] [Building Name] (Form 470 #[number])`

### Installation Services Quote (Separate)

E-Rate requires installation quoted separately from equipment.

**Tiered Installation Estimates:**

| Equipment Type | Quantity Range | Hours per Unit | Notes |
|---------------|---------------|----------------|-------|
| Access Points | 1-10 | 1.5 hours | Includes mounting, cabling, basic config |
| Access Points | 11-50 | 1.25 hours | Efficiency gains from batch deployment |
| Access Points | 50+ | 1.0 hour | Large-scale deployment with templates |
| Switches | Any | 2-3 hours each | Stacking, VLAN config, uplink verification |
| Firewalls | Any | 3-4 hours each | Policy migration, VPN setup, testing |

**Additional Line Items:**
- SKU: SIS101 at $200/hour
- **Project Management overhead** for deals over $100K list: add 10-15% of total installation hours
- Travel: separate line item for non-metro sites ($500-$1,500 typical)
- Multi-building: add travel time between sites
- Knowledge transfer: 2-4 hours for IT staff training

**IMPORTANT:** Always prompt for engineer input on complex deployments (multi-building, fiber runs, outdoor APs, legacy infrastructure removal).

### Items to Exclude
- Non-Cisco products (UPS, cabling infrastructure, existing equipment maintenance)
- Document exclusions in deal notes

---

## Phase 4: Cisco Discount Request

After quotes created at list price:
1. Use **cisco-rep-locator-v1-1** skill to identify the correct Cisco rep for the territory
2. Provide: customer name/address, Deal ID, full MSRP breakdown, competitive situation, deadline
3. Wait for discount approval before finalizing

**Do NOT hardcode a specific Cisco rep.** Territory assignments change.

---

## Phase 5: Bid Package Generation

**ONLY generate when explicitly requested** (after Cisco discount confirmed).

**Contents:**
1. Cover Letter (SPIN: 143052656, proposal summary, enclosed docs, E-Rate compliance statement)
2. Equipment quote(s) with discounted pricing (include discount column)
3. Installation services quote
4. Product equivalence documentation (spec comparison tables, including source URLs from web verification)
5. K-12 references (3 recent projects)

Use stratus-quote-pdf skill for quote formatting, pdf skill for full package assembly.

**Branding:** Stratus teal (#00B5AD or #3CBFBF), professional header on each page, footer with page numbers.

**Standard K-12 References:**
- Buffalo Trails Elementary (Denver, CO)
- Westchester Country Day School
- Holy Comforter Episcopal School

**Healthcare References (for RHC/Form 461):**
- Tepeyac Community Health Center (Denver, CO)
- Resilient Health (Phoenix, AZ)
- Northern Nevada Hopes (Reno, NV)

---

## Phase 6: Post-Bid Actions

### Opportunity Assessment Email Draft
Generate an email draft (no specific addressee) with:
1. Opportunity recap (district, Form 470#, scope, estimated list value)
2. **Fit rating** (Strong Fit, Partial Fit, Marginal/Hail Mary, or Pass) with specific reasoning
3. BOM concerns (imperfect matches, excluded items, uplink gaps)
4. Red flags (non-Cisco requirements, site visits, portal submissions, MIBS/BMIC components)
5. Recommended next steps

### CRM Updates
- Update Deal stage to "Proposal/Price Quote"
- Add note: submission method, date/time, confirmation receipt
- Set follow-up task after bid evaluation period

### SIRE Network Assessment (Deals over $200K)
Send request to Jay Florendo via Webex with: Customer Name, Country (USA), State, Deal Size (List), Business Case (2-3 sentences), Competitive (yes/no), Competitor Info, Cisco AM Name, Zoho Deal Link.

---

## CCW Import CSV Format

8-column format for Cisco Commerce Workspace import. Co-term items have ALL term fields blank.

```
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
C9300-48P-M,8,,,,,,
LIC-C9300-48E-5Y,8,,,,,,
CW9176I-RTG,100,,,,,,
LIC-ENT-5YR,100,,,,,,
```

---

## Firecrawl Agent Fallback

For edge cases where district websites require navigation (vendor registration portals, document repositories):

```
firecrawl_agent(
  prompt="Navigate to the RFP documents section and find network equipment bid specifications for Form 470 #{app_number}",
  urls=["https://district-website.org/bids"]
)
```

- Agent uses 0 credits but takes ~20 seconds
- Use ONLY when `firecrawl_scrape` returns empty or insufficient results
- Poll `firecrawl_agent_status` every 15-30 seconds for up to 3 minutes

---

## Common E-Rate Consultants

- **David Fringer** (david.fringer@iowaaea.org) — Iowa AEA, appears across many Iowa district RFPs. Create Contact records for both the consultant and district tech contact.

---

## Platform Compatibility

| Workflow | Claude.ai Web | Cowork Desktop | Notes |
|----------|--------------|----------------|-------|
| Bid scanner (scan.py) | ✅ | ✅ | Python requests, 0 credits |
| SODA API lookup | ✅ | ✅ | Python requests, 0 credits |
| PDF extraction | ✅ | ✅ | Firecrawl, ~6 credits/doc |
| BOM web verification | ✅ | ✅ | Firecrawl, 1 credit/product |
| Zoho CRM records | ✅ | ✅ | |
| CCW submission | ❌ | ✅ | Requires Chrome browser automation |
| Bid package PDF | ✅ | ✅ | |
| Excel export | ✅ | ✅ | scan.py generates automatically |

---

## Rules Summary

| Rule | Details |
|------|---------|
| Pre-Scan Prompt | ALWAYS ask for state, days, min score before scanning nationally |
| API Method | Python requests first (0 credits), Firecrawl fallback only |
| FY Calculation | Always use dynamic `current_erate_fy()` — NEVER hardcode year |
| Year Filter | ALL SODA queries must include `funding_year` to prevent old record returns |
| Tax Exemption | Tax_Type = "Tax Exempt" at Quote AND Account level. Never line items. |
| Bid Package Timing | Zoho quotes first. PDF only when explicitly requested. |
| Licensing | Co-term (LIC-ENT-xYR). Never CISCO-NETWORK-SUB. Match term to RFP. |
| Wi-Fi 7 Licensing | CW9176I/CW9172I/CW9178I all use co-term LIC-ENT-xYR. |
| Indoor Mesh | Same indoor AP model. MR86 is OUTDOOR ONLY. |
| Discounts | Never auto-apply. Wait for Cisco approval. Skip ecomm prompt. |
| L3 Switches | C9300-M series over pure Meraki MS for aggregation. |
| Lead Source | "Stratus Referal" (one R) default. Only change if Cisco rep involved. |
| Meraki_ISR | Default Stratus Sales. Create deal first, ask about rep after. |
| SPIN | 143052656 |
| Deal Notes | Add Claude chat thread link after quote creation. |
| Post-Quote | Generate assessment email with fit evaluation and red flags. |
| Validation | Display field table before creating Deal or Quote. |
| Communication | Never send without approval. Draft and present first. |
| IC vs MIBS | Only quote Internal Connections. Flag MIBS/BMIC as non-viable. |
| Fit Assessment | Rate every opportunity (Strong/Partial/Marginal/Pass). |
| State Codes | 2-letter abbreviations only (IA, not Iowa). |
| SKU Validation | Validate against unified-product-catalog before quote creation. |
| BOM Verification | Firecrawl web lookup of competitor specs before mapping. |
| Companion Skills | Read highest-version of each companion skill before CRM operations. |
| Multi-Building | Separate quotes per building when RFP itemizes by location. |
| Installation | Tiered hours formula + prompt for engineer input on complex jobs. |
| Deduplication | Check Zoho for existing deals with same Form 470 # before creating. |
| SIRE | Auto-flag all deals ≥ $200K est list for SIRE via Jay Florendo. |
| Urgency Sort | Sort Hot Leads by deadline ASC (most urgent first), not score only. |
| Cascade | NEVER create Zoho records inside sub-agents. Main thread only. |

---

## Workflow Quick Reference

```
Bid Scanner (On-Demand or Scheduled)
    → Pre-Scan Filter Prompt (state, days, min score)
    → Run scripts/scan.py --state [X] --days [N] --min-score [M]
    → Script auto-paginates, scores, and exports Excel
    → Present Excel via present_files
    → Optional: parallel sub-agents for 40+ scored bids
    → Present digest → On approval: create Zoho Deals

Form 470 Received (or Application Number Provided)
    → Step 0a: USAC SODA lookup via Python requests (0 credits)
    → Phase 0: Qualify (IC vs MIBS, red flags, fit assessment)
    → Phase 1: Analyze RFP, verify competitor specs (Firecrawl), map equivalences, validate SKUs
    → Phase 2: Zoho records (Account → Contact → Deal → Task) with proceed-first defaults
    → Phase 3: Quote(s) at list price, per-building if applicable, chat link in deal notes
    → Phase 4: Submit to Cisco rep for discount (via cisco-rep-locator)
    → [WAIT for discount approval]
    → Phase 5: Bid package PDF (only when requested)
    → Phase 6: Submit, update CRM, assessment email draft
```

---

## Changelog

### v1.3 (Current)
- **Zero-credit API access**: Python `requests` library replaces Firecrawl for all SODA JSON queries — saves 15-30 credits/week (Firecrawl retained as fallback only)
- **Dynamic funding year**: `current_erate_fy()` auto-calculates current E-Rate FY based on today's month — eliminates hardcoded `2026` that would fail in future years
- **Root cause fix — old records**: All SODA queries now enforce `funding_year`, `f470_status='Certified'`, and `allowable_contract_date > today` — prevents FY2017/2020/2024 records from appearing in current scan results
- **Pre-scan filter prompt**: Asks for state, deadline window, and min score before any scan — prevents unneeded national over-scans
- **Bundled `scripts/scan.py`**: Standalone CLI script with argparse interface (`--state`, `--days`, `--min-score`, `--output`) — handles pagination, deduplication, scoring, and Excel export in one run
- **Excel export with hyperlinks**: `scan.py` generates 4-sheet workbook (Bid Digest, Hot Leads, Warm Leads, Legend) — application numbers are hyperlinked to Form 470 PDF via `f470_number.url` field or USAC portal fallback URL
- **SIRE auto-flagging**: Hot Leads sheet highlights deals with estimated value ≥ $200K in yellow with SIRE label
- **Firecrawl fallback signal**: When requests fails, script prints `FIRECRAWL_FALLBACK_REQUIRED` and `FALLBACK_URL` for Claude to pick up and use
- **Auto-pagination**: `scan.py` loops via `$offset` until all records fetched — no more single-page 50-result limit
- **Territory gap detection**: After national scan, groups Hot Leads by state to identify high-density territories
- **Zoho deduplication gate**: Checks for existing deals with matching Form 470 application number before creating new record
- **Urgency countdown**: Days-remaining column in Excel, Hot Leads sorted deadline-first (most urgent at top)
- **SLED optimization section**: Batch qualification workflow, urgency prioritization, territory analysis, SIRE auto-flag documentation

### v1.2
- USAC SODA API integration via Firecrawl scrape (1 credit per query)
- Weekly bid scanner with fit-scoring (0-100) and digest generation
- RFP PDF extraction via Firecrawl (~6 credits per doc)
- BOM swap web verification via Firecrawl
- Zoho CRM v30 rule inheritance checklist
- SKU validation gate
- Proceed-first deal defaults
- Tiered installation estimates
- Multi-building quote splitting guidance
- Firecrawl MCP setup guide with graceful degradation
- Agent workflows for parallel bid evaluation
- Platform compatibility table

### v1.1
- Initial release with Phases 0-6
- Opportunity Fit Assessment with 8 poor-fit indicators
- Equivalence mapping rules for switching, wireless, firewalls
- License pairing reference and SKU suffix rules
- CCW Import CSV format
- Common E-Rate consultants reference
