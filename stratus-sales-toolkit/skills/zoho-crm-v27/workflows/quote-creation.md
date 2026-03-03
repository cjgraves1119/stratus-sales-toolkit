# Quote Creation Workflow

## Prerequisites

1. Deal must exist (or create one first using deal-creation workflow)
2. Account must exist with COMPLETE billing address (or will be looked up)
3. Contact should be associated

## REQUIRED FIELDS (MUST BE POPULATED)

### Quote Required Fields
| Field | Required | Default | Action if Missing |
|-------|----------|---------|-------------------|
| Subject | YES | {Account} - {Description} | Auto-generate |
| Deal_Name | YES | - | Create deal first |
| Account_Name | YES | - | Search/Create first |
| Contact_Name | YES | - | Lookup from Account (auto-assign if single contact) |
| Valid_Till | YES | Today + 30 days | Calculate dynamically |
| Cisco_Billing_Term | YES | "Prepaid Term" | Always set to "Prepaid Term" |
| Billing_Street | YES | From Account | Lookup if missing |
| Billing_City | YES | From Account | Lookup if missing |
| Billing_State | YES | From Account | Lookup if missing |
| Billing_Code | YES | From Account | Lookup if missing |
| Billing_Country | YES | "US" | Default to "US" if blank |
| Shipping_Country | YES | "US" | Mirror Billing_Country, default "US" |

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
- Products/services mentioned with quantities
- Timeline or urgency
- Address from email signature (if present)
- Customer's stated need or competitive context

### 2. Verify Account Exists

```
Search: word = "{company name}"
Module: Accounts
Fields: id,Account_Name,Billing_Street,Billing_City,Billing_State,Billing_Code,Billing_Country
```

### 3. Address Lookup (If Account Missing Address)

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

**Step C: Track address source**
- `Account record`
- `Email signature from {sender}`
- `Web search (company HQ)`
- `User provided`

**Step D: Offer to update Account**
If Account had no address and we found one:
> "Would you like me to update the Account record with this address for future quotes?"

### 4. ADDRESS VALIDATION TABLE

**Display before proceeding:**
```
ADDRESS VALIDATION:
| Field | Value | Source | Status |
|-------|-------|--------|--------|
| Billing_Street | 123 Main St | Account | ✓ |
| Billing_City | Chicago | Account | ✓ |
| Billing_State | IL | Account | ✓ |
| Billing_Code | 60601 | Account | ✓ |
| Billing_Country | US | Default | ✓ |
```

If ANY field is ⚠ MISSING (except Country which defaults to US):
→ Ask user: "What's the billing address for {Account}?"

### 5. Verify/Create Contact (REQUIRED)

**Step A: Search Account's Contacts**
```
Search: criteria = "(Account_Name:equals:{account_id})"
Module: Contacts
Fields: id,Full_Name,Email,Account_Name
```

**Step B: Contact Assignment Logic**
- If Account has **ONE contact** → Auto-assign (no prompt needed)
- If Account has **MULTIPLE contacts** → Prompt user: "Found {N} contacts for {Account}. Which should I use? {list names}"
- If Account has **NO contacts** → Prompt user: "No contacts found for {Account}. Please provide contact name and email."

**Step C: Create contact if needed**
If user provides new contact info:
```json
{
  "Last_Name": "{name}",
  "Email": "{email}",
  "Account_Name": {"id": "{account_id}"}
}
```

### 6. Create/Verify Deal

If no deal exists, follow deal-creation workflow FIRST (including Lead_Source, Reason, Deal Note).

If deal exists, verify it has Lead_Source:
```
Module: Deals
Fields: id,Deal_Name,Lead_Source,Stage
```

If Deal.Lead_Source is blank → flag to user: "Note: This deal is missing Lead_Source - consider updating"

### 7. Calculate Valid_Till

```python
from datetime import datetime, timedelta
valid_till = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
```

### 8. PRE-CREATION VALIDATION CHECKPOINT
*Note: Product IDs are NOT looked up at this stage. SKU lookup happens AFTER the quote shell is created (Step 11). This ensures a real Zoho record exists before any SKU resolution is attempted, enabling manual recovery if lookup fails.*

### 9. PRE-CREATION VALIDATION CHECKPOINT

**STOP and display this table before creating the quote:**

```
PRE-CREATION VALIDATION - QUOTE
| Field | Value | Status |
|-------|-------|--------|
| Subject | {value} | ✓ |
| Deal_Name | {value} | ✓ |
| Account_Name | {value} | ✓ |
| Contact_Name | {value} | ✓ REQUIRED |
| Cisco_Billing_Term | Prepaid Term | ✓ |
| Valid_Till | {value} | ✓ |
| Billing_Street | {value} | ✓ |
| Billing_City | {value} | ✓ |
| Billing_State | {value} | ✓ |
| Billing_Code | {value} | ✓ |
| Billing_Country | {value} | ✓ |
| Shipping_Country | US | ✓ |
| Address Source | {Account/Web/Signature} | ✓ |
| Line Items | {count} items | ✓ |
```

