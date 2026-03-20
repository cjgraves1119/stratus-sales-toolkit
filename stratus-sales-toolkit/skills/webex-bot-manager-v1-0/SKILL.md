---
name: webex-bot-manager-v1-0
description: "manage, update, test, and deploy the stratus ai webex quoting bot. covers cloudflare workers deployment, github sync, railway backup failover, price book updates via price-book-updater integration, system prompt iteration, eol catalog updates, deterministic engine bug fixes, regression testing via webex mcp (no-wait polling), secret rotation, and webhook failover. embeds full bot architecture knowledge including sku suffix rules, license mapping, eol handling, parser logic, and claude api fallback structure. triggers: update bot, fix bot, bot bug, deploy bot, bot deploy, push bot, webex bot, stratus bot, bot update, bot test, test bot, bot regression, bot price update, update bot prices, bot webhook, switch webhook, bot failover, railway failover, bot secret, rotate secret, bot prompt, update prompt, system prompt, bot eol, update eol, bot catalog, update catalog, bot engine, parser fix, bot code, edit bot, bot manager, manage bot."
---

# Webex Bot Manager v1-0

Manage the Stratus AI Webex quoting bot end-to-end: code changes, deployment, price updates, testing, and failover. This skill embeds deep knowledge of the bot's architecture so you can make targeted fixes without re-reading the full source each time.

## Architecture Overview

The Stratus AI bot is a Cisco/Meraki quoting assistant that runs in Webex. It uses a two-tier response system: a deterministic JavaScript engine handles well-formed SKU requests instantly, and a Claude API fallback handles ambiguous/conversational requests.

```
User message (Webex webhook POST)
  │
  ├─ parseMessage() → identifies SKUs, quantities, modifiers
  │     │
  │     ├─ Has items? → buildQuoteResponse()
  │     │     ├─ needsLlm: false → send deterministic reply
  │     │     └─ needsLlm: true  → fall through to Claude
  │     │
  │     ├─ Revision with no items? → Claude + revision context
  │     ├─ Advisory question? → Claude + specs context
  │     └─ null (no SKUs found) → Full Claude fallback
  │
  └─ Image attachment? → Claude with base64 vision
```

### Primary Environment: Cloudflare Workers (Free Plan)

| Setting | Value |
|---------|-------|
| Worker name | `stratus-ai-bot` |
| URL | `https://stratus-ai-bot.chrisg-ec1.workers.dev` |
| Account ID | `ec1888c5a0b51dc3eebf6bae13a3922b` |
| KV namespace | `CONVERSATION_KV` (ID: `360fbb8a75bf400e87cb96893a811a56`) |
| Compatibility date | `2024-01-01` |
| Entry point | `src/index.js` |
| Deploy command | `cd <worker-dir> && CLOUDFLARE_API_TOKEN=<token> npx wrangler deploy` |

Secrets (set via `wrangler secret put`): `WEBEX_BOT_TOKEN`, `ANTHROPIC_API_KEY`

### Backup Environment: Railway

| Setting | Value |
|---------|-------|
| URL | `https://stratus-bot-v2-production.up.railway.app` |
| Runtime | Express/Node.js |
| Plan | Trial (30-day / $4.99 limit) |

Railway runs the Express version of the same bot. It shares the same Webex bot token and Anthropic key but uses in-memory conversation history instead of KV.

### GitHub Repository

| Setting | Value |
|---------|-------|
| Repo | `cjgraves1119/stratus-bot-v2` |
| Clone | `git clone https://cjgraves1119:{PAT}@github.com/cjgraves1119/stratus-bot-v2.git` |
| Worker path | `worker/` (Cloudflare version) |
| Express path | root `/` (Railway version) |

PAT is stored in the user's CLAUDE.md preferences. Never commit it to the repo.

### Webex Webhook

| Setting | Value |
|---------|-------|
| Webhook ID | `Y2lzY29zcGFyazovL3VzL1dFQkhPT0svY2FlYTI5NjYtM2RmOC00MzE5LWI1MWYtOWFiZjJjZWJhODg3` |
| Bot email | `StratusAI@webex.bot` |
| DM room ID | `Y2lzY29zcGFyazovL3VzL1JPT00vYTNmMTllOTAtMjNjMC0xMWYxLWI5MmMtZDEwOTQxNGE1YTBh` |
| Target | Currently Cloudflare Workers URL |

