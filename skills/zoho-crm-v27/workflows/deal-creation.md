# Deal Creation Workflow

## When to Use

- User says "create deal for..."
- User says "new opportunity for..."
- User references a customer without existing deal
- User shares screenshot of email requesting quote

## REQUIRED FIELDS (MUST COLLECT BEFORE CREATION)

| Field | Required | Default | Action if Missing |
|-------|----------|---------|-------------------|
| Deal_Name | YES | {Account} - {Description} | Auto-generate |
| Account_Name | YES | - | Search/Create first |
| Lead_Source | YES | **NONE** | **PROMPT USER** |
| Stage | YES | Qualification | Use default |
| Closing_Date | YES | Today + 30 days | Calculate |
| Reason | CONDITIONAL | Meraki ISR recommended | Auto-set when Lead_Source = ISR |
| Meraki_ISR | CONDITIONAL | **NONE** | **PROMPT USER** when Lead_Source = ISR |

## Step-by-Step Process

### 1. If Screenshot/Email Referenced → Get Full Context

**Extract identifiers from screenshot:**
- Sender name or email address
- Subject line (if visible)
- Date/time
- Any unique phrases from email body

**Search Gmail:**
```
search_gmail_messages with q = "from:{sender} {subject keywords}"
```

**Read full thread:**
```
read_gmail_thread with thread_id = {found_thread_id}
```

**Extract from thread:**
- Full customer request details
- Products/services mentioned
- Timeline or urgency
- Address from email signature (if present)
- Customer's stated need or competitive context
- Save Gmail thread URL for Deal Note

### 2. Collect Required Information

Before doing ANY Zoho lookups, ensure you have:

1. Company/Account name
2. Lead Source (ask if not provided)
3. If ISR/ADR referral → rep name
4. Brief description of opportunity
5. Context from email (if available)

**If Lead Source is not provided, STOP and ask:**
> "What's the source of this opportunity? Options: Meraki ISR Referal, Meraki ADR Referal, VDC, Stratus Referal, Website, or Cisco ISR"

### 3. Check for Existing Account
```
Module: Accounts
Search: word = "{company name}"
Fields: id,Account_Name,Billing_Street,Billing_City,Billing_State,Billing_Code,Billing_Country
```

### 4. Address Lookup (If Account Missing Address)

**Sequence:**

**Step A: Check if address found in Gmail signature**
- If email thread was read, check for address in signature
- Compare with Account address:
  - If Account has address → use Account (default)
  - If Account has address AND signature differs → prompt user which to use
  - If Account has NO address → use signature address

**Step B: Web search for company HQ**
```
Web search: "{Company Name} headquarters address"
OR
Web search: "{email domain} company headquarters"
```

**Web search rules:**
- Single confident address found → use it, note source to user
- Multiple locations found → default to HQ
- International HQ → ask: "Company HQ is in {country}. Is there a US office to use instead?"
- No address found → prompt user manually

**Step C: Note the address source**
Track where address came from:
- `Account record`
- `Email signature from {sender}`
- `Web search (company HQ)`
- `User provided`

### 5. Check for Existing Deal (Avoid Duplicates)
```
Module: Deals
Search: word = "{company name}"
Fields: id,Deal_Name,Stage,Amount
Filter: Owner = Chris Graves (2570562000141711002)
```

If similar deal exists in active stage, confirm with user before creating duplicate.

### 6. Create Account (if needed)
```json
{
  "Account_Name": "{Company Name}",
  "Billing_Street": "{street}",
  "Billing_City": "{city}",
  "Billing_State": "{state}",
  "Billing_Code": "{zip}",
  "Billing_Country": "US"
}
```

**If Account existed without address and we found one:**
> "Would you like me to update the Account record with this address for future quotes?"

### 7. Create/Find Contact (if needed)
```json
{
  "First_Name": "{first}",
  "Last_Name": "{last}",
  "Email": "{email}",
  "Account_Name": {"id": "{account_id}"}
}
```

### 8. PRE-CREATION VALIDATION CHECKPOINT

**STOP and display this table before creating the deal:**

```
PRE-CREATION VALIDATION - DEAL
| Field | Value | Status |
|-------|-------|--------|
| Deal_Name | {value} | ✓ |
| Account_Name | {value} | ✓ |
| Lead_Source | {value} | ✓ or ⚠ PROMPT |
| Stage | {value} | ✓ |
| Closing_Date | {value} | ✓ |
| Reason | {value} | ✓ or N/A |
| Meraki_ISR | {value} | ✓ or ⚠ PROMPT or N/A |
| Address | {value} | ✓ ({source}) |
```

**Rules:**
- If Lead_Source shows ⚠ PROMPT → ask user before proceeding
- If Lead_Source = ISR referral and Meraki_ISR shows ⚠ PROMPT → ask for rep name
- NEVER proceed with blank required fields

### 9. Create Deal

**For ISR Referral deals:**
```json
{
  "Deal_Name": "{Account} - {Brief Description}",
  "Account_Name": {"id": "{account_id}"},
  "Contact_Name": {"id": "{contact_id}"},
  "Stage": "Qualification",
  "Lead_Source": "Meraki ISR Referal",
  "Reason": "Meraki ISR recommended",
  "Meraki_ISR": {"id": "{rep_zoho_id}"},
  "Closing_Date": "{30 days out}",
  "Amount": 0
}
```

