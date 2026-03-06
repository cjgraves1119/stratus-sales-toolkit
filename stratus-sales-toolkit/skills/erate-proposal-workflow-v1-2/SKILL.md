---
name: erate-proposal-workflow-v1-2
description: e-rate form 470 proposal workflow with firecrawl-powered usac soda api integration, automated weekly bid scanner with fit-scoring algorithm, form 470 instant lookup, rfp pdf extraction, zoho-crm-v30 rule inheritance, mandatory sku validation against live catalog, proceed-first deal defaults, tiered installation estimates, and multi-building quote splitting guidance. covers rfp qualification, equivalence mapping, zoho crm setup, quote creation, cisco discount coordination, bid package generation, and post-submission actions.
---

# E-Rate / Form 470 Proposal Workflow v1.2

Complete workflow for analyzing E-Rate Form 470 RFPs, mapping competitor equipment to Cisco/Meraki equivalents, creating Zoho CRM records and quotes, coordinating Cisco discounts, and generating bid packages for K-12 school districts. Now includes automated USAC data lookups and weekly bid scanning via Firecrawl.

## What Changed in v1.2

| Change | v1.1 | v1.2 |
|--------|------|------|
| USAC data lookup | Manual (user provides RFP) | Firecrawl SODA API auto-pull (1 credit per query) |
| Weekly bid scanning | Not available | Automated fit-scoring against 50+ open bids |
| RFP PDF extraction | Manual upload only | Firecrawl scrape (~6 credits per PDF) |
| BOM swap verification | Trust user-provided specs | Mandatory Firecrawl web verification of competitor specs |
| Zoho CRM rules | Generic "read zoho-crm skill" | Explicit zoho-crm-v30 rule inheritance with checklist |
| SKU validation | Not enforced | Mandatory validation against unified-product-catalog-v2-0 |
| Deal defaults | Hardcoded Eddy Zertuche | Proceed-first with Stratus Sales defaults, cisco-rep-locator after |
| Installation estimates | Vague "1-2 hours per AP" | Tiered formula + prompt for engineer input |
| Multi-building quotes | Not addressed | Guidance for Form 471 per-building filing |
| Agent workflows | Not available | Parallel bid evaluation and batch qualification via sub-agents |
| Firecrawl MCP setup | Not documented | Step-by-step setup guide with graceful degradation |
| Skill references | "Read the zoho-crm skill" | "Read the highest-version zoho-crm skill available" |

## When to Use

- User uploads or references a Form 470 / E-Rate RFP
- User mentions E-Rate, Form 470, school district network bid, or competitive displacement
- User asks to quote Meraki equipment against Aruba, Extreme, Ruckus, Ubiquiti, or Fortinet for a school district
- User references Healthcare Connect Fund (HCF/RHC) Form 461 opportunities
- User asks to scan for open E-Rate bids or check USAC for opportunities
- User provides a Form 470 application number for lookup
- Keywords: "E-Rate," "Form 470," "Form 461," "bid package," "USAC," "BEN," "Internal Connections," "bid scanner," "open bids"

## Company Details

- Company: Stratus Information Systems (Cisco-exclusive reseller, Meraki specialist)
- USAC SPIN: **143052656**
- Primary Contact: Chris Graves, Regional Sales Director, chrisg@stratusinfosystems.com, (888) 366-4911
- Installation SKU: SIS101 at $200/hour

## Firecrawl MCP Setup (REQUIRED for Automated Workflows)

The USAC SODA API lookups, weekly bid scanner, PDF extraction, and BOM verification workflows all require Firecrawl MCP. This section guides setup for any user.

### Pre-Flight Check

Before running any Firecrawl-powered workflow, verify Firecrawl is available:

```
IF firecrawl_scrape tool is available:
  → Firecrawl is connected. Proceed normally.

IF firecrawl_scrape tool is NOT available:
  → Check if user is Chris Graves (chrisg@stratusinfosystems.com)
    → YES: Firecrawl MCP should already be configured. Troubleshoot connection.
    → NO: Guide user through setup below.
```

### Setup Instructions (Non-Chris Users)

If you don't have Firecrawl MCP configured yet, follow these steps:

**Step 1: Create a Firecrawl Account**
1. Go to https://www.firecrawl.dev
2. Sign up for a free account (500 credits/month, no credit card required)
3. After signup, navigate to your dashboard

**Step 2: Get Your API Key**
1. In the Firecrawl dashboard, find the API Keys section
2. Copy your API key (starts with `fc-`)
3. Keep this key private, it's tied to your credit balance

