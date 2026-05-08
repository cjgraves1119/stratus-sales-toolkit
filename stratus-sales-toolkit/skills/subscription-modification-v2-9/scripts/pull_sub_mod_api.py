#!/usr/bin/env python3
"""
pull_sub_mod_api.py - Cisco Manage Quote API client (SOAP/XML).

Python port of the Ruby ccw_subscription_addon_quote.rb proven against live
Cisco endpoints. Replaces a downloaded CCW XLS with two SOAP calls:

    OAuth2 (id.cisco.com)
        -> ListQuoteService    (find QuoteNumber by DealId)
        -> AcquireQuoteService (full quote with QuoteLine + CiscoLine block)

Usage:
    CISCO_CLIENT_ID=... CISCO_CLIENT_SECRET=... \
        python3 pull_sub_mod_api.py <ccw_deal_id>

Optional env overrides (only if Cisco rotates hosts):
    CISCO_OAUTH_URL              default: https://id.cisco.com/oauth2/default/v1/token
    CISCO_LIST_QUOTE_URL         default: https://apix.cisco.com/commerce/QUOTING/v1/ListQuoteService
    CISCO_ACQUIRE_QUOTE_URL      default: https://apix.cisco.com/commerce/QUOTING/v1/AcquireQuoteService
    CISCO_OAUTH_SCOPE            default: customscope
    CISCO_SENDER_AUTHORIZATION   default: 00u85pbemqyottzf45d7   (B2B-3.0 sender)
    CISCO_SENDER_LOGICAL_ID      default: 096650750              (TD SYNNEX)
    CISCO_SENDER_REFERENCE_ID    default: TD SYNNEX CORPORATION

Output schema (consumed by build_quote_payloads.py and submod_quote_pricing.py):

{
  "source": "ccw_api",
  "fetched_at": "...",
  "quote_number": "1234567",
  "quote_status": "ORDERED" | "DRAFT" | ...,
  "header": {
    "ccw_deal_id": "84410290",
    "subscription_id": null,           # not surfaced by SOAP; populate from Zoho if needed
    "quote_number": "1234567",
    "deal_expiration": null,
    "cisco_am_name": null,
    "cisco_am_email": null,
    "end_customer_raw": null,
    "end_customer_name": null,
    "total_list_price": 933.92         # DealTotal from QuoteHeader
  },
  "term": {"term_months": null, "start_date": null, "end_date": null},
  "parent_sku": "MERAKI-SUB" | "CISCO-NETWORK-SUB" | "SECURE-ACCESS-SUB",
  "raw_line_item_count": 17,
  "consolidated_line_items": [
    {
      "sku": "LIC-ACCSMGR-A",
      "action": "ADDED" | "MODIFIED" | "NOCHANGE",
      "unit_list_price_per_month": 1.16,
      "unit_list_price_full_term": 26.6834,
      "new_qty": 35,
      "existing_qty": 0,
      "net_change_qty": 35,
      "ext_list_all_rows":   933.92,
      "ext_list_net_change": 933.92,
      "full_state_ext_list": 933.92,
      "net_change_ext_list": 933.92,
      "ccw_net_addon_cost":  542.79,        # primary key consumed by submod_quote_pricing.py
      "remaining_term_months": 22.806,
      "api": {
        "quantityChange":             35,
        "remainingTerm":              22.806,
        "billingAmountNetChange":     542.79,
        "contractAmountNetChange":    542.79,
        "currentBillingAmount":       0.0,
        "newBillingAmount":           542.79,
        "extendedListPrice":          933.92,
        "lineChangeType":             "Added",
        "quantityChangeType":         "Increase",
        "itemCategoryClassification": "SUBSCRIPTION",
        "additionalItemInfo":         "XAAS",
        "requestedStartDate":         "...",
        "xaasEndDate":                "..."
      }
    }
  ],
  "summary": {...}
}

Exit codes:
    0 = success
    1 = CLI / env error
    2 = OAuth or HTTP failure
    3 = response shape did not match expectation
    4 = quote could not be located for DID
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from xml.etree import ElementTree as ET


DEFAULT_OAUTH_URL = "https://id.cisco.com/oauth2/default/v1/token"
DEFAULT_LIST_QUOTE_URL = "https://apix.cisco.com/commerce/QUOTING/v1/ListQuoteService"
DEFAULT_ACQUIRE_QUOTE_URL = "https://apix.cisco.com/commerce/QUOTING/v1/AcquireQuoteService"
DEFAULT_OAUTH_SCOPE = "customscope"
DEFAULT_SENDER_AUTHORIZATION = "00u85pbemqyottzf45d7"
DEFAULT_SENDER_LOGICAL_ID = "096650750"
DEFAULT_SENDER_REFERENCE_ID = "TD SYNNEX CORPORATION"


# ----------------------------- OAuth ---------------------------------------

def get_access_token() -> str:
    client_id = os.environ.get("CISCO_CLIENT_ID")
    client_secret = os.environ.get("CISCO_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("ERROR: CISCO_CLIENT_ID and CISCO_CLIENT_SECRET must be set", file=sys.stderr)
        sys.exit(1)

    url = os.environ.get("CISCO_OAUTH_URL", DEFAULT_OAUTH_URL)
    scope = os.environ.get("CISCO_OAUTH_SCOPE", DEFAULT_OAUTH_SCOPE)

    data = urllib.parse.urlencode({
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
        "scope":         scope,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            payload = json.loads(body)
            return payload["access_token"]
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")[:600]
        print(f"ERROR: OAuth token request failed (HTTP {e.code}): {msg}", file=sys.stderr)
        sys.exit(2)
    except (KeyError, ValueError) as e:
        print(f"ERROR: OAuth response missing access_token: {e}", file=sys.stderr)
        sys.exit(2)


# ----------------------------- SOAP envelopes ------------------------------

def list_quote_envelope(deal_id: str) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    bod = f"AddonPricingList{int(time.time())}"
    sender_auth = os.environ.get("CISCO_SENDER_AUTHORIZATION", DEFAULT_SENDER_AUTHORIZATION)
    return f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://www.openapplications.org/oagis/9">
  <soapenv:Header/>
  <soapenv:Body>
    <ns1:GetQuote releaseID="2">
      <ns1:ApplicationArea>
        <ns1:Sender>
          <ns1:ComponentID>B2B-3.0</ns1:ComponentID>
          <ns1:AuthorizationID>{sender_auth}</ns1:AuthorizationID>
        </ns1:Sender>
        <ns1:CreationDateTime>{today}</ns1:CreationDateTime>
        <ns1:BODID schemeVersionID="1.0" schemeAgencyName="Cisco">{bod}</ns1:BODID>
      </ns1:ApplicationArea>
      <ns1:DataArea>
        <ns1:Get maxItems="25"><ns1:Expression expressionLanguage="DealId">{deal_id}</ns1:Expression></ns1:Get>
        <ns1:Quote><ns1:QuoteHeader><ns1:Status><ns1:Code>All</ns1:Code></ns1:Status></ns1:QuoteHeader></ns1:Quote>
      </ns1:DataArea>
    </ns1:GetQuote>
  </soapenv:Body>
</soapenv:Envelope>"""


