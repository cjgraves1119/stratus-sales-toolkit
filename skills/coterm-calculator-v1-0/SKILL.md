---
name: coterm-calculator-v1-0
description: "calculate meraki co-term expiration dates using weighted dollar-value method. embedded hot cache of 290 license SKUs for reliable price lookups."
---

# Co-Term Calculator Skill v1.0

## Purpose
Calculate accurate Meraki co-termination expiration dates using the Weighted Dollar-Value method. Uses embedded price cache for reliable lookups with zero hallucination risk.

## Trigger Phrases
- "calculate co-term"
- "co-term expiration"
- "what will my new expiration be"
- "how does this affect my expiration"
- "extend my licenses"
- User provides current expiration + inventory + new purchase

***

## EMBEDDED PRICE CACHE (MANDATORY SOURCE)

All price lookups MUST use this cache. NEVER estimate or guess prices.

### 1-Year License List Prices (for MSRP Weighting)

```
CACHE_1Y = {
  # Enterprise AP (MR, CW series)
  "LIC-ENT-1YR": 201,
  
  # MV Cameras
  "LIC-MV-1YR": 331,
  
  # MT Sensors
  "LIC-MT-1Y": 131,
  
  # MG Cellular
  "LIC-MG21-ENT-1Y": 236,
  "LIC-MG41-ENT-1Y": 473,
  "LIC-MG51-ENT-1Y": 432,
  "LIC-MG52-ENT-1Y": 452,
  
  # Z-Series Security
  "LIC-Z1-SEC-1YR": 101,
  "LIC-Z3-SEC-1YR": 299,
  "LIC-Z3C-SEC-1YR": 442,
  "LIC-Z4-SEC-1Y": 424,
  "LIC-Z4C-SEC-1Y": 513,
  
  # Z-Series Enterprise
  "LIC-Z1-ENT-1YR": 50,
  "LIC-Z3-ENT-1YR": 148,
  "LIC-Z3C-ENT-1YR": 221,
  "LIC-Z4-ENT-1Y": 201,
  "LIC-Z4C-ENT-1Y": 290,
  
  # MX Security Tier
  "LIC-MX50-SEC-1YR": 1000,
  "LIC-MX60-SEC-1YR": 525,
  "LIC-MX60W-SEC-1YR": 578,
  "LIC-MX64-SEC-1YR": 590,
  "LIC-MX64W-SEC-1YR": 639,
  "LIC-MX65-SEC-1YR": 639,
  "LIC-MX65W-SEC-1YR": 785,
  "LIC-MX67-SEC-1YR": 687,
  "LIC-MX67C-SEC-1YR": 834,
  "LIC-MX67W-SEC-1YR": 736,
  "LIC-MX68-SEC-1YR": 736,
  "LIC-MX68CW-SEC-1YR": 1031,
  "LIC-MX68W-SEC-1YR": 884,
  "LIC-MX70-SEC-1YR": 1000,
  "LIC-MX75-SEC-1Y": 1661,
  "LIC-MX80-SEC-1YR": 2100,
  "LIC-MX84-SEC-1YR": 1963,
  "LIC-MX85-SEC-1Y": 2453,
  "LIC-MX90-SEC-1YR": 4200,
  "LIC-MX95-SEC-1Y": 4907,
  "LIC-MX100-SEC-1YR": 4907,
  "LIC-MX105-SEC-1Y": 7359,
  "LIC-MX250-SEC-1YR": 9813,
  "LIC-MX400-SEC-1YR": 15699,
  "LIC-MX450-SEC-1YR": 19625,
  "LIC-MX600-SEC-1YR": 31399,
  
  # MX Enterprise Tier
  "LIC-MX50-ENT-1YR": 500,
  "LIC-MX60-ENT-1YR": 263,
  "LIC-MX60W-ENT-1YR": 290,
  "LIC-MX64-ENT-1YR": 295,
  "LIC-MX64W-ENT-1YR": 320,
  "LIC-MX65-ENT-1YR": 320,
  "LIC-MX65W-ENT-1YR": 393,
  "LIC-MX67-ENT-1YR": 344,
  "LIC-MX67C-ENT-1YR": 418,
  "LIC-MX67W-ENT-1YR": 369,
  "LIC-MX68-ENT-1YR": 369,
  "LIC-MX68CW-ENT-1YR": 515,
  "LIC-MX68W-ENT-1YR": 442,
  "LIC-MX75-ENT-1Y": 833,
  "LIC-MX80-ENT-1YR": 1050,
  "LIC-MX84-ENT-1YR": 982,
  "LIC-MX85-ENT-1Y": 1227,
  "LIC-MX90-ENT-1YR": 2100,
  "LIC-MX95-ENT-1Y": 2453,
  "LIC-MX100-ENT-1YR": 2453,
  "LIC-MX105-ENT-1Y": 3680,
  "LIC-MX250-ENT-1YR": 4907,
  "LIC-MX400-ENT-1YR": 7850,
  "LIC-MX450-ENT-1YR": 9813,
  "LIC-MX600-ENT-1YR": 15699,
  
  # MS120 Series
  "LIC-MS120-8-1YR": 48,
  "LIC-MS120-8LP-1YR": 60,
  "LIC-MS120-8FP-1YR": 78,
  "LIC-MS120-24-1YR": 107,
  "LIC-MS120-24P-1YR": 172,
  "LIC-MS120-48-1YR": 195,
  "LIC-MS120-48LP-1YR": 260,
  "LIC-MS120-48FP-1YR": 314,
  
  # MS125 Series
  "LIC-MS125-24-1Y": 160,
  "LIC-MS125-24P-1Y": 260,
  "LIC-MS125-48-1Y": 231,
  "LIC-MS125-48LP-1Y": 302,
  "LIC-MS125-48FP-1Y": 449,
  
  # MS130 Series
  "LIC-MS130-CMPT-1Y": 68,
  "LIC-MS130-CMPTA-1Y": 135,
  "LIC-MS130-24-1Y": 173,
  "LIC-MS130-24A-1Y": 346,
  "LIC-MS130-48-1Y": 299,
  "LIC-MS130-48A-1Y": 597,
  
  # MS150 Series
  "LIC-MS150-24-1Y": 173,
  "LIC-MS150-24A-1Y": 346,
  "LIC-MS150-48-1Y": 299,
  "LIC-MS150-48A-1Y": 597,
  
  # MS210 Series
  "LIC-MS210-24-1YR": 201,
  "LIC-MS210-24P-1YR": 248,
  "LIC-MS210-48-1YR": 308,
  "LIC-MS210-48LP-1YR": 385,
  "LIC-MS210-48FP-1YR": 437,
  
  # MS220 Series
  "LIC-MS220-8-1YR": 66,
  "LIC-MS220-8P-1YR": 83,
  "LIC-MS220-24-1YR": 142,
  "LIC-MS220-24P-1YR": 189,
  "LIC-MS220-48-1YR": 248,
  "LIC-MS220-48LP-1YR": 332,
  "LIC-MS220-48FP-1YR": 390,
  
  # MS225 Series
  "LIC-MS225-24-1YR": 311,
  "LIC-MS225-24P-1YR": 360,
  "LIC-MS225-48-1YR": 428,
  "LIC-MS225-48LP-1YR": 515,
  "LIC-MS225-48FP-1YR": 578,
  
  # MS250 Series
  "LIC-MS250-24-1YR": 447,
  "LIC-MS250-24P-1YR": 484,
  "LIC-MS250-48-1YR": 621,
  "LIC-MS250-48LP-1YR": 714,
  "LIC-MS250-48FP-1YR": 775,
  
  # MS320 Series
  "LIC-MS320-24-1YR": 296,
  "LIC-MS320-24P-1YR": 326,
  "LIC-MS320-48-1YR": 437,
  "LIC-MS320-48LP-1YR": 508,
  "LIC-MS320-48FP-1YR": 555,
  
  # MS350 Series
  "LIC-MS350-24-1YR": 410,
  "LIC-MS350-24P-1YR": 472,
  "LIC-MS350-24X-1YR": 558,
  "LIC-MS350-48-1YR": 670,
  "LIC-MS350-48LP-1YR": 782,
  "LIC-MS350-48FP-1YR": 850,
  
  # MS355 Series
  "LIC-MS355-24X-1YR": 734,
  "LIC-MS355-24X2-1YR": 997,
  "LIC-MS355-48X-1YR": 1206,
  "LIC-MS355-48X2-1YR": 1325,
  
  # MS390 Series
  "LIC-MS390-24E-1Y": 695,
  "LIC-MS390-24A-1Y": 1583,
  "LIC-MS390-48E-1Y": 1247,
  "LIC-MS390-48A-1Y": 2924,
  
  # MS410 Series
  "LIC-MS410-16-1YR": 592,
  "LIC-MS410-32-1YR": 1040,
  
  # MS425 Series
  "LIC-MS425-16-1YR": 975,
  "LIC-MS425-32-1YR": 1530,
  
  # MS450 Series
  "LIC-MS450-12-1YR": 1465,
  
  # C9200L Series (Meraki-managed Catalyst)
  "LIC-C9200L-24E-1Y": 447,
  "LIC-C9200L-24A-1Y": 1617,
  "LIC-C9200L-48E-1Y": 809,
  "LIC-C9200L-48A-1Y": 3028,
  
  # C9300 Series (Meraki-managed Catalyst)
  "LIC-C9300-24E-1Y": 809,
  "LIC-C9300-24A-1Y": 1986,
  "LIC-C9300-48E-1Y": 1494,
  "LIC-C9300-48A-1Y": 3638
}
```