**Step 3: Construct Your MCP Server URL**

Replace `{YOUR_API_KEY}` with your actual key:

```
https://mcp.firecrawl.dev/{YOUR_API_KEY}/v2/mcp
```

Example: If your key is `fc-abc123def456`, your URL is:
```
https://mcp.firecrawl.dev/fc-abc123def456/v2/mcp
```

**Step 4: Add to Claude**

**For Claude Desktop (Cowork mode):**
1. Open Claude Desktop Settings
2. Go to the MCP Servers section
3. Click "Add MCP Server"
4. Name: `Firecrawl`
5. URL: paste your constructed URL from Step 3
6. Save and restart Claude if prompted

**For Claude.ai (Web):**
1. Navigate to Claude.ai Settings → Integrations → MCP Servers
2. Click "Add Server"
3. Name: `Firecrawl`
4. Server URL: paste your constructed URL from Step 3
5. Save

**Step 5: Verify Connection**

Ask Claude to run a test query:
```
"Test Firecrawl by scraping https://opendata.usac.org/resource/jp7a-89nd.json?$limit=1"
```

If you get a JSON response with Form 470 data, you're good to go.

### Credit Budget Awareness

| Tier | Credits/Month | Cost |
|------|--------------|------|
| Free | 500 | $0 |
| Hobby | 3,000 | $16/mo |
| Standard | 100,000 | $83/mo |

Typical E-Rate weekly usage: 15-45 credits. Free tier is sufficient for most users.

### Graceful Degradation (No Firecrawl Available)

If Firecrawl is not configured and the user declines to set it up, the skill still works but with reduced automation:

| Workflow | With Firecrawl | Without Firecrawl |
|----------|---------------|-------------------|
| Form 470 lookup | Automated SODA query | User must provide RFP manually |
| Weekly bid scanner | Automated scanning + fit-scoring | Not available |
| PDF extraction | Automated scrape | User uploads PDF manually |
| BOM verification | Web lookup of competitor specs | User provides specs or Claude uses training data |
| Equivalence mapping | ✅ Works normally | ✅ Works normally |
| Zoho CRM records | ✅ Works normally | ✅ Works normally |
| Quote creation | ✅ Works normally | ✅ Works normally |

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
| **webex-bots-v1-6** | SIRE network assessment requests to Jay Florendo |

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

## USAC SODA API Integration (NEW in v1.2)

### Overview

The USAC Open Data Platform provides public access to all E-Rate Form 470 filings via the Socrata SODA API. Data is updated daily, requires no authentication, and can be queried via Firecrawl scrape for 1 credit per request (up to 50 results per query).

### Datasets

| Dataset | Resource ID | Contents |
|---------|------------|----------|
| Form 470 Basic Info | `jp7a-89nd` | 56 fields: applicant, BEN, contact info, category descriptions, dates, status |
| Services Requested | `39tn-hjzv` | Service types, functions, quantities per Form 470 |

### Query Patterns

**Single Form 470 Lookup (1 credit):**
```
firecrawl_scrape → https://opendata.usac.org/resource/jp7a-89nd.json?application_number={APP_NUMBER}
```

**Services Requested (1 credit):**
```
firecrawl_scrape → https://opendata.usac.org/resource/39tn-hjzv.json?application_number={APP_NUMBER}
```

**Keyword Search (1 credit for up to 50 results):**
```
firecrawl_scrape → https://opendata.usac.org/resource/jp7a-89nd.json?$where=upper(category_two_description) like '%25MERAKI%25'&funding_year=2026&$limit=50
```

**Open Bid Scanner (1 credit for 50 results):**
```
firecrawl_scrape → https://opendata.usac.org/resource/jp7a-89nd.json?$where=allowable_contract_date > '{TODAY}' AND funding_year='2026' AND f470_status='Certified' AND category_two_description IS NOT NULL&$limit=50&$select=application_number,billed_entity_name,billed_entity_state,contact_name,contact_email,technical_contact_email,allowable_contract_date,category_two_description,rfp_identifier&$order=allowable_contract_date ASC
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
| `rfp_identifier` | Link to RFP document on USAC portal |
| `number_of_eligible_entities` | Building count (triggers multi-building quote logic) |

### Data Completeness

Approximately 60-70% of Form 470 filings include complete BOM details in the `category_two_description` field, eliminating the need for PDF extraction. The remaining 30-40% contain vague descriptions like "see RFP for details" and require PDF follow-up.

**Decision Logic:**
```
IF category_two_description contains specific SKUs, model numbers, or port counts:
  → Sufficient for fit-scoring AND equivalence mapping
  → Proceed to Phase 1 analysis

