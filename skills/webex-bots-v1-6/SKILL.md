---
name: webex-bots-v1-6
description: "send messages to commerce bot (lead times) and stratus chatbot (pricing quotes) in stratus bot group via webex. includes batch sku queries, auto-polling, cisco rep zoho ids, direct web link fallback, chris voice replication, and cowork computer-use fallback to webex web client when mcp errors occur. requires both text and markdown fields. triggers: lead time, pricing quote, webex message, ping cisco rep, message bot, chat bot, commerce bot."
---

# Webex Bots Skill v1.6

Send messages to Cisco/Meraki bots in the Stratus Bot Group Webex room for lead times and pricing quotes. Also includes Cisco rep Zoho IDs for direct Webex messaging. All drafted messages use Chris's authentic voice.

## What's New in v1.6

**COWORK COMPUTER-USE FALLBACK** - When operating in Cowork mode and MCP/Pipedream Webex messaging fails (errors finding a person, bot, or room), automatically fall back to using computer use (browser automation) to navigate to the Webex web client and send the message directly. This ensures Webex messages always get through even when API integrations have issues.

### Cowork Webex Computer-Use Fallback Workflow

When in Cowork mode and Webex MCP messaging encounters errors:

```
1. Detect error (person not found, bot not found, room error, API timeout, etc.)
2. DO NOT retry MCP more than once
3. Fall back to computer use:
   a. Navigate to https://web.webex.com in browser
   b. Wait for Webex to load (may already be logged in)
   c. Search for the target room or person in the Webex search bar
   d. For bot messages: Navigate to Stratus Bot Group room
   e. For direct messages: Search for the Cisco rep by name or email
   f. Type and send the message using browser automation
4. Confirm message was sent by verifying the message appears in the chat
```

### When to Trigger Computer-Use Fallback

- Pipedream Webex create-message returns an error
- Person ID lookup fails ("person not found")
- Bot mention fails or message not delivered
- Room ID returns "not found" or "forbidden"
- Any Webex API error after one retry attempt
- User explicitly asks to "just send it through webex directly"

### Computer-Use Webex URLs

- **Stratus Bot Group**: https://web.webex.com/spaces/aHR0cHM6Ly9jb252LWEud2J4Mi5jb20vY29udmVyc2F0aW9uL2FwaS92MS9jb252ZXJzYXRpb25zL2U5NTFkOTEwLWIxMGEtMTFmMC05ODliLWExZGEzMTFmZDQzNA==
- **Direct messages**: Navigate to https://web.webex.com and search for the person by name

### Important Notes for Computer-Use Fallback

- This fallback is ONLY for Cowork mode where computer use (browser automation) is available
- In Chat mode (no browser), the existing web link fallback still applies (provide link for user to send manually)
- Always draft and confirm the message with Chris before sending, even via computer use
- The browser may need a moment to load Webex, use appropriate waits

## What's New in v1.5

**CHRIS VOICE REPLICATION** - All Webex messages drafted by Claude now match Chris's authentic communication style. See Voice Guide section below. Full detailed reference available at `references/chris-voice-guide.md`.

## What's New in v1.4

**WEB LINK FALLBACK** - When MCP integration fails, provides direct link to Stratus Bot Group with pre-formatted lead time request message for instant manual submission.

## Room Configuration

**Room Name**: Stratus Bot Group  
**Room ID**: Y2lzY29zcGFyazovL3VzL1JPT00vNjBiZWVmMDAtZDYzMi0xMWYwLThmYmMtZWRhMTE1OTNjY2Vh

Always use the Room ID for faster message delivery.

## Web Link Fallback (NEW in v1.4)

When MCP/Pipedream integration fails or is unavailable, provide a direct link to the Stratus Bot Group web interface with pre-formatted message text.

**Stratus Bot Group Web Link:**
https://web.webex.com/spaces/aHR0cHM6Ly9jb252LWEud2J4Mi5jb20vY29udmVyc2F0aW9uL2FwaS92MS9jb252ZXJzYXRpb25zL2U5NTFkOTEwLWIxMGEtMTFmMC05ODliLWExZGEzMTFmZDQzNA==

