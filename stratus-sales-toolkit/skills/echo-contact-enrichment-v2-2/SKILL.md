---
name: echo-contact-enrichment-v2-2
description: "cisco meraki echo contact list processor: partner filtering, zoho crm cross-ref, auto-detect geography, clay-first enrichment with async email polling, conditional zoominfo for it-leadership gaps, adaptive title filtering for micro-smbs, per-account state routing, deduplication, and partner cache. accepts csv or xlsx, outputs contact name + title + email. triggers: echo contacts, echo list, contact enrichment, clean echo, process echo, enrich contacts, partner filter, clean contact list, echo report, meraki echo, contact cleanup, remove partners, enrich echo."
---

# ECHO Contact Enrichment v2.2

Process Cisco Meraki ECHO contact reports and account lists by removing partner/MSP contacts, cross-referencing Zoho CRM, resolving company domains via web search, and enriching with Clay + ZoomInfo **in parallel** to produce a clean contact list with **verified email addresses**.

**The deliverable is: Account Name, Contact Name, Title, Email.**

## Architecture

```
PHASE 0: AUTO-DETECT & CONFIGURE  → Scan file for geography, confirm with user
PHASE 1: INGEST & PARTNER SCRUB   → Parse file, 3-layer partner filter (MANDATORY)
PHASE 2: ZOHO CRM CROSS-REF       → Tag existing customers, skip CRM-covered accounts
PHASE 3: DOMAIN & NAME CLEAN      → Extract domains, web search, domain-vs-account validation
PHASE 4: COMPANY RESOLUTION        → Clay + ZoomInfo confirm companies (lightweight)
PHASE 5: CONTACT ENRICHMENT        → Clay first → evaluate → conditional ZoomInfo for IT gaps
PHASE 6: OUTPUT GENERATION         → Multi-tab XLSX: contacts with emails as Tab 1
```

Key principles:
- Clean everything BEFORE enrichment. No loopbacks.
- CRM check before credits. Web search before paid lookups.
- Clay runs first on every account. ZoomInfo fires conditionally when Clay's results are missing IT-titled contacts or came back empty.
- The output is **names and email addresses**, not company profiles.
- Apollo removed from workflow (4.3% email hit rate in benchmarking, not worth credits).

## Input Format

**Echo contact lists:** "Cleaned Contacts" tab with columns: Account Name, Org Name, Recent Name 1-3, Recent Email 1-3. If "Extracted List" tab exists, ingest as baseline contacts.

**Account lists (no contacts):** Accept files with Account Name and State columns. Handle non-standard headers (like Cisco "Accounts by Spend" exports) by scanning first 20 rows for the row containing column names like "Account Name" and using that as header.

CSV also accepted. Drop SFDC Account ID and Org ID columns immediately.

---

## PHASE 0: AUTO-DETECT & CONFIGURE

**Geography detection is automatic. Manual prompting is the fallback, not the default.**

### Step 1: Scan the file for geography

Before asking the user anything, analyze the uploaded file to detect the geographic scope:

**If state column exists** (Billing State/Province, State, Company State, etc.):
- Tally state distribution
- Normalize variants (WI/Wisconsin/WISCONSIN → WI)
- Identify dominant states (any state with 5%+ of rows)

**If no state column but emails exist:**
- Extract corporate domains from emails
- Web search a sample of 3-5 domains to identify company locations
- Infer geography from the cluster of results

**If no state and no emails:**
- Check the filename or sheet name for state references
- Fall back to manual prompt

### Step 2: Confirm with user (not ask from scratch)

Present the auto-detected geography for confirmation:

"I see 1,398 WI accounts (51%) and 846 IL accounts (31%) in this file. Should I use **WI and IL** as the target states, or do you want to adjust?"

User can confirm, adjust, or add states. This replaces the old "what states?" open-ended prompt.

### Step 3: Config summary

Display before proceeding:
- Target state(s): [confirmed]
- Enrichment goal: IT/leadership contact names + verified email addresses
- Provider strategy: Clay + ZoomInfo in parallel (Apollo removed)
- Title filter: standard for companies 25+ employees, no-filter for micro-SMBs
- CRM skip threshold: 2+ relevant contacts

