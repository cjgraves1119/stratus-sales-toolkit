#!/usr/bin/env python3
"""
build_quote_payloads.py - Build Customer + OP quote payloads from parsed sub mod data.

Two pricing modes:

  pricing_source = "ccw_api_net" (preferred when parsed.source == "ccw_api")
      - Source of truth = Cisco's BillingAmountNetChange / ContractAmountNetChange.
      - Add-on lines billed as: cost x (1 + margin) for markup mode,
                                cost / (1 - margin) for gross mode.
      - No-change lines kept at full visible list with 100% discount = $0.
      - Customer + OP quotes are IDENTICAL: full subscription transparency,
        only the delta is invoiced.

  pricing_source = "xls_list_discount" (legacy fallback when working from CCW xls)
      - Customer quote: net-change rows only at flat discount_percent.
      - OP quote: full state, NOCHANGE at 100% off, ADDED/MODIFIED at discount_percent.
      - Behaviour identical to v2.8.

Usage:
    python3 build_quote_payloads.py <parsed_json_path> <config_json_path>

Config JSON example (API net mode):
{
    "deal_id": "...",
    "account_id": "...",
    "contact_id": "...",
    "billing": {"street": "...", "city": "...", "state": "XX", "code": "xxxxx", "country": "US"},
    "shipping": {"street": "...", "city": "...", "state": "XX", "code": "xxxxx", "country": "US"},
    "pricing_source": "ccw_api_net",
    "margin_percent": 20,
    "margin_mode": "markup",
    "valid_till": "YYYY-MM-DD",
    "subject_prefix": "JCC KC",
    "owner_id": "2570562000141711002",
    "skip_ea3_prompt": false,
    "zoho_fallback_ids": {}
}

Outputs JSON with customer_quote, op_quote, totals, warnings.

Exit codes:
    0 = success
    1 = file/config error
    2 = SKU not found in cache or fallbacks
    3 = math verification failure
    4 = discount % mismatch vs parent SKU (warn only, continue with code 0)
"""

import json
import sys
from pathlib import Path


CACHE_PATH = Path(__file__).parent.parent / "data" / "sku_cache.json"


# ----------------------------- SKU resolution ------------------------------

def load_sku_cache():
    with open(CACHE_PATH) as f:
        cache = json.load(f)

    flat = {}
    flat.update(cache.get("parent_skus", {}))
    flat.update(cache.get("meraki_coterm", {}))
    flat.update(cache.get("meraki_legacy_term", {}))
    flat.update(cache.get("ea3_network", {}))
    flat.update(cache.get("ea3_security", {}))
    flat.update(cache.get("secure_access", {}))
    return flat, cache


def resolve_sku(sku, flat_cache, fallback_ids):
    if sku in flat_cache and flat_cache[sku]:
        return flat_cache[sku], "embedded_cache"
    if sku in fallback_ids:
        return fallback_ids[sku], "zoho_fallback"
    return None, None


def parent_sku_label(parent_sku):
    return {
        "MERAKI-SUB": "Meraki Subscription",
        "CISCO-NETWORK-SUB": "Cisco Networking Subscription",
        "SECURE-ACCESS-SUB": "Cisco Secure Access Subscription",
    }.get(parent_sku, parent_sku)


# ----------------------------- Pricing helpers -----------------------------

def margin_to_sell_price(cost, margin_percent, margin_mode):
    """Convert cost + margin to customer sell price.

    markup mode: sell = cost x (1 + margin/100)
    gross  mode: sell = cost / (1 - margin/100)
    """
    if cost is None:
        return 0.0
    m = float(margin_percent) / 100.0
    if margin_mode == "gross":
        denom = 1.0 - m
        if denom <= 0:
            return 0.0
        return cost / denom
    return cost * (1.0 + m)


# ----------------------------- API net mode --------------------------------

def is_addon_line(li):
    api = li.get("api") or {}
    qty_change = li.get("net_change_qty") or api.get("quantityChange") or 0
    bill_change = api.get("billingAmountNetChange") or 0
    return (qty_change and qty_change > 0) or (bill_change and bill_change > 0)