To switch webhook target (e.g., failover to Railway):
```bash
curl -X PUT "https://webexapis.com/v1/webhooks/{WEBHOOK_ID}" \
  -H "Authorization: Bearer {BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"stratus-ai-bot","targetUrl":"{NEW_URL}/webhook"}'
```

---

## Bot Engine Knowledge (Embedded Reference)

This section captures the bot's core logic so Claude can make targeted fixes without reading the full 1200-line source every time.

### File Structure

```
worker/
├── src/
│   ├── index.js          — Main bot logic (all functions + Worker entry point)
│   └── data/
│       ├── prices.json    — SKU pricing (list, ecomm price, discount %). ~100KB
│       ├── auto-catalog.json — Valid SKUs by family + EOL products/replacements + common mistakes. ~8KB
│       └── specs.json     — Product specifications by model. ~28KB
├── wrangler.toml          — Cloudflare Workers config
└── package.json           — Dependencies (wrangler only)
```

### Key Functions (line numbers approximate, may shift after edits)

| Function | Purpose |
|----------|---------|
| `applySuffix(sku)` | Adds correct -HW, -MR, -RTG suffix based on product family |
| `getLicenseSkus(baseSku, tier)` | Returns 1Y/3Y/5Y license SKU array for a hardware model |
| `parseMessage(text)` | Extracts SKUs, quantities, modifiers (hardwareOnly, licenseOnly, showPricing, tier, term) |
| `buildQuoteResponse(parsed)` | Builds URL output from parsed data, decides if LLM fallback needed |
| `buildStratusUrl(items)` | Constructs stratusinfosystems.com/order URL |
| `validateSku(baseSku)` | Checks SKU against catalog, returns suggestions for invalid SKUs |
| `checkEol(baseSku)` / `isEol(baseSku)` | EOL detection and replacement lookup |
| `fixCommonMistake(sku)` | Maps common typos to correct SKUs |
| `getStaticSpecsContext(msg)` | Pulls specs.json data for models mentioned in message |
| `getRelevantDatasheetContext(msg)` | Fetches live Meraki datasheets for spec questions |
| `askClaude(msg, personId, env, imageData)` | Claude API fallback with conversation history |
| `getHistory(kv, personId)` / `addToHistory(...)` | KV-backed conversation history (10 messages, 30min TTL) |

### SKU Suffix Rules

| Family | Suffix | Examples |
|--------|--------|---------|
| MR (all), MV, MT, MG, Z (not X variants) | `-HW` | MR44-HW, MV63-HW, Z4-HW |
| MX non-cellular | `-HW` | MX67-HW, MX85-HW |
| MX cellular (MXxxC, MXxxCW) | `-HW-NA` | MX67C-HW-NA |
| CW916x (Wi-Fi 6E) | `-MR` | CW9166I-MR |
| CW917x (Wi-Fi 7) | `-RTG` | CW9172H-RTG |
| MS130, MS130R, MS390 | `-HW` | MS130-24P-HW, MS390-48UX-HW |
| MS150, MS450, C9xxx-M, MA- | No suffix | MS150-48LP-4G, C9300-24P-M |
| Z4X, Z4CX | No suffix | Z4X (sold as-is) |

### License Mapping Rules

| Hardware | License Pattern | Default Tier |
|----------|----------------|-------------|
| MR + CW APs | LIC-ENT-{1YR,3YR,5YR} | ENT (only option) |
| MX67/68/250/450 | LIC-MX{model}-{tier}-{1YR,3YR,5YR} | SEC |
| MX75/85/95/105 | LIC-MX{model}-{tier}-{1Y,3Y,5Y} | SEC |
| Z1/Z3/Z3C | LIC-Z{model}-ENT-{1YR,3YR,5YR} | ENT (only option) |
| Z4/Z4C | LIC-Z{model}-{tier}-{1Y,3Y,5Y} | SEC |
| MG | LIC-MG{model}-ENT-{1Y,3Y,5Y} | ENT |
| MV | LIC-MV-{1YR,3YR,5YR} | (single tier) |
| MT | LIC-MT-{1Y,3Y,5Y} | (single tier) |
| MS130 compact (8/8P/8X/12X) | LIC-MS130-CMPT-{1Y,3Y,5Y} | (single tier) |
| MS130 standard (24/48) | LIC-MS130-{24,48}-{1Y,3Y,5Y} | (single tier) |
| MS150 | LIC-MS150-{24,48}-{1Y,3Y,5Y} | (single tier) |
| MS390, MS450 | No license in URL (DNA separate) | N/A |