### Usage Instructions

When automated messaging fails, provide this to the user:

```
I'm unable to send the message through the automation, but you can check the lead time directly:

Open Stratus Bot Group: https://web.webex.com/spaces/aHR0cHM6Ly9jb252LWEud2J4Mi5jb20vY29udmVyc2F0aW9uL2FwaS92MS9jb252ZXJzYXRpb25zL2U5NTFkOTEwLWIxMGEtMTFmMC05ODliLWExZGEzMTFmZDQzNA==

Then send this message:
@Commerce BOT lead time of [SKU1,SKU2,SKU3]
```

**Example for batch query:**
```
@Commerce BOT lead time of MS150-24P-4X,MR44-HW,MX68-HW
```

**Example for single SKU:**
```
@Commerce BOT lead time of MS150-24P-4X
```

### When to Use Web Link Fallback

- MCP/Pipedream returns errors or timeouts
- User prefers manual verification
- Testing bot availability
- Quick ad-hoc queries during troubleshooting

## Bots

### Commerce BOT (Lead Times)

**• Person ID**: Y2lzY29zcGFyazovL3VzL1BFT1BMRS9hY2YwMTUxOC02MDFmLTRlY2YtOTYzYy1lMWZmZjliYzFkNGY
**• Email**: ccwbot@webex.bot
**• Purpose**: Check Cisco/Meraki hardware lead times
**• SKU Format**: Include -HW suffix for hardware (MX68-HW, MX85-HW, MR36-HW, MS130-24P-HW)

#### Single SKU Query Format
```
lead time of [SKU]
```

#### Batch SKU Query Format (PREFERRED)
```
lead time of [SKU1],[SKU2],[SKU3]
```

**Example Batch Query:**
```
lead time of MR44-HW,MS130-12X-HW,MS150-48LP-4G
```

**Batch Query Rules:**
- Comma-separated, NO spaces after commas
- Hardware SKUs only (not license SKUs)
- Recommended max: 10 SKUs per query (untested above this)
- If a SKU isn't recognized, the bot will return results for valid SKUs and skip unrecognized ones

### Stratus Chatbot (Pricing Quotes)

**• Person ID**: Y2lzY29zcGFyazovL3VzL1BFT1BMRS9jZmVhMjRmYi0zYzVhLTQwMGYtODA0Yy1kNWJmZTFhY2M2Yzg
**• Email**: stratus.chatbot@webex.bot
**• Purpose**: Get pre-approved pricing quotes with line item breakdown
**• Query Format**: quote [products] with [X] year license, list individual prices for each SKU

**Example Queries:**
- quote MR36 with 3 year license, list individual prices for each SKU
- quote 2x MR44, 1x MS130-24P with 5 year Enterprise license, list individual prices for each SKU
- quote MX85 with 1 year license, list individual prices for each SKU

**Response Includes:**
- Individual SKU prices (hardware + licenses)
- Total price
- Direct order URL (stratusinfosystems.com/order/...)

## Cisco Rep Direct Messaging (55 Active Reps)

Use these emails to send direct Webex messages to Cisco reps. Zoho IDs included for deal assignment reference.

### Hot Cache with Zoho IDs

