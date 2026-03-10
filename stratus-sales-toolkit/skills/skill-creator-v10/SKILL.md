---
name: skill-creator-v10
description: "skill creator with eval/benchmark framework, mandatory version comparison, plugin-aware mode for manifest updates, github auto-sync to stratus-sales-toolkit repo, auto-generates .skill file for one-click local install after every push, marketplace.json sync, parallel test case execution with grading and html benchmark viewer, blind a/b comparison, and description optimization loop. differentiates standalone skill updates from plugin-member skill updates with automatic plugin.json, marketplace.json, and readme.md maintenance. triggers: create skill, new skill, edit skill, improve skill, update skill, test skill, benchmark skill, eval skill, optimize skill description, skill performance, run evals, createskill."
---

# Skill Creator v10

Full-lifecycle skill development: **create → test → benchmark → deploy → distribute**. Combines Anthropic's eval/benchmark framework with the Stratus deployment pipeline, so skills get stress-tested before they ship and distributed seamlessly after.

## What Changed in v10

| Change | v9 | v10 |
|--------|----|-----|
| Eval framework | None | Full: test cases, parallel subagent runs, grading, HTML viewer |
| Benchmark system | None | Quantitative pass rates, timing, token usage with mean ± stddev |
| Blind A/B comparison | None | Independent agent judges two outputs without knowing which is which |
| Description optimization | None | Automated loop tests trigger accuracy across 20 queries |
| Skill creation from scratch | Not supported (deploy-only) | Full capture-intent → interview → draft → iterate workflow |
| Eval viewer | None | Interactive HTML with Outputs tab + Benchmark tab + feedback collection |
| All v9 deployment features | ✓ | ✓ Retained: version comparison, plugin-aware mode, GitHub sync, .skill gen |

## Architecture Overview

```
PHASE 1: CAPTURE INTENT          → What should the skill do?
PHASE 2: WRITE / EDIT SKILL      → Draft or modify SKILL.md
PHASE 3: EVAL & BENCHMARK        → Test cases, grading, viewer (NEW)
PHASE 4: VERSION COMPARISON       → Mandatory diff check (from v9)
PHASE 5: PLUGIN-AWARE MODE       → Manifest updates if needed (from v9)
PHASE 6: GITHUB SYNC + .SKILL    → Deploy and distribute (from v9)
PHASE 7: DESCRIPTION OPTIMIZATION → Trigger accuracy tuning (NEW, optional)
```

Phases 1-3 are the creative/quality loop. Phases 4-6 are the deployment pipeline. Phase 7 is post-deploy polish. The user can enter at any phase depending on where they are in the process.

## Built-in Skill Creator Resources

The eval framework references scripts and agents from the built-in skill-creator. All paths below are relative to the built-in skill-creator directory. Before using any of these, resolve the path:

```bash
BUILTIN_SC="/sessions/hopeful-intelligent-einstein/mnt/.skills/skills/skill-creator"
```

| Resource | Path | Purpose |
|----------|------|---------|
| Eval viewer | `$BUILTIN_SC/eval-viewer/generate_review.py` | HTML output reviewer with feedback |
| Viewer template | `$BUILTIN_SC/eval-viewer/viewer.html` | Template for the viewer |
| Grader agent | `$BUILTIN_SC/agents/grader.md` | Grades assertions against outputs |
| Comparator agent | `$BUILTIN_SC/agents/comparator.md` | Blind A/B comparison |
| Analyzer agent | `$BUILTIN_SC/agents/analyzer.md` | Pattern analysis across benchmark runs |
| Schemas | `$BUILTIN_SC/references/schemas.md` | JSON schemas for evals, grading, benchmarks |
| Run eval | `$BUILTIN_SC/scripts/run_eval.py` | Execute evaluation |
| Run loop | `$BUILTIN_SC/scripts/run_loop.py` | Description optimization loop |
| Aggregate benchmark | `$BUILTIN_SC/scripts/aggregate_benchmark.py` | Aggregate benchmark stats |
| Package skill | `$BUILTIN_SC/scripts/package_skill.py` | Package as .skill file |
| Eval review HTML | `$BUILTIN_SC/assets/eval_review.html` | Template for description eval review |