**Rules:**
- If ANY address field is blank → STOP and ask user
- If Contact_Name is blank → STOP (lookup or prompt for contact)
- Billing_Country defaults to "US" if blank
- Shipping_Country defaults to "US" (mirrors Billing)
- Cisco_Billing_Term defaults to "Prepaid Term"
- NEVER create quote with incomplete address
- NEVER create quote without Contact_Name

### 10. Create Quote Shell (WITHOUT Line Items)

Create the quote first, without Quoted_Items. This ensures a real Zoho record exists before SKU resolution is attempted.

```json
{
  "Subject": "{Account} - {Description}",
  "Deal_Name": {"id": "{deal_id}"},
  "Account_Name": {"id": "{account_id}"},
  "Contact_Name": {"id": "{contact_id}"},
  "Valid_Till": "{calculated_date}",
  "Quote_Stage": "Draft",
  "Cisco_Billing_Term": "Prepaid Term",
  "Billing_Street": "{street - REQUIRED}",
  "Billing_City": "{city - REQUIRED}",
  "Billing_State": "{state - REQUIRED}",
  "Billing_Code": "{zip - REQUIRED}",
  "Billing_Country": "US",
  "Shipping_Country": "US"
}
```

If this call fails, stop and report error. If it succeeds, proceed to SKU lookup.

### 11. Batch SKU Lookup (AFTER Shell Created)

Look up ALL SKUs in a single API call using OR criteria:

```
Module: Products
Criteria: (Product_Code:equals:SKU1)OR(Product_Code:equals:SKU2)OR(Product_Code:equals:SKU3)
Fields: id,Product_Code,Product_Name
```

**Variant Fallback Logic:**
- If any SKU returns no result, automatically retry with alternate suffix (-3Y vs -3YR, etc.)
- Common variants to try: append or strip trailing R, swap Y for YR

**After lookup, Update the Quote with Quoted_Items:**

```json
{
  "data": [{
    "id": "{quote_id}",
    "Quoted_Items": [
      {"Product_Name": {"id": "{product_id_1}"}, "Quantity": {qty}},
      {"Product_Name": {"id": "{product_id_2}"}, "Quantity": {qty}}
    ]
  }]
}
```

**If SKU lookup fails entirely:**
- Report which SKUs could not be resolved
- Provide the Quote URL so line items can be added manually in Zoho
- Do NOT delete the quote shell

### 13. Create Claude Reference Note (REQUIRED)

**After quote is successfully created, add a Note with the Claude conversation URL:**

```json
{
  "data": [{
    "Note_Title": "Claude Reference",
    "Note_Content": "Quote created via Claude: https://claude.ai/chat/{conversation_id}",
    "Parent_Id": {
      "id": "{quote_id}",
      "module": {"api_name": "Quotes"}
    }
  }]
}
```

**Purpose:** Traceability back to the conversation for context, decisions, and special instructions.

### 14. Create Follow-up Task (if new deal was created)
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

### 15. Return URLs and Address Source Note

```
Deal: https://crm.zoho.com/crm/org647122552/tab/Deals/{deal_id}
Quote: https://crm.zoho.com/crm/org647122552/tab/Quotes/{quote_id}
```

**Also notify user about address source:**
- "Address copied from Account record"
- "Address found in email signature from {sender}"
- "Address found via web search (company HQ) - please validate if needed"

**If Account was missing address:**
> "Would you like me to update the Account record with this address for future quotes?"

## Address Handling Scenarios

**Scenario 1: Account has complete address**
→ Copy all 5 fields to quote
→ Note: "Address copied from Account record"

**Scenario 2: Account missing address, found in email signature**
→ Use signature address
→ Note: "Address found in email signature"
→ Ask: "Update Account with this address?"

**Scenario 3: Account missing address, web search successful**
→ Use HQ address from web search
→ Note: "Address found via web search (company HQ) - please validate"
→ Ask: "Update Account with this address?"

**Scenario 4: International HQ found**
→ Ask: "Company HQ is in {country}. Is there a US office to use instead?"
→ If yes → search for US office
→ If no → use international address with proper country code

**Scenario 5: Conflicting addresses (Account vs signature)**
→ Prompt: "Account has {Account address}, but email signature shows {signature address}. Which should I use?"

**Scenario 6: No address found anywhere**
→ Prompt user: "What's the billing address for {Account}?"

## Multi-Option Quotes

When user requests multiple term options (1yr, 3yr, 5yr):
1. Create individual quote for each option
2. Create master quote containing all options
3. Name format: "{Account} - {Term} Option"

## Cloning Quotes

Use `ZohoCRM_Clone_Record` then modify:
```
Module: Quotes
ID: {source_quote_id}
```

After cloning, update Subject and line items as needed.

## NEVER DO

- Create quote with blank Billing_Street
- Create quote with blank Billing_City
- Create quote with blank Billing_State
- Create quote with blank Billing_Code
- Create quote with blank Billing_Country
- Create quote with blank Shipping_Country
- Create quote without Contact_Name
- Create quote with blank Cisco_Billing_Term
- Use "United States" instead of "US"
- Skip validation checkpoint
- Create quote without a Deal
- Skip address lookup when Account missing address
- Use international address without asking about US office
- Ignore conflicting addresses without prompting user
- Skip contact lookup/assignment
- Skip creating Claude Reference Note