### 3-Year License List Prices (for purchase credit calculation)

```
CACHE_3Y = {
  # Enterprise AP (MR, CW series)
  "LIC-ENT-3YR": 452,
  
  # MV Cameras
  "LIC-MV-3YR": 746,
  
  # MT Sensors
  "LIC-MT-3Y": 295,
  
  # MG Cellular
  "LIC-MG21-ENT-3Y": 531,
  "LIC-MG41-ENT-3Y": 1065,
  "LIC-MG51-ENT-3Y": 972,
  "LIC-MG52-ENT-3Y": 1018,
  
  # Z-Series Security
  "LIC-Z1-SEC-3YR": 228,
  "LIC-Z3-SEC-3YR": 673,
  "LIC-Z3C-SEC-3YR": 995,
  "LIC-Z4-SEC-3Y": 955,
  "LIC-Z4C-SEC-3Y": 1155,
  
  # Z-Series Enterprise
  "LIC-Z1-ENT-3YR": 113,
  "LIC-Z3-ENT-3YR": 333,
  "LIC-Z3C-ENT-3YR": 498,
  "LIC-Z4-ENT-3Y": 452,
  "LIC-Z4C-ENT-3Y": 653,
  
  # MX Security Tier
  "LIC-MX50-SEC-3YR": 2250,
  "LIC-MX60-SEC-3YR": 1181,
  "LIC-MX60W-SEC-3YR": 1301,
  "LIC-MX64-SEC-3YR": 1328,
  "LIC-MX64W-SEC-3YR": 1438,
  "LIC-MX65-SEC-3YR": 1438,
  "LIC-MX65W-SEC-3YR": 1767,
  "LIC-MX67-SEC-3YR": 1546,
  "LIC-MX67C-SEC-3YR": 1877,
  "LIC-MX67W-SEC-3YR": 1656,
  "LIC-MX68-SEC-3YR": 1655,
  "LIC-MX68CW-SEC-3YR": 2320,
  "LIC-MX68W-SEC-3YR": 1989,
  "LIC-MX70-SEC-3YR": 2250,
  "LIC-MX75-SEC-3Y": 3738,
  "LIC-MX80-SEC-3YR": 4725,
  "LIC-MX84-SEC-3YR": 4417,
  "LIC-MX85-SEC-3Y": 5519,
  "LIC-MX90-SEC-3YR": 9450,
  "LIC-MX95-SEC-3Y": 11041,
  "LIC-MX100-SEC-3YR": 11041,
  "LIC-MX105-SEC-3Y": 16558,
  "LIC-MX250-SEC-3YR": 22079,
  "LIC-MX400-SEC-3YR": 35323,
  "LIC-MX450-SEC-3YR": 44156,
  "LIC-MX600-SEC-3YR": 70648,
  
  # MX Enterprise Tier
  "LIC-MX50-ENT-3YR": 1125,
  "LIC-MX60-ENT-3YR": 592,
  "LIC-MX60W-ENT-3YR": 653,
  "LIC-MX64-ENT-3YR": 664,
  "LIC-MX64W-ENT-3YR": 720,
  "LIC-MX65-ENT-3YR": 720,
  "LIC-MX65W-ENT-3YR": 884,
  "LIC-MX67-ENT-3YR": 774,
  "LIC-MX67C-ENT-3YR": 941,
  "LIC-MX67W-ENT-3YR": 830,
  "LIC-MX68-ENT-3YR": 830,
  "LIC-MX68CW-ENT-3YR": 1159,
  "LIC-MX68W-ENT-3YR": 995,
  "LIC-MX75-ENT-3Y": 1874,
  "LIC-MX80-ENT-3YR": 2363,
  "LIC-MX84-ENT-3YR": 2210,
  "LIC-MX85-ENT-3Y": 2760,
  "LIC-MX90-ENT-3YR": 4725,
  "LIC-MX95-ENT-3Y": 5520,
  "LIC-MX100-ENT-3YR": 5520,
  "LIC-MX105-ENT-3Y": 8279,
  "LIC-MX250-ENT-3YR": 11041,
  "LIC-MX400-ENT-3YR": 17663,
  "LIC-MX450-ENT-3YR": 22079,
  "LIC-MX600-ENT-3YR": 35323,
  
  # MS120 Series
  "LIC-MS120-8-3YR": 108,
  "LIC-MS120-8LP-3YR": 135,
  "LIC-MS120-8FP-3YR": 176,
  "LIC-MS120-24-3YR": 241,
  "LIC-MS120-24P-3YR": 387,
  "LIC-MS120-48-3YR": 439,
  "LIC-MS120-48LP-3YR": 585,
  "LIC-MS120-48FP-3YR": 707,
  
  # MS125 Series
  "LIC-MS125-24-3Y": 360,
  "LIC-MS125-24P-3Y": 585,
  "LIC-MS125-48-3Y": 520,
  "LIC-MS125-48LP-3Y": 680,
  "LIC-MS125-48FP-3Y": 1010,
  
  # MS130 Series
  "LIC-MS130-CMPT-3Y": 153,
  "LIC-MS130-CMPTA-3Y": 304,
  "LIC-MS130-24-3Y": 389,
  "LIC-MS130-24A-3Y": 779,
  "LIC-MS130-48-3Y": 673,
  "LIC-MS130-48A-3Y": 1343,
  
  # MS150 Series
  "LIC-MS150-24-3Y": 389,
  "LIC-MS150-24A-3Y": 779,
  "LIC-MS150-48-3Y": 673,
  "LIC-MS150-48A-3Y": 1343,
  
  # MS210 Series
  "LIC-MS210-24-3YR": 452,
  "LIC-MS210-24P-3YR": 558,
  "LIC-MS210-48-3YR": 693,
  "LIC-MS210-48LP-3YR": 866,
  "LIC-MS210-48FP-3YR": 983,
  
  # MS220 Series
  "LIC-MS220-8-3YR": 149,
  "LIC-MS220-8P-3YR": 187,
  "LIC-MS220-24-3YR": 320,
  "LIC-MS220-24P-3YR": 425,
  "LIC-MS220-48-3YR": 558,
  "LIC-MS220-48LP-3YR": 747,
  "LIC-MS220-48FP-3YR": 878,
  
  # MS225 Series
  "LIC-MS225-24-3YR": 700,
  "LIC-MS225-24P-3YR": 810,
  "LIC-MS225-48-3YR": 963,
  "LIC-MS225-48LP-3YR": 1159,
  "LIC-MS225-48FP-3YR": 1301,
  
  # MS250 Series
  "LIC-MS250-24-3YR": 1006,
  "LIC-MS250-24P-3YR": 1089,
  "LIC-MS250-48-3YR": 1397,
  "LIC-MS250-48LP-3YR": 1607,
  "LIC-MS250-48FP-3YR": 1744,
  
  # MS320 Series
  "LIC-MS320-24-3YR": 666,
  "LIC-MS320-24P-3YR": 734,
  "LIC-MS320-48-3YR": 983,
  "LIC-MS320-48LP-3YR": 1143,
  "LIC-MS320-48FP-3YR": 1249,
  
  # MS350 Series
  "LIC-MS350-24-3YR": 923,
  "LIC-MS350-24P-3YR": 1062,
  "LIC-MS350-24X-3YR": 1256,
  "LIC-MS350-48-3YR": 1508,
  "LIC-MS350-48LP-3YR": 1760,
  "LIC-MS350-48FP-3YR": 1913,
  
  # MS355 Series
  "LIC-MS355-24X-3YR": 1652,
  "LIC-MS355-24X2-3YR": 2244,
  "LIC-MS355-48X-3YR": 2714,
  "LIC-MS355-48X2-3YR": 2981,
  
  # MS390 Series
  "LIC-MS390-24E-3Y": 1564,
  "LIC-MS390-24A-3Y": 3562,
  "LIC-MS390-48E-3Y": 2806,
  "LIC-MS390-48A-3Y": 6579,
  
  # MS410 Series
  "LIC-MS410-16-3YR": 1332,
  "LIC-MS410-32-3YR": 2340,
  
  # MS425 Series
  "LIC-MS425-16-3YR": 2194,
  "LIC-MS425-32-3YR": 3443,
  
  # MS450 Series
  "LIC-MS450-12-3YR": 3296,
  
  # C9200L Series
  "LIC-C9200L-24E-3Y": 1006,
  "LIC-C9200L-24A-3Y": 3638,
  "LIC-C9200L-48E-3Y": 1820,
  "LIC-C9200L-48A-3Y": 6813,
  
  # C9300 Series
  "LIC-C9300-24E-3Y": 1820,
  "LIC-C9300-24A-3Y": 4469,
  "LIC-C9300-48E-3Y": 3362,
  "LIC-C9300-48A-3Y": 8186
}
```

