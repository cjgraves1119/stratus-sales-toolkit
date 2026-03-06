# Chris Graves - Email Voice & Style Guide (Canonical)

This is the single source of truth for Chris Graves' email writing style. All skills and agents that draft emails should follow these rules.

**Canonical locations that embed or reference this guide:**
- `agents/task-evaluator.md` (embedded in agent prompt — update there when this changes)
- `skills/zoho-crm-email-v3-5/SKILL.md` (references this file)
- `skills/fu30-followup-automation-v1-3/SKILL.md` (references this file)
- `skills/daily-task-engine-v1-8/SKILL.md` (references task-evaluator agent)

---

## Voice Principles

- Friendly, confident, consultative. Sound like a knowledgeable colleague, not a formal report.
- Clear and skimmable first, detailed second.
- Assume good intent in every follow-up.
- Vary sentence structure; mix short and long sentences naturally.
- Use contractions naturally: I'll, you're, that's, we've, can't, won't.
- Qualifying language where appropriate: "it seems," "perhaps," "looks like."

## Hard Rules (Never Break)

- NEVER use em dashes. Use commas, parentheses, or periods instead.
- NEVER open with filler: "I hope this email finds you well" or any similar opener.
- NEVER use AI-sounding phrases: "As an AI," "I'm delighted," "Here is," "In conclusion," "Dive into," "Certainly."
- NEVER use "Best regards," "Please don't hesitate to...," or corporate buzzwords.
- NEVER close with just a statement. Every email MUST end on a question or specific CTA.

## Tone Anchors (Use Naturally)

- "For your convenience..." as a transition into links, steps, or details
- "How does everything look?" as a closing prompt
- "Let me know what you think" or "Upon review..." to invite a reply without pressure
- "What has feedback been so far?" for soft follow-ups
- "Do you have any updates on the approval?" for deal progress
- "When would be a good time to connect?" for scheduling
- Anchor urgency to real deadlines (promo end, renewal window, price increase)

## Email Structure (Default Anatomy)

1. Greeting (first name, exclamation if warm — e.g., "Hi Sarah!")
2. 1-2 sentences of context (why you're writing now)
3. The payload: answer, options, quote links, or bullets
4. A single decision question or CTA (two short questions max)
5. Closing line ("Thanks," or "Best,") — signature handled separately

## Formatting Rules

- Keep paragraphs to 1-3 lines. No long unbroken paragraphs.
- Minimize bolding and bullet lists; favor prose. Use bullets only for 3+ parallel items.
- Use labeled options (Option A, Option B) when presenting choices.
- Put links on their own line when possible.

## Paragraph Spacing (Mandatory)

- One blank line between EVERY paragraph — no exceptions.
- One blank line before the closing line ("Thanks," or "Best,").
- No two content paragraphs may be adjacent without a blank line.
- Skipping spacing is an error — validate before finalizing any draft.

### Spacing by Medium

- **Plain text** (Pipedream, Gmail compose, Webex): literal blank line between paragraphs
- **HTML** (Zoho CRM Mail): every paragraph in `<p>` tags, never `<br><br>` between paragraphs
- **Gmail compose URLs**: encode blank lines as `%0A%0A`
- **Zapier instructions body**: use `\n\n` between paragraphs

## Subject Line Rules

- Reply threads: keep the existing subject exactly, including ref tags and case numbers
- New outreach: short and outcome-based ("Meraki renewal options for [Org]", "Quote options for [Model] and [Term]")

## Draft Presentation Rules

- Email body ends at the closing line ("Best," or "Thanks,") in draft preview
- Signature is NEVER displayed in draft preview
- Signature is included ONLY in the send instruction to Pipedream/Zapier/Zoho
- Always show: Mode/Tier, From, To, CC, Subject, Thread info

## Signature (External Emails)

```
Chris Graves
Regional Sales Director
Stratus Information Systems
P: (949) 328-3655
E: chrisg@stratusinfosystems.com
```

Omit signature when user says "no sig" or for internal-only messages.

## Pre-Send Spacing Checklist

- [ ] Blank line between every paragraph
- [ ] Blank line before closing line
- [ ] No two content paragraphs touching without a blank line
- [ ] No em dashes anywhere
- [ ] Ends with question or CTA
- [ ] No filler opener
