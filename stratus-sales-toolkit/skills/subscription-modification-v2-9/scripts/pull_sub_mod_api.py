#!/usr/bin/env python3
"""
pull_sub_mod_api.py - API-first sub mod parser using Cisco Manage Quote APIs.

Replaces the downloaded-CCW-XLS path when Chris has a CCW DID. Pulls quote
header + line economics directly from Cisco using:

    - OAuth2 client_credentials flow (id.cisco.com)
    - ListQuoteService          -> find quoteId by DealId
    - AcquireQuoteService       -> full quote, line items, net-change figures

Usage:
    CISCO_CLIENT_ID=...  CISCO_CLIENT_SECRET=...  python3 pull_sub_mod_api.py <ccw_deal_id>

Optional env overrides (keep defaults unless Cisco rotates host):
    CISCO_OAUTH_URL   default: https://id.cisco.com/oauth2/default/v1/token
    CISCO_QUOTE_HOST  default: https://api.cisco.com
    CISCO_QUOTE_LIST_PATH      default: /commerce/QUOTE/v3/sync/quotes/list
    CISCO_QUOTE_ACQUIRE_PATH   default: /commerce/QUOTE/v3/sync/quotes/{quoteId}/acquire
    CISCO_QUOTE_VERSION        default: v3

Outputs JSON to stdout in a schema that is a SUPERSET of parse_sub_mod.py:

{
  "source": "ccw_api",
  "file": null,
  "header": {
    "ccw_deal_id":        "84410290",
    "subscription_id":    "Sub123456789",
    "quote_name":         "...",
    "deal_expiration":    "YYYY-MM-DD",
    "cisco_am_name":      "...",
    "cisco_am_email":     "...",
    "end_customer_raw":   "...",
    "end_customer_name":  "...",
    "total_list_price":   12345.67
  },
  "term": {
    "term_months": 22.81,
    "start_date":  "YYYY-MM-DD",
    "end_date":    "YYYY-MM-DD"
  },
  "parent_sku": "MERAKI-SUB" | "CISCO-NETWORK-SUB" | "SECURE-ACCESS-SUB",
  "raw_line_item_count": 17,
  "consolidated_line_items": [
    {
      "sku":  "LIC-ACCSMGR-A",
      "action": "ADDED" | "MODIFIED" | "NOCHANGE",
      "unit_list_price_per_month":  1.16,                 # informational only
      "unit_list_price_full_term":  26.6834...,           # ext_list_all_rows / new_qty
      "new_qty": 35,
      "existing_qty": 0,
      "net_change_qty": 35,
      "ext_list_all_rows":   933.92,
      "ext_list_net_change": 933.92,
      "full_state_ext_list": 933.92,
      "net_change_ext_list": 933.92,
      "api": {
        "quantityChange": 35,
        "remainingTerm":  22.806,
        "billingAmountNetChange":   542.79,
        "contractAmountNetChange":  542.79,
        "extendedListPrice":        933.92,
        "extendedNetPrice":         542.79,
        "billingFrequency":         1
      }
    },
    ...
  ],
  "summary": {
    "total_skus": 17,
    "added_skus": 4,
    "modified_skus": 0,
    "nochange_skus": 13,
    "net_change_qty_total": 41
  },
  "raw_api": { ... pruned response payload ... }
}

Exit codes:
    0 = success (clean parsed JSON on stdout)
    1 = CLI / env error
    2 = OAuth or HTTP failure
    3 = response shape did not match expectation (likely API change)
    4 = quote could not be located for DID
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


DEFAULT_OAUTH_URL = "https://id.cisco.com/oauth2/default/v1/token"
DEFAULT_QUOTE_HOST = "https://api.cisco.com"
DEFAULT_LIST_PATH = "/commerce/QUOTE/v3/sync/quotes/list"
DEFAULT_ACQUIRE_PATH = "/commerce/QUOTE/v3/sync/quotes/{quoteId}/acquire"
DEFAULT_SCOPE = "customscope"


# ----------------------------- HTTP helpers --------------------------------

def http_post_form(url, form_dict, headers=None, timeout=30):
    data = urllib.parse.urlencode(form_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def http_post_json(url, body, headers=None, timeout=60):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


# ----------------------------- OAuth ---------------------------------------

def get_access_token():
    client_id = os.environ.get("CISCO_CLIENT_ID")
    client_secret = os.environ.get("CISCO_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("ERROR: CISCO_CLIENT_ID and CISCO_CLIENT_SECRET must be set", file=sys.stderr)
        sys.exit(1)

    url = os.environ.get("CISCO_OAUTH_URL", DEFAULT_OAUTH_URL)
    scope = os.environ.get("CISCO_OAUTH_SCOPE", DEFAULT_SCOPE)

    status, body = http_post_form(
        url,
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        },
    )
    if status != 200:
        print(f"ERROR: OAuth token request failed (HTTP {status}): {body[:500]}", file=sys.stderr)
        sys.exit(2)
    try:
        token = json.loads(body)["access_token"]
    except (ValueError, KeyError):
        print(f"ERROR: OAuth response missing access_token: {body[:500]}", file=sys.stderr)
        sys.exit(2)
    return token


# ----------------------------- Cisco API calls -----------------------------

def list_quotes_for_did(token, ccw_deal_id):
    host = os.environ.get("CISCO_QUOTE_HOST", DEFAULT_QUOTE_HOST)
    path = os.environ.get("CISCO_QUOTE_LIST_PATH", DEFAULT_LIST_PATH)
    url = host + path

    body = {
        "DataArea": {
            "ListQuoteService": {
                "QueryExpression": {
                    "DealId": str(ccw_deal_id)
                }
            }
        }
    }

    status, raw = http_post_json(
        url,
        body,
        headers={"Authorization": f"Bearer {token}"},
    )
    if status != 200:
        print(f"ERROR: ListQuoteService HTTP {status}: {raw[:500]}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(raw)
    except ValueError:
        print(f"ERROR: ListQuoteService non-JSON response: {raw[:500]}", file=sys.stderr)
        sys.exit(3)


def acquire_quote(token, quote_id):
    host = os.environ.get("CISCO_QUOTE_HOST", DEFAULT_QUOTE_HOST)
    path = os.environ.get("CISCO_QUOTE_ACQUIRE_PATH", DEFAULT_ACQUIRE_PATH)
    url = host + path.replace("{quoteId}", urllib.parse.quote(str(quote_id), safe=""))

    body = {
        "DataArea": {
            "AcquireQuoteService": {
                "AcquireQuoteRequest": {
                    "QuoteId": str(quote_id),
                    "IncludeLineItems": True,
                    "IncludeDeltaQuantities": True,
                }
            }
        }
    }

    status, raw = http_post_json(
        url,
        body,
        headers={"Authorization": f"Bearer {token}"},
    )
    if status != 200:
        print(f"ERROR: AcquireQuoteService HTTP {status}: {raw[:500]}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(raw)
    except ValueError:
        print(f"ERROR: AcquireQuoteService non-JSON response: {raw[:500]}", file=sys.stderr)
        sys.exit(3)


# ----------------------------- Response parsing ----------------------------

def deepfind(obj, key):
    """Best-effort lookup of the first occurrence of `key` anywhere in a nested dict."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = deepfind(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = deepfind(v, key)
            if r is not None:
                return r
    return None