***

## HARDWARE TO LICENSE MAPPING

Use this table to map hardware models to their 1-Year license SKU for weighting.

| Hardware Pattern | License Tier | 1Y License SKU |
|------------------|--------------|----------------|
| MR* (any MR AP) | Enterprise | LIC-ENT-1YR |
| CW* (any CW AP) | Enterprise | LIC-ENT-1YR |
| MV* (any camera) | - | LIC-MV-1YR |
| MT* (any sensor) | - | LIC-MT-1Y |
| MG21 | Enterprise | LIC-MG21-ENT-1Y |
| MG41 | Enterprise | LIC-MG41-ENT-1Y |
| MG51 | Enterprise | LIC-MG51-ENT-1Y |
| MG52 | Enterprise | LIC-MG52-ENT-1Y |
| Z1 | SEC or ENT | LIC-Z1-{tier}-1YR |
| Z3 | SEC or ENT | LIC-Z3-{tier}-1YR |
| Z3C | SEC or ENT | LIC-Z3C-{tier}-1YR |
| Z4 | SEC or ENT | LIC-Z4-{tier}-1Y |
| Z4C | SEC or ENT | LIC-Z4C-{tier}-1Y |
| MX{model} | SEC or ENT | LIC-MX{model}-{tier}-1YR (or -1Y for newer) |
| MS120-{port} | - | LIC-MS120-{port}-1YR |
| MS125-{port} | - | LIC-MS125-{port}-1Y |
| MS130-8/12X | - | LIC-MS130-CMPT-1Y |
| MS130-24* | - | LIC-MS130-24-1Y |
| MS130-48* | - | LIC-MS130-48-1Y |
| MS150-24* | - | LIC-MS150-24-1Y |
| MS150-48* | - | LIC-MS150-48-1Y |
| MS210-{port} | - | LIC-MS210-{port}-1YR |
| MS220-{port} | - | LIC-MS220-{port}-1YR |
| MS225-{port} | - | LIC-MS225-{port}-1YR |
| MS250-{port} | - | LIC-MS250-{port}-1YR |
| MS320-{port} | - | LIC-MS320-{port}-1YR |
| MS350-{port} | - | LIC-MS350-{port}-1YR |
| MS355-{port} | - | LIC-MS355-{port}-1YR |
| MS390-24* | E or A | LIC-MS390-24{tier}-1Y |
| MS390-48* | E or A | LIC-MS390-48{tier}-1Y |
| MS410-{port} | - | LIC-MS410-{port}-1YR |
| MS425-{port} | - | LIC-MS425-{port}-1YR |
| MS450-{port} | - | LIC-MS450-{port}-1YR |
| C9200L-24* | E or A | LIC-C9200L-24{tier}-1Y |
| C9200L-48* | E or A | LIC-C9200L-48{tier}-1Y |
| C9300-24* | E or A | LIC-C9300-24{tier}-1Y |
| C9300-48* | E or A | LIC-C9300-48{tier}-1Y |