def acquire_quote_envelope(quote_number: str) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    bod = f"AddonPricingAcquire{int(time.time())}"
    logical_id = os.environ.get("CISCO_SENDER_LOGICAL_ID", DEFAULT_SENDER_LOGICAL_ID)
    reference_id = os.environ.get("CISCO_SENDER_REFERENCE_ID", DEFAULT_SENDER_REFERENCE_ID)
    return f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://www.openapplications.org/oagis/9">
  <soapenv:Header/>
  <soapenv:Body>
    <ns1:GetQuote releaseID="2">
      <ns1:ApplicationArea>
        <ns1:Sender>
          <ns1:LogicalID>{logical_id}</ns1:LogicalID>
          <ns1:ComponentID>B2B-3.0</ns1:ComponentID>
          <ns1:ReferenceID>{reference_id}</ns1:ReferenceID>
        </ns1:Sender>
        <ns1:Receiver><ns1:LogicalID>364132837</ns1:LogicalID><ns1:ID>Cisco Systems Inc.</ns1:ID></ns1:Receiver>
        <ns1:CreationDateTime>{today}</ns1:CreationDateTime>
        <ns1:BODID schemeVersionID="1.0" schemeAgencyName="Cisco">{bod}</ns1:BODID>
      </ns1:ApplicationArea>
      <ns1:DataArea>
        <ns1:Get/>
        <ns1:Quote>
          <ns1:QuoteHeader>
            <ns1:DocumentID><ns1:ID>{quote_number}</ns1:ID></ns1:DocumentID>
            <ns1:Status><ns1:Code>All</ns1:Code></ns1:Status>
          </ns1:QuoteHeader>
        </ns1:Quote>
      </ns1:DataArea>
    </ns1:GetQuote>
  </soapenv:Body>