---

## PHASE 1: CAPTURE INTENT

Start by understanding what the user wants. The conversation might already contain a workflow to capture (e.g., "turn this into a skill"). If so, extract answers from conversation history first.

### Key Questions

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Skills with objectively verifiable outputs (file transforms, data extraction, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style) often don't. Suggest the appropriate default, but let the user decide.

### Interview and Research

Ask about edge cases, input/output formats, example files, success criteria, and dependencies. Check available MCPs for research. Come prepared with context to reduce burden on the user.

**Skip this phase** if the user already has a draft skill and wants to improve/deploy it.

---

## PHASE 2: WRITE / EDIT SKILL

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description in quotes required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context when skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited, scripts execute without loading)

Keep SKILL.md under 500 lines. For large reference files (>300 lines), include a table of contents. Reference files clearly from SKILL.md with guidance on when to read them.

#### Frontmatter Rules

| Rule | Requirement |
|------|-------------|
| **Lowercase only** | Name and description entirely lowercase |
| **Hyphenated versions** | Use `v1-0` not `v1.0` |
| **No angle brackets** | No `<` or `>` in description |
| **Quote description** | Wrap description value in double quotes (colons and special chars break YAML parsing otherwise) |
| **Max lengths** | Name: 64 chars, Description: 1024 chars, Body: 500 lines |

#### Writing Patterns

Prefer imperative form. Explain the **why** behind instructions rather than heavy-handed MUSTs. Today's LLMs are smart; good theory of mind and clear reasoning are more effective than rigid constraints. If you find yourself writing ALWAYS or NEVER in all caps, reframe with reasoning instead.

Make descriptions "pushy" to combat undertriggering. Include both what the skill does AND specific contexts for when to use it, including edge cases and adjacent domains.

---

## PHASE 3: EVAL & BENCHMARK

This is the quality assurance phase. Test the skill against realistic prompts, grade the outputs, and review results before deploying. This phase is **recommended for all skill updates** and **mandatory for new skills or major rewrites**.

### Step 1: Create Test Cases

Draft 2-3 realistic test prompts. Share them with the user for approval. Save to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": [],
      "expectations": []
    }
  ]
}
```

Test prompts should be realistic, detailed, and specific. Include file paths, personal context, column names, company names. Mix lengths, include edge cases. Don't write assertions yet; just the prompts.

### Step 2: Spawn Parallel Runs

For each test case, spawn two subagents in the **same turn**:

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
```

**Baseline run** (depends on context):
- **New skill**: No skill at all. Same prompt, no skill path. Save to `without_skill/outputs/`.
- **Improving existing skill**: Old version snapshot. `cp -r <skill-path> <workspace>/skill-snapshot/`, point baseline at snapshot. Save to `old_skill/outputs/`.

Write `eval_metadata.json` for each test case with descriptive eval names.

### Step 3: Draft Assertions While Runs Execute

Don't wait. Draft quantitative assertions for each test case. Good assertions are objectively verifiable with descriptive names. Update `eval_metadata.json` and `evals/evals.json`. Explain to the user what they'll see in the viewer.

### Step 4: Capture Timing Data

When each subagent completes, the notification contains `total_tokens` and `duration_ms`. Save immediately to `timing.json` in the run directory. This data is only available at notification time.

### Step 5: Grade, Aggregate, and Launch Viewer

Once all runs complete:

1. **Grade each run** — Read `$BUILTIN_SC/agents/grader.md`, evaluate assertions against outputs. Save to `grading.json`. Use fields `text`, `passed`, `evidence` (not `name`/`met`/`details`). For programmatically checkable assertions, write and run a script.

2. **Aggregate into benchmark**:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   (Run from the $BUILTIN_SC directory.) Produces `benchmark.json` and `benchmark.md`.

3. **Analyst pass** — Read `$BUILTIN_SC/agents/analyzer.md` and surface patterns the aggregate stats might hide: non-discriminating assertions, high-variance evals, time/token tradeoffs.

4. **Launch the viewer** (use `--static` for Cowork since no display):
   ```bash
   python $BUILTIN_SC/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     --static /mnt/outputs/eval-review.html
   ```
   For iteration 2+, add `--previous-workspace <workspace>/iteration-<N-1>`.

