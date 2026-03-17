---
name: echo-contact-enrichment-v2-0
description: "cisco meraki echo contact list processor with 6-phase workflow: partner filtering (cache-first with 63 known msp/reseller domains + 7 known partner accounts), zoho crm cross-reference for existing customer tagging, zoominfo enrichment for missing it/leadership contacts, territory-aware disambiguation, smb sub-agent expansion option, and self-updating partner cache. accepts csv or xlsx input, outputs multi-tab xlsx with enriched contacts, existing crm accounts, new accounts, removed partners, and manual review tabs. triggers: echo contacts, echo list, contact enrichment, clean echo, process echo, enrich contacts, partner filter, clean contact list, echo report, meraki echo, contact cleanup, remove partners, enrich echo."
---

# ECHO Contact Enrichment v2.0

Process Cisco Meraki ECHO contact reports by removing partner/MSP contacts, cross-referencing Zoho CRM, resolving company identities via web search, and enriching with Clay/ZoomInfo/Apollo to produce a clean, actionable contact list with verified emails.

## Architecture

```
PHASE 0: CONFIGURE              → Prompt for state(s), check Clay credits
PHASE 1: INGEST & PARTNER SCRUB → Parse file, 3-layer partner filter (MANDATORY)
PHASE 2: ZOHO CRM CROSS-REF     → Tag existing customers, skip CRM-covered accounts
PHASE 3: DOMAIN & NAME CLEAN    → Extract domains, web search to resolve unknowns
PHASE 4: COMPANY RESOLUTION     → Clay + ZoomInfo confirm companies, get IDs
PHASE 5: CONTACT ENRICHMENT     → Clay primary, ZoomInfo fallback, Apollo gap fill
PHASE 6: OUTPUT GENERATION       → Multi-tab XLSX + cache update
```

Key principle: clean everything BEFORE enrichment APIs. No loopbacks. CRM check before credits. Web search before paid lookups.

## Input Format

Expect "Cleaned Contacts" tab (or similar) with columns: Account Name, Org Name, Recent Name 1-3, Recent Email 1-3. If an "Extracted List" tab exists (prior ZoomInfo results), ingest as baseline contacts to avoid duplicate lookups. CSV also accepted. Drop SFDC Account ID and Org ID columns immediately.

---

## PHASE 0: CONFIGURE

**This phase is mandatory. Never skip or assume defaults.**

### Step 1: Prompt for state(s)

Ask: "What state(s) should I use for contact enrichment? (e.g., OH, or IL,WI,IN,OH for multi-state)"

Store as session variable `target_states`. Used in ALL enrichment calls downstream (Clay locations, ZoomInfo state, Apollo person_locations, web search queries).

### Step 2: Check Clay credits

Call `Clay:get-credits-available` (app-only tool, if available). Display balance. If Clay is not connected or credits are low, note that the workflow will fall back to ZoomInfo + Apollo as primary enrichment providers.

### Step 3: Quick config summary

Display to user before proceeding:
- Target state(s): [from step 1]
- Clay credits: [from step 2, or "not connected"]
- CRM skip threshold: 2+ relevant contacts (default, confirm with user)
- Enrichment goal: Contact emails for IT/procurement/operations decision makers

---

## PHASE 1: INGEST & PARTNER SCRUB

### 1A: Parse the uploaded file

```python
import pandas as pd

if file_path.endswith('.csv'):
    df = pd.read_csv(file_path)
else:
    df = pd.read_excel(file_path, sheet_name='Cleaned Contacts')  # or first sheet

drop_cols = ['SFDC Account ID', 'Org ID']
df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
```

If an "Extracted List" tab exists, read it separately as `df_baseline` — these are contacts already found in a prior ZoomInfo pass.

### 1B: Partner Domain Scrubbing (MANDATORY — always runs)

This runs on EVERY contact email in the file regardless of whether a "Removed" tab exists. Three-layer filter:

**Layer 1 — Hardcoded cache.** Read `references/partner_cache.json`. Contains 63+ known MSP/VAR/reseller domains and 7+ known partner account names. Check every email domain against this list. Also check Account Name against `partner_accounts`.

**Layer 2 — "Removed" tab ingestion.** If file has "Removed - Partner Accounts" or "Removed - Partner Contacts" tabs, extract every partner domain and merge into the filter set for this run.

**Layer 3 — Cross-account pattern detection.** Flag any email domain appearing across 3+ different Account Names in the same file. Present flagged domains to user for confirmation before removing. A single domain serving multiple unrelated accounts is a strong MSP/VAR signal.

Also filter generic/ISP domains that can't be used for enrichment: gmail.com, yahoo.com, sbcglobal.net, att.net, comcast.net, hotmail.com, aol.com, outlook.com, icloud.com, msn.com, live.com, verizon.net, earthlink.net, frontier.com, roadrunner.com, charter.net, windstream.net.

