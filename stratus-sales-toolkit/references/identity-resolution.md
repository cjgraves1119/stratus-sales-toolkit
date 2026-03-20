# Identity Resolution Reference

All skills in the Stratus Sales Toolkit resolve the current user's identity dynamically at runtime. No skill hardcodes a specific person's name, email, or Zoho ID.

## Identity Variables

### USER_NAME and USER_EMAIL

Every Claude session includes a `<user>` block in the system prompt containing the current user's full name and email address. Read these directly — no lookup required.

Use USER_NAME for: email signatures, display names, quote rep fields, task owner labels.
Use USER_EMAIL for: Pipedream `from` address, Zoho CRM mail `from` field, reply-all exclusions, Gmail search context.

### ZOHO_OWNER_ID

The current user's Zoho CRM numeric user ID. Used in task/deal query filters (`Owner:equals:{ZOHO_OWNER_ID}`), record creation payloads (`"Owner": {"id": "{ZOHO_OWNER_ID}"}`), and successor task creation.

**Resolution order:**

1. Check CLAUDE.md for a line: `ZOHO_OWNER_ID: 2570562000XXXXXXXXX`
2. If not found, call the Zoho CRM API:
   ```
   ZohoCRM_getRecords(module="Users", type="CurrentUser")
   ```
   Extract the `id` field from the response.
3. If the API call succeeds, prompt the user to cache it:
   > Add this to your CLAUDE.md: `ZOHO_OWNER_ID: {resolved_id}`

**If ZOHO_OWNER_ID cannot be resolved**, display this before proceeding:

```
⚠️ SETUP NEEDED — Zoho Owner ID not found

Your Zoho CRM Owner ID isn't configured yet. Add this line to your CLAUDE.md:
  ZOHO_OWNER_ID: [your ID]

To find it: run "check my setup" and it will auto-detect and display your ID.
```

## Stratus-Wide Constants (do not change per user)

These values are the same for all Stratus Information Systems team members:

| Constant | Value | Usage |
|----------|-------|-------|
| ZOHO_ORG_ID | `org647122552` | Zoho CRM URL base path |
| STRATUS_SALES_ID | `2570562000027286729` | Default Meraki_ISR when no Cisco rep is assigned |

These are org-level constants, not personal settings.

## Quick Reference

| Variable | Source | Example |
|----------|--------|---------|
| USER_NAME | `<user>` block in system prompt | "Jordan Smith" |
| USER_EMAIL | `<user>` block in system prompt | "jordans@stratusinfosystems.com" |
| ZOHO_OWNER_ID | CLAUDE.md → Zoho API fallback | "2570562000999999999" |
| ZOHO_ORG_ID | Constant: `org647122552` | org647122552 |
| STRATUS_SALES_ID | Constant: `2570562000027286729` | 2570562000027286729 |