IF category_two_description is vague ("see attached RFP," "see RFP for details"):
  → Check rfp_identifier for PDF link
  → Use Firecrawl scrape on PDF (~6 credits per document)
  → If no PDF available, flag for manual review
```

---

## Automated Weekly Bid Scanner (NEW in v1.2)

### Purpose

Scan all open E-Rate Form 470 bids weekly to identify opportunities that are strong fits for Stratus (Cisco/Meraki-focused, equipment-only, low admin burden).

### Fit-Scoring Algorithm

Each bid is scored 0-100 across five dimensions:

| Dimension | Points | Trigger |
|-----------|--------|---------|
| CISCO_MERAKI | +40 | Keywords: meraki, cisco catalyst, c9300, c9200, cw916, cw917, ms120, ms125, ms225, ms250, ms350, ms390, ms425, mx4, mx6, mx8, mx9, mx1, mr , mr-, mr4, mr5, mr7, lic-ent |
| COMPETITIVE_SWAP | +25 | Keywords: fortinet, fortigate, fortiap, aruba, ruckus, extreme, sonicwall, palo alto, juniper, ubiquiti, unifi |
| NO_WALKTHROUGH | +15 | ABSENCE of: walkthrough, walk-through, walk through, site visit |
| EQUIP_ONLY | +10 | ABSENCE of: mibs, managed internal broadband, managed services |
| SKU_SPECIFIC | +10 | Presence of specific model numbers (regex: pattern matching alphanumeric-dash sequences like CW9176I, MS130-48P, FortiAP-231F) |

**Score Interpretation:**

| Score | Rating | Action |
|-------|--------|--------|
| 70-100 | Hot Lead | Auto-create Zoho Deal + flag for immediate action |
| 40-69 | Warm Lead | Include in weekly digest, review manually |
| 20-39 | Cool | Include in digest as low-priority |
| 0-19 | Pass | Exclude from digest |

### Weekly Scanner Workflow

```
1. Query SODA API for all open certified bids (funding_year=2026, allowable_contract_date > today)
   → 1 credit per 50 results (typically 2-4 credits for full scan)

2. Run fit-scoring algorithm on each bid's category_two_description

3. Sort by score descending

4. For bids scoring 40+:
   a. Pull full application details (1 credit each for top 10)
   b. Check services_requested dataset for service types
   c. Generate digest with: district name, state, score, deadline, key equipment, fit reasoning

5. Present digest for review:
   → Hot Leads (70+): recommend immediate Zoho Deal creation
   → Warm Leads (40-69): recommend manual review
   → Include deadline countdown for urgency

6. On approval: create Zoho Deals for selected opportunities
```

### Credit Budget

| Step | Credits | Frequency |
|------|---------|-----------|
| Initial scan (50 results) | 1-4 | Weekly |
| Top-10 detail pulls | 10 | Weekly |
| PDF extraction (if needed) | ~6 each | As needed |
| **Estimated weekly total** | **15-30** | Out of 500/month |

---

## Agent Workflows for Parallel Bid Evaluation (NEW in v1.2)

### When to Use Agent Workflows

Agent sub-agents (via the `Agent` tool with `subagent_type: "general-purpose"`) enable parallel evaluation of multiple bids simultaneously, similar to how the daily-task-engine evaluates CRM tasks in parallel. This dramatically reduces wall-clock time for batch operations.

| Scenario | Use Agent Workflows? | Reason |
|----------|---------------------|--------|
| Weekly bid scanner (15-20 bids to score) | YES | Evaluate all bids in parallel, 5-10x faster |
| Batch qualification (5-10 selected bids) | YES | Run Phase 0-1 on multiple bids simultaneously |
| Single bid deep-dive (one Form 470) | NO | Sequential by nature, no parallelism benefit |
| SODA API query | NO | Single API call returns all results at once |

### Parallel Bid Evaluation (Weekly Scanner Enhancement)

When the weekly scanner returns 15+ bids scoring 40+, use sub-agents to evaluate them in parallel instead of sequentially:

```
1. Run SODA query for all open certified bids (1-4 credits)
2. Run fit-scoring algorithm on all results (local, no credits)
3. Filter to bids scoring 40+ (typically 10-20 bids)
4. Launch parallel sub-agents (up to 10 at a time):

   For each bid in the 40+ batch, launch an Agent with:
   - subagent_type: "general-purpose"
   - prompt: Include the bid's application_number, billed_entity_name, state,
     category_two_description, allowable_contract_date, and fit score.
     Instruct the agent to:
     a. Parse the category_two_description for equipment details
     b. Identify competitor products and quantities
     c. Map to Cisco/Meraki equivalents (use equivalence rules from this skill)
     d. Estimate deal value (list price)
     e. Flag any red flags (MIBS, walkthrough, portal-only)
     f. Return JSON with: district_name, state, score, deadline,
        competitor_products, meraki_equivalents, estimated_value,
        red_flags, recommendation (pursue/review/pass)