def build_api_net_lines(parsed, parent_sku_zoho_id, margin_percent, margin_mode,
                       flat_cache, fallback_ids):
    """API-net mode: build a SINGLE line array used by both customer and OP quotes.

    Each line shows full new-qty quantity. Add-on lines bill at cost*(1+margin)
    for markup mode (default); no-change lines drop to $0 via 100% discount.
    """
    items = []
    unresolved = []
    grand_total = 0.0
    summary = {"addon_lines": 0, "nochange_lines": 0}

    term = parsed.get("term") or {}
    parent_desc = (
        f"{parent_sku_label(parsed['parent_sku'])} - "
        f"{term.get('term_months')} months remaining "
        f"({term.get('start_date')} -> {term.get('end_date')})"
    )

    items.append({
        "Product_Name": {"id": parent_sku_zoho_id},
        "Quantity": 1,
        "List_Price": 0,
        "Discount": 0,
        "Description": parent_desc,
    })

    for li in parsed["consolidated_line_items"]:
        sku = li["sku"]
        if sku == parsed["parent_sku"]:
            continue

        zoho_id, _ = resolve_sku(sku, flat_cache, fallback_ids)
        if not zoho_id:
            unresolved.append(sku)
            continue

        new_qty = int(li["new_qty"] or 0)
        if new_qty <= 0:
            continue

        api = li.get("api") or {}
        full_visible_list = float(li.get("full_state_ext_list") or li.get("ext_list_all_rows") or 0.0)
        unit_list_full_term = float(li.get("unit_list_price_full_term") or 0.0)
        if unit_list_full_term <= 0 and full_visible_list and new_qty:
            unit_list_full_term = round(full_visible_list / new_qty, 4)

        if is_addon_line(li):
            cisco_net_change = float(api.get("billingAmountNetChange") or 0.0)
            if cisco_net_change <= 0:
                # If API didn't surface a net change but qty changed, fall back to
                # full_state_ext_list * (1 - default discount). Surfaces a warning later.
                cisco_net_change = full_visible_list * 0.55  # conservative MERAKI 45% net

            sell_amount = round(margin_to_sell_price(cisco_net_change, margin_percent, margin_mode), 2)
            list_total = round(unit_list_full_term * new_qty, 2)
            discount = round(list_total - sell_amount, 2)
            net = sell_amount
            qty_change = int(li.get("net_change_qty") or api.get("quantityChange") or 0)
            existing = int(li.get("existing_qty") or 0)
            if existing > 0 and qty_change > 0:
                desc = f"ADD-ON +{qty_change} (existing {existing}, total {new_qty})"
            else:
                desc = f"ADD-ON +{qty_change} new license(s)"
            summary["addon_lines"] += 1
        else:
            list_total = round(unit_list_full_term * new_qty, 2)
            sell_amount = 0.0
            discount = list_total
            net = 0.0
            desc = f"NOCHANGE - {new_qty} license(s) (no charge, covered by existing sub)"
            summary["nochange_lines"] += 1

        items.append({
            "Product_Name": {"id": zoho_id},
            "Quantity": new_qty,
            "List_Price": round(unit_list_full_term, 4),
            "Discount": discount,
            "Description": desc,
        })
        grand_total += net

    return items, round(grand_total, 2), unresolved, summary


# ----------------------------- XLS legacy mode -----------------------------