Note the YR vs Y suffix pattern: older models use YR (e.g., 1YR), newer models use Y (e.g., 1Y). MX75+ and Z4 use Y. MX67/68/250/450 and Z1/Z3 use YR. SD-WAN licenses always use Y.

### System Prompt Sections

The `SYSTEM_PROMPT` constant contains these key sections that are frequently updated:
1. YOUR ROLE / REASONING APPROACH / PERSONA
2. URL FORMAT + SKU SUFFIX RULES + LICENSE RULES
3. VALID PRODUCT CATALOG (full list of valid models)
4. LICENSE DASHBOARD SCREENSHOT HANDLING (OCR mismatch rules)
5. REFRESH / UPGRADE / HARDWARE UPGRADE SEMANTICS
6. HARDWARE-ONLY MODE
7. Z-SERIES DEFAULT LICENSE TIER
8. OUTPUT RULES

When updating system prompt sections, locate them by searching for the `##` headers within the SYSTEM_PROMPT template literal.

### Parser Modifiers

`parseMessage()` detects these modifiers from user text:
- **hardwareOnly**: "hardware only", "hardware", "no license", "hw only" (excludes "hardware specs/info/details")
- **licenseOnly**: "license only", "just the license", "renewal only", "no hardware"
- **showPricing**: "how much", "price/pricing/cost", "with pricing"
- **requestedTier**: SEC, ENT, or SDW based on keywords
- **requestedTerm**: 1, 3, or 5 (only when preceded by "just" or "only")
- **isAdvisory**: comparison/recommendation/spec questions (routes to Claude)
- **isRevision**: modification verbs like "remove", "add", "change", "instead of"

---

## Workflow 1: Code Changes and Deployment

Use this workflow for any bug fix, feature addition, or engine update.

### Step 1 — Get the Source

If the bot source is not already in the session:
```bash
cd /sessions/$(basename $PWD)
git clone https://cjgraves1119:{PAT}@github.com/cjgraves1119/stratus-bot-v2.git
cd stratus-bot-v2/worker
```

If already cloned, pull latest:
```bash
cd /sessions/$(basename $PWD)/stratus-bot-v2 && git pull origin main
```

The Cloudflare worker code lives in `worker/src/index.js`.

### Step 2 — Make the Change

Use the embedded architecture knowledge above to locate the right function. For common change types:

| Change Type | Where to Look |
|-------------|--------------|
| Suffix rule fix | `applySuffix()` function |
| License mapping fix | `getLicenseSkus()` function |
| New parser modifier | `parseMessage()` function, modifiers section |
| System prompt update | `SYSTEM_PROMPT` template literal |
| EOL product update | `auto-catalog.json` → `_EOL_PRODUCTS` and `_EOL_REPLACEMENTS` |
| Common mistake addition | `auto-catalog.json` → `_COMMON_MISTAKES` |
| Price update | `prices.json` (use Workflow 3 for bulk updates) |
| Specs update | `specs.json` |
| New product family | Add to catalog JSON + update `detectFamily()` + update `applySuffix()` + update `getLicenseSkus()` |

### Step 3 — Deploy to Cloudflare

```bash
cd /sessions/$(basename $PWD)/stratus-bot-v2/worker
CLOUDFLARE_API_TOKEN={token} npx wrangler deploy
```

The Cloudflare API token is stored in user preferences. Deployment takes ~5 seconds and is zero-downtime.

### Step 4 — Test via Webex

Read the latest webex-bots skill before testing. Use the Webex MCP to send a test message and immediately poll for the response (no wait delay needed, the bot responds in ~1 second on Cloudflare):

```
1. Send test message to bot DM room
2. Immediately list messages in the room (no sleep/delay)
3. Read the bot's response
4. Compare against expected output
```