5. Collect all sub-agent results
6. Sort by score descending, then by deadline ascending
7. Present consolidated digest table for approval
```

**Sub-Agent Prompt Template:**
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

### Batch Bid Qualification

When a user provides multiple Form 470 application numbers (e.g., "Qualify these 8 bids for me"), launch parallel agents to run Phase 0 and Phase 1 on each:

```
1. For each application number, launch an Agent:
   - subagent_type: "general-purpose"
   - prompt: Include the application number and instruct the agent to:
     a. Query SODA API via Firecrawl for the application details
     b. Run Phase 0 qualification (IC vs MIBS, red flags)
     c. Run fit assessment scoring
     d. If scoring 40+: parse equipment, map equivalences
     e. Return JSON with qualification result

2. Collect results from all agents
3. Present batch qualification table:

   | # | District | State | Score | Value Est. | Deadline | Fit | Action |
   |---|----------|-------|-------|-----------|----------|-----|--------|
   | 1 | West Jefferson Hills | PA | 85 | $245K | Apr 15 | Strong | Pursue |
   | 2 | Sergeant Bluff-Luton | IA | 35 | $8K | Mar 30 | Marginal | Pass |
   ...

4. On approval: create Zoho Deals for selected bids (sequentially, per cascade rules)
```

### Agent Workflow Rules

- **Verbosity cap**: Sub-agents must return JSON only, no prose (keeps context lean)
- **Model selection**: Use `model: "haiku"` for bid scoring agents (fast, cheap, sufficient for parsing)
- **Parallel limits**: Launch up to 10 agents simultaneously. If more than 10 bids, batch in groups of 10.
- **Firecrawl in sub-agents**: Sub-agents CAN use Firecrawl tools if available. Each agent's SODA query costs 1 credit.
- **Error handling**: If a sub-agent fails or times out, flag the bid for manual review rather than retrying
- **Cascade prevention**: NEVER create Zoho records inside sub-agents. Collect results first, then create records sequentially in the main thread after user approval.

---

## RFP PDF Extraction via Firecrawl (NEW in v1.2)

When `category_two_description` is insufficient, extract full RFP details from the USAC portal PDF.

### PDF URL Pattern
```
https://publicdata.usac.org/EPC/Prd/Form470/{app_number}/{ben}/{doc_id}-{filename}
```

The `rfp_identifier` field in the SODA response often contains the direct PDF URL or a reference to locate it.

### Extraction Workflow
```
1. Get rfp_identifier from SODA lookup
2. firecrawl_scrape(url=PDF_URL, formats=["markdown"])
   → ~6 credits (1 per page, typical RFP is 4-8 pages)
