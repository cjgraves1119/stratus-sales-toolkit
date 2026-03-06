---
name: skill-creator-v9
description: skill creator with mandatory version comparison, plugin-aware mode for manifest updates, github auto-sync to stratus-sales-toolkit repo, auto-generates .skill file for one-click local install after every push, and marketplace.json sync. differentiates standalone skill updates from plugin-member skill updates with automatic plugin.json, marketplace.json, and readme.md maintenance.
---

# Skill Creator v9

Optimized skill creation with **mandatory version comparison**, **automatic GitHub sync**, and **plugin-aware mode** that handles plugin.json manifest updates when skill folder names change.

## What Changed in v9

| Change | v8 | v9 |
|--------|----|-----|
| Plugin manifest update | Manual (not documented) | Auto-triggered when folder name changes |
| Plugin version bump | Not documented | Decision tree: patch/minor/major |
| Plugin skills list | Outdated (v1-4, v27) | Current (v1-7, v28, v9) |
| Folder rename detection | None | Auto-detects version bump in name |
| Standalone vs. plugin-member | Not differentiated | Explicit workflow split |
| marketplace.json sync | Not included | Bumped alongside plugin.json on every push |
| .skill file output | Not generated | Auto-generated after every push for one-click local install |
| PAT guard clause | Not present | Checks for PAT before git ops; skips sync gracefully if missing |

## GitHub Sync Configuration

```
Repository: github.com/cjgraves1119/stratus-sales-toolkit
Branch: main
Auth: Classic PAT (stored in user preferences, never commit to repo)
Local plugin clone: /home/claude/stratus-sales-toolkit
```

### Plugin Skills (auto-sync enabled)

These skills are part of the stratus-sales-toolkit plugin. When any of these are created or updated, the GitHub sync step AND the plugin-aware manifest check both run automatically.

- ccw-subscription-renewal-v1-2
- coterm-calculator-v1-0
- daily-task-engine-v1-8
- erate-proposal-workflow-v1-2
- fu30-followup-automation-v1-3
- pharos-iq-automation
- skill-creator-v9
- stratus-quote-pdf-v2-0
- stratus-quoting-bot-v4-5
- subscription-modification-v2-6
- webex-bots-v1-6
- weborder-to-deal-automation-v1-1
- zoho-crm-email-v3-5
- zoho-crm-v28

**Skills NOT in this list** are local-only and skip the GitHub sync step and plugin manifest update.

---

## MANDATORY VERSION COMPARISON

**When updating an existing skill, ALWAYS run version comparison BEFORE deploying.** This prevents accidental deletion of existing logic.

### When to Run
- Every skill update (not new skills)
- Before final deployment
- No exceptions

### Comparison Checklist

**Step 1: Line Count Check**
```bash
wc -l /mnt/skills/user/old-skill-vX/SKILL.md /home/claude/new-skill-vY/SKILL.md
```
- New version should have EQUAL or MORE lines than old version
- If fewer lines → STOP and investigate what was removed

**Step 2: File Structure Comparison**
```bash
find /mnt/skills/user/old-skill-vX -type f | sort
find /home/claude/new-skill-vY -type f | sort
```
- All files from old version must exist in new version
- Supporting files (workflows/, data/, references/) should be identical unless intentionally changed

**Step 3: Diff Analysis**
```bash
diff /mnt/skills/user/old-skill-vX/SKILL.md /home/claude/new-skill-vY/SKILL.md | head -100
```
- Review diff output
- Should show only ADDITIONS (lines starting with `>`)
- Any DELETIONS (lines starting with `<`) must be intentional and explained

**Step 4: Key Section Verification**
```bash
# Extract section headers from both versions
grep "^##" /mnt/skills/user/old-skill-vX/SKILL.md > /tmp/old_sections.txt
grep "^##" /home/claude/new-skill-vY/SKILL.md > /tmp/new_sections.txt
diff /tmp/old_sections.txt /tmp/new_sections.txt
```
- All old section headers must exist in new version
- New sections can be added