def deepfind_all(obj, key):
    out = []
    if isinstance(obj, dict):
        if key in obj:
            out.append(obj[key])
        for v in obj.values():
            out.extend(deepfind_all(v, key))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(deepfind_all(v, key))
    return out


def parse_quote_id_from_list(list_resp):
    """Find the quoteId for a DID lookup. Cisco varies field names; try several."""
    for k in ("QuoteId", "QuoteID", "quoteId", "Id"):
        v = deepfind(list_resp, k)
        if v:
            return str(v)
    return None


def safe_float(v):
    try:
        if v in (None, "", "--"):
            return 0.0
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def safe_int(v):
    try:
        if v in (None, "", "--"):
            return 0
        return int(float(v))
    except (ValueError, TypeError):
        return 0


def normalize_iso_date(s):
    if not s:
        return None
    s = str(s)
    # Already ISO-ish
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    # DD-Mon-YYYY
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    parts = s.replace(",", "").split("-")
    if len(parts) == 3 and parts[1].lower()[:3] in months:
        return f"{parts[2]}-{months[parts[1].lower()[:3]]}-{parts[0].zfill(2)}"
    return s


def derive_action(line):
    qty_change = safe_int(deepfind(line, "QuantityChange"))
    new_qty = safe_int(deepfind(line, "NewQuantity") or deepfind(line, "Quantity"))
    existing_qty = safe_int(deepfind(line, "ExistingQuantity") or deepfind(line, "PriorQuantity"))

    if existing_qty == 0 and qty_change > 0:
        return "ADDED"
    if qty_change == 0:
        return "NOCHANGE"
    if qty_change > 0 and existing_qty > 0:
        return "MODIFIED"
    if qty_change < 0:
        return "MODIFIED"  # decrement still falls into modify bucket
    return "NOCHANGE"