</soapenv:Envelope>"""


def post_soap(url: str, token: str, body: str, timeout: int = 120) -> str:
    req = urllib.request.Request(url, data=body.encode("utf-8"), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "text/xml")
    req.add_header("Accept", "text/xml")
    req.add_header("SOAPAction", '""')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")[:600]
        print(f"ERROR: SOAP {url} HTTP {e.code}: {msg}", file=sys.stderr)
        sys.exit(2)


# ----------------------------- XML helpers ---------------------------------

def local_name(tag: str) -> str:
    """Strip XML namespace from a tag, e.g. {ns}QuoteLine -> QuoteLine."""
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def find_first_local(elem: ET.Element, name: str) -> ET.Element | None:
    """Depth-first search for the first descendant whose local name matches."""
    for child in elem.iter():
        if local_name(child.tag) == name:
            return child
    return None


def findall_local(elem: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in elem.iter() if local_name(child.tag) == name]


def text_of(elem: ET.Element | None) -> str:
    return (elem.text or "").strip() if elem is not None else ""


def to_float(raw: str) -> float:
    if raw is None:
        return 0.0
    s = str(raw).replace(",", "").replace("$", "").strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def to_int(raw: str) -> int:
    return int(round(to_float(raw)))


# ----------------------------- Quote parsing -------------------------------

def parse_quote_number_from_list(xml_body: str) -> str | None:
    root = ET.fromstring(xml_body)
    headers = findall_local(root, "QuoteHeader")
    for header in headers:
        document_id = None
        for child in header:
            if local_name(child.tag) == "DocumentID":
                document_id = child
                break
        if document_id is None:
            continue
        for child in document_id:
            if local_name(child.tag) == "ID" and (child.text or "").strip():
                return child.text.strip()
    return None


def first_child_local(elem: ET.Element, name: str) -> ET.Element | None:
    for child in elem:
        if local_name(child.tag) == name:
            return child
    return None


def collect_namevalues(line: ET.Element) -> dict[str, str]:
    """Pull all <NameValue name='X'>Y</NameValue> from a QuoteLine subtree."""
    out: dict[str, str] = {}
    for nv in line.iter():
        if local_name(nv.tag) != "NameValue":
            continue
        name = nv.attrib.get("name", "").strip()
        if not name:
            continue
        out[name] = (nv.text or "").strip()
    return out


def collect_cisco_line(line: ET.Element) -> dict[str, str]:
    """Pull text children from the first <CiscoLine> block under a QuoteLine."""
    out: dict[str, str] = {}
    cl = find_first_local(line, "CiscoLine")
    if cl is None:
        return out
    for child in cl:
        text = (child.text or "").strip()
        if text:
            out[local_name(child.tag)] = text
    return out


def derive_action(line_change_type: str, qty_change: int, existing_qty: int, new_qty: int) -> str:
    lct = (line_change_type or "").strip().lower()
    if lct == "added" or (existing_qty == 0 and qty_change > 0):
        return "ADDED"
    if qty_change == 0:
        return "NOCHANGE"
    return "MODIFIED"


def parse_quote_lines(xml_body: str) -> tuple[list[dict], dict, str]:
    root = ET.fromstring(xml_body)

    # Header
    quote_status = ""
    quote_total = 0.0
    quote_number = ""
    deal_total_amount = None

    qh = find_first_local(root, "QuoteHeader")
    if qh is not None:
        status_node = find_first_local(qh, "Status")
        if status_node is not None:
            code_node = find_first_local(status_node, "Code")
            quote_status = text_of(code_node)
        doc_id = find_first_local(qh, "DocumentID")
        if doc_id is not None:
            id_node = find_first_local(doc_id, "ID")
            quote_number = text_of(id_node)
        # Look for Extension Amount @typeCode="DealTotal"
        for amount in qh.iter():
            if local_name(amount.tag) == "Amount" and amount.attrib.get("typeCode") == "DealTotal":
                deal_total_amount = to_float(amount.text or "0")
                break

    header = {
        "quote_number":     quote_number,
        "quote_status":     quote_status,
        "deal_total":       deal_total_amount,
    }

    # Lines
    lines = []
    for line in findall_local(root, "QuoteLine"):
        nvs = collect_namevalues(line)
        cl = collect_cisco_line(line)

        line_no = text_of(first_child_local(line, "LineNumber")) or text_of(first_child_local(line, "LineNumberID"))

        # SKU - try multiple locations: ItemID/ID, Item/ID
        sku = ""
        for path in (("ItemID", "ID"), ("Item", "ID")):
            cur: ET.Element | None = line
            for part in path:
                cur = first_child_local(cur, part) if cur is not None else None
                if cur is None:
                    break
            if cur is not None and (cur.text or "").strip():
                sku = cur.text.strip()
                break
        if not sku:
            for child in line.iter():
                if local_name(child.tag) == "ID" and (child.text or "").strip():
                    candidate = child.text.strip()
                    if candidate.startswith(("LIC-", "E3N-", "E3S-", "SA-", "MERAKI", "CISCO", "SECURE")):
                        sku = candidate
                        break
        if not sku:
            continue

        description = text_of(find_first_local(line, "Description"))

        # Quantities
        display_qty = to_int(text_of(first_child_local(line, "Quantity")))
        if display_qty == 0:
            qty_node = find_first_local(line, "Quantity")
            display_qty = to_int(text_of(qty_node))

        qty_change = to_int(nvs.get("QuantityChange", "0"))
        line_change_type = nvs.get("LineChangeType", "")
        quantity_change_type = nvs.get("QuantityChangeType", "")
        item_category = nvs.get("ItemCategoryClassification", "")
        additional_info = cl.get("AdditionalItemInfo", "")

        # Pricing
        unit_list = 0.0
        for amount in line.iter():
            if local_name(amount.tag) != "UnitPrice":
                continue
            inner_amount = find_first_local(amount, "Amount")
            if inner_amount is not None:
                unit_list = to_float(inner_amount.text or "0")
                break
        full_line_list = to_float(text_of(first_child_local(line, "ExtendedAmount")))

        remaining_term = to_float(cl.get("RemainingTerm", "0"))
        billing_net_change = to_float(cl.get("BillingAmountNetChange", "0"))
        contract_net_change = to_float(cl.get("ContractAmountNetChange", "0"))
        current_billing = to_float(cl.get("CurrentBillingAmount", "0"))
        new_billing = to_float(cl.get("NewBillingAmount", "0"))
        requested_start = cl.get("RequestedStartDate", "")
        xaas_end = cl.get("XaaSEndDate", "")

        existing_qty = max(display_qty - qty_change, 0)
        new_qty = display_qty if display_qty > 0 else qty_change
        action = derive_action(line_change_type, qty_change, existing_qty, new_qty)

        # Per-unit list across the full visible quote line
        unit_list_full_term = round(full_line_list / new_qty, 4) if new_qty > 0 and full_line_list > 0 else 0.0

        # ccw_net_addon_cost: prefer BillingAmountNetChange, fall back to
        # ContractAmountNetChange, last-resort to remaining-term derivation.
        if billing_net_change > 0:
            ccw_net = billing_net_change
        elif contract_net_change > 0:
            ccw_net = contract_net_change
        else:
            ccw_net = 0.0

        addon = (
            line_change_type.lower() == "added"
            or qty_change > 0
            or billing_net_change > 0
            or contract_net_change > 0
        )

        lines.append({
            "sku": sku,
            "action": action,
            "unit_list_price_per_month": unit_list,
            "unit_list_price_full_term": unit_list_full_term,
            "new_qty": new_qty,
            "existing_qty": existing_qty,
            "net_change_qty": qty_change if qty_change else (new_qty if action == "ADDED" else 0),
            "ext_list_all_rows":   full_line_list,
            "ext_list_net_change": full_line_list if addon else 0.0,
            "full_state_ext_list": full_line_list,
            "net_change_ext_list": round(unit_list_full_term * (qty_change if qty_change else (new_qty if action == "ADDED" else 0)), 2),
            "ccw_net_addon_cost":  ccw_net if addon else 0.0,
            "remaining_term_months": remaining_term,
            "description": description,
            "api": {
                "quantityChange":             qty_change,
                "remainingTerm":              remaining_term,
                "billingAmountNetChange":     billing_net_change,
                "contractAmountNetChange":    contract_net_change,
                "currentBillingAmount":       current_billing,
                "newBillingAmount":           new_billing,
                "extendedListPrice":          full_line_list,
                "lineChangeType":             line_change_type,
                "quantityChangeType":         quantity_change_type,
                "itemCategoryClassification": item_category,
                "additionalItemInfo":         additional_info,
                "requestedStartDate":         requested_start,
                "xaasEndDate":                xaas_end,
                "lineNumber":                 line_no,
            },
        })

    return lines, header, quote_status


def detect_parent_sku(skus: list[str]) -> str:
    if any(s.startswith("E3N-") for s in skus):
        return "CISCO-NETWORK-SUB"
    if any(s.startswith("SA-") or s.startswith("E3S-") for s in skus):
        return "SECURE-ACCESS-SUB"
    if any(s.startswith("LIC-") for s in skus):
        return "MERAKI-SUB"
    return "MERAKI-SUB"


def build_summary(items: list[dict]) -> dict:
    summary = {
        "total_skus":     len(items),
        "added_skus":     0,
        "modified_skus":  0,
        "nochange_skus":  0,
        "net_change_qty_total": 0,
    }
    for it in items:
        if it["action"] == "ADDED":
            summary["added_skus"] += 1
        elif it["action"] == "MODIFIED":
            summary["modified_skus"] += 1
        elif it["action"] == "NOCHANGE":
            summary["nochange_skus"] += 1
        summary["net_change_qty_total"] += it["net_change_qty"]
    return summary


# ----------------------------- Driver --------------------------------------

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: pull_sub_mod_api.py <ccw_deal_id>", file=sys.stderr)
        sys.exit(1)

    ccw_deal_id = str(sys.argv[1]).strip()
    if not ccw_deal_id:
        print("ERROR: empty CCW Deal Id", file=sys.stderr)
        sys.exit(1)

    token = get_access_token()

    list_url = os.environ.get("CISCO_LIST_QUOTE_URL", DEFAULT_LIST_QUOTE_URL)
    list_resp = post_soap(list_url, token, list_quote_envelope(ccw_deal_id))
    quote_number = parse_quote_number_from_list(list_resp)
    if not quote_number:
        print(f"ERROR: no quote found for DID {ccw_deal_id} in ListQuoteService response", file=sys.stderr)
        sys.exit(4)

    acquire_url = os.environ.get("CISCO_ACQUIRE_QUOTE_URL", DEFAULT_ACQUIRE_QUOTE_URL)
    acquire_resp = post_soap(acquire_url, token, acquire_quote_envelope(quote_number))
    items, soap_header, quote_status = parse_quote_lines(acquire_resp)

    if not items:
        print("ERROR: AcquireQuoteService returned 0 line items", file=sys.stderr)
        sys.exit(3)

    parent_sku = detect_parent_sku([i["sku"] for i in items])
    summary = build_summary(items)

    # Term info: borrow remaining_term_months from a representative line
    # (most CCW sub mods carry the same RemainingTerm across lines).
    term_months = None
    for it in items:
        if it["remaining_term_months"]:
            term_months = it["remaining_term_months"]
            break

    output = {
        "source":          "ccw_api",
        "fetched_at":      datetime.utcnow().isoformat() + "Z",
        "quote_number":    quote_number,
        "quote_status":    quote_status,
        "header": {
            "ccw_deal_id":       ccw_deal_id,
            "subscription_id":   None,                  # SOAP doesn't surface; pull from Zoho deal
            "quote_number":      quote_number,
            "deal_expiration":   None,
            "cisco_am_name":     None,
            "cisco_am_email":    None,
            "end_customer_raw":  None,
            "end_customer_name": None,
            "total_list_price":  soap_header.get("deal_total"),
        },
        "term": {
            "term_months": term_months,
            "start_date":  None,
            "end_date":    None,
        },
        "parent_sku": parent_sku,
        "raw_line_item_count":     len(items),
        "consolidated_line_items": items,
        "summary":                 summary,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