**License Tier Detection:**
- If dashboard shows "Advanced Security" or MX has SEC licenses → use SEC tier
- If dashboard shows "Enterprise" → use ENT tier
- If MS390/C9200L/C9300 shows "Advantage" → use A tier
- If MS390/C9200L/C9300 shows "Essentials" → use E tier

***

## CALCULATION WORKFLOW

### Step 1: Gather Required Inputs

Before ANY calculation, confirm you have:
- [ ] Current expiration date
- [ ] Current device inventory with quantities
- [ ] License tier (Enterprise, Advanced Security, etc.)
- [ ] New licenses being added (SKU, quantity, term)

If ANY input is missing, STOP and ask.

### Step 2: Build Validation Table (MANDATORY)

Create a table mapping each device to its license and price. This MUST be displayed before proceeding.

```
| Device | Qty | License SKU (1Y) | List Price | Weight | Source |
|--------|-----|------------------|------------|--------|--------|
| MR44 | 10 | LIC-ENT-1YR | $201 | $2,010 | ✓ CACHE |
| MX68 | 1 | LIC-MX68-SEC-1YR | $736 | $736 | ✓ CACHE |
| MS130-24P | 4 | LIC-MS130-24-1Y | $173 | $692 | ✓ CACHE |
| **TOTAL** | **15** | | | **$3,438** | |
```