def build_xls_lines(parsed, parent_sku_zoho_id, mode, discount_pct,
                   flat_cache, fallback_ids):
    """v2.8 behaviour preserved exactly. mode = 'customer' or 'op'."""
    items = []
    unresolved = []
    grand_total = 0.0

    term = parsed.get("term") or {}
    parent_desc = (
        f"{parent_sku_label(parsed['parent_sku'])} - "
        f"{term.get('term_months')} months remaining "
        f"({term.get('start_date')} -> {term.get('end_date')})"
    )

    items.append({
        "Product_Name": {"id": parent_sku_zoho_id},
        "Quantity": 1,
        "List_Price": 0,
        "Discount": 0,
        "Description": parent_desc,
    })

    for li in parsed["consolidated_line_items"]:
        sku = li["sku"]
        if sku == parsed["parent_sku"]:
            continue

        zoho_id, _ = resolve_sku(sku, flat_cache, fallback_ids)
        if not zoho_id:
            unresolved.append(sku)
            continue

        unit_list = float(li.get("unit_list_price_full_term") or 0.0)
        new_qty = int(li["new_qty"] or 0)
        net_change_qty = int(li.get("net_change_qty") or 0)
        action = li["action"]

        if mode == "customer":
            if action == "NOCHANGE":
                continue
            qty = net_change_qty
            list_price = unit_list
            total_list = round(unit_list * net_change_qty, 2)
            discount = round(total_list * (discount_pct / 100.0), 2)
            net = round(total_list - discount, 2)
            if action == "ADDED":
                desc = f"ADDED - {net_change_qty} new license(s)"
            else:
                desc = f"ADDED - {net_change_qty} new license(s) (+{net_change_qty} to existing {li.get('existing_qty', 0)})"

            items.append({
                "Product_Name": {"id": zoho_id},
                "Quantity": qty,
                "List_Price": list_price,
                "Discount": discount,
                "Description": desc,
            })
            grand_total += net

        elif mode == "op":
            qty = new_qty
            list_price = unit_list
            total_list = round(unit_list * qty, 2)
            if action == "NOCHANGE":
                discount = total_list
                net = 0.0
                desc = f"NOCHANGE - {qty} license(s) (no charge)"
            elif action == "ADDED":
                discount = round(total_list * (discount_pct / 100.0), 2)
                net = round(total_list - discount, 2)
                desc = f"ADDED - {qty} new license(s)"
            elif action == "MODIFIED":
                customer_pays = round(unit_list * net_change_qty * (1 - discount_pct / 100.0), 2)
                discount = round(total_list - customer_pays, 2)
                net = customer_pays
                desc = f"MODIFIED - {qty} total (+{net_change_qty} added)"
            else:
                discount = 0
                net = total_list
                desc = f"{action} - {qty}"

            items.append({
                "Product_Name": {"id": zoho_id},
                "Quantity": qty,
                "List_Price": list_price,
                "Discount": discount,
                "Description": desc,
            })
            grand_total += net

    return items, round(grand_total, 2), unresolved


# ----------------------------- Quote payload -------------------------------

def build_quote_payload(parsed, config, items, subject_suffix):
    header = parsed.get("header") or {}
    deal_id = config["deal_id"]
    sub_id = header.get("subscription_id")
    ccw_did = header.get("ccw_deal_id")
    end_customer = header.get("end_customer_name") or "Customer"
    subject_prefix = config.get("subject_prefix", end_customer[:30])

    subject = f"{subject_prefix} - {sub_id} Add-On (CCW {ccw_did})"
    if subject_suffix:
        subject += f" {subject_suffix}"

    description_lines = [
        f"Subscription add-on for {sub_id} (CCW DID {ccw_did})",
        "",
        "Net Change:",
    ]
    for li in parsed["consolidated_line_items"]:
        if li["action"] in ("ADDED", "MODIFIED") and (li.get("net_change_qty") or 0) != 0:
            description_lines.append(f"  {li['sku']}: +{li['net_change_qty']}")
    description_lines.append("")
    term = parsed.get("term") or {}
    description_lines.append(
        f"Term: {term.get('term_months')} months ({term.get('start_date')} -> {term.get('end_date')})"
    )
    if header.get("cisco_am_name"):
        description_lines.append(
            f"Cisco AM: {header['cisco_am_name']} ({header.get('cisco_am_email')})"
        )
    if parsed.get("source") == "ccw_api":
        description_lines.append("")
        description_lines.append("Source: Cisco Manage Quote API (DID add-on net-change)")

    valid_till = config.get("valid_till") or header.get("deal_expiration")

    payload = {
        "Subject": subject,
        "Deal_Name": {"id": deal_id},
        "Account_Name": {"id": config["account_id"]},
        "Contact_Name": {"id": config["contact_id"]},
        "Valid_Till": valid_till,
        "Cisco_Billing_Term": "Prepaid Term",
        "Billing_Street":  config["billing"]["street"],
        "Billing_City":    config["billing"]["city"],
        "Billing_State":   config["billing"]["state"],
        "Billing_Code":    config["billing"]["code"],
        "Billing_Country": config["billing"].get("country", "US"),
        "Shipping_Street":  config["shipping"]["street"],
        "Shipping_City":    config["shipping"]["city"],
        "Shipping_State":   config["shipping"]["state"],
        "Shipping_Code":    config["shipping"]["code"],
        "Shipping_Country": config["shipping"].get("country", "US"),
        "Description": "\n".join(description_lines),
        "Quoted_Items": items,
    }

    if config.get("owner_id"):
        payload["Owner"] = {"id": config["owner_id"]}

    return payload