def detect_parent_sku(skus):
    if any(s.startswith("E3N-") for s in skus):
        return "CISCO-NETWORK-SUB"
    if any(s.startswith("SA-") or s.startswith("E3S-") for s in skus):
        return "SECURE-ACCESS-SUB"
    if any(s.startswith("LIC-") for s in skus):
        return "MERAKI-SUB"
    return "MERAKI-SUB"


def parse_acquire_into_schema(acquire_resp, ccw_deal_id):
    header = {
        "ccw_deal_id":        str(ccw_deal_id),
        "subscription_id":    None,
        "quote_name":         None,
        "deal_expiration":    None,
        "cisco_am_name":      None,
        "cisco_am_email":     None,
        "end_customer_raw":   None,
        "end_customer_name":  None,
        "total_list_price":   None,
    }

    sub_id = (
        deepfind(acquire_resp, "SubscriptionReferenceId")
        or deepfind(acquire_resp, "SubscriptionId")
        or deepfind(acquire_resp, "SubscriptionRefId")
    )
    if sub_id:
        header["subscription_id"] = str(sub_id)

    quote_name = deepfind(acquire_resp, "QuoteName") or deepfind(acquire_resp, "Description")
    if quote_name:
        header["quote_name"] = str(quote_name)

    expiration = (
        deepfind(acquire_resp, "ExpirationDate")
        or deepfind(acquire_resp, "QuoteExpirationDate")
        or deepfind(acquire_resp, "DealExpirationDate")
    )
    header["deal_expiration"] = normalize_iso_date(expiration)

    am = deepfind(acquire_resp, "AccountManager") or deepfind(acquire_resp, "Owner")
    if isinstance(am, dict):
        name = am.get("Name") or am.get("FullName") or am.get("DisplayName")
        email = am.get("Email") or am.get("EmailAddress")
        if name:
            header["cisco_am_name"] = str(name)
        if email:
            header["cisco_am_email"] = str(email)

    end_cust = (
        deepfind(acquire_resp, "EndCustomer")
        or deepfind(acquire_resp, "Customer")
    )
    if isinstance(end_cust, dict):
        name = end_cust.get("Name") or end_cust.get("CompanyName")
        if name:
            header["end_customer_raw"] = str(name)
            header["end_customer_name"] = str(name)
    elif isinstance(end_cust, str):
        header["end_customer_raw"] = end_cust
        header["end_customer_name"] = end_cust

    total_list = (
        deepfind(acquire_resp, "TotalListPrice")
        or deepfind(acquire_resp, "ExtendedListPriceTotal")
    )
    if total_list is not None:
        header["total_list_price"] = safe_float(total_list)

    # Term info — pull from the most common remaining-term field
    remaining_term_months = (
        deepfind(acquire_resp, "RemainingTermInMonths")
        or deepfind(acquire_resp, "RemainingTerm")
        or deepfind(acquire_resp, "DurationInMonths")
    )
    start_date = deepfind(acquire_resp, "StartDate") or deepfind(acquire_resp, "BillingStartDate")
    end_date = deepfind(acquire_resp, "EndDate") or deepfind(acquire_resp, "BillingEndDate")
    term_info = {
        "term_months": safe_float(remaining_term_months) if remaining_term_months is not None else None,
        "start_date":  normalize_iso_date(start_date),
        "end_date":    normalize_iso_date(end_date),
    }

    # Lines: locate the most likely list under several common keys
    lines_root = None
    for key in ("LineItems", "QuoteLineItems", "Lines", "LineItem"):
        v = deepfind(acquire_resp, key)
        if isinstance(v, list) and v:
            lines_root = v
            break
        if isinstance(v, dict):
            # Sometimes wrapped {"LineItem": [...]}
            inner = v.get("LineItem") if isinstance(v.get("LineItem"), list) else None
            if inner:
                lines_root = inner
                break

    if lines_root is None:
        return header, term_info, [], None

    raw_line_count = len(lines_root)
    consolidated = []
    for li in lines_root:
        sku = (
            deepfind(li, "PartNumber")
            or deepfind(li, "SKU")
            or deepfind(li, "ProductId")
        )
        if not sku:
            continue
        sku = str(sku).strip()

        new_qty = safe_int(deepfind(li, "NewQuantity") or deepfind(li, "Quantity"))
        existing_qty = safe_int(deepfind(li, "ExistingQuantity") or deepfind(li, "PriorQuantity"))
        qty_change = safe_int(deepfind(li, "QuantityChange"))
        if qty_change == 0 and (new_qty - existing_qty) != 0:
            qty_change = new_qty - existing_qty

        action = derive_action(li)

        billing_freq = safe_int(deepfind(li, "BillingFrequency") or deepfind(li, "PricingTermMonths") or 1) or 1
        unit_list_pm = safe_float(
            deepfind(li, "UnitListPrice")
            or deepfind(li, "UnitListPricePerMonth")
            or deepfind(li, "UnitPrice")
        )
        ext_list = safe_float(
            deepfind(li, "ExtendedListPrice")
            or deepfind(li, "ListPrice")
        )
        ext_net = safe_float(
            deepfind(li, "ExtendedNetPrice")
            or deepfind(li, "NetPrice")
        )
        billing_net_change = safe_float(deepfind(li, "BillingAmountNetChange"))
        contract_net_change = safe_float(deepfind(li, "ContractAmountNetChange"))
        remaining_term_line = safe_float(deepfind(li, "RemainingTerm") or deepfind(li, "RemainingTermInMonths"))

        unit_list_full_term = round(ext_list / new_qty, 4) if new_qty > 0 and ext_list > 0 else 0.0

        consolidated.append({
            "sku": sku,
            "action": action,
            "unit_list_price_per_month": unit_list_pm,
            "unit_list_price_full_term": unit_list_full_term,
            "new_qty": new_qty,
            "existing_qty": existing_qty,
            "net_change_qty": qty_change,
            "ext_list_all_rows": ext_list,
            "ext_list_net_change": (ext_list if action in ("ADDED", "MODIFIED") and qty_change != 0 else 0.0),
            "full_state_ext_list": ext_list,
            "net_change_ext_list": round(unit_list_full_term * qty_change, 2),
            "api": {
                "quantityChange":            qty_change,
                "remainingTerm":             remaining_term_line,
                "billingAmountNetChange":    billing_net_change,
                "contractAmountNetChange":   contract_net_change,
                "extendedListPrice":         ext_list,
                "extendedNetPrice":          ext_net,
                "billingFrequency":          billing_freq,
            },
        })

    return header, term_info, consolidated, raw_line_count