3. Parse markdown output for: equipment specs, quantities, license terms, installation requirements, deadline, submission method
4. Feed parsed data into Phase 1 analysis
```

### Cost-Benefit Rule
- Only extract PDFs for bids scoring 40+ in fit-scoring
- For bids with complete `category_two_description`, skip PDF extraction entirely
- Maximum PDF budget: ~30 credits/week (5 PDFs at 6 credits each)

---

## BOM Swap Web Verification (NEW in v1.2)

Before mapping any competitor product to a Cisco/Meraki equivalent, verify the competitor's actual specifications via web lookup. This prevents incorrect mappings based on assumed specs.

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

### When to Verify
- ALWAYS verify when the RFP lists specific competitor model numbers
- Skip verification when the RFP uses generic descriptions ("Wi-Fi 6E access points, quantity 50")
- If Firecrawl cannot access the manufacturer's page, note "specs not independently verified" in equivalence documentation

---

## Phase 0: RFP Qualification

Determine viability before starting any work.

### Step 0a: USAC SODA Lookup (NEW)

If the user provides a Form 470 application number, ALWAYS run a SODA lookup first:

```
firecrawl_scrape → https://opendata.usac.org/resource/jp7a-89nd.json?application_number={APP_NUMBER}
```

This provides: applicant name, BEN, state, contact info, category descriptions, deadline, and status — often enough to qualify without reading the full RFP.

### Step 0b: Viability Check

**Viable (Proceed):** Internal Connections (IC) = new equipment purchases. This is Stratus's focus.

**Non-Viable (Flag):** MIBS (Managed Internal Broadband Services) = managed services for existing equipment. Stratus cannot service non-Cisco gear.

**BMIC (Basic Maintenance):** License renewals for existing non-Cisco equipment. Not viable unless paired with IC.

**Mixed Form 470s:** Some RFPs combine IC and BMIC. Example: 6 new APs (IC, quote these) + 145 license renewals for existing Aruba (BMIC, exclude). Only quote the IC portion and document the exclusion in deal notes.

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

After initial qualification, assess the opportunity against these patterns derived from prior deal experience. Assign a fit rating and communicate it clearly in the deal notes and post-bid assessment email.

**Fit Ratings:**

| Rating | Meaning | Action |
|--------|---------|--------|
| Strong Fit | IC-focused, clean displacement, email submission, $50K+ | Pursue aggressively |
| Partial Fit | Mixed IC/BMIC, can bid IC portion only, some exclusions | Pursue IC portion, document scope limitations |
| Marginal / Hail Mary | Small IC scope, high admin burden, submit anyway if low effort | Submit if convenient, don't invest significant time |
| Not a Fit / Pass | MIBS-only, BMIC-only, or deal-breaking requirements | Document reasoning, close or skip |

**Indicators of a Strong Fit:**
- District is requesting Cisco/Meraki by name (no competitive displacement needed)
- Primarily IC (new equipment), minimal or no BMIC/MIBS components
- Email submission accepted (low admin overhead)
- Equipment value over $50K
- Wireless refresh or full network infrastructure (APs + switches)
- Standard license terms (3-5 year co-term)

**Indicators of a Poor Fit (flag or pass):**

1. **MIBS-Only RFP:** District wants managed services for existing non-Cisco equipment. Stratus cannot service Fortinet, Aruba, Ruckus, or Ubiquiti gear. Example: Dodgeville SD was 100% MIBS for existing Fortinet/Extreme/Ruckus, closed as lost immediately.

2. **BMIC-Only (License Renewals for Non-Cisco):** District is renewing licenses on existing competitor hardware. No new equipment to sell. Example: Sergeant Bluff-Luton had 145 Aruba APs that were BMIC license renewals, not new purchases. Only the 6 new APs + 3 switches were quotable.

3. **Firewall-Only with High Admin Burden:** If the IC portion is only 1-3 firewalls ($10-15K total) AND the submission requires portal uploads, notarized affidavits, or complex documentation, the effort-to-reward ratio is poor. Example: New Lisbon was 3x MX85 firewalls ($14K total) with notarized Noncollusion Affidavit + portal submission. Submitted as a hail mary via email.

4. **Mandatory Pre-Bid Site Visits for Remote Locations:** Stratus engineers require a minimum of $2,000 upfront for paid site visits. If the RFP mandates a pre-bid walkthrough with no guarantee of award, and the deal isn't large enough to justify travel, flag as a concern. Example: Spirit Lake CSD required site visit for fiber routing assessment.

5. **Strong Incumbent Vendor Relationship with Co-Term Language:** When an RFP uses language about "co-terming licenses" on existing competitor gear or the district is clearly expanding within an existing ecosystem, displacement is an uphill battle. Example: Interstate 35 CSD was a Fortinet shop wanting to co-term licensing on existing FortiSwitches/FortiAPs while also buying new Fortinet equipment.

6. **One-Person IT Department Seeking Managed Services:** Small districts with sole IT staff often want an MSP relationship (ongoing management, monitoring, help desk) rather than just equipment procurement. Stratus is an equipment reseller with installation services, not an MSP. Example: Griswold CSD had a one-person IT department explicitly looking for managed services support alongside their Fortinet BMIC.

7. **Non-Cisco Products Required in BOM:** RFPs that spec UPS units, structured cabling, racks, or other non-networking infrastructure that Stratus doesn't sell. These items must be excluded from our quote. Example: Newton CSD requested Vertiv/Liebert GXT5 UPS units which were excluded, with a note for the district to procure separately.

8. **Portal-Only Submission for Sub-$15K Deals:** The administrative overhead of registering for vendor portals, navigating submission workflows, and uploading multiple documents may not justify small opportunities. Weigh against pipeline capacity.

**Mixed Signals (Proceed with Caution):**
- Large IC component ($100K+) bundled with MIBS/BMIC: Bid IC portion only, document exclusions clearly
- Competitor-specific SKUs listed but "or equivalent" language present: Fair game for competitive displacement
- Installation "requested" vs "required": If ambiguous, include on-site installation to be fully responsive
- Pre-bid site visit "optional" vs "mandatory": Optional = skip unless deal is large; Mandatory = factor cost into go/no-go decision

## Phase 1: RFP Analysis & Equivalence Mapping

Parse the Form 470 and RFP documents for:
1. Equipment specs (models, quantities, ports, PoE, MIMO)
2. License term preference (1, 3, 5, or 7 year). If "3-5 year preference," lean toward 5-year
3. Installation requirements (separate from equipment? site constraints?)
4. Submission deadline (exact date/time/timezone)
5. Work window dates (typically summer for K-12)
6. Contact info (direct contact AND E-Rate consultant if applicable)
7. Submission method (email, portal, mail)
8. Number of eligible entities/buildings

### Step 1a: Web Verification of Competitor Specs (NEW)

Before mapping competitor products, verify their specifications:

```
For each competitor product in the RFP:
  1. firecrawl_scrape manufacturer's product page (1 credit)
  2. Extract: Wi-Fi standard, MIMO, PoE class, port count, uplink speed
  3. Use VERIFIED specs for equivalence mapping
  4. Document source URL in equivalence rationale