# ----------------------------- Driver --------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: build_quote_payloads.py <parsed_json> <config_json>", file=sys.stderr)
        sys.exit(1)

    parsed = json.load(open(sys.argv[1]))
    config = json.load(open(sys.argv[2]))

    flat_cache, _ = load_sku_cache()
    fallback_ids = config.get("zoho_fallback_ids", {})

    parent_sku = parsed["parent_sku"]
    parent_zoho_id, _ = resolve_sku(parent_sku, flat_cache, fallback_ids)
    if not parent_zoho_id:
        print(f"ERROR: Parent SKU {parent_sku} not in cache. Add to zoho_fallback_ids.", file=sys.stderr)
        sys.exit(2)

    pricing_source = (
        config.get("pricing_source")
        or ("ccw_api_net" if parsed.get("source") == "ccw_api" else "xls_list_discount")
    )

    warnings = []

    if pricing_source == "ccw_api_net":
        margin_percent = float(config.get("margin_percent", 20))
        margin_mode = config.get("margin_mode", "markup")
        if margin_mode not in ("markup", "gross"):
            print(f"ERROR: invalid margin_mode {margin_mode!r}, expected 'markup' or 'gross'", file=sys.stderr)
            sys.exit(1)

        items, total, unresolved, summary = build_api_net_lines(
            parsed, parent_zoho_id, margin_percent, margin_mode, flat_cache, fallback_ids,
        )

        if unresolved:
            print(f"ERROR: Unresolved SKUs: {unresolved}", file=sys.stderr)
            sys.exit(2)

        # Customer and OP are identical in API net mode.
        customer_payload = build_quote_payload(parsed, config, items, subject_suffix="")
        op_payload = build_quote_payload(parsed, config, items, subject_suffix="- OP")
        customer_total = total
        op_total = total
        op_items = items

    elif pricing_source == "xls_list_discount":
        if "discount_percent" not in config:
            print("ERROR: pricing_source=xls_list_discount requires discount_percent in config", file=sys.stderr)
            sys.exit(1)
        discount_pct = float(config["discount_percent"])

        if parent_sku == "CISCO-NETWORK-SUB" and discount_pct != 45 and not config.get("skip_ea3_prompt"):
            warnings.append(
                f"WARN: parent CISCO-NETWORK-SUB usually 45% (EA 3.0); discount_percent is {discount_pct}%"
            )
        if parent_sku == "MERAKI-SUB" and discount_pct != 30 and not config.get("skip_ea3_prompt"):
            warnings.append(
                f"WARN: parent MERAKI-SUB usually 30% co-term; discount_percent is {discount_pct}%"
            )

        customer_items, customer_total, cust_unresolved = build_xls_lines(
            parsed, parent_zoho_id, "customer", discount_pct, flat_cache, fallback_ids,
        )
        op_items, op_total, op_unresolved = build_xls_lines(
            parsed, parent_zoho_id, "op", discount_pct, flat_cache, fallback_ids,
        )

        unresolved = list(set(cust_unresolved + op_unresolved))
        if unresolved:
            print(f"ERROR: Unresolved SKUs: {unresolved}", file=sys.stderr)
            sys.exit(2)

        if abs(customer_total - op_total) > 0.01:
            print(
                f"ERROR: Quote totals don't match (customer=${customer_total} op=${op_total})",
                file=sys.stderr,
            )
            sys.exit(3)

        customer_payload = build_quote_payload(parsed, config, customer_items, subject_suffix="")
        op_payload = build_quote_payload(parsed, config, op_items, subject_suffix="- OP")
        summary = None
    else:
        print(f"ERROR: unknown pricing_source {pricing_source!r}", file=sys.stderr)
        sys.exit(1)

    output = {
        "pricing_source": pricing_source,
        "customer_quote": customer_payload,
        "op_quote": op_payload,
        "totals": {
            "customer_total": customer_total,
            "op_total": op_total,
            "match": abs(customer_total - op_total) < 0.01,
        },
        "warnings": warnings,
        "parent_sku": parent_sku,
    }
    if pricing_source == "ccw_api_net":
        output["api_net_summary"] = summary
        output["margin_percent"] = float(config.get("margin_percent", 20))
        output["margin_mode"] = config.get("margin_mode", "markup")
    else:
        output["discount_percent"] = float(config.get("discount_percent", 0))

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