**Step 5: Supporting Files Check (if applicable)**
```bash
# For skills with multiple files
diff /mnt/skills/user/old-skill-vX/workflows/file.md /home/claude/new-skill-vY/workflows/file.md
```
- Supporting files should be identical unless specifically being updated
- Report any changes to user

### Comparison Output Format

Display this summary before deploying:

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

**If ANY check fails or shows unexpected deletions → STOP and review with user before proceeding.**

### Common Issues Prevented

| Issue | How Comparison Catches It |
|-------|---------------------------|
| Accidentally deleted section | Line count drops, diff shows `<` lines |
| Overwrote instead of appended | Section count drops |
| Lost supporting files | File count mismatch |
| Corrupted workflow file | Supporting file diff shows changes |

---

## PLUGIN-AWARE MODE

When a skill is a member of the stratus-sales-toolkit plugin (see list above), additional steps are required depending on whether the skill's **folder name** changes.

### Step 1: Folder Name Change Detection

Before deploying, determine if the skill folder name changed:

```
OLD folder name: daily-task-engine-v1-6
NEW folder name: daily-task-engine-v1-7
→ FOLDER NAME CHANGED → Plugin manifest update REQUIRED
```

```
OLD folder name: pharos-iq-automation
NEW folder name: pharos-iq-automation
→ FOLDER NAME UNCHANGED → Plugin manifest update SKIPPED (skill files only)
```

**Rule:** If the version number is embedded in the folder name (e.g., `v1-6`, `v27`, `v3-5`) and that number changes, the plugin manifest MUST be updated. If the skill uses a versionless folder name (e.g., `pharos-iq-automation`, `coterm-calculator`), no manifest update is needed.

### Step 2: Plugin Version Bump Decision Tree

When the folder name changes, bump the plugin version in `plugin.json` according to the type of change:

| Change Type | Examples | Version Bump |
|-------------|----------|--------------|
| Bug fix / gate logic fix / query correction | DR01 closed-won fix, canonical query hardcode, IR01 pre-filter | **Patch** (1.2.1 → 1.2.2) |
| New feature / new phase / new workflow | Inbox scan phase, parallel sub-agents, plugin-aware mode | **Minor** (1.2.1 → 1.3.0) |
| Breaking change / restructured workflow | Renamed triggers, removed gates, changed return format | **Major** (1.2.1 → 2.0.0) |

**When in doubt, use Patch.** Minor and Major bumps require explicit user confirmation.

### Step 3: Plugin Manifest Update (when folder name changed)

Update these three files in the plugin repo:

#### 3a. plugin.json AND marketplace.json — Update skill reference and bump versions

**Both files must always be bumped together.** `marketplace.json` controls the "update available" notification for all team members. Missing it breaks update detection.

`marketplace.json` is at the repo root: `/.claude-plugin/marketplace.json`
`plugin.json` is inside the plugin folder: `/stratus-sales-toolkit/.claude-plugin/plugin.json`

Update both to the same version simultaneously:

```json
// marketplace.json — update metadata.version AND plugins[].version
"metadata": { "version": "1.2.3" },
"plugins": [{ "version": "1.2.3" }]

// plugin.json — update version
"version": "1.2.3"
```

#### 3c. plugin.json — Update skill reference

Find the old skill entry and replace with new folder name:

```json
// BEFORE
{
  "name": "daily-task-engine-v1-6",
  "description": "..."
}

// AFTER
{
  "name": "daily-task-engine-v1-7",
  "description": "..."  // Use new skill's frontmatter description
}
```

Also bump the top-level `version` field per the decision tree above:

```json
// BEFORE
"version": "1.2.1"

// AFTER
"version": "1.2.2"  // Patch bump for bug fix / optimization
```

#### 3d. README.md — Update skills table

Find the skill row in the skills table and update the name and description:

```markdown
| daily-task-engine-v1-6 | ... | old description |
↓
| daily-task-engine-v1-7 | ... | new description |
```

#### 3e. Remove old skill folder from plugin repo

```bash
rm -rf skills/daily-task-engine-v1-6
```

This is safe — the new folder will be copied in the next step.

### Plugin-Aware Mode Summary Table

