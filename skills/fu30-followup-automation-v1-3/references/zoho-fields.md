# Zoho CRM Field Reference

## Tasks Module
| Field | API Name | Notes |
|-------|----------|-------|
| Subject | Subject | Contains "FU30" for 30-day follow-ups |
| Status | Status | "Not Started", "In Progress", "Completed" |
| Due Date | Due_Date | Date format |
| Related To (Deal) | What_Id | Lookup to Deals module |
| Contact | Who_Id | Lookup to Contacts module |
| Owner | Owner | User lookup |

## Contacts Module
| Field | API Name | Notes |
|-------|----------|-------|
| First Name | First_Name | |
| Last Name | Last_Name | |
| Email | Email | Primary email |
| Email Opt Out | Email_Opt_Out | Boolean |
| Account | Account_Name | Lookup to Accounts |

## Deals Module
| Field | API Name | Notes |
|-------|----------|-------|
| Deal Name | Deal_Name | |
| Amount | Amount | Currency |
| Stage | Stage | See stage values below |
| Type | Type | "Renewal", "New Business", etc. |
| Account | Account_Name | Lookup to Accounts |

### Deal Stages (Active = Skip for FU30)
- Qualification ← **Active**
- Proposal/Negotiation ← **Active**
- Verbal Commit/Invoicing ← **Active**
- Closed Won
- Closed Lost
- Closed - Loss to Competition

## Invoices Module
| Field | API Name | Notes |
|-------|----------|-------|
| Invoice Number | Invoice_Number | For payment URL |
| Grand Total | Grand_Total | Amount for payment URL |
| Status | Status | "Paid", "Unpaid", etc. |
| Account | Account_Name | Lookup to Accounts |

## Quotes Module
| Field | API Name | Notes |
|-------|----------|-------|
| Quote Name | Subject | |
| Deal | Deal_Name | Lookup to Deals |
| Product Details | Product_Details | Subform with line items |

## Owner IDs
| Name | ID |
|------|-----|
| Chris Graves | 2570562000141711002 |

## URL Structures

### Zoho CRM Record URLs
```
https://crm.zoho.com/crm/org647122552/tab/{MODULE}/{RECORD_ID}
```

Modules:
- Tasks
- Contacts
- Deals
- Quotes
- Invoices
- Accounts

### Stratus Payment URL
```
https://www.stratusinfosystems.com/invoicing/?inva={AMOUNT}&invn={INVOICE_NUMBER}&curr=usd
```

Example:
- Invoice #24461 for $1,321
- URL: `https://www.stratusinfosystems.com/invoicing/?inva=1321&invn=24461&curr=usd`