**For non-ISR deals:**
```json
{
  "Deal_Name": "{Account} - {Brief Description}",
  "Account_Name": {"id": "{account_id}"},
  "Contact_Name": {"id": "{contact_id}"},
  "Stage": "Qualification",
  "Lead_Source": "{selected option}",
  "Closing_Date": "{30 days out}",
  "Amount": 0
}
```

### 10. Create Deal Note (NEW DEALS ONLY)

**Note Format:**
```
Source: {source description}
Request: {brief description of products/services, quantities, terms}
Context: {customer's stated need, competitive situation, timeline}
Address Source: {where address came from}
Gmail Thread: {URL if available}
```

**Example Note Content:**
```
Source: Email from matt.wiegert@bisonequities.com (01/13/26)
Request: 100-user Secure Access quote, 3-year term
Context: Customer evaluating Cisco Secure Access vs Zscaler. Needs competitive pricing for Q1 budget approval. Timeline: decision by end of January.
Address Source: Web search (company HQ in Milwaukee, WI)
Gmail Thread: https://mail.google.com/mail/u/0/#inbox/{thread_id}
```

**API Call:**
```json
{
  "data": [{
    "Note_Title": "Deal Summary",
    "Note_Content": "{formatted note}",
    "Parent_Id": {
      "id": "{deal_id}",
      "module": {"api_name": "Deals"}
    }
  }]
}
```

### 11. Create Follow-up Task
```json
{
  "Subject": "Follow up - {Deal_Name}",
  "Due_Date": "{7 days out}",
  "Status": "Not Started",
  "What_Id": {"id": "{deal_id}"},
  "$se_module": "Deals",
  "Who_Id": {"id": "{contact_id}"}
}
```

### 12. Return URLs and Summary

```
Account: https://crm.zoho.com/crm/org647122552/tab/Accounts/{account_id}
Contact: https://crm.zoho.com/crm/org647122552/tab/Contacts/{contact_id}
Deal: https://crm.zoho.com/crm/org647122552/tab/Deals/{deal_id}
Task: https://crm.zoho.com/crm/org647122552/tab/Tasks/{task_id}
```

**Also notify user:**
- Address source (if looked up): "Address found via web search (company HQ) - please validate if needed"
- If Account was updated: "Updated Account with new address"

## Lead Source Options (USE EXACTLY AS SHOWN)

- `-None-` (only if explicitly told to leave blank)
- `Meraki ISR Referal` (note: one R)
- `Meraki ADR Referal`
- `VDC`
- `Stratus Referal`
- `Website`
- `Cisco ISR`

## Reason Options (USE EXACTLY AS SHOWN)

- `-None-`
- `Does not have reseller`
- `Needs new reseller`
- `Needs competitive quote`
- `Needs faster response`
- `Needs a specialist`
- `MSP Consultant needs reseller`
- `Meraki ISR recommended`

## Conditional Logic

```
IF Lead_Source = "Meraki ISR Referal":
    → Reason = "Meraki ISR recommended" (auto-set, do not prompt)
    → Meraki_ISR = REQUIRED (prompt: "Which Cisco rep referred this deal?")
    → Use cisco-rep-locator skill to find rep's Zoho ID
    
IF Lead_Source = "Meraki ADR Referal":
    → Meraki_ADR = REQUIRED (prompt: "Which ADR referred this deal?")
    
IF Lead_Source = "Cisco ISR":
    → Meraki_ISR = REQUIRED (prompt: "Which Cisco rep is involved?")
    
IF Lead_Source = "Stratus Referal", "VDC", or "Website":
    → Reason = "-None-" (no reason needed)
    → No rep lookup needed
```

## Deal Stages

| Stage | When to Use |
|-------|-------------|
| Qualification | Initial inquiry, needs assessment |
| Quote Sent to Customer | Quote delivered, awaiting response |
| Proposal/Negotiation | Active discussions, pricing adjustments |
| Verbal Commit/Invoicing | Customer committed, awaiting PO |
| Closed Won | PO received |
| Closed Lost | Opportunity lost |

## Common Scenarios

**Scenario 1: User shares screenshot of email**
→ Extract sender, subject, phrases from screenshot
→ Search Gmail for full thread
→ Extract request details, check signature for address
→ Create deal with full context in Note
→ Include Gmail thread link in Note

**Scenario 2: User says "Create deal for ABC Company"**
→ Ask: "What's the source of this deal?"
→ Check Account for address, web search if missing
→ Note address source

**Scenario 3: User says "New ISR deal from Mike Smith for XYZ Corp"**
→ Lead_Source = "Meraki ISR Referal"
→ Reason = "Meraki ISR recommended" (auto-set)
→ Use cisco-rep-locator to find Mike Smith's Zoho ID
→ Set Meraki_ISR field

**Scenario 4: International company detected**
→ Ask: "Company HQ is in {country}. Is there a US office to use instead?"

## NEVER DO

- Leave Lead_Source blank
- Create records without showing validation checkpoint
- Create new dropdown values (use existing only)
- Assume Lead_Source without asking
- Skip the Meraki_ISR lookup when it's an ISR referral
- Use "Referral" spelling (correct is "Referal" with one R)
- Skip Deal Note creation on new deals
- Skip address lookup when Account missing address
- Use international address without asking about US office
