# Subscription Modification - Changelog

### v2.6 (Current)
- **EMBEDDED SKU CACHE**: 30+ common subscription SKUs with Zoho IDs built-in
- **ENFORCED PARENT SKU**: Always include with term months in description
- **CORRECT FIELD NAME**: Documents "Description" not "Product_Description"
- **PRE-VALIDATION**: Check product active status before quote creation
- **LOGGING**: Log when falling back from cache to Zoho search
- **SKU UPDATE FLAG**: Flag new SKUs found via Zoho for skill updates
- **DEAL VALIDATION**: All required fields enforced from Zoho CRM skill
- **DEFAULT LEAD_SOURCE**: All sub mods default to "Stratus Referal"
- **DEFAULT MERAKI_ISR**: All sub mods default to "Stratus Sales" (ID: 2570562000027286729)
- **CONTACT AUTO-ASSIGN**: Lookup contact, auto-assign if single contact on account
- **TASK $se_module**: Enforces $se_module: "Deals" on task creation
- **PRE-CREATION TABLES**: Validation table displayed before each record creation
- **FULL ADDRESS**: All 10 address fields (5 billing + 5 shipping) required

### v2.5
- Customer quote first workflow
- Consolidated OP items
- Dollar-based discounts
- Existing deal detection

### v2.4
- Address lookup integration
- Deal Notes on creation
- Required fields enforcement
