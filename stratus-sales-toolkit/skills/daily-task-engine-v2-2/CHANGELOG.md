# Daily Task Engine Changelog

### v2.2

- **ORCHESTRATOR-LEVEL DEAL PRE-LOAD (Phase 1d)**: Deal data fetched once at orchestrator level using batched `ZohoCRM_Get_Records` calls (up to 10 IDs per call). Results written to `/tmp/deal_context.json` and injected into sub-agent prompts. Eliminates redundant per-agent deal lookups that caused 28/38 failures in Haiku testing.
- **ORCHESTRATOR-LEVEL GMAIL PRE-LOAD (Phase 2a)**: Gmail context fetched in batches of 5 contacts using OR-combined queries (`from:email1 OR to:email1 OR from:email2...`). Results written to `/tmp/gmail_context.json`. Eliminates per-agent Gmail searches that consumed 2 API calls each.
- **BATCHED SUB-AGENT LAUNCHES (Phase 2b)**: Sub-agents launched in groups of ~12 (2-3 batches) instead of all at once. Reduces parallel execution pressure and improves reliability across all model tiers.
- **LEAN SUB-AGENT PROMPTS**: Voice/style guide removed from sub-agent prompts entirely. Sub-agents focus on evaluation logic only. Saves ~2K tokens per agent (~60-70K total for 30 tasks).
- **PHASE 3 AS EXCLUSIVE VALIDATION POINT**: All voice/style validation consolidated in Phase 3 pre-presentation gate. Sub-agents no longer responsible for style compliance. Five-check gate (paragraph spacing, filler openers, AI phrases, em dashes, closing CTA) runs on all drafts before dashboard generation.
- **HYBRID EMAIL TEMPLATES**: Structural templates for DR01 and FU30 task types with personalized sentence slots. Templates provide opening/body/closing structure while allowing context-specific personalization. Reduces draft variance and token usage.
- **RESULT AGGREGATION WITH ERROR HANDLING (Phase 2c)**: Dedicated aggregation step collects sub-agent JSON from `/tmp/task_eval_*.json` files. Catches JSONDecodeError and missing files, inserts NEEDS_REVIEW placeholders instead of failing the entire run.
- **TWO NEW NEVER RULES**: "NEVER embed the full voice/style guide in sub-agent prompts" and "NEVER have sub-agents fetch deal records or search Gmail independently."
- **DYNAMIC COMPANION SKILL VERSIONING**: Companion skills resolved at runtime via folder prefix globbing (`zoho-crm-v*/SKILL.md`), never hardcoded version numbers.
- **ESTIMATED SAVINGS**: ~120-150K tokens per run for 30 tasks. Enables reliable Haiku execution (~$2.40/run vs ~$7-9/run on Opus, 73% cost reduction).
- All v2.1 features retained.

### v2.1

- **ORPHANED DEAL CHECK (Phase 1c)**: New phase scans for deals with open tasks but no recent activity, flags for review.
- **DYNAMIC COMPANION SKILL VERSION RESOLUTION**: Skills loaded by prefix glob pattern instead of hardcoded version numbers.
- All v2.0 features retained.

### v2.0

- **TOKEN-OPTIMIZED ARCHITECTURE**: Complete audit of context window usage identified ~180K bytes/run of savings across 5 optimizations. Session previously compacted 2x before reaching Phase 5; these changes target root causes.
- **SORT FIX (Due_Date → Created_Time)**: Zoho Search API only supports `id`, `Created_Time`, `Modified_Time` for `sort_by`. Previous `Due_Date asc` caused INVALID_DATA errors and wasted retry tokens. Now uses `Created_Time asc` with inline documentation of valid values.
- **FILE-PIPED SUB-AGENT RESULTS**: Each sub-agent writes evaluation JSON to `/tmp/task_eval_{task_id}.json` instead of returning inline. Results collected via bash one-liner after all agents complete. Keeps ~40-50K of structured JSON out of conversation context.
- **PRE-BUILT DASHBOARD INJECTOR SCRIPT**: New `assets/build_dashboard.py` handles template injection using `str.find()` + string concatenation (never regex, which crashes on `\u` escapes in JSON). Replaces ~80K of inline Python generation that was rebuilt from scratch every run.
- **DEFERRED COMPANION SKILL LOADING**: Companion skills (zoho-crm-v30, zoho-crm-email-v3-5, etc.) no longer loaded at trigger time. Deferred to Phase 5 just-in-time when execution actually begins. Saves ~20K context during evaluation phases.
- **JUST-IN-TIME SKILL LOADING SECTION (Phase 5)**: New subsection at Phase 5 start documents which companion skills to read for which task types, loaded once per session rather than per-task.
- All v1.9 features retained.

### v1.9