**VALIDATION RULES:**
1. Every row MUST show "✓ CACHE" in Source column
2. If ANY SKU is not in the cache → show "⚠ NOT FOUND" and STOP
3. Weight = List Price × Qty
4. Verify TOTAL weight = sum of all individual weights (checksum)

**If a SKU is NOT FOUND:**
```
⚠ STOP: Cannot find 1-year list price for [SKU].

Please provide the 1-Year List Price (MSRP) for this license, or I can exclude this device from the calculation.
```

### Step 3: Calculate Current Daily Burn Rate

```
Current Annual Value = Sum of all weights from validation table
Current Daily Burn = Current Annual Value / 365
```

Show the math:
```
Current Annual Value: $3,438
Current Daily Burn: $3,438 / 365 = $9.42/day
```

### Step 4: Calculate Remaining Credit

```
Days Remaining = Current Expiration Date - Today
Remaining Credit = Current Daily Burn × Days Remaining
```

Show the math:
```
Today: January 22, 2026
Current Expiration: March 15, 2026
Days Remaining: 52 days

Remaining Credit: $9.42 × 52 = $489.84
```

### Step 5: Calculate New Credit from Purchase

Look up the purchased license in the 3Y cache (or 1Y if 1-year term).

```
New Credit = License List Price × Quantity
```