```

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

**Document equivalence rationale** for each mapping: port count/type, PoE budget, MIMO config, uplink speed, management platform. Include source URL from web verification when available.

### Known Gaps to Address

- Aruba CX 6300M 50G SFP56 uplinks vs C9300-M 10G SFP+: 10G is more than sufficient for K-12 environments. State this explicitly.
- If Wi-Fi 6E and Wi-Fi 7 price identically, always lead with Wi-Fi 7 (future-proof, matches district preference).

### Step 1b: SKU Validation (MANDATORY — NEW in v1.2)

After equivalence mapping, validate EVERY SKU before proceeding to quote creation:

```
1. Parse mapped SKUs: separate hardware from licenses, note quantities
2. Validate each SKU against unified-product-catalog-v2-0 or Zoho Products module:
   - Confirm SKU exists and is active (not EOL)
   - Verify correct suffix per suffix rules below
   - Confirm license pairing matches hardware and requested term
3. Display validation table:
   | Requested SKU | Validated SKU | Status | Notes |
   |---------------|---------------|--------|-------|
   | CW9176I-RTG | CW9176I-RTG | ✓ Active | Wi-Fi 7 indoor |
   | LIC-ENT-5YR | LIC-ENT-5YR | ✓ Active | 5-year co-term |
   | MS130-48P | MS130-48P | ✓ Active | No suffix needed |
4. If ANY SKU is invalid, EOL, or ambiguous → STOP and clarify before proceeding
```

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
- **Meraki_ISR (Proceed-First Logic — NEW in v1.2):**
  - DEFAULT: Set to "Stratus Sales" (ID: 2570562000027286729)
  - Create the deal first with this default
  - AFTER creation: ask if a Cisco rep is involved
  - If yes: use cisco-rep-locator-v1-1 skill to find the rep, then update Meraki_ISR and Lead_Source
  - If no: leave as Stratus Sales
- Description: Form 470 number, BEN, entity count, scope summary, work window, deadline, submission contact

### Task
- Subject: "Submit E-Rate Bid - [District Name] (Form 470 #[number])"
- Due Date: **2 business days BEFORE actual deadline** (buffer)
- Priority: High
- Link to Deal

### Deal Notes
- After creating quote, add note with Claude chat thread link: `https://claude.ai/chat/{uri}`

### Pre-Creation Validation (MANDATORY)

Display a validation table for ALL required fields before creating any Deal or Quote:

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

## Phase 3: Quote Creation

### Equipment Quote(s)

**Tax Exemption (CRITICAL):**
- Set `Tax_Type` = "Tax Exempt" at the **quote level**
- NEVER modify taxes at line item level
- Also ensure Account has Tax_Type = "Tax Exempt"