### Step 4: Per-account state routing

Store each account's specific state from the file (if available) as `account_state`. During enrichment, use that account's individual state rather than blanketing all accounts with the same filter. A WI account searches for WI contacts, an IL account searches for IL contacts. The `target_states` from Step 2 is the fallback for accounts without a state column.

---

## PHASE 1: INGEST & PARTNER SCRUB

### 1A: Parse the uploaded file

```python
import pandas as pd

if file_path.endswith('.csv'):
    df = pd.read_csv(file_path)
else:
    # Try standard sheet names first, fall back to first sheet
    df = pd.read_excel(file_path, sheet_name='Cleaned Contacts')

drop_cols = ['SFDC Account ID', 'Org ID']
df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
```

Handle non-standard headers: scan first 20 rows for a row containing "Account Name" or "Account Owner" and use that as header. Skip metadata rows above it.

If "Extracted List" tab exists, read separately as `df_baseline`.

### 1B: Partner Domain Scrubbing (MANDATORY — always runs)

Three-layer filter on every contact email:

**Layer 1 — Hardcoded cache.** Read `references/partner_cache.json` (63+ MSP/VAR domains, 7+ partner account names). Check every email domain and Account Name.

**Layer 2 — "Removed" tab ingestion.** If file has "Removed" tabs, extract partner domains and merge into filter set.

**Layer 3 — Cross-account pattern detection.** Flag any email domain across 3+ different Account Names. Present to user for confirmation.

Also filter generic/ISP domains: gmail.com, yahoo.com, sbcglobal.net, att.net, comcast.net, hotmail.com, aol.com, outlook.com, icloud.com, msn.com, live.com, verizon.net, earthlink.net, frontier.com, roadrunner.com, charter.net, windstream.net.

### 1C: Deduplication

One row per unique Account Name. Collect unique Org Names, corporate emails, contact names.

---

## PHASE 2: ZOHO CRM CROSS-REFERENCE

Read latest zoho-crm-v* companion skill before CRM calls.

### 2A: Account Matching

`ZohoCRM_Search_Records` on Accounts module by Account_Name. Batch to avoid rate limits.

### 2B: Contact Inventory + Classification

- `CRM Covered` — 2+ relevant contacts in Zoho. Skip enrichment.
- `CRM Partial` — Account exists, 0-1 relevant contacts. Enrich for more.
- `CRM New` — Not in Zoho. Full enrichment.

### Phase 2 Checkpoint

Summary table. Get confirmation before proceeding.

---

## PHASE 3: DOMAIN EXTRACTION & NAME CLEANING

No credits consumed. Resolve every account to a searchable domain BEFORE paid API calls.

### 3A: Domain Extraction

Extract corporate domains from surviving Echo emails (post-partner scrub).

### 3B: Domain-vs-Account Validation

Flag Echo emails where domain doesn't plausibly match Account Name. Example: Account "A And W Restaurant" with email ces@aecompanies.com → flag as mismatch. Still attempt enrichment under both identities but flag for human review.

### 3C: Best Name Resolution

1. Account Name = `primary_name`
2. Non-Meraki-URL Org Name = `alt_name`
3. Multiple independent Org Names = `multi_org` (each gets own enrichment)
4. Meraki URLs ignored as name sources

### 3D: Web Search Pre-Clean

For accounts WITHOUT a domain, use `web_search` to find one. Flag during resolution:
- **Defunct/acquired companies** → Manual Review
- **IT/MSP companies** → potential partner flag
- **Franchisees** without own domain → Manual Review
- **"OOB" suffix** → verify still in business

### 3E: Tier Classification

- **Tier 1:** Has domain → domain-based enrichment (Clay + ZoomInfo)
- **Tier 2:** No domain, confirmed name → ZoomInfo name-search only (Clay requires domain)
- **Tier 3:** Unresolvable → Manual Review

### Phase 3 Checkpoint

Resolution summary. Approval before credit-consuming phases.

---

## PHASE 4: COMPANY RESOLUTION

Lightweight. Confirm company exists and get metadata (employee count is used for adaptive filtering in Phase 5).

### Tier 1 (have domain)

**Clay:** `find-and-enrich-company` with domain. Returns employee count, industry, confirmed name.

