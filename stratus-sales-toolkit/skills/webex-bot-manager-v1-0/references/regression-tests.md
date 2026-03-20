# Regression Test Suite — Stratus AI Webex Bot

Run these tests via Webex MCP after any code change. Send each message to the bot DM room and immediately list messages to check the response (no-wait polling).

Bot DM Room ID: `Y2lzY29zcGFyazovL3VzL1JPT00vYTNmMTllOTAtMjNjMC0xMWYxLWI5MmMtZDEwOTQxNGE1YTBh`

## Core Quoting Tests

### T01 — Single AP
**Input:** `MR44`
**Expected:** 3 URLs (1-Year, 3-Year, 5-Year). Each URL contains `MR44-HW` and `LIC-ENT-{1YR,3YR,5YR}`.

### T02 — Single AP with Quantity
**Input:** `5 MR44`
**Expected:** 3 URLs. qty=5,5 for both hardware and license.

### T03 — Multi-SKU Quote
**Input:** `2 MR44, 1 MX67`
**Expected:** 3 URLs. Each contains MR44-HW, LIC-ENT, MX67-HW, LIC-MX67-SEC (default tier).

### T04 — MX with Explicit Tier
**Input:** `MX85 enterprise`
**Expected:** 3 URLs with LIC-MX85-ENT-{1Y,3Y,5Y} (not SEC).

### T05 — MX SD-WAN Tier
**Input:** `MX85 SD-WAN`
**Expected:** 3 URLs with LIC-MX85-SDW-{1Y,3Y,5Y}.

## Suffix Tests

### T06 — CW Wi-Fi 6E Suffix
**Input:** `CW9166I`
**Expected:** URLs contain `CW9166I-MR` (not -HW).

### T07 — CW Wi-Fi 7 Suffix
**Input:** `CW9172H`
**Expected:** URLs contain `CW9172H-RTG` (not -MR or -HW).

### T08 — MX Cellular Suffix
**Input:** `MX67C`
**Expected:** URLs contain `MX67C-HW-NA`.

### T09 — MS150 No Suffix
**Input:** `MS150-48LP-4G`
**Expected:** URLs contain `MS150-48LP-4G` (no suffix added).

### T10 — MS130 HW Suffix
**Input:** `MS130-24P`
**Expected:** URLs contain `MS130-24P-HW`.

## Modifier Tests

### T11 — Hardware Only
**Input:** `MR44 hardware`
**Expected:** Single URL (no 1Y/3Y/5Y breakdown). Contains `MR44-HW` only, no LIC-ENT.

### T12 — Hardware Only Multi-SKU
**Input:** `2 MR44, 1 MX67 hardware only`
**Expected:** Single URL with MR44-HW and MX67-HW. No licenses.

### T13 — License Only
**Input:** `MR44 license only`
**Expected:** 3 URLs containing only LIC-ENT-{1YR,3YR,5YR}. No MR44-HW.

### T14 — With Pricing
**Input:** `MR44 with pricing`
**Expected:** 3 URLs plus pricing breakdown with dollar amounts.

### T15 — Single Term
**Input:** `just 3 year MR44`
**Expected:** Single URL (3-Year only) with MR44-HW and LIC-ENT-3YR.

### T16 — Hardware Specs (Should NOT Trigger Hardware-Only)
**Input:** `MR44 hardware specs`
**Expected:** Routes to Claude for a specs response (not a hardware-only quote URL).

## Z-Series Tests

### T17 — Z4 Default SEC
**Input:** `Z4`
**Expected:** 3 URLs with `Z4-HW` and `LIC-Z4-SEC-{1Y,3Y,5Y}` (default SEC, not ENT).

### T18 — Z4 Explicit ENT
**Input:** `Z4 enterprise`
**Expected:** 3 URLs with `LIC-Z4-ENT-{1Y,3Y,5Y}`.

### T19 — Z4C Default SEC
**Input:** `Z4C`
**Expected:** 3 URLs with `Z4C-HW` and `LIC-Z4C-SEC-{1Y,3Y,5Y}`.

### T20 — Z4X No Suffix
**Input:** `Z4X`
**Expected:** URLs contain `Z4X` (no -HW suffix). Z4X has no license.

## EOL Tests

### T21 — EOL Product
**Input:** `MX64`
**Expected:** EOL warning message mentioning MX67 as replacement. Option A (renew license) and Option B (hardware refresh to MX67).

### T22 — EOL with Refresh Semantics
**Input:** (requires conversation context) After quoting an MX64 renewal, say "include a refresh option"
**Expected:** Claude adds hardware refresh option with MX67-HW + all original licenses carried over.

## License Dashboard Tests

### T23 — Dashboard Screenshot (License Table Only)
**Input:** Screenshot of license SKU table (no device counts visible)
**Expected:** Quotes licenses exactly as shown. Does NOT ask for device counts.

### T24 — Dashboard Screenshot (Full Dashboard)
**Input:** Screenshot with both license table and active device counts
**Expected:** Applies 5 mismatch rules (match, fewer, zero, more, MT free-tier).

## Direct License SKU Tests

### T25 — Direct License Input
**Input:** `LIC-ENT-3YR`
**Expected:** Single URL with just `LIC-ENT-3YR`, qty 1.

### T26 — Direct License with Quantity
**Input:** `10 LIC-ENT-3YR`
**Expected:** Single URL with `LIC-ENT-3YR`, qty 10.

## Edge Cases

### T27 — Invalid SKU
**Input:** `MR99`
**Expected:** Error message with "not a recognized model" and suggestions of valid MR models.

### T28 — Common Mistake
**Input:** Any SKU in the `_COMMON_MISTAKES` catalog
**Expected:** Error message with the correct suggestion.

### T29 — Partial Match (Ambiguous)
**Input:** `MS130`
**Expected:** Lists MS130 variants and asks which one the user needs.

### T30 — Conversational (Claude Fallback)
**Input:** `what's the difference between MX85 and MX95?`
**Expected:** Claude responds with a comparison using specs data. Should NOT produce quote URLs.

---

## Running Tests

### Quick Smoke Test (5 tests)
Run T01, T11, T17, T06, T21 to cover core quoting, hardware-only, Z4 SEC default, CW suffix, and EOL.

### Full Regression (all 30 tests)
Run all tests sequentially. Expected time: ~2 minutes total (most responses are instant from deterministic engine, Claude fallback tests take 2-3 seconds each).

### Test via Webex MCP

```
1. Fetch webex-bots skill to get proper message format
2. Send message to bot DM room ID
3. Immediately list messages (no delay)
4. Compare bot response against expected output
5. Log pass/fail
```

For screenshot tests (T23, T24), attach an image file to the message.