**For 3-year purchases:** Use CACHE_3Y prices directly (they already represent 3 years of value)

Example:
```
Adding: 5 × LIC-ENT-3YR
List Price: $452 (from CACHE_3Y)
New Credit: $452 × 5 = $2,260
```

### Step 6: Calculate New Daily Burn Rate

Add the new devices to the weighting table using their 1-YEAR list prices.

```
| Device | Qty | License SKU (1Y) | List Price | Weight |
|--------|-----|------------------|------------|--------|
| MR44 | 10 | LIC-ENT-1YR | $201 | $2,010 |
| MX68 | 1 | LIC-MX68-SEC-1YR | $736 | $736 |
| MS130-24P | 4 | LIC-MS130-24-1Y | $173 | $692 |
| [NEW] MR44 | 5 | LIC-ENT-1YR | $201 | $1,005 |
| **TOTAL** | **20** | | | **$4,443** |

New Daily Burn: $4,443 / 365 = $12.17/day
```

### Step 7: Calculate New Expiration Date

```
Total Credit = Remaining Credit + New Credit
Days from Today = Total Credit / New Daily Burn
New Expiration = Today + Days from Today
```

Show the math:
```
Total Credit: $489.84 + $2,260 = $2,749.84
Days from Today: $2,749.84 / $12.17 = 226 days
New Expiration: January 22, 2026 + 226 days = September 5, 2026
```