```json
{
  "awittema@cisco.com": {"name": "Aleksandr Wittemann", "zoho_id": "2570562000349281304"},
  "rsosnak@cisco.com": {"name": "Ryan Sosnak", "zoho_id": "2570562000369233873"},
  "domholme@cisco.com": {"name": "Domonique Holmes", "zoho_id": "2570562000335756226"},
  "kevausti@cisco.com": {"name": "Kevin Austin", "zoho_id": "2570562000026885406"},
  "jkos@cisco.com": {"name": "Joe Kos", "zoho_id": "2570562000065903216"},
  "ejimene2@cisco.com": {"name": "Edgar Jimenez", "zoho_id": "2570562000081042054"},
  "medmond@cisco.com": {"name": "Monique Edmond", "zoho_id": "2570562000082642242"},
  "alexisma@cisco.com": {"name": "Alex Martinez", "zoho_id": "2570562000087456908"},
  "tsilvas@cisco.com": {"name": "Tyler Silvas", "zoho_id": "2570562000090688731"},
  "rfitzgib@cisco.com": {"name": "Ryan Fitzgibbons", "zoho_id": "2570562000095985250"},
  "kedick@cisco.com": {"name": "Kenzie Dick", "zoho_id": "2570562000121830395"},
  "matgille@cisco.com": {"name": "Matt Gillespie", "zoho_id": "2570562000126163158"},
  "chgard@cisco.com": {"name": "Chris Gard", "zoho_id": "2570562000135812196"},
  "amycalle@cisco.com": {"name": "Amy Allen", "zoho_id": "2570562000145305112"},
  "evwatkin@cisco.com": {"name": "Evan Watkins", "zoho_id": "2570562000146084558"},
  "darrjoh2@cisco.com": {"name": "Darrell Johnson", "zoho_id": "2570562000146113206"},
  "jdisla@cisco.com": {"name": "Josh Disla", "zoho_id": "2570562000169902001"},
  "ccarafio@cisco.com": {"name": "Camille Carafiol", "zoho_id": "2570562000180614089"},
  "fanayadi@cisco.com": {"name": "Francisco Anaya-Diaz", "zoho_id": "2570562000181578324"},
  "maufmann@cisco.com": {"name": "Michael Aufmann", "zoho_id": "2570562000196914620"},
  "jikillen@cisco.com": {"name": "Jimmy Killen", "zoho_id": "2570562000196914674"},
  "jrmuller@cisco.com": {"name": "Jordan Muller", "zoho_id": "2570562000200008387"},
  "lcleys@cisco.com": {"name": "Lindsey Cley", "zoho_id": "2570562000243941625"},
  "nclayton@cisco.com": {"name": "Nathan Clayton", "zoho_id": "2570562000268401261"},
  "jberline@cisco.com": {"name": "Joey Berliner", "zoho_id": "2570562000275341406"},
  "mclaymil@cisco.com": {"name": "Martez Clay-Miller", "zoho_id": "2570562000286378992"},
  "johnm4@cisco.com": {"name": "John Martin", "zoho_id": "2570562000308746249"},
  "alexbla@cisco.com": {"name": "Alex Blanco", "zoho_id": "2570562000318456256"},
  "abrmarti@cisco.com": {"name": "Abraham Martinez", "zoho_id": "2570562000330061316"},
  "mocleary@cisco.com": {"name": "Morgan Cleary", "zoho_id": "2570562000334408515"},
  "ezertuch@cisco.com": {"name": "Eddy Zertuche", "zoho_id": "2570562000027514084"},
  "dtrombet@cisco.com": {"name": "Dylan Trombetta", "zoho_id": "2570562000349096576"},
  "josturdi@cisco.com": {"name": "Joel Sturdivant", "zoho_id": "2570562000349236055"},
  "bdoster@cisco.com": {"name": "Bill Doster", "zoho_id": "2570562000349256051"},
  "jerush@cisco.com": {"name": "Jeff Rush", "zoho_id": "2570562000349256052"},
  "abliss@cisco.com": {"name": "Allie Bliss", "zoho_id": "2570562000349279090"},
  "chrevang@cisco.com": {"name": "Chris Evangelista", "zoho_id": "2570562000349279091"},
  "mibalder@cisco.com": {"name": "Michael Balderrama", "zoho_id": "2570562000349279092"},
  "ashilen@cisco.com": {"name": "Ashley Shilen", "zoho_id": "2570562000349279093"},
  "lkirtser@cisco.com": {"name": "Lauren Kirtser", "zoho_id": "2570562000349279094"},
  "tibunten@cisco.com": {"name": "Tim Bunten", "zoho_id": "2570562000349279095"},
  "zehasan@cisco.com": {"name": "Zeina Hasan", "zoho_id": "2570562000349279096"},
  "jaliving@cisco.com": {"name": "Jake Livingston", "zoho_id": "2570562000349279098"},
  "darucker@cisco.com": {"name": "Dave Rucker", "zoho_id": "2570562000349279100"},
  "frataylo@cisco.com": {"name": "Frank Taylor", "zoho_id": "2570562000349279101"},
  "katbende@cisco.com": {"name": "Kate Morgan", "zoho_id": "2570562000349279102"},
  "mklimczy@cisco.com": {"name": "Matt Klimczyk", "zoho_id": "2570562000349279103"},
  "dastraub@cisco.com": {"name": "Darin Straub", "zoho_id": "2570562000349279104"},
  "kijennin@cisco.com": {"name": "Kimberly Jennings", "zoho_id": "2570562000349279105"},
  "cscott3@cisco.com": {"name": "Chris Scott", "zoho_id": "2570562000349279106"},
  "phmeyers@cisco.com": {"name": "Phil Meyers", "zoho_id": "2570562000349279107"},
  "joshjo@cisco.com": {"name": "Josh Jones", "zoho_id": "2570562000349279212"},
  "klindblo@cisco.com": {"name": "Kyle Lindblom", "zoho_id": "2570562000349279215"},
  "kfarwick@cisco.com": {"name": "Katie Alis", "zoho_id": "2570562000349281305"},
  "tiluongo@cisco.com": {"name": "Tim Luongo", "zoho_id": "2570562000349281306"},
  "jvandery@cisco.com": {"name": "Jake Vanderydt", "zoho_id": "2570562000349281307"}
}
```

