---
name: pharos-iq-automation
description: Automates creation of Zoho CRM quotes and deals from Pharos IQ leads. Parses PharosIQ contact information, creates Deals with PharosIQ lead source, generates placeholder quotes routed to appropriate Cisco teams (Collaboration/Networking/Security), creates follow-up tasks, and manages account/contact records. Streamlines the workflow for converting PharosIQ leads into tracked sales opportunities.
---

# Pharos IQ Automation Skill

Automate the process of converting Pharos IQ leads into Zoho CRM deals and quotes with intelligent team routing.

## Quick Start

**When you have a Pharos IQ lead, provide:**

```
Create a Pharos IQ quote for [Contact Name]
Notes: [paste relevant PharosIQ information]
[Optional: Account name, opportunity details, timeline, quantity hints]
```

**I will:**
1. Parse the PharosIQ information
2. Search for or create Account and Contact records
3. Create a Zoho Deal with "PharosIQ" lead source
4. Generate a Quote with products priced at list rates
5. Set quantities based on notes (or default to 10 if not specified)
6. Create a follow-up Task
7. Search Gmail & Calendar for prior meetings with customer
8. Return links to all created records with total quote amount

## Workflow Overview

### Step 1: Parse PharosIQ Lead Information
Extract from the notes:
- Contact name, title, email, phone
- Company/Account name and location
- Opportunity type (Collaboration, Networking, Security)
- Budget/timeline hints
- Key business drivers

### Step 2: Prepare Zoho Records

**Account Record:**
- Search for existing account by name
- If not found, create new account with:
  - Account Name
  - Industry (inferred from opportunity type if available)
  - Billing City/State (if provided)

**Contact Record:**
- Link to Account
- Full Name, Email, Phone, Title (if available)
- Create if doesn't exist

### Step 3: Create Deal in Zoho

**Required Fields:**
- Deal Name: `[Account Name] - [Opportunity Summary]`
- Account: Link to Account record
- Contact Name: Link to Contact record
- Amount: Calculated from products and quantities
- Stage: **Qualification**
- Lead Source: **PharosIQ**
- Close Date: 30 days from today (default)
- Sales Owner: Your Zoho user

**Optional but recommended:**
- Description: Notes from PharosIQ lead

### Step 4: Create Quote in Zoho

**Required Fields:**
- Quote Name: `[Account Name] - [Product Category]`
- Related Deal: Link to Deal just created
- Quote Stage: **Quoted**
- Valid Until: 30 days from today

**Product Routing by Opportunity Type:**

See `references/team-routing.md` for detailed product assignments.

**Summary:**
- **Collaboration**: Cisco IP Phone 8841 (placeholder for routing to Collaboration team)
- **Networking**: Meraki access point or appropriate network product (route to Networking team)
- **Security**: Duo, Email Threat Defense, or Umbrella (route to Security team)

**Quantity & Pricing:**
- **Quantity**: Extract estimate from PharosIQ notes if possible; otherwise default to **10**
- **Unit Price**: Use list price automatically associated with the SKU (do not modify)
- Total quote amount will be calculated automatically

### Step 5: Create Follow-up Task

**Task Details:**
- Task Title: `Follow up on [Account] - [Opportunity Type]`
- Related To: Deal
- Due Date: 5 business days from today
- Priority: High
- Task Type: Call or Email

### Step 6: Search Gmail & Google Calendar

Search for any prior meetings or communications with customer:
- Gmail: Company name, contact name, contact email
- Google Calendar: Look for existing meetings in past 3 months or upcoming
- If meeting found: Note date, time, and include calendar link
- If no meeting found: Note "No prior meetings found"

### Step 7: Confirm and Return Links

Provide clickable links to:
- Deal (Zoho)
- Quote (Zoho) with calculated total
- Task (Zoho)
- Contact details and any prior meetings/calendar invites for reference

---

## Field Defaults

See `references/field-defaults.md` for:
- Default stage/values for Deals
- Quote validity periods
- Task assignment rules
- Lead source settings

---

## Product Routing Logic

Different opportunity types route to different Cisco teams:

- **Collaboration keywords**: calling, meetings, video conferencing, webex, phones, contact center → **Collaboration products**
- **Networking keywords**: wireless, switching, routing, meraki, catalyst, firepower, access points, switches → **Networking products** (note: Firepower is network infrastructure)
- **Security keywords**: email security, umbrella, duo, mfa, endpoint security, anyconnect, threat defense → **Security products**

See `references/team-routing.md` for complete mappings and specific SKUs.

---

## Common Questions

**Q: What if the contact/account already exists in Zoho?**
A: I'll search and link to existing records rather than creating duplicates.

**Q: Should I fill in real products or use placeholders?**
A: Products are team-appropriate routing placeholders (e.g., Meraki for Networking). Pricing is automatically pulled from list rates for the selected SKU. Once the relevant team confirms detailed requirements, update quantities and adjust product selection if needed for more specific models.

**Q: What's the expected timeline for these deals?**
A: Default close date is 30 days out. Adjust based on PharosIQ notes about decision timeline.

**Q: Can I provide additional context?**
A: Yes. Include any notes about the opportunity, budget, timeline, competing solutions, or technical requirements. This helps route to the right team and improves follow-up quality.

---

## Integration Notes

This skill integrates with:
- **Zoho CRM** - Creates Deals, Quotes, Tasks, and manages Accounts/Contacts
- **Gmail** - Searches for prior communications with customer
- **Google Calendar** - Searches for existing/upcoming meetings with customer
- **Team Routing** - Assigns products based on opportunity type (see references/team-routing.md)

---

## Success Criteria

✓ Deal created with PharosIQ lead source  
✓ Quote generated with placeholder products  
✓ Contact/Account properly linked  
✓ Follow-up task scheduled  
✓ All records accessible in Zoho CRM dashboard  