***

## OUTPUT FORMAT

Present the full calculation with this structure:

```
## Co-Term Calculation Results

**Current Status:**
• Organization Expiration: [Current Date]
• Days Remaining: [X] days
• Total Devices: [X]
• License Tier: [Tier]

**Adding:**
• [Qty] × [License SKU] ([Term])

***

### SKU Weighting Table (Current Inventory)

| Device | Qty | License SKU (1Y) | List Price | Weight | Source |
|--------|-----|------------------|------------|--------|--------|
| ... | ... | ... | ... | ... | ✓ CACHE |
| **TOTAL** | **X** | | | **$X,XXX** | ✓ Verified |

***

### Calculation Breakdown

**Step 1: Current Daily Burn**
$[annual] / 365 = **$[daily]/day**

**Step 2: Remaining Credit**
$[daily] × [days remaining] = **$[remaining]**

**Step 3: New Credit (from purchase)**
[Qty] × $[list price] = **$[new credit]**

**Step 4: New Weighting (with additions)**

| Device | Qty | License SKU (1Y) | List Price | Weight |
|--------|-----|------------------|------------|--------|
| ... | ... | ... | ... | ... |
| [NEW] ... | ... | ... | ... | ... |
| **TOTAL** | **X** | | | **$X,XXX** |

New Daily Burn: $[new annual] / 365 = **$[new daily]/day**

**Step 5: New Expiration**
Total Credit: $[remaining] + $[new] = **$[total]**
Days from Today: $[total] / $[new daily] = **[days] days**

***

## **New Co-Term Expiration: [DATE]**

This extends your organization approximately [X months/years] beyond the current expiration.

***

*Note: This is an estimate using the weighted dollar-value method. Meraki's actual calculation may vary slightly.*
```

