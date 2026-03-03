---
name: skill-creator-v8
description: skill creator with mandatory version comparison, github auto-sync to stratus-sales-toolkit repo, and streamlined output (no zip/docx). deploys skill to local folder and pushes to github in one workflow.
---

# Skill Creator v8

Optimized skill creation with **mandatory version comparison** and **automatic GitHub sync** to the stratus-sales-toolkit plugin repo.

## What Changed in v8

| Change | v7 | v8 |
|--------|----|----|
| Packaging | .zip + .skill + optional .docx | Direct folder deploy (no zip/skill/docx) |
| GitHub sync | Manual | Auto-push to stratus-sales-toolkit repo |
| Output location | /mnt/user-data/outputs/ | /mnt/skills/user/ + GitHub |

## GitHub Sync Configuration

```
Repository: github.com/cjgraves1119/stratus-sales-toolkit
Branch: main
Auth: Classic PAT (stored in user preferences, never commit to repo)
Local plugin clone: /home/claude/stratus-sales-toolkit
```

### Plugin Skills (auto-sync enabled)
These 14 skills are part of the stratus-sales-toolkit plugin. When any of these are created or updated, the GitHub sync step runs automatically.

- ccw-subscription-renewal-v1-2
- coterm-calculator-v1-0
- daily-task-engine-v1-4
- erate-proposal-workflow-v1-1
- fu30-followup-automation-v1-3
- pharos-iq-automation
- skill-creator-v8
- stratus-quote-pdf-v2-0
- stratus-quoting-bot-v4-5
- subscription-modification-v2-6
- webex-bots-v1-6
- weborder-to-deal-automation-v1-1
- zoho-crm-email-v3-5
- zoho-crm-v27

**Skills NOT in this list** are local-only and skip the GitHub sync step.

## MANDATORY VERSION COMPARISON

**When updating an existing skill, ALWAYS run version comparison BEFORE deploying.** This prevents accidental deletion of existing logic, which has happened multiple times.

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
cp -r /home/claude/my-skill-v2-3 /mnt/skills/user/my-skill-v2-3

# 5. GitHub Sync (if skill is in plugin list above)
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
cp -r /home/claude/new-version /mnt/skills/user/new-version

# 4. GitHub Sync (if skill is in plugin list above)
# See "GitHub Sync Workflow" section below
```

## GitHub Sync Workflow

**Runs automatically after deploying any skill in the plugin list.** Skip for local-only skills.

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

# Copy new version
cp -r /mnt/skills/user/new-skill-name-vY-Y skills/new-skill-name-vY-Y
```

**Important:** If the skill version changed (e.g., v7 → v8), also update:
- `plugin.json` version field (bump minor: 1.0.0 → 1.1.0)
- `README.md` skills table with new version name and description

### Step 3: Commit and Push

```bash
git add -A
git commit -m "Update {skill-name} to {version}: {brief description of changes}"
git push origin main
```

### Step 4: Verify

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
| Commit | ✓ (abc1234) |
| Push to main | ✓ |
| Plugin repo | github.com/cjgraves1119/stratus-sales-toolkit |
```

### Version Bump Handling

When a skill's version changes (e.g., skill-creator-v7 → skill-creator-v8):

1. Remove old version folder from plugin: `rm -rf skills/skill-creator-v7`
2. Add new version folder: `cp -r ... skills/skill-creator-v8`
3. Update `README.md` skills table with new version
4. Update `plugin.json` version field (bump minor: 1.0.0 → 1.1.0)
5. Update the plugin skills list in THIS skill's SKILL.md to reflect new version name
6. Commit message should note the version bump

### Error Recovery

| Error | Fix |
|-------|-----|
| `git push` rejected | `git pull --rebase origin main` then retry push |
| PAT expired/invalid | Ask user for new classic PAT, update clone URL |
| Merge conflict | Show conflict to user, resolve manually |
| Network error | Retry once, then inform user |

## Frontmatter Rules (Unchanged)

| Rule | Requirement |
|------|-------------|
| **Lowercase only** | Name and description entirely lowercase |
| **Hyphenated versions** | Use `v1-0` not `v1.0` |
| **No angle brackets** | No `<` or `>` in description |
| **Max lengths** | Name: 64 chars, Description: 1024 chars, Body: 500 lines |

## Quick Reference

```
CORE CHANGES IN V8:
- No more .zip or .skill or .docx files
- Deploy directly to /mnt/skills/user/
- Auto-push to GitHub for plugin skills

VERSION COMPARISON (MANDATORY FOR UPDATES):
1. wc -l old/SKILL.md new/SKILL.md  → line count should increase
2. diff old/SKILL.md new/SKILL.md   → only additions, no deletions
3. find old -type f | sort          → all files preserved
4. Display comparison table before deploying
NEVER SKIP THIS STEP.

QUICK UPDATE (minor changes):
1. cp -r old-skill new-skill
2. Edit SKILL.md
3. Run version comparison (MANDATORY)
4. cp -r new-skill /mnt/skills/user/
5. GitHub sync (if plugin skill)

FULL RELEASE (major changes):
1. Create/update skill folder
2. Run version comparison (MANDATORY if updating)
3. cp -r to /mnt/skills/user/
4. GitHub sync (if plugin skill)

GITHUB SYNC:
1. git clone/pull the repo
2. rm old skill folder, cp new one into skills/
3. Update README.md + plugin.json if version bumped
4. git add -A && git commit && git push
5. Display sync results table
```

## Changelog

### v8 (Current)
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
