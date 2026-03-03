---
name: skill-creator-v7
description: "skill creator with mandatory version comparison to prevent logic loss. .skill is renamed .zip. docx optional for major releases. auto-validates no content deleted."
---

# Skill Creator v7

Optimized skill creation with **mandatory version comparison** to prevent accidental logic loss.

## Key Optimization: .skill = .zip

**The .skill file is just a renamed .zip file.** No separate creation needed.

```bash
zip -r my-skill-v1-0.zip my-skill-v1-0/
cp my-skill-v1-0.zip my-skill-v1-0.skill  # Instant copy
```

## MANDATORY VERSION COMPARISON (NEW IN V7)

**When updating an existing skill, ALWAYS run version comparison BEFORE packaging.** This prevents accidental deletion of existing logic, which has happened multiple times.

### When to Run
- Every skill update (not new skills)
- Before final packaging
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

Display this summary before packaging:

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

## Output Tiers

### Quick Update (Minor Changes)
For typo fixes, small tweaks, minor additions:

**Required:**
- `skill-name-vX-X.zip` - Package the folder
- `skill-name-vX-X.skill` - Copy of .zip (renamed)

**Skip:** DOCX reference (not needed for minor updates)

```bash
# Quick update workflow - 2 commands total
zip -r skill-v2-3.zip skill-v2-3/
cp skill-v2-3.zip skill-v2-3.skill
```

### Full Release (Major Changes)
For new skills, major rewrites, or when user requests documentation:

**Required:**
- `skill-name-vX-X.zip`
- `skill-name-vX-X.skill` (copy of .zip)
- `skill-name-vX-X.docx` - Professional reference document

## Quick Update Workflow

```bash
# 1. Copy existing skill, bump version
cp -r /mnt/skills/user/my-skill-v2-2 /home/claude/my-skill-v2-3

# 2. Edit SKILL.md (update version in frontmatter + make changes)

# 3. RUN VERSION COMPARISON (MANDATORY)
wc -l /mnt/skills/user/my-skill-v2-2/SKILL.md /home/claude/my-skill-v2-3/SKILL.md
diff /mnt/skills/user/my-skill-v2-2/SKILL.md /home/claude/my-skill-v2-3/SKILL.md | head -50
# Verify: line count equal or higher, no unexpected deletions

# 4. Package (2 commands)
cd /home/claude
zip -r my-skill-v2-3.zip my-skill-v2-3/
cp my-skill-v2-3.zip my-skill-v2-3.skill

# 5. Output
cp my-skill-v2-3.zip my-skill-v2-3.skill /mnt/user-data/outputs/
```

**CRITICAL: Never skip step 3. Version comparison prevents accidental logic loss.**

## Full Release Workflow

```bash
# 1. Create/update skill folder with SKILL.md

# 2. RUN VERSION COMPARISON (if updating existing skill)
wc -l /mnt/skills/user/old-version/SKILL.md /home/claude/new-version/SKILL.md
diff /mnt/skills/user/old-version/SKILL.md /home/claude/new-version/SKILL.md
find /mnt/skills/user/old-version -type f | sort
find /home/claude/new-version -type f | sort
# Display comparison results table before proceeding

# 3. Package zip and skill
cd /home/claude
zip -r my-skill-v1-0.zip my-skill-v1-0/
cp my-skill-v1-0.zip my-skill-v1-0.skill

# 4. Generate DOCX (only for full releases)
node generate-docx.js my-skill-v1-0

# 5. Output all three
cp my-skill-v1-0.zip my-skill-v1-0.skill my-skill-v1-0.docx /mnt/user-data/outputs/
```

## When to Use Each Workflow

| Scenario | Workflow | Outputs |
|----------|----------|---------|
| Typo fix | Quick Update | .zip, .skill |
| Add one product ID | Quick Update | .zip, .skill |
| Update a few lines | Quick Update | .zip, .skill |
| New skill | Full Release | .zip, .skill, .docx |
| Major rewrite | Full Release | .zip, .skill, .docx |
| User requests docs | Full Release | .zip, .skill, .docx |

## DOCX Generation (When Needed)

Only generate DOCX for full releases. Use docx-js:

```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
        TableOfContents, Header, Footer, PageNumber, ShadingType, BorderStyle } = require('docx');
const fs = require('fs');

const skillFolder = process.argv[2] || 'skill-folder';
const skillContent = fs.readFileSync(`${skillFolder}/SKILL.md`, 'utf8');
const lines = skillContent.split('\n');

// Parse frontmatter
let skillName = skillFolder;
let skillDescription = '';
let inFrontmatter = false;
let contentStart = 0;

for (let i = 0; i < lines.length; i++) {
  if (lines[i].trim() === '---') {
    inFrontmatter ? (contentStart = i + 1, inFrontmatter = false) : (inFrontmatter = true);
  } else if (inFrontmatter) {
    if (lines[i].startsWith('name:')) skillName = lines[i].replace('name:', '').trim();
    if (lines[i].startsWith('description:')) skillDescription = lines[i].replace('description:', '').trim().replace(/^["']|["']$/g, '');
  }
  if (contentStart) break;
}

// Build document content
const children = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: skillName.toUpperCase(), bold: true })] }),
  new Paragraph({ spacing: { before: 200, after: 400 }, children: [new TextRun({ text: skillDescription, italics: true, size: 24 })] }),
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Table of Contents")] }),
  new TableOfContents("TOC", { hyperlink: true, headingStyleRange: "1-3" }),
  new Paragraph({ children: [] })
];

let inCodeBlock = false, codeLines = [], sectionCount = 0;

for (let i = contentStart; i < lines.length; i++) {
  const line = lines[i];
  
  if (line.startsWith('```')) {
    if (inCodeBlock) {
      children.push(new Paragraph({
        spacing: { before: 100, after: 100 },
        shading: { fill: "F8F8F8", type: ShadingType.CLEAR },
        children: [new TextRun({ text: codeLines.join('\n'), font: "Courier New", size: 18 })]
      }));
      codeLines = [];
    }
    inCodeBlock = !inCodeBlock;
    continue;
  }
  
  if (inCodeBlock) { codeLines.push(line); continue; }
  
  if (line.startsWith('# ')) {
    sectionCount++;
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: sectionCount > 1,
      children: [new TextRun(line.slice(2))] }));
  } else if (line.startsWith('## ')) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(line.slice(3))] }));
  } else if (line.startsWith('### ')) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(line.slice(4))] }));
  } else if (line.trim() === '') {
    children.push(new Paragraph({ children: [] }));
  } else if (line.startsWith('- ') || line.startsWith('* ')) {
    children.push(new Paragraph({ indent: { left: 360 }, children: [new TextRun("• " + line.replace(/^[-*]\s+/, ''))] }));
  } else if (line.trim()) {
    const textRuns = [];
    line.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/).forEach(part => {
      if (part.startsWith('**') && part.endsWith('**')) textRuns.push(new TextRun({ text: part.slice(2, -2), bold: true }));
      else if (part.startsWith('*') && part.endsWith('*')) textRuns.push(new TextRun({ text: part.slice(1, -1), italics: true }));
      else if (part.startsWith('`') && part.endsWith('`')) textRuns.push(new TextRun({ text: part.slice(1, -1), font: "Courier New", size: 22 }));
      else if (part) textRuns.push(new TextRun(part));
    });
    if (textRuns.length) children.push(new Paragraph({ children: textRuns }));
  }
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { size: 48, bold: true, color: "2E74B5" }, paragraph: { alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", run: { size: 32, bold: true, color: "2E74B5" }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", run: { size: 28, bold: true, color: "404040" }, paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", run: { size: 24, bold: true, color: "404040" }, paragraph: { spacing: { before: 200, after: 60 }, outlineLevel: 2 } }
    ]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: skillName, italics: true, size: 20, color: "808080" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Page ", size: 20 }), new TextRun({ children: [PageNumber.CURRENT], size: 20 }), new TextRun({ text: " of ", size: 20 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20 })] })] }) },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(`${skillName}.docx`, buffer);
  console.log(`Created ${skillName}.docx`);
});
```

Save as `generate-docx.js` and run: `node generate-docx.js skill-folder-name`

## Frontmatter Rules (Unchanged)

| Rule | Requirement |
|------|-------------|
| **Lowercase only** | Name and description entirely lowercase |
| **Hyphenated versions** | Use `v1-0` not `v1.0` |
| **No angle brackets** | No `<` or `>` in description |
| **Max lengths** | Name: 64 chars, Description: 1024 chars, Body: 500 lines |

## Quick Reference

```
CORE INSIGHT:
.skill = .zip (just renamed)

VERSION COMPARISON (MANDATORY FOR UPDATES):
1. wc -l old/SKILL.md new/SKILL.md  → line count should increase
2. diff old/SKILL.md new/SKILL.md   → only additions, no deletions
3. find old -type f | sort          → all files preserved
4. Display comparison table before packaging
NEVER SKIP THIS STEP.

QUICK UPDATE (minor changes):
1. cp -r old-skill new-skill
2. Edit SKILL.md
3. Run version comparison (MANDATORY)
4. zip -r skill-v2-3.zip skill-v2-3/
5. cp skill-v2-3.zip skill-v2-3.skill

FULL RELEASE (major changes):
1. Create/update skill folder
2. Run version comparison (MANDATORY if updating)
3. zip + cp to .skill
4. node generate-docx.js skill-folder
# Outputs: .zip, .skill, .docx

WHEN TO SKIP DOCX:
• Typo fixes
• Adding a few lines
• Small corrections
• Version bumps with minor changes

WHEN TO INCLUDE DOCX:
• New skill creation
• Major rewrites
• User explicitly requests it
• Public/shared skills
```

## Changelog

### v7 (Current)
- **MANDATORY VERSION COMPARISON**: Auto-compare old vs new version before packaging to prevent logic loss
- **5-Step Comparison Checklist**: Line count, file structure, diff analysis, section verification, supporting files
- **Comparison Output Table**: Display results summary before packaging
- **Updated Workflows**: Both Quick Update and Full Release now include comparison step
- All v6 features retained

### v6
- **Optimized workflow**: .skill is just renamed .zip (no duplicate work)
- **DOCX is optional**: Only generate for major releases
- **Quick Update mode**: 2 commands for minor changes
- **Compressed DOCX script**: Single file, ~60 lines

### v5
- DOCX output replaced TXT
- Added Table of Contents, headers/footers

### v4
- Lowercase frontmatter required
- Hyphenated versions
