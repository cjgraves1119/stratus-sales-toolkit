# FU30 Email Templates

## Standard Renewal Template

**Subject:** Checking In on Your Renewal

```html
Hey {First_Name},<br><br>

Now that it's been a few weeks since your license renewal went through, I wanted to send a friendly check-in to make sure everything is running smoothly.<br><br>

How are things going so far?<br><br>

Best,<br>
Chris Graves<br>
Regional Sales Director
```

## Hardware Order Template

**Subject:** Quick Check-In on Your {Product_Summary}

```html
Hey {First_Name},<br><br>

Now that it's been a few weeks since you received your {Product_Details}, I wanted to send a friendly check-in to make sure everything went smoothly.<br><br>

How are things going so far?<br><br>

Best,<br>
Chris Graves<br>
Regional Sales Director
```

## High-Value Deal Template ($5k+)

**Subject:** Checking In on {Project_Context}

```html
Hey {First_Name},<br><br>

Now that it's been a few weeks since {project_specific_context}, I wanted to send a friendly check-in. {additional_context_from_gmail}<br><br>

How are things going so far?{optional_offer}<br><br>

Best,<br>
Chris Graves<br>
Regional Sales Director
```

## Unpaid Invoice Addendum

Insert before signature when unpaid invoice exists:

```html
By the way, I noticed invoice #{Invoice_Number} for ${Grand_Total} is still showing as outstanding. If there's anything I can help with on that front, or if you'd prefer to pay online, here's a quick link: <a href="{Payment_URL}">{Payment_URL}</a><br><br>
```

## Subject Line Examples

### By Product Type
| Product | Subject |
|---------|---------|
| MX Firewalls | Quick Check-In on Your MX75s |
| Switches | Checking In on Your MS210 Switches |
| Access Points | Quick Check-In on Your MR78 Access Points |
| Wi-Fi 7 APs | Checking In on Your Wi-Fi 7 Access Points |
| Cameras | Quick Check-In on Your MV Cameras |
| Renewal | Checking In on Your Renewal |
| Generic Order | Checking In on Your Order |

### By Context
| Context | Subject |
|---------|---------|
| Multi-product order | Checking In on Your Switches and Access Points |
| Large project | Checking In on the Network Refresh |
| Specific product | Quick Check-In on Your {Exact_Product_Name} |
| AnyConnect | Quick Check-In on Your AnyConnect Expansion |

## Personalization Guidelines

### Renewals
- Keep generic unless Gmail shows recent support interaction
- If recent support: "I know we worked through some license claim questions last month, so hopefully everything is running smoothly now."

### Hardware Orders
- Always reference specific products from quote
- For multi-product: List major items (switches, APs, firewalls)
- Skip accessories (SFPs, cables, power supplies) in subject

### High-Value Deals ($5k+)
- Search Gmail for project context
- Reference: deployment timeline, migration from competitor, recent support
- Offer additional assistance if complex project

### Multiple Orders/Tasks for Same Contact
- Combine into single email
- Reference all relevant products/renewals
- Complete all associated tasks