### Direct Rep Messaging via Pipedream

To send a direct Webex message to a Cisco rep (not in Stratus Bot Group):

```
Send a direct message via Webex to: [rep_email@cisco.com]

text: [Your message here]
```

Use the rep's @cisco.com email address from the cache above.

## Critical: Message Format

**Both `text` AND `markdown` fields are REQUIRED.** The Pipedream integration will render HTML literally if only markdown is provided.

### Pipedream Instructions for Commerce BOT (Batch Lead Time)

```
Send a message to Webex room ID: Y2lzY29zcGFyazovL3VzL1JPT00vNjBiZWVmMDAtZDYzMi0xMWYwLThmYmMtZWRhMTE1OTNjY2Vh

Include BOTH fields:
- text: lead time of MR44-HW,MS130-12X-HW,MS150-48LP-4G
- markdown: <spark-mention data-object-type="person" data-object-id="Y2lzY29zcGFyazovL3VzL1BFT1BMRS9hY2YwMTUxOC02MDFmLTRlY2YtOTYzYy1lMWZmZjliYzFkNGY"></spark-mention> lead time of MR44-HW,MS130-12X-HW,MS150-48LP-4G

Use roomId parameter for faster delivery.
```

### Pipedream Instructions for Stratus Chatbot (Pricing)

```
Send a message to Webex room ID: Y2lzY29zcGFyazovL3VzL1JPT00vNjBiZWVmMDAtZDYzMi0xMWYwLThmYmMtZWRhMTE1OTNjY2Vh

Include BOTH fields:
- text: quote MR36 with 3 year license, list individual prices for each SKU
- markdown: <spark-mention data-object-type="person" data-object-id="Y2lzY29zcGFyazovL3VzL1BFT1BMRS9jZmVhMjRmYi0zYzVhLTQwMGYtODA0Yy1kNWJmZTFhY2M2Yzg"></spark-mention> quote MR36 with 3 year license, list individual prices for each SKU

Use roomId parameter for faster delivery.
```

## Auto-Polling for Responses

After sending a message to either bot, automatically poll for the response.

### Polling Workflow

1. **Send the message** using the format above
2. **Wait 3-5 seconds** for bot processing
3. **List messages** from Stratus Bot Group to retrieve the response
4. **Parse the response** and present to user

### Polling Instructions for Pipedream

