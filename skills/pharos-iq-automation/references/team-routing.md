# Pharos IQ Team Routing Guide

Maps opportunity types to Cisco product teams and placeholder products for initial quoting.

## Routing by Opportunity Type

### Collaboration Opportunities

**Keywords to detect:**
- Calling, voice, phones, IP phones
- Video conferencing, meetings, webex
- Contact center, customer service
- Unified communications, UC
- Messaging, chat, team collaboration

**Placeholder Product for Quote:**
- **Cisco IP Phone 8841** (PRODUCT_ID: 8841)
  - Qty: 1 initially (update when actual phone count known)
  - Route to: Cisco Collaboration team
  - Typical follow-up: Phone count, deployment model, licensing needs

**Real SKUs to use after requirements gathered:**
- IP Phone 6800/7800/8800 series
- Cisco Webex Meeting Suite licensing
- Contact Center Express/Premium
- See with Collaboration team for specific requirements

---

### Networking Opportunities

**Keywords to detect:**
- Wireless, Wi-Fi, access points, AP
- Switching, switches, layer 2/3
- Routing, routers
- Meraki, Catalyst
- Network infrastructure, upgrades
- SD-WAN, network modernization
- WAN, LAN

**Placeholder Product for Quote:**
- **Meraki MR Access Point** (placeholder SKU varies by region)
  - Qty: 1 initially (update when actual AP count known)
  - Route to: Cisco Networking/Meraki team
  - Typical follow-up: RF survey results, coverage area, density requirements, licensing terms (co-term vs subscription)

**Real SKUs to use after requirements gathered:**
- Meraki MR46E, MR44, MR42, MR32 (access points)
- Meraki MS130 series (switches)
- Catalyst 9300-L, 9200-L (enterprise switches)
- See with Networking team for specific requirements and licensing

---

### Security Opportunities

**Keywords to detect:**
- Email security, web filtering, threat prevention
- Umbrella, DNS security
- Endpoint security, AnyConnect
- DLP, data loss prevention
- SIEM, security monitoring
- Duo, MFA, multi-factor authentication
- Email threat defense, advanced threat protection

**Note:** Firepower aligns to Cisco Networking, not Security. Do not use Firepower for Security routing.

**Placeholder Product for Quote:**

Use **one of the following** based on what's mentioned in PharosIQ notes:

1. **Duo Authentication** (if MFA/identity mentioned)
   - Qty: Extract from notes or default to 10 seats
   - Route to: Cisco Security team

2. **Email Threat Defense** (if email security mentioned)
   - Qty: Extract from notes or default to 10 seats
   - Route to: Cisco Security team

3. **Cisco Umbrella** (if DNS/web filtering mentioned)
   - Qty: Extract from notes or default to 10 seats
   - Route to: Cisco Security team

4. **Generic Security Placeholder** (if Security need is mentioned but type unclear)
   - Use as holding place for further requirements gathering
   - Route to: Cisco Security team for clarification

**Important:** If the lead mentions Firepower but seems to be primarily a network security need, route to NETWORKING team, not Security. Firepower appliances are network infrastructure.

**Real SKUs to use after requirements gathered:**
- Cisco Duo Authentication licenses
- Email security/threat defense products
- Cisco Umbrella subscriptions
- AnyConnect licenses
- See with Security team for specific requirements

---

## Decision Tree for Routing

```
Does the lead mention...

Phones/calling/webex/meetings?
  → COLLABORATION

Wireless/switches/networks/Meraki/Catalyst/Firepower/ASA?
  → NETWORKING
  (Note: Firepower is network infrastructure, not app security)

Email security/Umbrella/Duo/AnyConnect/DLP/SIEM?
  → SECURITY

Multiple categories?
  → Pick PRIMARY use case
  → Route to primary team
  → Note secondary needs in quote description for cross-team collaboration
```

---

## Quote Creation with Placeholder Products

When creating the initial quote:

1. **Product** (from appropriate category above)
2. **Unit Price**: Set to $0 (placeholder)
3. **Qty**: 1 (placeholder - will scale when requirements confirmed)
4. **Description**: `[Placeholder for [Team] requirements - to be updated when [specific requirement] confirmed]`

**Example:**
- Product: Meraki MR Access Point
- Qty: 1
- Description: "Placeholder for Networking team - to be updated when RF survey completed and AP count confirmed"

---

## Transition to Real Products

When moving from placeholder to real quote:

1. **Requirements gathering call**: Networking/Collaboration/Security team confirms specifics
2. **Product selection**: Replace placeholder with actual SKU from requirements
3. **Licensing terms**: Confirm 3-year co-term, 5-year, or subscription model
4. **Pricing**: Update quantity and pricing
5. **Quote revision**: Send updated quote with real products to customer

---

## Team Contact Preferences

Suggested contacts for each team (update as needed):

**Collaboration Team:**
- Cisco Collaboration contacts for escalation

**Networking Team:**
- Meraki specialists for AP/switch recommendations
- Licensing team for co-term vs subscription decisions

**Security Team:**
- Threat/Security specialists for firewall sizing
- Licensing team for advanced features

---

