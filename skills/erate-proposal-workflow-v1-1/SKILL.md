---
name: erate-proposal-workflow-v1-1
description: end-to-end e-rate form 470 proposal workflow for cisco/meraki competitive bids. covers rfp qualification with fit assessment scoring, equivalence mapping, zoho crm setup, quote creation, cisco discount coordination, bid package generation, and post-submission actions. embeds all corrections and best practices from prior deals.
---

# E-Rate / Form 470 Proposal Workflow v1.1

Complete workflow for analyzing E-Rate Form 470 RFPs, mapping competitor equipment to Cisco/Meraki equivalents, creating Zoho CRM records and quotes, coordinating Cisco discounts, and generating bid packages for K-12 school districts.

## When to Use

- User uploads or references a Form 470 / E-Rate RFP
- User mentions E-Rate, Form 470, school district network bid, or competitive displacement
- User asks to quote Meraki equipment against Aruba, Extreme, Ruckus, Ubiquiti, or Fortinet for a school district
- User references Healthcare Connect Fund (HCF/RHC) Form 461 opportunities
- Keywords: "E-Rate," "Form 470," "Form 461," "bid package," "USAC," "BEN," "Internal Connections"

## Company Details

- Company: Stratus Information Systems (Cisco-exclusive reseller, Meraki specialist)
- USAC SPIN: **143052656**
- Primary Contact: Chris Graves, Regional Sales Director, chrisg@stratusinfosystems.com, (888) 366-4911
- Installation SKU: SIS101 at $200/hour

## Phase 0: RFP Qualification

Determine viability before starting any work.

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

**Document equivalence rationale** for each mapping: port count/type, PoE budget, MIMO config, uplink speed, management platform.

### Known Gaps to Address

- Aruba CX 6300M 50G SFP56 uplinks vs C9300-M 10G SFP+: 10G is more than sufficient for K-12 environments. State this explicitly.
- If Wi-Fi 6E and Wi-Fi 7 price identically, always lead with Wi-Fi 7 (future-proof, matches district preference).

## Phase 2: Zoho CRM Setup

Read the zoho-crm skill before creating any records.

### Account
- Search existing accounts first (avoid duplicates)
- If new: populate ALL address fields (Billing AND Shipping)
- **Set Tax_Type = "Tax Exempt"** at Account level

### Contact
- Link to Account
- Include: first name, last name, email, phone, title
- Create records for BOTH tech contact AND E-Rate consultant if applicable

### Deal
- **Name format:** `[District Name] - E-Rate FY[XX] [Project Type] (Form 470 #[number])`
- Stage: "Qualification"
- Type: "E-Rate" (or "RHC" for Healthcare Connect Fund)
- **Lead_Source:** Default to **"Stratus Referal"** (one R, correct Zoho picklist value)
  - Change to "Meraki ISR Referal" only if a Cisco rep explicitly referred the deal
  - NEVER create new picklist options. If unsure, STOP and ask.
- **Meraki_ISR:**
  - "Stratus Referal" → set to "Stratus Sales" (ID: 2570562000027286729)
  - "Meraki ISR Referal" → use cisco-rep-locator skill to find the rep
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
| Deal_Name | [format check] | ✓ |
| Lead_Source | Stratus Referal | ⚠️ Confirm |
| Meraki_ISR | Stratus Sales | ✓ |

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

**Discounts:** NEVER auto-apply. Wait for Cisco approval.

**Quote Options Logic:**
- If Wi-Fi 6E and Wi-Fi 7 price identically, lead with Wi-Fi 7 (single recommendation)
- Only present multiple options if meaningful price/feature tradeoff exists

**Line Item Descriptions:** Include equivalence notes.
Format: `[SKU] | [Product Name] | Equivalent to: [Competitor] | [Key specs]`

### Installation Services Quote (Separate)

E-Rate requires installation quoted separately from equipment.

- SKU: SIS101 at $200/hour
- APs: 1-2 hours each
- Switches: 2-3 hours each
- Add time for: multi-building sites, fiber runs, stacking, VLAN config, RF optimization, knowledge transfer
- Travel: separate line item for non-metro sites ($500-$1,500 typical)

### Items to Exclude
- Non-Cisco products (UPS, cabling infrastructure, existing equipment maintenance)
- Document exclusions in deal notes

## Phase 4: Cisco Discount Request

After quotes created at list price:
1. Identify correct Cisco rep (user will specify, or use cisco-rep-locator skill)
2. Provide: customer name/address, Deal ID, full MSRP breakdown, competitive situation, deadline
3. Wait for discount approval before finalizing

**Key Cisco Rep:** Eddy Zertuche (ezertuch@cisco.com) covers Iowa and surrounding territory.

## Phase 5: Bid Package Generation

**ONLY generate when explicitly requested** (after Cisco discount confirmed).

**Contents:**
1. Cover Letter (SPIN: 143052656, proposal summary, enclosed docs, E-Rate compliance statement)
2. Equipment quote(s) with discounted pricing (include discount column)
3. Installation services quote
4. Product equivalence documentation (spec comparison tables)
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

## Common E-Rate Consultants

- **David Fringer** (david.fringer@iowaaea.org) — Iowa AEA, appears across many Iowa district RFPs. Create Contact records for both the consultant and district tech contact.

## Rules Summary

| Rule | Details |
|------|---------|
| Tax Exemption | Tax_Type = "Tax Exempt" at Quote AND Account level. Never line items. |
| Bid Package Timing | Zoho quotes first. PDF only when explicitly requested. |
| Licensing | Co-term (LIC-ENT-xYR). Never CISCO-NETWORK-SUB. Match term to RFP. |
| Wi-Fi 7 Licensing | CW9176I/CW9172I/CW9178I all use co-term LIC-ENT-xYR. |
| Indoor Mesh | Same indoor AP model. MR86 is OUTDOOR ONLY. |
| Discounts | Never auto-apply. Wait for Cisco approval. |
| L3 Switches | C9300-M series over pure Meraki MS for aggregation. |
| Lead Source | "Stratus Referal" (one R) default. Only change if Cisco rep involved. |
| SPIN | 143052656 |
| Deal Notes | Add Claude chat thread link after quote creation. |
| Post-Quote | Generate assessment email with fit evaluation and red flags. |
| Validation | Display field table before creating Deal or Quote. |
| Communication | Never send without approval. Draft and present first. |
| IC vs MIBS | Only quote Internal Connections. Flag MIBS/BMIC as non-viable. |
| Fit Assessment | Rate every opportunity (Strong/Partial/Marginal/Pass). Include rating in deal notes and assessment email. |

## Workflow Quick Reference

```
Form 470 Received
    → Phase 0: Qualify (IC vs MIBS, red flags)
    → Phase 1: Analyze RFP, map equivalences, validate SKUs
    → Phase 2: Zoho records (Account → Contact → Deal → Task)
    → Phase 3: Quote(s) at list price, chat link in deal notes
    → Phase 4: Submit to Cisco rep for discount
    → [WAIT for discount approval]
    → Phase 5: Bid package PDF (only when requested)
    → Phase 6: Submit, update CRM, assessment email draft
```