**Licensing Rules (CRITICAL):**
- **ALWAYS use co-term licensing:** LIC-ENT-xYR
- **NEVER use CISCO-NETWORK-SUB** (subscription model) unless explicitly requested
- Wi-Fi 7 APs (CW9176I-RTG, CW9172I-RTG, CW9178I-RTG) ALL work with co-term LIC-ENT-xYR licenses, same as Wi-Fi 6E
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

**Quote Options Logic:**
- If Wi-Fi 6E and Wi-Fi 7 price identically, lead with Wi-Fi 7 (single recommendation)
- Only present multiple options if meaningful price/feature tradeoff exists

**Line Item Descriptions:** Include equivalence notes.
Format: `[SKU] | [Product Name] | Equivalent to: [Competitor] | [Key specs]`

### Multi-Building Quote Splitting (NEW in v1.2)

When the Form 470 covers multiple buildings (check `number_of_eligible_entities` from SODA data):

- **Create separate quotes per building** when the RFP itemizes equipment by location
- This simplifies Form 471 filing, where districts must allocate costs per eligible entity
- Name format: `[District Name] - E-Rate FY[XX] [Building Name] (Form 470 #[number])`
- If the RFP does NOT itemize by building, create a single consolidated quote and note in deal description that the district will need to allocate costs for Form 471

### Installation Services Quote (Separate)

E-Rate requires installation quoted separately from equipment.

**Tiered Installation Estimates (UPDATED in v1.2):**

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

**IMPORTANT:** These are estimates. Always prompt for engineer input on complex deployments (multi-building, fiber runs, outdoor APs, legacy infrastructure removal). Present estimates as a starting point, not a final number.

### Items to Exclude
- Non-Cisco products (UPS, cabling infrastructure, existing equipment maintenance)
- Document exclusions in deal notes

## Phase 4: Cisco Discount Request

After quotes created at list price:
1. Use **cisco-rep-locator-v1-1** skill to identify the correct Cisco rep for the territory
2. Provide: customer name/address, Deal ID, full MSRP breakdown, competitive situation, deadline
3. Wait for discount approval before finalizing

**Do NOT hardcode a specific Cisco rep.** Territory assignments change. Always use the cisco-rep-locator skill for current rep lookup.

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

## Phase 6: Post-Bid Actions