Display before committing:

```
PLUGIN-AWARE MODE RESULTS:
| Check | Status | Detail |
|-------|--------|--------|
| Folder name changed | YES | v1-6 → v1-7 |
| Change type | Bug fix / optimization | Patch bump |
| plugin.json skill ref | ✓ Updated | daily-task-engine-v1-7 |
| plugin.json version | ✓ Bumped | 1.2.1 → 1.2.2 |
| README.md row | ✓ Updated | |
| Old folder removed | ✓ | skills/daily-task-engine-v1-6 |
```

### Plugin-Aware Mode: Versionless Skill (no manifest update needed)

When the skill folder name does NOT change:

```
PLUGIN-AWARE MODE RESULTS:
| Check | Status | Detail |
|-------|--------|--------|
| Folder name changed | NO | pharos-iq-automation (stable) |
| Manifest update | SKIPPED | Folder name unchanged |
| GitHub sync | ✓ Proceed | Skill files only |
```

---

## Workflow: Quick Update (Minor Changes)

For typo fixes, small tweaks, minor additions.

```bash
# 1. Copy existing skill, bump version
cp -r /mnt/skills/user/my-skill-v2-2 /home/claude/my-skill-v2-3

# 2. Edit SKILL.md (update version in frontmatter + make changes)

# 3. RUN VERSION COMPARISON (MANDATORY)
wc -l /mnt/skills/user/my-skill-v2-2/SKILL.md /home/claude/my-skill-v2-3/SKILL.md
diff /mnt/skills/user/my-skill-v2-2/SKILL.md /home/claude/my-skill-v2-3/SKILL.md | head -50
# Verify: line count equal or higher, no unexpected deletions

# 4. Deploy to skills folder
# PLUGIN SKILLS: SKIP THIS STEP. Plugin skill folders are read-only (managed by the plugin system).
#   Local install is handled by the .skill file generated inside the GitHub Sync workflow (step 6, sub-step 4).
#   GitHub sync copies directly from your working directory, not from /mnt/skills/user/.
# NON-PLUGIN SKILLS ONLY:
#   cp -r /home/claude/my-skill-v2-3 /mnt/skills/user/my-skill-v2-3

# 5. Plugin-Aware Mode Check (if skill is in plugin list above)
# → Did folder name change? (v2-2 → v2-3 = YES)
# → Determine bump type, update plugin.json + README.md
# See "Plugin-Aware Mode" section above

# 6. GitHub Sync (if skill is in plugin list above)
# → .skill file is generated BEFORE the push (sub-step 4), then committed
# See "GitHub Sync Workflow" section below
```

**CRITICAL: Never skip step 3. Version comparison prevents accidental logic loss.**

## Workflow: Full Release (New Skill or Major Rewrite)

```bash
# 1. Create/update skill folder with SKILL.md

# 2. RUN VERSION COMPARISON (if updating existing skill)
wc -l /mnt/skills/user/old-version/SKILL.md /home/claude/new-version/SKILL.md
diff /mnt/skills/user/old-version/SKILL.md /home/claude/new-version/SKILL.md
find /mnt/skills/user/old-version -type f | sort
find /home/claude/new-version -type f | sort
# Display comparison results table before proceeding

# 3. Deploy to skills folder
# PLUGIN SKILLS: SKIP THIS STEP. Plugin skill folders are read-only (managed by the plugin system).
#   Local install is handled by the .skill file generated inside the GitHub Sync workflow (step 5, sub-step 4).
#   GitHub sync copies directly from your working directory, not from /mnt/skills/user/.
# NON-PLUGIN SKILLS ONLY:
#   cp -r /home/claude/new-version /mnt/skills/user/new-version

# 4. Plugin-Aware Mode Check (if skill is in plugin list above)
# → Did folder name change? → Update plugin.json + README.md if yes
# See "Plugin-Aware Mode" section above

# 5. GitHub Sync (if skill is in plugin list above)
# → .skill file is generated BEFORE the push (sub-step 4), then committed
# See "GitHub Sync Workflow" section below
```

---

## GitHub Sync Workflow