def build_summary(items):
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


def main():
    if len(sys.argv) != 2:
        print("Usage: pull_sub_mod_api.py <ccw_deal_id>", file=sys.stderr)
        sys.exit(1)

    ccw_deal_id = str(sys.argv[1]).strip()
    if not ccw_deal_id:
        print("ERROR: empty CCW Deal Id", file=sys.stderr)
        sys.exit(1)

    token = get_access_token()
    list_resp = list_quotes_for_did(token, ccw_deal_id)
    quote_id = parse_quote_id_from_list(list_resp)
    if not quote_id:
        print(f"ERROR: no quote found for DID {ccw_deal_id} in ListQuoteService response", file=sys.stderr)
        sys.exit(4)

    acquire_resp = acquire_quote(token, quote_id)
    header, term_info, items, raw_line_count = parse_acquire_into_schema(acquire_resp, ccw_deal_id)
    if not items:
        print("ERROR: AcquireQuoteService returned 0 line items", file=sys.stderr)
        sys.exit(3)

    parent_sku = detect_parent_sku([i["sku"] for i in items])
    summary = build_summary(items)

    output = {
        "source": "ccw_api",
        "file":   None,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "quote_id":   quote_id,
        "header":     header,
        "term":       term_info,
        "parent_sku": parent_sku,
        "raw_line_item_count": raw_line_count if raw_line_count is not None else len(items),
        "consolidated_line_items": items,
        "summary": summary,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