5. **Present the viewer** to the user via computer:// link. The viewer has two tabs: "Outputs" for qualitative review and "Benchmark" for quantitative comparison.

**IMPORTANT: ALWAYS generate the eval viewer BEFORE evaluating outputs yourself.** Get results in front of the human ASAP.

### Step 6: Read Feedback and Iterate

When the user finishes reviewing, read `feedback.json` (downloaded via "Submit All Reviews" button). Empty feedback means the user thought it was fine. Focus improvements on test cases with specific complaints.

**Improvement principles:**
- Generalize from feedback. Don't overfit to the few test cases.
- Keep the prompt lean. Remove things not pulling their weight.
- Explain the why. Theory of mind over rigid constraints.
- Look for repeated work across test cases. If all subagents wrote similar scripts, bundle that script in the skill.

After improving, rerun all test cases into `iteration-<N+1>/`. Launch viewer with `--previous-workspace`. Repeat until the user is satisfied or feedback is empty.

### Advanced: Blind Comparison

For rigorous A/B comparison between two skill versions, read `$BUILTIN_SC/agents/comparator.md` and `$BUILTIN_SC/agents/analyzer.md`. This gives two outputs to an independent agent without revealing which is which. Optional; most users won't need it.

### Cowork-Specific Notes

- Subagents available, so parallel execution works. If timeouts are severe, run in series.
- No display, so use `--static <output_path>` for the eval viewer. Present via computer:// link.
- "Submit All Reviews" downloads `feedback.json`. Request access to read it if needed.
- Description optimization (`run_loop.py`) should work via `claude -p` subprocess.

---

## PHASE 4: MANDATORY VERSION COMPARISON

**When updating an existing skill, ALWAYS run version comparison BEFORE deploying.** This prevents accidental deletion of existing logic. No exceptions.

### Comparison Checklist

**Step 1: Line Count Check**
```bash
wc -l /mnt/skills/user/old-skill-vX/SKILL.md /home/claude/new-skill-vY/SKILL.md
```
New version should have EQUAL or MORE lines. If fewer, STOP and investigate.

**Step 2: File Structure Comparison**
```bash
find /mnt/skills/user/old-skill-vX -type f | sort
find /home/claude/new-skill-vY -type f | sort
```
All files from old version must exist in new version.

**Step 3: Diff Analysis**
```bash
diff /mnt/skills/user/old-skill-vX/SKILL.md /home/claude/new-skill-vY/SKILL.md | head -100
```
Should show only ADDITIONS. Any DELETIONS must be intentional and explained.

**Step 4: Key Section Verification**
```bash
grep "^##" /mnt/skills/user/old-skill-vX/SKILL.md > /tmp/old_sections.txt
grep "^##" /home/claude/new-skill-vY/SKILL.md > /tmp/new_sections.txt
diff /tmp/old_sections.txt /tmp/new_sections.txt
```
All old section headers must exist in new version.

**Step 5: Supporting Files Check**
```bash
diff /mnt/skills/user/old-skill-vX/workflows/file.md /home/claude/new-skill-vY/workflows/file.md
```

### Comparison Output Format

Display before deploying:

```
VERSION COMPARISON RESULTS:
| Check | Old (vX) | New (vY) | Status |
|-------|----------|----------|--------|
| Line count | 604 | 718 | ✓ (+114 lines) |
| File count | 7 | 7 | ✓ |
| Sections | 15 | 18 | ✓ (+3 new) |
| Deletions | - | 0 | ✓ |
| Supporting files | 6 | 6 | ✓ (all identical) |
```

**If ANY check fails or shows unexpected deletions, STOP and review with user.**

---

## PHASE 5: PLUGIN-AWARE MODE

When a skill is a member of the stratus-sales-toolkit plugin (see list below), additional steps are required depending on whether the skill's folder name changes.

### Plugin Skills (auto-sync enabled)