**Runs automatically after deploying any skill in the plugin list.** Skip for local-only skills.

### ⚠️ PAT Guard — Check Before Any Git Operation

Before attempting any GitHub sync step, verify that a GitHub Classic PAT exists in the user's Cowork preferences.

```
IF no PAT found in user preferences:
  → STOP GitHub sync entirely
  → Display this message:
    "GitHub sync skipped — no PAT found in your Cowork preferences.
     The skill has been deployed locally. To enable GitHub sync and
     plugin distribution, add your GitHub Classic PAT to Cowork Settings
     → Cowork preferences."
  → Proceed directly to Step 4 (generate .skill file) so the user
    still gets a local-installable output
  → Do NOT attempt git clone, pull, or push
```

This guard exists because the stratus-sales-toolkit GitHub repo belongs to the plugin author (Chris Graves). Team members who install the plugin inherit this skill but should not push to that repo. A missing PAT is the natural signal that GitHub sync should be skipped — fail gracefully, not with a cryptic auth error.

### Step 1: Clone or Update Local Plugin Repo

```bash
# If repo not yet cloned in this session:
cd /home/claude
git clone https://cjgraves1119:{CLASSIC_PAT}@github.com/cjgraves1119/stratus-sales-toolkit.git
cd stratus-sales-toolkit
git config user.name "Chris Graves"
git config user.email "chrisg@stratusinfosystems.com"

# If already cloned:
cd /home/claude/stratus-sales-toolkit
git pull origin main
```

### Step 2: Copy Updated Skill into Plugin

```bash
# Remove old version of the skill from plugin (handles version bumps)
rm -rf skills/old-skill-name-vX-X

# Copy new version directly from working directory
# (Plugin skill folders are read-only — do NOT copy from /mnt/skills/user/)
cp -r /home/claude/new-skill-name-vY-Y skills/new-skill-name-vY-Y
```

### Step 3: Apply Plugin Manifest Updates (if folder name changed)

```bash
# Edit plugin.json: update skill name + bump plugin version
# Edit README.md: update skills table row
# (Done manually in editor or via sed/python if needed)
```

**This step is only required when the skill's folder name changed.** See Plugin-Aware Mode above for exact field locations and update format.

### Step 4: Generate .skill File for Local Install

Before pushing to GitHub, zip the updated skill folder as a `.skill` file and present it. This packages the local artifact first, then distributes via GitHub.

```bash
# Zip the skill folder with .skill extension (from cloned repo — already has updated files)
cd /home/claude/stratus-sales-toolkit/stratus-sales-toolkit/skills
zip -r /tmp/{skill-name}.skill {skill-name}/

# Copy to outputs folder
cp /tmp/{skill-name}.skill /mnt/outputs/{skill-name}.skill
```

Then use `present_files` to surface the file:

```
present_files([{ file_path: "/mnt/outputs/{skill-name}.skill" }])
```

This gives the user a "Copy to your skills" button so the skill exists both as a standalone local install AND in the plugin (via GitHub push in the next step). Both are required for the skill to be accessible with or without the plugin active.

**Always generate the .skill file before pushing.** Do not skip this step even if the user doesn't explicitly ask for it.

### Step 5: Commit and Push

```bash
git add -A
git commit -m "Update {skill-name} to {version}: {brief description of changes}"
git push origin main
```

Commit message convention:
- Bug fix: `"Fix DR01 closed-won auto-close in daily-task-engine-v1-7"`
- New feature: `"Add inbox scan phase to daily-task-engine-v1-7"`
- Version bump: `"Bump plugin to 1.2.2: daily-task-engine v1-6 → v1-7"`

### Step 6: Verify

```bash
git log --oneline -1  # Confirm commit
git status            # Should be clean
```

### GitHub Sync Summary Table

Display after push completes:

```
GITHUB SYNC RESULTS:
| Step | Status |
|------|--------|
| Pull latest | ✓ |
| Copy skill files | ✓ (X files) |
| Version comparison | ✓ |
| SKILL.md changes confirmed | ✓ (key additions verified via grep) |
| Plugin manifest updated | ✓ (or SKIPPED - folder unchanged) |
| marketplace.json bumped | ✓ 1.2.2 → 1.2.3 (or SKIPPED) |
| plugin.json bumped | ✓ 1.2.2 → 1.2.3 (or SKIPPED) |
| README.md updated | ✓ (or SKIPPED) |
| .skill file generated | ✓ outputs/{skill-name}.skill |
| Commit | ✓ (abc1234) |
| Push to main | ✓ |
| Plugin repo | github.com/cjgraves1119/stratus-sales-toolkit |
```

### Version Bump Handling

When a skill's version changes (e.g., skill-creator-v8 → skill-creator-v9):

1. Remove old version folder from plugin: `rm -rf skills/skill-creator-v8`
2. Add new version folder: `cp -r ... skills/skill-creator-v9`
3. Update `README.md` skills table with new version
4. Update `plugin.json` — both skill name reference AND top-level plugin version field
5. Update the plugin skills list in THIS skill's SKILL.md to reflect new version name
6. Commit message should note the version bump

### Error Recovery

| Error | Fix |
|-------|-----|
| `git push` rejected | `git pull --rebase origin main` then retry push |
| PAT expired/invalid | Ask user for new classic PAT, update clone URL |
| Merge conflict | Show conflict to user, resolve manually |
| Network error | Retry once, then inform user |
| Bash ENOSPC / no space | Use GitHub REST API (PUT /repos/{owner}/{repo}/contents/{path}) as fallback |

### GitHub REST API Fallback (when Bash/git unavailable)

If the Bash tool is non-functional (ENOSPC, EROFS, etc.), use the GitHub REST API directly:

```
PUT https://api.github.com/repos/cjgraves1119/stratus-sales-toolkit/contents/skills/{skill-name}/SKILL.md
Headers:
  Authorization: Bearer {CLASSIC_PAT}
  Content-Type: application/json
Body:
  {
    "message": "Update {skill-name}: {description}",
    "content": "{base64-encoded file content}",
    "sha": "{current file SHA if updating, omit if new file}"
  }
```

Steps:
1. GET current file SHA: `GET /repos/cjgraves1119/stratus-sales-toolkit/contents/skills/{path}`
2. Base64-encode new file content
3. PUT with SHA + new content
4. Repeat for plugin.json and README.md if manifest update needed

---

## Frontmatter Rules (Unchanged)

| Rule | Requirement |
|------|-------------|
| **Lowercase only** | Name and description entirely lowercase |
| **Hyphenated versions** | Use `v1-0` not `v1.0` |
| **No angle brackets** | No `<` or `>` in description |
| **Max lengths** | Name: 64 chars, Description: 1024 chars, Body: 500 lines |

---

## Quick Reference

```
CORE CHANGES IN V9:
- Plugin-aware mode: detects folder name changes, triggers manifest update
- Plugin version bump decision tree: patch/minor/major
- marketplace.json + plugin.json ALWAYS bumped together on every push
- .skill file auto-generated after every push for one-click local install
- Updated plugin skills list (v1-7, v28, v9)
- GitHub REST API fallback when Bash unavailable

VERSION COMPARISON (MANDATORY FOR UPDATES):
1. wc -l old/SKILL.md new/SKILL.md  → line count should increase
2. diff old/SKILL.md new/SKILL.md   → only additions, no deletions
3. find old -type f | sort          → all files preserved
4. Display comparison table before deploying
NEVER SKIP THIS STEP.

PLUGIN-AWARE MODE (NEW):
1. Did folder name change? (v1-6 → v1-7 = YES; pharos-iq = NO)
2. If YES: determine bump type (patch/minor/major)
3. Update plugin.json AND marketplace.json: skill name + plugin version (both same version)
4. Update README.md: skills table row
5. rm old folder, cp new folder into plugin

QUICK UPDATE (minor changes):
1. cp -r old-skill new-skill
2. Edit SKILL.md
3. Run version comparison (MANDATORY)
4. PLUGIN SKILLS: SKIP (read-only folder). NON-PLUGIN: cp -r new-skill /mnt/skills/user/
5. Plugin-aware mode check (if plugin skill)
6. GitHub sync (if plugin skill):
   → sub-step 4: zip → .skill file → present_files (BEFORE push)
   → sub-step 5: git commit && push

FULL RELEASE (major changes):
1. Create/update skill folder
2. Run version comparison (MANDATORY if updating)
3. PLUGIN SKILLS: SKIP (read-only folder). NON-PLUGIN: cp -r to /mnt/skills/user/
4. Plugin-aware mode check (if plugin skill)
5. GitHub sync (if plugin skill):
   → sub-step 4: zip → .skill file → present_files (BEFORE push)
   → sub-step 5: git commit && push

GITHUB SYNC:
0. CHECK FOR PAT — if not in preferences, skip to step 4 (local .skill only)
1. git clone/pull the repo
2. rm old skill folder, cp new one into skills/
3. Apply manifest updates (plugin.json + marketplace.json + README.md) if folder name changed
4. zip skill/ → outputs/{skill-name}.skill → present_files (ALWAYS)
5. git add -A && git commit && git push
6. Display sync results table
```