***

## GUARDRAILS

### Same Tier Requirement
Co-term only works when all devices share the same license tier. If mixing is detected:

```
⚠ TIER MISMATCH DETECTED

Your inventory appears to have mixed license tiers:
- MX68 → Advanced Security
- MR44 → Enterprise

Co-term requires all devices on the same tier. Options:
1. Upgrade MR APs to Advanced Security (LIC-MR-ADV) for true co-term
2. Calculate separate expirations for each tier

Which would you like to do?
```

### No Estimation Policy
NEVER estimate or guess prices. If a SKU is not in CACHE_1Y or CACHE_3Y:
1. State exactly which SKU is missing
2. Ask user for the 1-Year List Price (MSRP)
3. Do NOT proceed until price is confirmed

### Checksum Verification
Before final calculation, verify:
1. Sum of individual weights = Total weight shown
2. Days calculation is reasonable (positive, not exceeding 10 years)
3. New expiration is after current expiration (unless very small purchase)

***

## EXAMPLE CONVERSATION

**User:** I need to calculate co-term. Current expiration March 15, 2026. We have 10 MR44, 4 MS130-24P, and 1 MX68 on Advanced Security. Adding 5 more MR44 with 3-year licenses.

**Claude:**

## Co-Term Calculation Results

**Current Status:**
• Organization Expiration: March 15, 2026
• Days Remaining: 52 days
• Total Devices: 15
• License Tier: Advanced Security

**Adding:**
• 5 × LIC-ENT-3YR (3-year)

***

### SKU Weighting Table (Current Inventory)

| Device | Qty | License SKU (1Y) | List Price | Weight | Source |
|--------|-----|------------------|------------|--------|--------|
| MR44 | 10 | LIC-ENT-1YR | $201 | $2,010 | ✓ CACHE |
| MS130-24P | 4 | LIC-MS130-24-1Y | $173 | $692 | ✓ CACHE |
| MX68 | 1 | LIC-MX68-SEC-1YR | $736 | $736 | ✓ CACHE |
| **TOTAL** | **15** | | | **$3,438** | ✓ Verified |

***

### Calculation Breakdown

**Step 1: Current Daily Burn**
$3,438 / 365 = **$9.42/day**

**Step 2: Remaining Credit**
$9.42 × 52 days = **$489.84**

**Step 3: New Credit (from purchase)**
LIC-ENT-3YR list price: $452 (from CACHE_3Y)
5 × $452 = **$2,260**

**Step 4: New Weighting (with additions)**

| Device | Qty | License SKU (1Y) | List Price | Weight |
|--------|-----|------------------|------------|--------|
| MR44 | 10 | LIC-ENT-1YR | $201 | $2,010 |
| MS130-24P | 4 | LIC-MS130-24-1Y | $173 | $692 |
| MX68 | 1 | LIC-MX68-SEC-1YR | $736 | $736 |
| [NEW] MR44 | 5 | LIC-ENT-1YR | $201 | $1,005 |
| **TOTAL** | **20** | | | **$4,443** |

New Daily Burn: $4,443 / 365 = **$12.17/day**

**Step 5: New Expiration**
Total Credit: $489.84 + $2,260 = **$2,749.84**
Days from Today: $2,749.84 / $12.17 = **226 days**

***

## **New Co-Term Expiration: September 5, 2026**

This extends your organization approximately 6 months beyond the current March 15, 2026 expiration.

***

*Note: This is an estimate using the weighted dollar-value method. Meraki's actual calculation may vary slightly.*

***

Want me to generate a quote for the 5 MR44 licenses?

***

## PRICE CACHE METADATA

```
Source: Meraki Price Book 01-14-2026
Last Updated: 2026-01-22
Total 1Y SKUs: 140
Total 3Y SKUs: 138
```