- ccw-subscription-renewal-v1-2
- coterm-calculator-v1-0
- daily-task-engine-v1-8
- erate-proposal-workflow-v1-2
- fu30-followup-automation-v1-3
- pharos-iq-automation
- skill-creator-v10
- skill-downloader-v1-0
- stratus-quote-pdf-v2-0
- stratus-quoting-bot-v4-6
- subscription-modification-v2-6
- webex-bots-v1-7
- weborder-to-deal-automation-v1-1
- zoho-crm-email-v3-5
- zoho-crm-v30

Skills NOT in this list are local-only and skip GitHub sync and plugin manifest updates.

### Folder Name Change Detection

```
OLD folder name: daily-task-engine-v1-7
NEW folder name: daily-task-engine-v1-8
→ FOLDER NAME CHANGED → Plugin manifest update REQUIRED

OLD folder name: pharos-iq-automation
NEW folder name: pharos-iq-automation
→ FOLDER NAME UNCHANGED → Plugin manifest update SKIPPED
```

**Rule:** If the version number is embedded in the folder name and that number changes, the plugin manifest MUST be updated. Versionless folder names skip manifest update.

### Plugin Version Bump Decision Tree

| Change Type | Examples | Version Bump |
|-------------|----------|--------------|
| Bug fix / gate logic fix / query correction | DR01 closed-won fix, canonical query hardcode | **Patch** (1.2.1 → 1.2.2) |
| New feature / new phase / new workflow | Eval framework, parallel sub-agents, plugin-aware mode | **Minor** (1.2.1 → 1.3.0) |
| Breaking change / restructured workflow | Renamed triggers, removed gates, changed return format | **Major** (1.2.1 → 2.0.0) |

When in doubt, use Patch. Minor and Major require explicit user confirmation.

### Plugin Manifest Update (when folder name changed)

Update these files in the plugin repo:

**plugin.json AND marketplace.json** — Both must always be bumped to the same version simultaneously.

- `marketplace.json` at repo root: `/.claude-plugin/marketplace.json`
- `plugin.json` in plugin folder: `/stratus-sales-toolkit/.claude-plugin/plugin.json`

```json
// marketplace.json — update metadata.version AND plugins[].version
"metadata": { "version": "1.2.3" },
"plugins": [{ "version": "1.2.3" }]

// plugin.json — update version
"version": "1.2.3"
```

**plugin.json skill reference** — Replace old folder name with new:
```json
// BEFORE
{ "name": "skill-creator-v9", "description": "..." }
// AFTER
{ "name": "skill-creator-v10", "description": "..." }
```

**README.md** — Update skills table row with new name and description.

**Remove old skill folder**: `rm -rf skills/old-skill-vX`

### Plugin-Aware Mode Summary Tables

Display before committing:

```
PLUGIN-AWARE MODE RESULTS (folder changed):
| Check | Status | Detail |
|-------|--------|--------|
| Folder name changed | YES | v9 → v10 |
| Change type | New feature | Minor bump |
| plugin.json skill ref | ✓ Updated | skill-creator-v10 |
| plugin.json version | ✓ Bumped | 1.5.0 → 1.6.0 |
| marketplace.json | ✓ Bumped | 1.5.0 → 1.6.0 |
| README.md row | ✓ Updated | |
| Old folder removed | ✓ | skills/skill-creator-v9 |
```

```
PLUGIN-AWARE MODE RESULTS (folder unchanged):
| Check | Status | Detail |
|-------|--------|--------|
| Folder name changed | NO | pharos-iq-automation (stable) |
| Manifest update | SKIPPED | Folder name unchanged |
| GitHub sync | ✓ Proceed | Skill files only |
```

---

## PHASE 6: GITHUB SYNC + .SKILL GENERATION

Runs automatically after deploying any plugin skill. Skip for local-only skills.

### GitHub Sync Configuration

```
Repository: github.com/cjgraves1119/stratus-sales-toolkit
Branch: main
Auth: Classic PAT (stored in user preferences, never commit to repo)
Local plugin clone: /home/claude/stratus-sales-toolkit
```

### PAT Guard — Check Before Any Git Operation

```
IF no PAT found in user preferences:
  → STOP GitHub sync entirely
  → Display: "GitHub sync skipped — no PAT found. Skill deployed locally.
     To enable sync, add your GitHub Classic PAT to Cowork preferences."
  → Proceed to Step 4 (.skill file generation) so user still gets local install
  → Do NOT attempt git clone, pull, or push
```