All removed contacts → "Removed Partners" output tab with: Account Name, Org Name, Contact Name, Email, Domain, Removal Reason, Layer (cache/tab/pattern).

### 1C: Deduplication

Consolidate to one row per unique Account Name. Collect all unique Org Names (excluding Meraki URLs), non-partner corporate emails, and contact names. Track row count per account (Meraki network count = opportunity sizing).

Present summary: total rows, unique accounts, contacts removed as partners, remaining contacts with emails.

---

## PHASE 2: ZOHO CRM CROSS-REFERENCE

Read latest zoho-crm-v* companion skill before any CRM calls.

### 2A: Account Matching

For each deduplicated account, call `ZohoCRM_Search_Records` on Accounts module by Account_Name. Pull Zoho Account ID and linked contacts. Process in batches to avoid rate limits.

### 2B: Contact Inventory

For matched accounts, pull all Contacts linked to that Account. If an account has 2+ contacts with titles containing: IT, Director, Manager, Network, Systems, Infrastructure, Operations, CFO, Procurement, Purchasing, CTO, CIO — tag as `CRM Covered`.

### 2C: Classification

- `CRM Covered` — 2+ relevant contacts in Zoho. Skip from enrichment (Phases 4-5). Include in output for reference.
- `CRM Partial` — Account exists in Zoho but 0-1 relevant contacts. Include in enrichment.
- `CRM New` — Not in Zoho. Full enrichment.

### Phase 2 Checkpoint

Present summary table: X accounts CRM Covered (skipping), Y CRM Partial (enriching for more), Z CRM New (full enrichment). Get confirmation before proceeding.

---

## PHASE 3: DOMAIN EXTRACTION & NAME CLEANING

No credits consumed in this phase. Goal: resolve every account to its best searchable identity BEFORE any paid API calls.

### 3A: Domain Extraction

From surviving Echo emails (post-partner scrub), extract corporate domains. These are the highest-value search inputs because Clay requires a domain and ZoomInfo domain search is more accurate than name search.

### 3B: Best Name Resolution

For each account, determine the best searchable name(s):

1. Account Name = `primary_name` (always the default search key)
2. If any Org Name is a real company name (not a Meraki URL like `n1.meraki.com/...`, not identical to Account Name, not a personal name), store as `alt_name`
3. If multiple Org Names look like independent companies (completely different names, not branches), flag as `multi_org` — each sub-org gets its own enrichment pass
4. Meraki URLs are ignored as name sources but counted for network sizing

Account Name is always the primary search key. Org Name is a fallback if Account Name returns zero results.

### 3C: Web Search Pre-Clean (critical step)

For every account that does NOT have a corporate domain from Echo emails, use `web_search` to find the domain before enrichment. This is mandatory because:
- Clay `find-and-enrich-contacts-at-company` requires a domain or LinkedIn URL
- ZoomInfo domain search is significantly more accurate than name search
- Resolving names upfront eliminates loopbacks after failed enrichment

Process in priority order:

**Tier A** — Have alt_name, no domain: `web_search` "[account name] OR [alt_name] [state] company website"

**Tier B** — Formal business name (Inc/LLC/multi-word), no domain: `web_search` "[account name] [state]"

**Tier C** — Short/ambiguous names: `web_search` "[account name] [state] company" to confirm business and find domain

**Tier D** — Multi-org accounts: web search each sub-org separately

For each result, capture: confirmed company name, domain, city. Store as enrichment input.

### 3D: Post-Clean Tier Classification

- **Tier 1:** Has corporate domain (Echo email or web search) → domain-based enrichment
- **Tier 2:** No domain found, but confirmed company name → name-based enrichment with state filter
- **Tier 3:** Unresolvable → Manual Review, skip enrichment

### Phase 3 Checkpoint

Resolution summary: Account → Resolved Company → Domain → Source (Echo/web) → Tier. Show counts: X domain-search ready, Y name-search ready, Z manual review. Get approval before credit-consuming phases.

---

## PHASE 4: COMPANY RESOLUTION

Resolve each account to confirmed company identities in Clay and/or ZoomInfo.

### Tier 1 (have domain — highest confidence)

**Clay (primary, if connected):** Call `Clay:find-and-enrich-company` with `companyIdentifier` = domain. Returns confirmed company metadata + taskId.

**ZoomInfo (parallel):** Call `ZoomInfo:enrich_companies` in batches of 10 with domain. Returns ZI Company ID, confirmed name, employee count, industry. Useful for fallback contact search in Phase 5.

### Tier 2 (name only, no domain)

Call `ZoomInfo:search_companies` with `companyName` + `state` = target_states. Returns ZI Company ID + domain. If ZoomInfo returns a domain, also call Clay with discovered domain.