Bot DM room ID: `Y2lzY29zcGFyazovL3VzL1JPT00vYTNmMTllOTAtMjNjMC0xMWYxLWI5MmMtZDEwOTQxNGE1YTBh`

Run at least 2-3 test messages covering the specific change plus a regression test from the suite (see references/regression-tests.md).

### Step 5 — Push to GitHub

```bash
cd /sessions/$(basename $PWD)/stratus-bot-v2
git add -A
git commit -m "fix: {brief description of change}"
git push origin main
```

### Step 6 — Copy to Outputs

```bash
cp -r /sessions/$(basename $PWD)/stratus-bot-v2/worker /mnt/outputs/stratus-ai-worker
```

---

## Workflow 2: System Prompt Iteration

For updates to how Claude handles ambiguous requests, screenshot analysis, or conversational behavior.

### Step 1 — Identify the Section

Search for the relevant `##` header in the SYSTEM_PROMPT:
```bash
grep -n "^##" worker/src/index.js
```

### Step 2 — Edit the Section

Use the Edit tool to modify the specific section within the SYSTEM_PROMPT template literal. Keep changes focused and avoid touching unrelated sections.

### Step 3 — Test with a Real Scenario

Send a message that exercises the updated prompt logic. For screenshot handling, attach an image. For advisory questions, ask a product comparison question.

Since system prompt changes only affect Claude fallback behavior (not the deterministic engine), test messages should be ones that route to Claude:
- Advisory questions: "what's the difference between MX85 and MX95?"
- Screenshot handling: send a license dashboard screenshot
- Revision requests: "actually change that to 5-year"
- Ambiguous requests: "I need something for a small office, 50 users"

### Step 4 — Deploy and Verify

Follow Steps 3-6 from Workflow 1.

---

## Workflow 3: Price Book Update

Integrates with the `price-book-updater` skill. When a new Meraki price book arrives, the flow is:

### Step 1 — Run Price Book Updater

Invoke the price-book-updater skill with the new XLSX. It produces:
- `prices.json` — cleaned pricing data in Stratus format
- `Price List {date} (Cleaned).xlsx` — filtered Excel for reference

### Step 2 — Replace Bot Prices

```bash
cp /mnt/outputs/prices.json /sessions/$(basename $PWD)/stratus-bot-v2/worker/src/data/prices.json
```

### Step 3 — Verify SKU Count

```bash
node -e "const p = require('./src/data/prices.json'); console.log('Total SKUs:', Object.keys(p.prices).length)"
```

Compare with the previous count. A significant drop may indicate filtering issues.

### Step 4 — Deploy, Test, and Push

Follow Workflow 1, Steps 3-6. Test with a few common SKUs to verify pricing is correct:
- "MR44 with pricing" (AP)
- "MX67 with pricing" (security appliance)
- "MS130-24P with pricing" (switch)

---

## Workflow 4: EOL Catalog Update

When Cisco announces new End-of-Life products or replacements.

### Step 1 — Edit auto-catalog.json

Add to `_EOL_PRODUCTS` (family → variant array) and `_EOL_REPLACEMENTS` (old SKU → new SKU):

```json
{
  "_EOL_PRODUCTS": {
    "MX64": ["", "W"],
    "MX84": [""]
  },
  "_EOL_REPLACEMENTS": {
    "MX64": "MX67",
    "MX64W": "MX67W",
    "MX84": "MX85"
  }
}
```

### Step 2 — Verify Replacement SKUs Exist

Every replacement SKU must exist in the main catalog families. Check:
```bash
node -e "const c = require('./src/data/auto-catalog.json'); const r = c._EOL_REPLACEMENTS; for (const [old, repl] of Object.entries(r)) { console.log(old, '→', repl); }"
```

### Step 3 — Deploy, Test, and Push

Test with: "quote MX64" (should show EOL warning + replacement option).

---

## Workflow 5: Webhook Failover

Switch the Webex webhook between Cloudflare (primary) and Railway (backup).