### Tier 2 (name only, no domain)

**ZoomInfo:** `search_companies` with companyName + state. ZoomInfo does not require a domain (Clay does). If ZI returns a domain, feed to Clay for contact search. If no domain found, ZoomInfo remains the only enrichment path for this account.

---

## PHASE 5: CONTACT ENRICHMENT

**Clay-first architecture with conditional ZoomInfo.**

Clay runs on every Tier 1 account. ZoomInfo only fires when Clay's results have a gap. This conserves ZoomInfo credits (which cost 3-5x more per contact than Clay) while still catching the IT leadership contacts that ZoomInfo finds better.

### Step 1: Clay — Run on ALL Tier 1 accounts (async email)

**Step 1A: Find contacts + request email enrichment**

```
Clay: find-and-enrich-contacts-at-company
  companyIdentifier: <domain>
  contactFilters:
    job_title_keywords: [see adaptive filter below]
    locations: [account_state or target_states, as full names e.g. "Wisconsin"]
  dataPoints:
    contactDataPoints: [{"type": "Email"}]
```

**Adaptive title filtering:**
- Companies with 25+ employees (from Phase 4 company data): use full title filter: ["IT Director", "IT Manager", "Network Administrator", "Systems Administrator", "Director of IT", "VP of IT", "CTO", "CIO", "Director of Operations", "Operations Manager", "Office Manager", "CFO", "Procurement Manager", "Purchasing Director", "Facilities Manager", "Director of Infrastructure"]
- Companies under 25 employees: drop job_title_keywords entirely, keep only locations filter. At a 10-person company, the buyer is the owner or office manager, not someone with "IT Director" in their title.

**Step 1B: Poll for async email results (MANDATORY)**

```
Clay: get-task
  taskId: <taskId from Step 1A>
```

Wait 5-8 seconds, then poll. Check enrichments array:
- `state: "completed"` + `value: "user@domain.com"` → email found
- `state: "in-progress"` → poll again (up to 5 retries)
- `state: "completed"` + `value: null` → email not found

### Step 2: Evaluate Clay results → conditionally trigger ZoomInfo

After Clay returns, evaluate what you got for each account:

**Clay found 2+ contacts with IT-relevant titles AND verified emails → DONE.** Skip ZoomInfo. Clay found the right people.

**Clay found contacts but NONE with IT/networking/infrastructure titles → TRIGGER ZoomInfo.** This is ZoomInfo's sweet spot. Clay returned C-suite or general management, but no one in IT. ZoomInfo is better at finding the dedicated IT layer (IT Director, Network Admin, Systems Admin) at mid-size companies. Benchmark example: Clay found an EVP at The DRG, but ZoomInfo found the CIO.

**Clay found 0 contacts → TRIGGER ZoomInfo.** ZoomInfo can search by company name + state, so it may find contacts at companies where Clay drew a blank. Benchmark example: Clay found 0 at Keene's Transfer, ZoomInfo found the Operations Manager.

**Clay found contacts but all email enrichments failed → RE-POLL Clay once more.** If still no emails after the extra poll, trigger ZoomInfo as fallback for email retrieval.

**Tier 2 accounts (no domain) → ZoomInfo ALWAYS runs.** Clay requires a domain, so ZoomInfo is the only path for these accounts.

### Step 3: ZoomInfo (when triggered)

```
ZoomInfo: search_contacts
  companyName: <resolved company name>
  state: <account_state or target_states>
  jobTitle: "IT Director OR IT Manager OR CIO OR CTO OR VP of IT OR Network Administrator OR Systems Administrator OR Operations Manager OR CFO OR President OR CEO"
  managementLevel: "Director,VP,C-Level,Manager"
  requiredFields: "email"
  contactAccuracyScoreMin: "75"
  pageSize: 10
```

Then call `enrich_contacts` with ZoomInfo person IDs to retrieve actual email addresses (search_contacts returns hasEmail flags, not the addresses themselves).

### Step 4: Deduplicate (if both ran)

If ZoomInfo ran on an account where Clay also returned results:
1. Match contacts by normalized name + domain
2. Same person in both → prefer Clay email
3. Different people → keep both
4. Remove exact duplicates