### Step 1: Clone or Update Local Plugin Repo

```bash
cd /home/claude
git clone https://cjgraves1119:{CLASSIC_PAT}@github.com/cjgraves1119/stratus-sales-toolkit.git
cd stratus-sales-toolkit
git config user.name "Chris Graves"
git config user.email "chrisg@stratusinfosystems.com"

# If already cloned:
cd /home/claude/stratus-sales-toolkit && git pull origin main
```

### Step 2: Copy Updated Skill into Plugin

```bash
rm -rf skills/old-skill-name-vX-X
cp -r /home/claude/new-skill-name-vY-Y skills/new-skill-name-vY-Y
```

### Step 3: Apply Plugin Manifest Updates (if folder name changed)

Edit plugin.json, marketplace.json, README.md per Phase 5 instructions.

### Step 4: Generate .skill File for Local Install

```bash
cd /home/claude/stratus-sales-toolkit/stratus-sales-toolkit/skills
zip -r /tmp/{skill-name}.skill {skill-name}/
cp /tmp/{skill-name}.skill /mnt/outputs/{skill-name}.skill
```

Then use `present_files` to surface the file. Always generate the .skill file before pushing, even if the user doesn't explicitly ask.

### Step 5: Commit and Push

```bash
git add -A
git commit -m "Update {skill-name} to {version}: {brief description}"
git push origin main
```

### Step 6: Verify

```bash
git log --oneline -1
git status
```

### GitHub Sync Summary Table

```
GITHUB SYNC RESULTS:
| Step | Status |
|------|--------|
| Pull latest | ✓ |
| Copy skill files | ✓ (X files) |
| Version comparison | ✓ |
| Plugin manifest updated | ✓ (or SKIPPED) |
| marketplace.json bumped | ✓ X.X.X → X.X.X (or SKIPPED) |
| plugin.json bumped | ✓ X.X.X → X.X.X (or SKIPPED) |
| README.md updated | ✓ (or SKIPPED) |
| .skill file generated | ✓ outputs/{skill-name}.skill |
| Commit | ✓ (abc1234) |
| Push to main | ✓ |
```

### Error Recovery

| Error | Fix |
|-------|-----|
| `git push` rejected | `git pull --rebase origin main` then retry |
| PAT expired/invalid | Ask user for new classic PAT |
| Merge conflict | Show to user, resolve manually |
| Network error | Retry once, then inform user |
| Bash ENOSPC / no space | Use GitHub REST API fallback (PUT /repos/{owner}/{repo}/contents/{path}) |

---

## PHASE 7: DESCRIPTION OPTIMIZATION (Optional)

After the skill is finished and deployed, offer to optimize the description for better trigger accuracy. This uses an automated loop that tests how reliably Claude invokes the skill for different prompts.

### Step 1: Generate Trigger Eval Queries

Create 20 eval queries (8-10 should-trigger, 8-10 should-not-trigger). Save as JSON:

```json
[
  {"query": "realistic user prompt", "should_trigger": true},
  {"query": "near-miss prompt", "should_trigger": false}
]
```

**Should-trigger queries**: Different phrasings of the same intent. Formal, casual, edge cases, uncommon use cases. Include cases where the skill competes with another but should win.

**Should-not-trigger queries**: Near-misses that share keywords but need something different. Adjacent domains, ambiguous phrasing. Don't use obviously irrelevant queries.

All queries must be realistic, detailed, and specific. Include file paths, personal context, company names. Mix lengths.

### Step 2: Review with User

Read the eval review template from `$BUILTIN_SC/assets/eval_review.html`. Replace placeholders and open for user review. User edits queries, toggles triggers, exports to `eval_set.json`.

### Step 3: Run Optimization Loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-eval-set.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

(Run from $BUILTIN_SC directory.) This splits into 60% train / 40% test, evaluates current description 3x per query, proposes improvements, and iterates up to 5 times. Selects best by test score to avoid overfitting.

### Step 4: Apply Result

Take `best_description` from the output and update SKILL.md frontmatter. Show user before/after with scores.

---