### Failover to Railway
```bash
curl -X PUT "https://webexapis.com/v1/webhooks/Y2lzY29zcGFyazovL3VzL1dFQkhPT0svY2FlYTI5NjYtM2RmOC00MzE5LWI1MWYtOWFiZjJjZWJhODg3" \
  -H "Authorization: Bearer {BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"stratus-ai-bot","targetUrl":"https://stratus-bot-v2-production.up.railway.app/webhook"}'
```

### Restore to Cloudflare
```bash
curl -X PUT "https://webexapis.com/v1/webhooks/Y2lzY29zcGFyazovL3VzL1dFQkhPT0svY2FlYTI5NjYtM2RmOC00MzE5LWI1MWYtOWFiZjJjZWJhODg3" \
  -H "Authorization: Bearer {BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"stratus-ai-bot","targetUrl":"https://stratus-ai-bot.chrisg-ec1.workers.dev/webhook"}'
```

After switching, send a test message to verify the bot responds.

---

## Workflow 6: Secret Rotation

### Cloudflare Workers Secrets

```bash
cd /sessions/$(basename $PWD)/stratus-bot-v2/worker
echo "{NEW_VALUE}" | CLOUDFLARE_API_TOKEN={cf_token} npx wrangler secret put WEBEX_BOT_TOKEN
echo "{NEW_VALUE}" | CLOUDFLARE_API_TOKEN={cf_token} npx wrangler secret put ANTHROPIC_API_KEY
```

### Railway Secrets

Update via Railway dashboard or CLI. Railway environment variables are set in the project settings.

### Cloudflare API Token

If the Cloudflare API token itself needs rotation, create a new one at dash.cloudflare.com with Workers permissions (All zones, Account: Workers Scripts Edit) and update the deploy command.

---

## Testing Protocol

### No-Wait Polling Pattern

The bot on Cloudflare responds in ~1 second. When testing via Webex MCP:
1. Send the test message
2. Immediately list messages in the room (do NOT add any sleep or delay)
3. The bot's response will be the most recent message

This pattern works because Cloudflare Workers processes the webhook and sends the reply faster than the round-trip time of the list request.

### Regression Test Suite

See `references/regression-tests.md` for the full test suite. At minimum, run these after any change:

| Test | Input | Expected |
|------|-------|----------|
| Basic AP quote | "MR44" | 3 URLs (1Y/3Y/5Y) with MR44-HW + LIC-ENT |
| Multi-SKU | "2 MR44, 1 MX67" | 3 URLs with both items |
| Hardware only | "MR44 hardware" | Single URL, MR44-HW only, no license |
| Z4 default SEC | "Z4" | 3 URLs with LIC-Z4-SEC (not ENT) |
| EOL product | "MX64" | EOL warning + MX67 replacement option |
| With pricing | "MR44 with pricing" | URLs + price breakdown |
| CW suffix | "CW9166I" | -MR suffix |
| Wi-Fi 7 suffix | "CW9172H" | -RTG suffix |

### Debugging Failed Tests

If a test produces unexpected output:
1. Check if the request was handled by deterministic engine or Claude (deterministic responses are instant, Claude takes 2-3 seconds)
2. For deterministic issues: trace through parseMessage() → buildQuoteResponse()
3. For Claude issues: review the SYSTEM_PROMPT section relevant to the failure
4. Check the Cloudflare Workers logs: `CLOUDFLARE_API_TOKEN={token} npx wrangler tail`

---

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Bot doesn't respond | Webhook pointing to wrong URL | Check webhook target, run Workflow 5 |
| Wrong suffix on SKU | `applySuffix()` rule missing or wrong | Add/fix the regex pattern |
| Wrong license term format (YR vs Y) | `getLicenseSkus()` using wrong suffix | Check model number thresholds |
| "Hardware" triggers hardware-only mode when user asked about specs | Parser regex too broad | Ensure exclusion pattern covers the context word |
| Z4 gets ENT instead of SEC | Default tier logic inverted | Check `getLicenseSkus()` Z-series section |
| Price update didn't take effect | Deployed but didn't push to GitHub | Push to GitHub after deploying |
| KV conversation history missing | TTL expired (30 min) | Expected behavior, not a bug |
| Datasheet fetch returns null | Meraki docs URL changed | Update DATASHEET_URLS mapping |
| Deploy fails | API token expired or wrong | Rotate token per Workflow 6 |