---

## Changelog

### v9 (Current)
- **Plugin-Aware Mode**: Detects when skill folder name changes (version bump) and automatically triggers plugin.json manifest update + plugin version bump + README.md update
- **Plugin version bump decision tree**: Patch for bug fixes, Minor for new features, Major for breaking changes. Requires user confirmation for Minor/Major.
- **Folder name change detection**: Explicit rule — if version number is in folder name and changes, manifest update is required; versionless folder names skip manifest update
- **marketplace.json sync**: `marketplace.json` (repo root) and `plugin.json` (plugin folder) must ALWAYS be bumped to the same version on every push. Missing `marketplace.json` breaks "update available" detection for all team members.
- **.skill file auto-generation**: After every GitHub push (or sync skip), zip the updated skill folder as `{skill-name}.skill` and present with `present_files`. This ensures the skill exists both in the plugin (distributed via GitHub) AND as a standalone local install. Both copies are required for the skill to be accessible with or without the plugin active.
- **PAT guard clause**: Before any git operation, check for a GitHub Classic PAT in Cowork preferences. If not found, skip all GitHub sync steps and display a clear message explaining why. Proceed directly to .skill file generation so the user still gets a local-installable output. This prevents team members who install the plugin from hitting a confusing auth error when trying to create skills — they get local-only mode automatically.
- **Updated plugin skills list**: Reflects current accurate versions (daily-task-engine-v1-7, zoho-crm-v28, skill-creator-v9)
- **GitHub REST API fallback**: Documents how to push files via REST API when Bash/git is unavailable (ENOSPC, EROFS)
- **Plugin-aware summary tables**: Two table formats (folder changed vs. unchanged) for display before commit
- All v8 version comparison logic and GitHub sync workflow retained

### v8
- **GitHub Auto-Sync**: Automatically pushes updated skills to stratus-sales-toolkit repo after deployment
- **Removed .zip/.skill/.docx outputs**: No longer needed since plugin distributes via GitHub
- **Plugin skill list**: 14 skills tracked for auto-sync; local-only skills skip GitHub step
- **Version bump handling**: Instructions for updating plugin.json and README.md when skill versions change
- **Error recovery**: Git push rejection, PAT expiry, merge conflict handling
- All v7 version comparison logic retained

### v7
- **MANDATORY VERSION COMPARISON**: Auto-compare old vs new version before packaging to prevent logic loss
- **5-Step Comparison Checklist**: Line count, file structure, diff analysis, section verification, supporting files
- **Comparison Output Table**: Display results summary before packaging
- **Updated Workflows**: Both Quick Update and Full Release now include comparison step

### v6
- **Optimized workflow**: .skill is just renamed .zip (no duplicate work)
- **DOCX is optional**: Only generate for major releases
- **Quick Update mode**: 2 commands for minor changes

### v5
- DOCX output replaced TXT
- Added Table of Contents, headers/footers

### v4
- Lowercase frontmatter required
- Hyphenated versions
