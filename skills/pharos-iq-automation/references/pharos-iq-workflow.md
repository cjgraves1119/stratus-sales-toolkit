# Pharos IQ Automation Workflow

Complete step-by-step workflow for converting Pharos IQ leads into Zoho CRM deals and quotes.

## Input Format

When providing a Pharos IQ lead, use this format:

```
Create a Pharos IQ quote for [Contact Name]

Company: [Account Name]
Title: [Contact Title]
Email: [Email Address]
Phone: [Phone Number]

Opportunity Type: [Collaboration/Networking/Security]
Key details: [What they need]
Timeline: [When they need it]
Budget: [If mentioned]
Competing solutions: [If mentioned]
```

**Minimal input:**
```
Create Pharos IQ quote for John Smith at Acme Corp
Notes: Interested in wireless network upgrade, need quote ASAP
```

## Execution Steps

### Step 1: Parse and Validate Lead Information

**Extract from PharosIQ notes:**
- Contact name ✓
- Company/Account name ✓
- Email and phone (if available) ✓
- Opportunity type (Collaboration/Networking/Security) ✓
- Key business drivers ✓
- Timeline hints ✓
- Budget indicators ✓

**Classify opportunity:**
Use keywords to determine primary team routing:
- See references/team-routing.md for keyword mapping

**Ask for clarification if:**
- Opportunity type unclear (multiple categories mentioned)
- Contact name or company name missing
- No timeline indicators given

---

### Step 2: Search/Create Account and Contact Records in Zoho

#### Account Lookup

```
Search Zoho Accounts module:
  - Search by Account Name (from PharosIQ)
  - If found: Use existing record
  - If not found: Create new Account record
```

**If creating new Account, use fields from references/field-defaults.md:**
- Account Name (required)
- Billing City, State (if available)
- Billing Country (default: USA)
- Industry (optional; infer from opportunity type)

#### Contact Lookup

```
Search Zoho Contacts module:
  - Search by email first (from PharosIQ)
  - If not found, search by name
  - If found: Use existing record
  - If not found: Create new Contact record
```

**If creating new Contact, use fields from references/field-defaults.md:**
- Full Name (required)
- Email (required)
- Account Name (link to Account from Step 2)
- Phone (optional)
- Title (optional)

---

### Step 3: Create Deal in Zoho

**Create Deal record with:**

| Field | Value |
|-------|-------|
| Deal Name | `[Account Name] - [Opportunity Type/Summary]` |
| Account | Link from Step 2 |
| Contact Name | Link from Step 2 |
| Amount | $0 |
| Stage | Qualification |
| Lead Source | **PharosIQ** |
| Close Date | Today + 30 days (or timeline from notes) |
| Description | PharosIQ notes/context |

**Full field mapping:** See references/field-defaults.md

**Result:** New Deal created. Note the Deal ID for the Quote link.

---

### Step 4: Create Quote in Zoho

**Create Quote record with:**

| Field | Value |
|-------|-------|
| Quote Name | `[Account] - [Product Category]` |
| Related Deal | Link to Deal from Step 3 |
| Quote Stage | Quoted |
| Valid Until | Today + 30 days |

**Add Quote Line Items (with real list pricing):**

1. Determine product from references/team-routing.md based on opportunity type
2. Extract quantity estimate from PharosIQ notes if available (e.g., "25 access points", "10 phones", "50 users")
3. If no quantity mentioned, use **default quantity of 10**
4. Add line item with:
   - Product: Team-appropriate product (see team-routing.md)
   - Qty: Extracted from notes or default to 10
   - Unit Price: Use list price automatically associated with the SKU
   - Description: "[Product] for [Opportunity Type]"
5. Total quote amount will be calculated automatically from qty × unit price

**Full field mapping:** See references/field-defaults.md

**Result:** New Quote created linked to Deal.

---

### Step 5: Create Follow-up Task

**Create Task record with:**

| Field | Value |
|-------|-------|
| Task Title | `Follow up: [Account] - [Opportunity Type]` |
| Related To | Deal from Step 3 |
| Due Date | Today + 5 business days |
| Priority | High |
| Activity Type | Call or Email |
| Description | Brief context: "Confirm [Opportunity Type] requirements and timeline for [Account]" |