```
List messages from Webex room ID: Y2lzY29zcGFyazovL3VzL1JPT00vNjBiZWVmMDAtZDYzMi0xMWYwLThmYmMtZWRhMTE1OTNjY2Vh

Retrieve the most recent messages (max 10) to find the bot's response.
```

### Identifying Bot Responses

**• Commerce BOT responses** come from: ccwbot@webex.bot
**• Stratus Chatbot responses** come from: stratus.chatbot@webex.bot

Look for the most recent message from the relevant bot email after your query.

## Error Handling & Contingencies

### SKU Not Recognized in Batch Query

If Commerce Bot returns results for some SKUs but not others:

1. Note which SKUs returned results
2. For missing SKUs, try alternate formats:
   - With/without -HW suffix
   - Check for typos
   - Verify SKU exists in product catalog
3. If still not found, report that SKU isn't indexed in Commerce Bot

### Batch Query Returns No Results

If the entire batch query fails:

1. Fall back to individual SKU queries (one message per SKU)
2. Report which SKUs succeeded/failed
3. Note: This may indicate a bot service issue

### Response Not Found After Polling

If no bot response appears after 10 seconds:

1. Wait additional 5 seconds and poll again
2. If still no response, check if message was delivered
3. Retry the query once
4. If still failing, report potential bot service issue

## Common Mistakes to Avoid

- **Missing text field**: Always include BOTH text and markdown
- **Missing -HW suffix**: Hardware SKUs need -HW (MX68-HW not MX68)
- **Spaces in batch query**: No spaces after commas (MR44-HW,MS130-12X-HW not MR44-HW, MS130-12X-HW)
- **Using room name instead of ID**: Use roomId for reliability
- **Not polling for response**: Always follow up with list-messages to get the bot's answer
- **Text content in spark-mention tag**: Keep the spark-mention tag empty (no text between opening and closing tags)
- **Including license SKUs in lead time queries**: Only hardware SKUs work for lead times

## Chris Voice Guide (Apply to ALL Drafted Webex Messages)

**NOTE:** This section applies when drafting messages TO people (Cisco reps, partners, team, customers). Bot commands (lead times, pricing queries) are mechanical and do NOT get voice styling.

For the full detailed reference with conversation flow examples, see `references/chris-voice-guide.md`.

### Core Tone Rules

- Casual yet professional. Write like talking to a colleague, not a formal email.
- Short and punchy. 1-2 lines per message preferred. Multiple short messages > one long paragraph.
- Genuine warmth with light humor. Use "lol" to soften, not to be silly.
- Transparent. Admit when you don't know something.
- NEVER use formal language like "I am writing to inform you...", "Best regards", corporate buzzwords, or excessive punctuation (!!!, ???).
- NEVER use emojis in every message. Keep them occasional and purposeful.

### Greetings (Match Relationship)

| Context | Examples |
|---------|----------|
| Morning (team) | "Morning Team!", "Morning boys" |
| Morning (partner) | "Good morning!", "Happy Monday [Name] 🙂" |
| Casual hello | "Hey [Name]!", "Hey Hey!", "Yo yo!" |
| Close contact | "Yo dude" |

### Key Phrases (Use Naturally, Don't Force)

| Situation | Go-to phrases |
|-----------|---------------|
| Acknowledging | "Roger that", "Got it thanks!", "Sounds good!", "Gotcha!" |
| Taking action | "I'm on it!", "Can do🫡", "Let me [check/look into] now", "On it! Thanks for looping me in 🙂" |
| Offering help | "Happy to help out", "I can definitely get something whipped up ASAP" |
| Flagging | "FYI -", "Just a heads up", "Figured I'd flag it in case..." |
| Seeking clarity | "Just to confirm...", "Just making sure we are all on the same page", "Happen to have...?" |
| Setting expectations | "Before I [action], can you confirm...?", "Want to make sure you get credit for this one 🙂" |
| Light frustration | "Lame lol", "sheesh", "Womp Womp" |
| Appreciation | "Thanks for looping me in 🙂", "I appreciate the support lol", "lol appreciate you" |
| Apologizing | "Sorry about missing that!", keep it genuine and brief, don't over-apologize |