## Quick Reference

```
V10 FULL LIFECYCLE:
┌─────────────────────────────────────────────────┐
│ PHASE 1: Capture Intent (new skills)            │
│ PHASE 2: Write/Edit SKILL.md                    │
│ PHASE 3: Eval & Benchmark (test → grade → view) │  ← NEW
│ PHASE 4: Version Comparison (MANDATORY)         │
│ PHASE 5: Plugin-Aware Mode                      │
│ PHASE 6: GitHub Sync + .skill                   │
│ PHASE 7: Description Optimization (optional)    │  ← NEW
└─────────────────────────────────────────────────┘

EVAL & BENCHMARK (Phase 3):
1. Create 2-3 test cases → evals/evals.json
2. Spawn parallel runs (with_skill + baseline) in same turn
3. Draft assertions while runs execute
4. Capture timing data from subagent notifications
5. Grade → Aggregate → Analyst pass → Launch viewer
6. Present viewer to user (--static for Cowork)
7. Read feedback → improve skill → iterate

VERSION COMPARISON (Phase 4, MANDATORY FOR UPDATES):
1. wc -l old/SKILL.md new/SKILL.md  → line count should increase
2. diff old/SKILL.md new/SKILL.md   → only additions, no deletions
3. find old -type f | sort          → all files preserved
4. Display comparison table before deploying
NEVER SKIP THIS STEP.

PLUGIN-AWARE MODE (Phase 5):
1. Did folder name change? (v9 → v10 = YES; pharos-iq = NO)
2. If YES: determine bump type (patch/minor/major)
3. Update plugin.json AND marketplace.json (both same version)
4. Update README.md skills table row
5. rm old folder, cp new folder into plugin

GITHUB SYNC (Phase 6):
0. CHECK FOR PAT — if not in preferences, skip to step 4
1. git clone/pull the repo
2. rm old skill folder, cp new one into skills/
3. Apply manifest updates if folder name changed
4. zip skill/ → outputs/{skill-name}.skill → present_files (ALWAYS)
5. git add -A && git commit && git push
6. Display sync results table
```

---

## Changelog

### v10 (Current)
- **Eval & Benchmark Framework** (Phase 3): Full test case creation, parallel subagent execution (with_skill + baseline), assertion grading, benchmark aggregation with pass rates and timing, interactive HTML viewer for qualitative review, feedback collection loop, and iterative improvement cycle. References built-in skill-creator scripts and agents rather than duplicating them.
- **Blind A/B Comparison**: Optional rigorous comparison between two skill versions using independent judge agent that doesn't know which output came from which skill.
- **Description Optimization** (Phase 7): Automated loop generates 20 trigger/no-trigger queries, splits into train/test, iterates up to 5 times to find the description with best trigger accuracy. Prevents both over- and under-triggering.
- **Architecture Overview**: Clear 7-phase lifecycle diagram showing where each capability fits.
- **Updated Plugin Skills List**: Reflects current versions (daily-task-engine-v1-8, zoho-crm-v30, skill-creator-v10, webex-bots-v1-7, stratus-quoting-bot-v4-6, erate-proposal-workflow-v1-2, skill-downloader-v1-0)
- **Cowork-Specific Notes**: Static HTML viewer, feedback download workflow, subprocess-based description optimization
- All v9 features retained: version comparison, plugin-aware mode, GitHub sync, .skill generation, PAT guard, marketplace.json sync, folder rename detection, REST API fallback

### v9
- Plugin-Aware Mode: folder name change detection, manifest update, version bump decision tree
- marketplace.json sync with plugin.json
- .skill file auto-generation after every push
- PAT guard clause for graceful GitHub sync skip
- GitHub REST API fallback when Bash unavailable

### v8
- GitHub Auto-Sync to stratus-sales-toolkit repo
- Plugin skill list tracking for auto-sync
- Version bump handling for plugin.json and README.md

### v7
- MANDATORY VERSION COMPARISON with 5-step checklist
- Comparison output table before packaging

### v6
- .skill is just renamed .zip
- DOCX optional, Quick Update mode

### v5
- DOCX output, ToC, headers/footers

### v4
- Lowercase frontmatter, hyphenated versions
