# Pharos IQ Field Defaults

Standard field values and defaults for creating Deals and Quotes from Pharos IQ leads.

## Deal Fields

### Required Fields

| Field | Default Value | Notes |
|-------|---------------|-------|
| **Deal Name** | `[Account Name] - [Opportunity Type/Summary]` | Descriptive, includes customer name |
| **Account** | Linked Account record | Search existing or create new |
| **Contact Name** | Linked Contact record | From PharosIQ information |
| **Amount** | Calculated from products and quantities | Auto-populated from quote line items |
| **Stage** | Qualification | Initial stage for all PharosIQ leads |
| **Lead Source** | PharosIQ | Consistent tracking across all PharosIQ opportunities |
| **Close Date** | Today + 30 days | Default timeline; adjust based on PharosIQ notes |

### Recommended Fields

| Field | Default Value | Notes |
|-------|---------------|-------|
| **Deal Owner/Sales Owner** | Your Zoho user ID | Track ownership for follow-up |
| **Description** | PharosIQ notes | Include relevant context from the lead |
| **Pipeline** | Standard Sales Pipeline | Or appropriate pipeline for your org |

### Optional Fields

| Field | When to Use |
|-------|-------------|
| **Team** | If using team-based ownership model |
| **Territory** | If using territory management |
| **Expected Revenue** | Only if probability/forecasting needed |
| **Deal Type** | New Business, Expansion, Renewal (usually "New Business" for PharosIQ) |

---

## Quote Fields

### Required Fields

| Field | Default Value | Notes |
|-------|---------------|-------|
| **Quote Name** | `[Account] - [Product Category] - [Date]` | Example: "Acme Corp - Networking - Dec 2025" |
| **Related Deal** | Link to Deal created in Step 3 | Must be associated with a deal |
| **Quote Stage** | Quoted | Standard stage for new quotes |
| **Valid Until** | Today + 30 days | Standard 30-day quote validity |
| **Quote Line Items** | Placeholder product (qty=1) | See team-routing.md for product selection |

### Recommended Fields

| Field | Default Value | Notes |
|-------|---------------|-------|
| **Currency** | USD | Adjust if customer is international |
| **Quote Date** | Today | Auto-populated |
| **Quote Number** | Auto-generated | Zoho CRM generates these automatically |
| **Description** | Placeholder note | Include message about placeholder products |

### Optional Fields

| Field | When to Use |
|-------|-------------|
| **Discount** | Only if customer-specific discount applicable |
| **Tax** | Configure based on customer location |
| **Shipping** | Only if physical products with shipping |

---

## Quote Line Item Defaults

When adding placeholder products to the quote:

| Field | Default Value |
|-------|----------------|
| **Product** | Team-specific placeholder from references/team-routing.md |
| **Unit Price** | Use list price automatically associated with SKU (do not modify) |
| **Quantity** | Extract from PharosIQ notes if possible; otherwise default to 10 |
| **Line Item Description** | `Placeholder for [Team] - to be updated when [requirement] confirmed` |

**Important:** Always use the list price that Zoho CRM automatically pulls from the product/SKU record. Do not manually adjust or override pricing.

---

## Contact Fields

### Required if creating new Contact

| Field | Source | Notes |
|-------|--------|-------|
| **Full Name** | PharosIQ information | From lead data |
| **Email** | PharosIQ information | Primary contact email |
| **Account Name** | Linked Account record | Must link to Account |
| **Phone** | PharosIQ information (optional) | Add if available |
| **Title** | PharosIQ information (optional) | Add if available |

---

## Account Fields

### Required if creating new Account

| Field | Source | Notes |
|-------|--------|-------|
| **Account Name** | PharosIQ information | Customer company name |
| **Billing City** | PharosIQ information (if available) | For order routing |
| **Billing State** | PharosIQ information (if available) | For order routing |
| **Billing Country** | Inferred (default: USA) | Adjust if international |
| **Industry** | Inferred from opportunity type (optional) | Can help with routing |

---

## Task Fields

### Required for Follow-up Tasks

| Field | Default Value | Notes |
|-------|---------------|-------|
| **Task Title** | `Follow up: [Account] - [Opportunity Type]` | Clear action statement |
| **Related To** | Link to Deal | Tasks associated with the deal |
| **Due Date** | Today + 5 business days | Quick follow-up timeline |
| **Priority** | High | Ensure timely follow-up |
| **Activity Type** | Call or Email | Specify engagement method |
| **Description** | Notes from placeholder quote | Remind team of opportunity type and next steps |

---

## Timeline Defaults

| Activity | Default Timing | Notes |
|----------|----------------|-------|
| **Deal Created** | When PharosIQ lead received | Day 0 |
| **Quote sent to customer** | Within 1-2 business days | Quick response for hot leads |
| **First follow-up task** | 5 business days after deal creation | Ensures timely engagement |
| **Quote expires** | 30 days from quote date | Standard sales cycle |
| **Deal close expected** | 30 days from deal creation | Baseline; adjust per opportunity |

**Overrides:** If PharosIQ notes mention specific timeline (e.g., "decision in January"), adjust close date and task timeline accordingly.

---

## Notes on Placeholder vs. Real Values

### Placeholder Phase (Initial Quote)
- **Products**: Category placeholders (see team-routing.md)
- **Pricing**: $0
- **Quantities**: 1
- **Purpose**: Get opportunity into CRM, route to right team

### Transition to Real Products
- Happens after requirements gathering with appropriate Cisco team
- Replace placeholder products with actual SKUs
- Update quantities based on actual requirements
- Add real pricing from Cisco systems
- Send revised quote to customer

### Timeline
- **Placeholder quote**: Sent within 1-2 days to show quick response
- **Requirements gathering**: 3-5 days (Cisco team gathers details)
- **Real quote**: Sent within 7-10 days with actual products/pricing

---