- **INTERACTIVE HTML DASHBOARD OUTPUT (DEFAULT)**: New Phase 3a replaces the chat-based approval table as the default output. Generates a standalone HTML dashboard file populated with live sub-agent evaluation data via `window.TASK_DATA_INJECT`. Dashboard features: Card/Compact/Kanban views, inline email editing with character counts, batch approve/skip/reject with toggle, drag-and-drop in Kanban, dark mode, search and filter by type/status, auto-save every 30 seconds, and three export paths (Send to Claude URL injection, Save to Folder JSON, Copy to Clipboard).
- **DASHBOARD DATA SCHEMA**: Sub-agent JSON results mapped to dashboard-compatible objects with full Zoho CRM and Gmail URLs, email drafts, and smart successor defaults.
- **SEND TO CLAUDE INTEGRATION**: Dashboard "Send to Claude" button encodes approved decisions as a URL payload with multi-tab overflow for large batches. Decisions route back to Phase 5 for sequential execution.
- **THREE-SOURCE DECISION INPUT**: Phase 5 now accepts decisions from dashboard (Send to Claude payload or JSON file), or traditional chat commands (approve all, approve #1, etc.).
- **DASHBOARD SUCCESSOR OVERRIDES**: User can toggle successor creation and adjust follow-up days per task in the dashboard. Phase 5 respects these overrides.
- **CHAT TABLE AS FALLBACK**: Previous approval table format preserved as Phase 3b fallback if dashboard generation fails.
- **COMPANION SKILLS UPDATED**: zoho-crm-v28 references updated to zoho-crm-v30, webex-bots-v1-6 updated to webex-bots-v1-7.
- **BUNDLED ASSET**: Dashboard HTML template bundled at `assets/task-dashboard.html`.
- All v1.8 features retained.

### v1.8

- **EMBEDDED VOICE/STYLE GUIDE IN SUB-AGENT PROMPT**: Full Chris Graves style guide now embedded inline in the sub-agent prompt. Includes: friendly/confident tone, sentence variety, contractions (I'll, you're, that's, we've), qualifying language, banned phrases (em dashes, filler openers, AI phrases), tone anchors ("How does everything look?", "What has feedback been so far?", "For your convenience..."), and email structure. Previously was a single line; now a full block.
- **MANDATORY PARAGRAPH SPACING IN SUB-AGENT PROMPT**: Sub-agents explicitly required to place blank lines between every paragraph. Rule embedded alongside voice/style guide — both enforced at draft creation time.
- **PHASE 3 PRE-PRESENTATION GATE**: New mandatory gate runs on all sub-agent email drafts before the approval table is built. Five checks: (1) paragraph spacing, (2) filler openers, (3) AI phrases, (4) em dashes, (5) closing CTA. Gate runs silently and corrects drafts before display.
- **NEVER RULE ADDED**: "NEVER skip the Phase 3 pre-presentation gate."
- All v1.7 features retained.

### v1.7

- **CANONICAL ZOHO QUERY**: Phase 1 hardcodes the correct query. Primary: `(Owner:equals:2570562000141711002)and(Due_Date:less_equal:{TODAY})and(Status:equals:Not Started)`. Fallback for INVALID_QUERY. Banned patterns documented (no `not_equals`, no missing owner filter).
- **IR01 BATCH PRE-FILTER**: New Phase 1b step. IR01 auto-reminder tasks identified before sub-agent launch and batch-classified as NEEDS_REVIEW in a single approval table row. Prevents wasted sub-agent budget on noise tasks.
- **SUB-AGENT VERBOSITY CAP**: Sub-agent prompt now ends with explicit VERBOSITY CAP — return ONLY the structured JSON object. No prose, no preamble, no narrative. Prevents context exhaustion before Phase 3 when evaluating 20+ tasks.
- **DR01 CLOSED WON AUTO-CLOSE**: DR01 gate checks deal stage first. Closed (Won) or Closed (Lost) -> auto-close the task with a note, no email drafted, no successor created.
- **COMPANION SKILLS UPDATED**: zoho-crm-v27 -> zoho-crm-v28.
- **IR01_BATCH triage category**: Added to gate quick reference and NEVER rules.
- All v1.6 features retained.

### v1.6

- REVISED DRAFT APPROVAL RULE: Full revised draft must be shown before sending any modified email.
- REPLY-ALL THREAD ENFORCEMENT: gmail_read_thread required before any thread reply.
- All v1.5 features retained.

### v1.5

- PARALLEL SUB-AGENT EVALUATION: All tasks evaluated simultaneously in one message block.
- 5-PHASE WORKFLOW: Fetch -> Parallel eval -> Approval table -> Inbox scan -> Sequential execution.
- INLINE EMAIL DRAFT PREVIEWS: Full email body shown in approval table.
- CLICKABLE ZOHO CRM + GMAIL LINKS: All rows hyperlinked.
- All v1.4 features retained.

### v1.4

- INBOX SCAN PHASE, 4 INBOX CATEGORIES, UNIFIED BATCH TABLE, DEDUPLICATION LOGIC.

### v1.3

- NEVER MANUALLY CLOSE WON, GMAIL AS SOURCE OF TRUTH, SUCCESSOR AFTER EVERY ACTION, PIPEDREAM/ZAPIER TOOL ID.

### v1.2

- Per-Task-Type Evaluation Gates, Batch Approval Table, Successor Task Enforcement, Business Day Calculator.

### v1.1

- Slim Trigger Router, 20+ trigger phrases.

### v1.0

- Initial release.
