---
description: Run daily task review, inbox scan, and batch approvals
argument-hint: "[filter: fu30 | overdue | all]"
---

# /daily-tasks

Trigger the daily task engine. Fetch all open Zoho CRM tasks, evaluate each one using parallel sub-agents (Gmail context + deal stage + task type), build a batch approval table with inline email drafts and clickable Zoho/Gmail links, then execute approved actions sequentially.

Arguments: $ARGUMENTS

## What this runs

1. Fetch all open tasks from Zoho CRM (owner = Chris Graves)
2. Launch one sub-agent per task simultaneously — each searches Gmail for last contact, runs the evaluation gate, and drafts any needed email
3. Present a batch approval table with clickable links and full email previews
4. Scan Gmail inbox for untracked action items (runs during user review)
5. Execute approved actions sequentially: send → confirm → close task → create successor

Follow the `daily-task-engine-v1-5` skill exactly. Never batch Zoho and Pipedream calls in the same parallel block.