**Full field mapping:** See references/field-defaults.md

**Result:** Task scheduled for team follow-up.

---

### Step 6: Search Gmail & Google Calendar for Existing Meetings

**Search Gmail for customer contact:**
```
Search Gmail for:
  - Customer company name
  - Customer contact name
  - Customer email address
```

**Search Google Calendar for meetings:**
```
Search Calendar for:
  - Customer company name
  - Customer contact name
  - Time range: Past 3 months to next 3 months
```

**If meeting found:**
- Note meeting date/time
- Include calendar invite link in results
- Update Task description if follow-up already scheduled in calendar

**If no meeting found:**
- Note in results: "No prior meetings found"
- This is normal for new PharosIQ leads

---

### Step 7: Confirm and Provide Results

### Step 7: Confirm and Provide Results

Return structured information:

```
✓ Pharos IQ Lead Processed

ACCOUNT:
  Name: [Account Name]
  Link: [Zoho account link]

CONTACT:
  Name: [Contact Name]
  Email: [Email]
  Link: [Zoho contact link]

DEAL:
  Name: [Deal Name]
  Amount: [Calculated from products/quantities]
  Stage: Qualification
  Close Date: [Date]
  Link: [Zoho deal link]

QUOTE:
  Name: [Quote Name]
  Products: [Product name] (qty [quantity]) @ [list price]
  Total: [Calculated amount]
  Valid Through: [Date]
  Link: [Zoho quote link]

PRIOR MEETINGS:
  [None found] OR
  Date: [Meeting date/time]
  Subject: [Meeting subject if available]
  Calendar Link: [Link to calendar invite]

NEXT STEPS:
  - [Specific Cisco team] to gather detailed requirements
  - Follow-up call: [Due date from task]
  - [If meeting found: "Next scheduled meeting: [date/time]"]
```

---

## Special Cases

### Multiple Opportunities at Same Company

If same Account has multiple opportunities (e.g., both Networking and Security needs):

1. **Create separate deals:**
   - Deal A: Company - Networking Opportunity
   - Deal B: Company - Security Opportunity

2. **Create separate quotes:**
   - Quote A: Linked to Networking deal
   - Quote B: Linked to Security deal

3. **Create one overarching task:**
   - "Comprehensive infrastructure assessment for [Company]"
   - Link to both deals
   - Coordinate both teams

### International Customers

If PharosIQ lead indicates non-US customer:

1. Set Account Billing Country appropriately
2. Note in Deal description (timezone, region, compliance needs)
3. Flag for team to route through regional sales channel

### Highly Urgent Leads

If PharosIQ notes indicate urgent/hot lead:

1. Create with tighter timeline (close date = 14 days instead of 30)
2. Set Task due date = 1-2 business days (not 5)
3. Set Task priority = Urgent instead of High
4. Note urgency in Task description for team awareness

---

## Quality Checks Before Submitting

✓ Account name recorded accurately  
✓ Contact name matches PharosIQ source  
✓ Opportunity type clearly identified (Collab/Network/Security)  
✓ Deal Stage = Qualification  
✓ Lead Source = PharosIQ (not missed/blank)  
✓ Quote linked to Deal  
✓ Quote includes placeholder product from correct team  
✓ Follow-up task scheduled within 5 business days  
✓ All records accessible via Zoho links  

---

## Common Issues and Resolutions

### Issue: Contact exists but at different company
**Resolution:** Create new contact record (don't reuse old contact)

### Issue: Unclear whether Networking or Collaboration
**Resolution:** Ask "Is this primarily about wireless/switching (Networking) or calling/meetings (Collaboration)?"

### Issue: PharosIQ notes have only company name, no contact
**Resolution:** Create Account, note in Deal description that specific contact needs confirmation, mark Task as "Confirm contact information"

### Issue: Customer wants product/pricing immediately
**Resolution:** Send placeholder quote immediately to show responsiveness, note "Real pricing coming after requirements gathering" in quote description

### Issue: Deal or Quote not showing in Zoho
**Resolution:** Check filters (may be hidden by default) or wait 30 seconds for indexing

---