### Emoji Usage

Occasional, not constant. Common picks: 🙂 (friendly/professional), 😅 (self-deprecation), 🫡 (acknowledgment), 😉 (pro-tips), 😂 (genuinely funny), ☀️ (mornings).

Best spots: end of friendly requests, lightening tense moments, showing appreciation, acknowledging tasks.

### Audience Adaptation

| Audience | Style |
|----------|-------|
| Cisco reps (AEs/SEs) | Technical depth, collaborative, reference Cisco systems (CCW, DIDs) |
| Distributors (TD Synnex) | Professional but friendly, PO/order focused, proactive follow-ups |
| Internal team (Wolf Pack) | Most casual, humor welcome, celebrate wins ("Let's goooo babeeee!") |
| Managers (Tim) | Casual but respectful, thorough context when escalating |
| New contacts | Slightly more professional initially, warm up quickly |

### Message Flow Pattern

For anything beyond a quick one-liner, follow this rhythm:

1. **Hook/greeting** - Short opener that sets the tone
2. **Context** - What this is about (1-2 sentences)
3. **The ask or info** - Be specific (PO numbers, SKUs, etc.)
4. **Close** - Action item or friendly sign-off (no "Best regards" ever)

For longer technical topics, break into multiple messages rather than one wall of text. Use numbered lists only when explaining technical steps or multiple items.

### Abbreviations & Casual Language

Use naturally: "nvm", "fyi", "lol", "lmao", "bruh" (team only), "omg", "my dude" (team only), "heck of a [noun]", "end of rant lol", "lol yo"

### Apology Pattern (When Needed)

1. Acknowledge the specific issue
2. Explain briefly without excusing ("Think you caught me at a bad time")
3. Show you value the relationship
4. Pivot to next steps immediately

## Triggers

Use this skill when user asks for:

- Lead time on any Cisco/Meraki SKU(s)
- Pricing quote with Stratus pre-approved rates
- Quick quote for Zoho CRM integration
- Commerce bot or CCW bot queries
- Direct Webex message to a Cisco rep

## Changelog

### v1.6 (Current)

**- NEW**: Cowork computer-use fallback for Webex messaging when MCP/Pipedream fails
**- NEW**: Automatic browser navigation to Webex web client (web.webex.com)
**- NEW**: Handles person not found, bot errors, room errors by switching to browser automation
**- SCOPE**: Computer-use fallback only available in Cowork mode (Chat mode retains web link fallback)
**- INCLUDES**: All v1.5 features (Chris Voice Guide, web link fallback, batch queries, rep cache)

### v1.5

**• NEW**: Chris Voice Guide integrated for all drafted Webex messages
**• NEW**: Full voice reference at `references/chris-voice-guide.md`
**• INCLUDES**: Greetings, key phrases, emoji rules, audience adaptation, message flow patterns
**• SCOPE**: Voice applies to human messages only, not bot commands

### v1.4

**• NEW**: Web link fallback with direct Stratus Bot Group URL
**• NEW**: Pre-formatted message instructions when MCP integration fails
**• IMPROVED**: Error recovery workflow with manual verification option

### v1.3

**• NEW**: Added Cisco rep hot cache with 55 active reps and Zoho IDs
**• NEW**: Direct rep messaging instructions via Pipedream
**• Synced with cisco-rep-locator-v1-1 for consistent data

### v1.2

**• NEW**: Batch lead time queries - send multiple SKUs comma-separated in single message
**• NEW**: Error handling for partial batch results
**• NEW**: Contingency for batch query failures (fall back to individual queries)
**• OPTIMIZED**: Reduced API calls from N to 1 for N-SKU lead time checks

### v1.1

**• Fixed**: Emphasized that BOTH text AND markdown fields are required
**• Added**: Auto-polling workflow to retrieve bot responses
**• Added**: Complete workflow examples for lead time and pricing

### v1.0

**• Initial release with bot configuration and message format