### Multi-org accounts

Each independent sub-org runs through resolution separately. Link results back to parent Account Name.

---

## PHASE 5: CONTACT ENRICHMENT

Only runs on accounts NOT tagged `CRM Covered`. Goal: find contacts with verified email addresses.

### Step 1: Clay (primary for Tier 1 accounts with domains)

Call `Clay:find-and-enrich-contacts-at-company` with:
- `companyIdentifier`: resolved domain
- `contactFilters.job_title_keywords`: ["IT Director", "IT Manager", "Network Administrator", "Systems Administrator", "Director of IT", "VP of IT", "CTO", "CIO", "Director of Operations", "Operations Manager", "Office Manager", "CFO", "Procurement Manager", "Purchasing Director", "Facilities Manager", "Director of Infrastructure"]
- `contactFilters.locations`: [target_states from Phase 0, formatted as state names e.g. "Ohio"]
- `dataPoints.contactDataPoints`: [{"type": "Email"}]

Store taskId. Poll `Clay:get-existing-search` with taskId to retrieve async email enrichment results. Wait ~5 seconds between polls, retry up to 5 times.

### Step 2: ZoomInfo search_contacts (supplement + fallback)

For companies where Clay returned fewer than 2 contacts, OR for Tier 2 accounts (no domain):

Call `ZoomInfo:search_contacts` with:
- `companyName` or `companyId`: resolved company
- `state`: target_states
- `jobTitle`: "IT Director OR IT Manager OR CIO OR CTO OR VP of IT OR Director of IT OR Network Administrator OR Systems Administrator OR Operations Manager OR Office Manager OR CFO OR Procurement Manager"
- `managementLevel`: "Director,VP,C-Level,Manager"
- `requiredFields`: "email"
- `contactAccuracyScoreMin`: "75"
- `pageSize`: 10

### Step 3: ZoomInfo get_recommended_contacts (ML-based)

For companies with a ZI Company ID where Steps 1-2 returned fewer than 2 contacts:

Call `ZoomInfo:get_recommended_contacts` with `useCaseType` = "PROSPECTING" and `ziCompanyId`.

### Step 4: Apollo (free search, gap filler)

For remaining gaps where Clay and ZoomInfo both missed:

Call `Apollo.io:apollo_mixed_people_api_search` with:
- `q_organization_domains_list`: [domain] (or `q_keywords` with company name)
- `person_titles`: [same title list]
- `organization_locations`: [target_states formatted as "Ohio, United States"]
- `person_seniorities`: ["manager", "director", "vp", "c_suite"]
- `per_page`: 25

Note: Apollo people search is free (no credits consumed for searching). It does not return emails directly. Names/titles found here can be enriched via `apollo_people_bulk_match` if needed, which does consume credits.

### Post-Enrichment Partner Scrub (MANDATORY)

Run ALL newly discovered contacts through the same partner domain filter from Phase 1B. Any MSP/partner domain → Removed Partners tab, not enriched output. This catches cases where Clay/ZoomInfo/Apollo returns an MSP contact listed at the customer company.

---

## PHASE 6: OUTPUT GENERATION

### Multi-tab XLSX

**Tab 1 — Enriched Contacts:** One row per new contact found. Columns: Account Name, Org Name, First Name, Last Name, Title, Email, Company Domain, City, State, Source (Clay/ZoomInfo/Apollo/Echo), CRM Status (New Account / Existing Account), Search Tier.

**Tab 2 — Account Summary:** One row per account. Columns: Account Name, Resolved Company, Domain, Search Tier, Contacts Found (new), Existing CRM Contacts, Source Breakdown, CRM Status, Echo Emails (existing), Org Names, Meraki Network Count.

**Tab 3 — CRM Covered (Skipped):** Accounts with sufficient contacts in Zoho. Columns: Account Name, Zoho Account ID (hyperlinked), Existing Contact Count, Contact Names/Titles, Reason Skipped.

**Tab 4 — Not Found / Manual Review:** Unresolvable accounts. Columns: Account Name, Org Names, Tier, What Was Tried, Why It Failed, Suggested Manual Action.

**Tab 5 — Removed Partners:** All filtered partner contacts from Phase 1B + Phase 5 post-scrub. Columns: Account Name, Org Name, Contact Name, Email, Domain, Removal Reason, Phase Caught (Input / Post-Enrichment).

**Tab 6 — Run Stats:** Credit consumption (Clay, ZoomInfo, Apollo), accounts per tier, accounts skipped (CRM Covered), find rates per tier, total new contacts vs starting Echo contacts, partners removed, timestamp.

### Formatting

- Freeze header rows on all tabs
- Auto-filter on all tabs
- Column widths auto-sized
- Arial font, professional styling