### Post-Enrichment Partner Scrub (MANDATORY)

Run ALL newly discovered contacts through the partner domain filter from Phase 1B. Any MSP/partner domain → Removed Partners tab.

---

## PHASE 6: OUTPUT GENERATION

### Multi-tab XLSX

**Tab 1 — Enriched Contacts (THE DELIVERABLE):**

| Column | Description |
|--------|-------------|
| Account Name | Original account name from input file |
| Contact Name | Full name |
| Title | Job title |
| Email | Verified email address |
| Source | Clay / ZoomInfo / Both |
| Domain | Company domain |
| State | Contact or company state |

No company background data unless explicitly requested.

**Tab 2 — Manual Review:** Defunct companies, potential partners, domain mismatches, franchisees, OOB accounts. Columns: Account Name, Flag, Resolution, Recommended Action.

**Tab 3 — CRM Covered (Skipped):** Accounts with 2+ contacts in Zoho. Columns: Account Name, Zoho Account ID (hyperlinked), Contact Count, Contact Names/Titles.

**Tab 4 — Removed Partners:** Phase 1B + Phase 5 post-scrub. Columns: Account Name, Contact Name, Email, Domain, Removal Reason, Phase Caught.

**Tab 5 — Run Stats:** Credit consumption, accounts per tier, Clay vs ZoomInfo hit rates, overlap percentage, total contacts with emails, partners removed, timestamp.

### Formatting

- Freeze header rows, auto-filter, auto-width columns
- Arial font, professional styling
- Green highlight on verified emails
- Red highlight on zero-result accounts

### Cache Update

Update `references/partner_cache.json` with newly discovered partner domains.

---

## Guardrails

- **Phase 0 auto-detects geography** from the file and confirms with user. Manual prompt is the fallback only when the file has no state data.
- **Per-account state routing:** Each account uses its own state from the file for enrichment calls, not a single global state filter.
- **Phase 2 (CRM check) runs BEFORE enrichment.** Don't burn credits on covered accounts.
- **Phase 3 (web search) runs BEFORE paid APIs.** Clay requires a domain.
- **Clay runs first, ZoomInfo is conditional.** ZoomInfo only fires when Clay didn't find IT-titled contacts, found 0 contacts, or on Tier 2 (no domain) accounts. This saves ZoomInfo credits (3-5x more expensive per contact than Clay).
- **Partner scrubbing runs twice:** Phase 1B (input) and Phase 5 (post-enrichment).
- **Clay email enrichment is async.** Poll `get-task` with taskId. Skipping the poll = zero emails.
- **ZoomInfo enrich_contacts** for actual email addresses after search_contacts (which only returns hasEmail flags).
- **Adaptive title filtering:** drop title keywords for companies under 25 employees.
- **Deduplicate** across Clay + ZoomInfo results before output.
- **Apollo is NOT used.** Benchmarking showed 4.3% email hit rate (1 of 23 attempts). Not worth credits.
- **Output is names + emails, not company profiles.**
- Batch sizes: ZoomInfo enrich = 10/call. Clay = 1 company per call (async).
- For lists >100 accounts, process in batches of 50 with intermediate file writes.
- Read latest zoho-crm-v* companion skill before CRM operations. Phase 2 is READ-ONLY.

## Provider Hierarchy (quick reference)

