---
name: skill-downloader-v1-0
description: >-
  bulk export all plugin skills as .skill files for one-click install into standard claude desktop.
  triggers: update skills, download skills, skill update, skill download, get latest skills,
  install skills, sync skills, updateskills, skilldownload, skillupdate.
---

# Skill Downloader v1.0

One-command bulk export of every skill in the stratus-sales-toolkit plugin into `.skill` format for one-click install into a normal Claude desktop session (non-plugin).

## When to Trigger

Any of these phrases:
- `/UpdateSkills`
- `/SkillDownload`
- `/SkillUpdate`
- "update skills", "download skills", "get latest skills", "install skills", "sync skills"

## Workflow

### Step 1: Locate Plugin Skills

```bash
PLUGIN_DIR="/sessions/$(hostname)/mnt/.local-plugins/cache/stratus-sales-toolkit/stratus-sales-toolkit"
# Find the latest version directory
LATEST=$(ls -v "$PLUGIN_DIR" | tail -1)
SKILLS_DIR="$PLUGIN_DIR/$LATEST/skills"
```

If the path doesn't resolve, fall back to globbing:
```bash
SKILLS_DIR=$(find /sessions/*/mnt/.local-plugins/cache/stratus-sales-toolkit -name "skills" -type d 2>/dev/null | head -1)
```

### Step 2: Package Each Skill

For every subdirectory in `$SKILLS_DIR`, create a `.skill` zip archive:

```bash
OUTDIR="/sessions/$(ls /sessions/ | head -1)/mnt/outputs/skill-files"
mkdir -p "$OUTDIR"

cd "$SKILLS_DIR"
for skill_dir in */; do
    skill_name="${skill_dir%/}"
    # Create zip in temp location first, then copy to outputs (avoids permission issues)
    zip -r "/tmp/${skill_name}.skill" "$skill_name/"
    cp "/tmp/${skill_name}.skill" "$OUTDIR/${skill_name}.skill"
done
```

### Step 3: Build Summary Table

After packaging, display a markdown table showing what was exported:

| Skill | Version | File |
|-------|---------|------|
| zoho-crm | v30 | zoho-crm-v30.skill |
| daily-task-engine | v1.8 | daily-task-engine-v1-8.skill |
| ... | ... | ... |

Include the plugin version from plugin.json at the top: **"Stratus Sales Toolkit v1.5.0 — {count} skills exported"**

### Step 4: Present Files

Use the `present_files` MCP tool to render each .skill file as a card with the "Copy to your skills" install button:

```
mcp__cowork__present_files with all .skill file paths
```

### Step 5: Provide computer:// Links

Also provide a direct link to the output folder so the user can grab everything at once:

```
[View all skill files](computer:///sessions/.../mnt/outputs/skill-files/)
```

And individual links for each file:
```
[skill-name.skill](computer:///sessions/.../mnt/outputs/skill-files/skill-name.skill)
```

## Important Notes

- This skill reads from the **plugin cache** (`.local-plugins/cache/`), so it always reflects the currently installed plugin version.
- The `.skill` format is a standard zip archive containing the skill directory (with SKILL.md and any supporting files). Claude desktop's "Copy to your skills" button handles extraction.
- If a skill directory contains subdirectories (like `data/` or `workflows/`), they are included in the zip automatically.
- No GitHub access or PAT required — this works entirely from the local plugin cache.
- Team members on standard Claude desktop (without the plugin) can use these .skill files to get the same capabilities.