### Cache Update

After run, update `references/partner_cache.json` with any newly discovered partner domains from Phase 1B Layer 3 or Phase 5 post-scrub. Note new additions for next skill version.

---

## Guardrails

- **Phase 0 state prompt is MANDATORY.** Never assume a state. Always ask.
- **Phase 2 (CRM check) runs BEFORE any enrichment.** Don't burn credits on accounts already covered.
- **Phase 3 (web search pre-clean) runs BEFORE any paid APIs.** Clay requires a domain. Resolving upfront eliminates loopbacks.
- **Partner scrubbing runs twice:** Phase 1B (input) and Phase 5 post-enrichment. No partner contact should ever appear in the enriched output.
- **Always prompt before Phase 4/5.** Show resolution summary and estimated credit impact.
- Clay `find-and-enrich-contacts-at-company` is the primary enrichment path when connected. ZoomInfo `search_contacts` is the fallback.
- Apollo people search is free (no credits for searching). Apollo enrichment consumes credits.
- State filter from Phase 0 propagates to ALL enrichment calls.
- Batch sizes: ZoomInfo enrich = 10/call. Apollo bulk = 10/call. Clay = 1 company per call (async with taskId).
- Poll Clay `get-existing-search` after each contact search. ~5 seconds between polls, up to 5 retries.
- Rate limiting: brief pause between sequential API calls.
- Context window: for lists >100 accounts, process in batches and write intermediate results to file.
- Read latest zoho-crm-v* companion skill before any CRM operations. Phase 2 is READ-ONLY.
- Never create new Zoho picklist values.
- CRM Covered skip threshold configurable (default: 2+ relevant-titled contacts).

## Provider Hierarchy (quick reference)

```
COMPANY RESOLUTION:
  1. Clay: find-and-enrich-company (domain) → if connected
  2. ZoomInfo: enrich_companies (domain, batch 10) → parallel with Clay
  3. ZoomInfo: search_companies (name + state) → Tier 2 fallback

CONTACT ENRICHMENT:
  1. Clay: find-and-enrich-contacts-at-company (domain + titles + state + Email)
  2. ZoomInfo: search_contacts (company + state + titles + requiredFields=email)
  3. ZoomInfo: get_recommended_contacts (ML, uses ZI Company ID)
  4. Apollo: apollo_mixed_people_api_search (free search, no emails returned)
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Clay not connected | Fall back to ZoomInfo + Apollo as primary |
| Clay credits exhausted | Switch to ZoomInfo + Apollo mid-run |
| ZoomInfo rate limit | Pause 30s, retry. If persistent, smaller batches |
| ZoomInfo returns no company | Try without Inc/LLC suffix. Try domain search if available |
| Zoho CRM search returns 0 | Try partial name match (first 3 words) |
| Apollo returns 0 for domain | Try q_keywords with company name instead |
| File parse error | Check encoding, try latin-1 fallback for CSV |
| Large list (200+) | Process in chunks of 50, write intermediate results to file |

## Dependencies

- **Clay MCP** — Company resolution, contact enrichment with email (primary when connected)
- **ZoomInfo MCP** — Company search/enrich, contact search, recommended contacts (fallback)
- **Apollo MCP** — People search (free), company search, contact enrichment
- **Zoho CRM MCP** — Account search, contact lookup (read-only)
- **Web Search** — Domain resolution for accounts without Echo emails
- **pandas + openpyxl** — Data processing and XLSX output
- **zoho-crm companion skill** — Business rules for CRM operations

## Changelog

### v2.0 (2026-03-17)
- **Mandatory state prompt** (Phase 0): never assume geographic scope, always ask
- **CRM check moved to Phase 2**: runs before any enrichment to skip covered accounts
- **Web search pre-clean** (Phase 3C): resolves company domains before paid API calls, eliminates loopbacks
- **Clay MCP integration** (Phases 4-5): primary enrichment path when connected, with inline Email dataPoint
- **Provider waterfall**: Clay → ZoomInfo → Apollo with automatic fallback
- **Account name vs Org name resolution** (Phase 3B): Account Name is primary, Org Name is fallback, multi-org accounts get separate enrichment
- **Post-enrichment partner scrub**: catches MSP contacts returned by enrichment providers
- **Removed Step 5 (existing contact enrichment)**: only finding new contacts with emails, not re-enriching known contacts
- **Simplified output**: focused on contact emails as the deliverable
- All v1.0 features retained: partner cache, 3-layer filter, dedup, CRM cross-ref, multi-tab output

### v1.0 (2026-03-11)
- Initial release: 6-phase workflow with partner filtering, Zoho CRM cross-ref, ZoomInfo enrichment
- 63 known MSP/reseller domains, 7 known partner accounts in embedded cache