### Opportunity Assessment Email Draft
Generate an email draft (no specific addressee) with:
1. Opportunity recap (district, Form 470#, scope, estimated list value)
2. **Fit rating** (Strong Fit, Partial Fit, Marginal/Hail Mary, or Pass) with specific reasoning from the Opportunity Fit Assessment criteria
3. BOM concerns (imperfect matches, excluded items, uplink gaps)
4. Red flags (non-Cisco requirements, site visits, portal submissions, incumbent advantages, MIBS/BMIC components, one-person IT shops seeking MSP)
5. Recommended next steps

### CRM Updates
- Update Deal stage to "Proposal/Price Quote"
- Add note: submission method, date/time, confirmation receipt
- Set follow-up task after bid evaluation period

### SIRE Network Assessment (Deals over $200K)
Send request to Jay Florendo via Webex with: Customer Name, Country (USA), State, Deal Size (List), Business Case (2-3 sentences), Competitive (yes/no), Competitor Info, Cisco AM Name, Zoho Deal Link.

## CCW Import CSV Format

8-column format for Cisco Commerce Workspace import. Co-term items have ALL term fields blank.

```
ProductIdentifier,Quantity,ServiceLength,Initial Term(Months),Auto Renew Term(Months),Billing Model,Requested Start Date,Custom Name
C9300-48P-M,8,,,,,,
LIC-C9300-48E-5Y,8,,,,,,
CW9176I-RTG,100,,,,,,
LIC-ENT-5YR,100,,,,,,
```

## Firecrawl Agent Fallback (NEW in v1.2)

For edge cases where district websites require navigation (e.g., vendor registration portals, document repositories behind multiple clicks), use `firecrawl_agent` instead of `firecrawl_scrape`:

```
firecrawl_agent(prompt="Navigate to the RFP documents section and find the network equipment bid specifications for Form 470 #{app_number}", urls=["https://district-website.org/bids"])
```

- Agent uses 0 credits but takes ~20 seconds (vs. 2 seconds for scrape)
- Use ONLY when scrape returns empty or insufficient results
- Poll `firecrawl_agent_status` every 15-30 seconds for up to 3 minutes

## Common E-Rate Consultants

- **David Fringer** (david.fringer@iowaaea.org) — Iowa AEA, appears across many Iowa district RFPs. Create Contact records for both the consultant and district tech contact.

## Platform Compatibility

| Workflow | Claude.ai Web | Cowork Desktop | Notes |
|----------|--------------|----------------|-------|
| SODA API lookup | ✅ | ✅ | Firecrawl MCP works everywhere |
| Weekly bid scan | ✅ | ✅ | |
| PDF extraction | ✅ | ✅ | |
| BOM web verification | ✅ | ✅ | |
| Zoho CRM records | ✅ | ✅ | |
| CCW submission | ❌ | ✅ | Requires Chrome browser automation |
| Bid package PDF | ✅ | ✅ | |

## Rules Summary

| Rule | Details |
|------|---------|
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
| Fit Assessment | Rate every opportunity (Strong/Partial/Marginal/Pass). Include rating in deal notes and assessment email. |
| State Codes | 2-letter abbreviations only (IA, not Iowa). |
| SKU Validation | Validate against unified-product-catalog before quote creation. |
| BOM Verification | Firecrawl web lookup of competitor specs before mapping. |
| Companion Skills | Read highest-version of each companion skill before CRM operations. |
| Multi-Building | Separate quotes per building when RFP itemizes by location. |
| Installation | Tiered hours formula + prompt for engineer input on complex jobs. |

## Workflow Quick Reference

```
Form 470 Received (or Application Number Provided)
    → Step 0a: USAC SODA lookup via Firecrawl (1 credit)
    → Phase 0: Qualify (IC vs MIBS, red flags, fit assessment)
    → Phase 1: Analyze RFP, verify competitor specs (Firecrawl), map equivalences, validate SKUs
    → Phase 2: Zoho records (Account → Contact → Deal → Task) with proceed-first defaults
    → Phase 3: Quote(s) at list price, per-building if applicable, chat link in deal notes
    → Phase 4: Submit to Cisco rep for discount (via cisco-rep-locator)
    → [WAIT for discount approval]
    → Phase 5: Bid package PDF (only when requested)
    → Phase 6: Submit, update CRM, assessment email draft

Weekly Bid Scanner (Scheduled or On-Demand)
    → Query SODA API for open certified bids
    → Run fit-scoring algorithm
    → Generate digest (Hot/Warm/Cool/Pass)
    → On approval: create Zoho Deals for selected opportunities
```

## Changelog

### v1.2 (Current)
- **USAC SODA API integration**: Automated Form 470 lookup via Firecrawl scrape (1 credit per query, no auth needed)
- **Weekly bid scanner**: Fit-scoring algorithm (0-100) across 5 dimensions, digest generation, auto-deal creation for approved leads
- **RFP PDF extraction**: Firecrawl scrape of USAC portal PDFs (~6 credits per doc) when category_two_description is insufficient
- **BOM swap web verification**: Mandatory Firecrawl lookup of competitor product specs before equivalence mapping
- **Zoho CRM v30 rule inheritance**: Explicit checklist of all inherited rules (state codes, Contact_Name, Billing_Term, Country, Product_Name, skip ecomm)
- **SKU validation gate**: Mandatory validation against unified-product-catalog-v2-0 before quote creation
- **Proceed-first deal defaults**: Create with Stratus Referal + Stratus Sales, prompt for Cisco rep AFTER creation (replaces hardcoded Eddy Zertuche)
- **Tiered installation estimates**: Formula-based hours (1-10 APs: 1.5hr, 11-50: 1.25hr, 50+: 1hr) plus PM overhead for $100K+, with prompt for engineer input
- **Multi-building quote splitting**: Guidance for per-building quotes to support Form 471 filing
- **Companion skill references**: All references updated to "highest-version available" pattern
- **Firecrawl Agent fallback**: For district websites requiring navigation
- **Agent workflows for parallel evaluation**: Sub-agent pattern for batch bid scoring (haiku model, JSON-only returns, 10-agent parallel limit)
- **Firecrawl MCP setup guide**: Step-by-step instructions for non-Chris users with graceful degradation table
- **Platform compatibility table**: Shows which workflows work on web vs. desktop

### v1.1
- Initial release with Phases 0-6
- Opportunity Fit Assessment with 8 poor-fit indicators
- Equivalence mapping rules for switching, wireless, firewalls
- License pairing reference and SKU suffix rules
- CCW Import CSV format
- Common E-Rate consultants reference