```
COMPANY RESOLUTION:
  1. Clay: find-and-enrich-company (domain) → Tier 1
  2. ZoomInfo: enrich_companies (domain, batch 10) → parallel with Clay, gets ZI Company ID
  3. ZoomInfo: search_companies (name + state) → Tier 2 (no domain needed, ZI advantage)

CONTACT ENRICHMENT (Clay-first, conditional ZoomInfo):
  Step 1 — Clay (all Tier 1 accounts):
    → find-and-enrich-contacts-at-company (domain + titles + state + Email dataPoint)
    → get-task (poll for async emails, 5-8s delay, up to 5 retries)

  Step 2 — Evaluate Clay results per account:
    → 2+ IT-titled contacts with emails? → DONE, skip ZoomInfo
    → Contacts but no IT titles? → TRIGGER ZoomInfo (IT leadership gap)
    → 0 contacts? → TRIGGER ZoomInfo (name+state search, no domain needed)
    → Tier 2 (no domain)? → ZoomInfo ALWAYS (Clay can't search without domain)

  Step 3 — ZoomInfo (when triggered, ~30-40% of accounts):
    → search_contacts (company + state + titles + requiredFields=email)
    → enrich_contacts (person IDs → actual email addresses)

  Step 4 — Deduplicate if both ran
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Clay not connected | ZoomInfo becomes sole provider |
| Clay email still "in-progress" after 5 polls | Keep contact with name+title, note email pending |
| ZoomInfo rate limit | Pause 30s, retry. Smaller batches if persistent |
| ZoomInfo returns no company | Try without Inc/LLC suffix. Try domain search |
| ZoomInfo enrich_contacts fails | Use hasEmail flag contacts without verified email, note in output |
| Zoho CRM search returns 0 | Try partial name match (first 3 words) |
| Domain mismatch in Echo | Flag for manual review, attempt enrichment under both identities |
| No state column in file | Fall back to manual state prompt |
| Non-standard file headers | Scan first 20 rows for header row |
| Large list (200+) | Process in chunks of 50, intermediate file writes |
| Company <25 employees | Drop title filter, search all seniority levels |

## Dependencies

- **Clay MCP** — Company resolution, contact discovery + async email enrichment
- **ZoomInfo MCP** — Company search/enrich, contact search + enrich_contacts for emails
- **Zoho CRM MCP** — Account search, contact lookup (read-only)
- **Web Search** — Domain resolution for accounts without Echo emails
- **pandas + openpyxl** — Data processing and XLSX output
- **zoho-crm companion skill** — Business rules for CRM operations

Note: Apollo MCP removed from dependencies in v2.2. If Apollo is later needed, use `people_bulk_match` (not `people_search`) with name+domain for email retrieval.

## Changelog

### v2.2 (2026-03-17)
- **Auto-detect geography** (Phase 0): scans file for state columns, tallies distribution, and presents auto-detected states for user confirmation instead of open-ended prompt. Falls back to manual prompt only when file has no state data.
- **Per-account state routing** (Phase 0): each account uses its own state from the file during enrichment calls, rather than a single global state filter for all accounts.
- **Clay-first with conditional ZoomInfo** (Phase 5): Clay runs on every account first. ZoomInfo only fires when Clay's results lack IT-titled contacts, returned 0 contacts, or for Tier 2 accounts (no domain). This saves ZoomInfo credits (~30-40% of accounts trigger ZI vs 100% under parallel). Benchmarking showed ZI's value is specifically finding IT leadership (CIO at The DRG, IT Director at Therma-Stor) that Clay misses, not general contact discovery.
- **Apollo removed** (Phase 5): benchmark test showed 4.3% email hit rate (1 email from 23 bulk_match attempts). Clay + ZoomInfo together cover everything Apollo was doing.
- **Adaptive title filtering** (Phase 5): drops job_title_keywords for companies under 25 employees. Micro-SMBs rarely have anyone with "IT Director" in their title; the buyer is typically the owner or office manager.
- **ZoomInfo enrich_contacts** (Phase 5): added explicit call to retrieve actual email addresses after search_contacts (which only returns hasEmail flags).
- **Cross-provider deduplication** (Phase 5): merge Clay + ZoomInfo results by name+domain before output to prevent duplicate contacts.
- **ZoomInfo for Tier 2** (Phase 4-5): ZoomInfo is the only provider that can search by company name + state without a domain. Covers the ~20% of accounts where domain resolution fails.
- All v2.1 features retained: partner cache, 3-layer filter, CRM cross-ref, web search pre-clean, domain-vs-account validation, manual review flags

### v2.1 (2026-03-17)
- Clay async email polling fix, Apollo endpoint correction, output restructured to names+emails, domain-vs-account validation, non-standard header detection

### v2.0 (2026-03-17)
- Mandatory state prompt, CRM check before enrichment, web search pre-clean, Clay integration, provider waterfall

### v1.0 (2026-03-11)
- Initial release: 6-phase workflow with partner filtering, Zoho CRM cross-ref, ZoomInfo enrichment
