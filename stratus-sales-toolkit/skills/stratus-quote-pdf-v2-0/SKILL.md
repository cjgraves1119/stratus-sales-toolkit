---
name: stratus-quote-pdf-v2-0
description: optimized stratus-branded pdf quote generator using fpdf2 for 2x faster generation. generates professional quotes from zoho crm data with automatic fallback to reportlab if needed.
---

# Stratus Quote PDF Generator v2.0

Generate branded PDF quotes from Zoho CRM data. Optimized for speed using FPDF2 (2x faster than v1.0).

## Performance

| Quote Size | v1.0 (ReportLab) | v2.0 (FPDF2) | Improvement |
|------------|------------------|--------------|-------------|
| Simple (2 items) | 23ms | 12ms | 1.9x faster |
| Medium (8 items) | 24ms | 13ms | 1.8x faster |
| Large (15 items) | 36ms | 19ms | 2.0x faster |

## Quick Usage

```python
from generate_quote_pdf import generate_quote_pdf

# Primary method (FPDF2, fastest)
generate_quote_pdf(quote_data, "/mnt/user-data/outputs/Quote_XXXX.pdf")
```

## Dependencies

Install before first use:
```bash
pip install fpdf2 --break-system-packages
```

## Required JSON Structure

```python
quote_data = {
    "quote_number": "QT-2025-001234",
    "subject": "Quote Subject/Offer Name",
    "stage": "Review",
    "valid_till": "Feb 28, 2025",
    "account_rep": "Chris Graves",
    "sub_total": 7827.30,
    "grand_total": 7827.30,
    "bill_to": {
        "name": "Company Name",
        "street": "123 Main St",
        "city": "City",
        "state": "ST",
        "zip": "12345"
    },
    "ship_to": {
        "name": "Contact Name", 
        "street": "123 Main St",
        "city": "City",
        "state": "ST",
        "zip": "12345"
    },
    "line_items": [
        {
            "name": "Product Name",
            "sku": "SKU-123",
            "term": "5-Year License",  # optional
            "qty": 65,
            "list_price": 7827.30,
            "client_price": 7827.30,
            "tax": 0.00,
            "net_total": 7827.30
        }
    ],
    "terms": "Optional custom terms text"  # optional, has default
}
```

## Zoho Field Mapping

| JSON Field | Zoho Field |
|------------|------------|
| quote_number | Quote_Number |
| subject | Subject |
| stage | Quote_Stage |
| valid_till | Valid_Till (format to readable date) |
| account_rep | Owner.name |
| sub_total | Sub_Total |
| grand_total | Grand_Total |
| bill_to.name | Account_Name.name |
| bill_to.street | Billing_Street |
| bill_to.city | Billing_City |
| bill_to.state | Billing_State |
| bill_to.zip | Billing_Code |
| ship_to.name | Contact_Name.name |
| ship_to.street | Shipping_Street |
| ship_to.city | Shipping_City |
| ship_to.state | Shipping_State |
| ship_to.zip | Shipping_Code |
| line_items | Quoted_Items array |

## Changelog

### v2.0
- Switched from ReportLab Platypus to FPDF2 for 2x speed improvement
- Direct coordinate rendering eliminates layout calculation overhead
- Reduced object instantiation (no per-row style creation)
- Same visual output and branding as v1.0

### v1.0
- Initial release with ReportLab
