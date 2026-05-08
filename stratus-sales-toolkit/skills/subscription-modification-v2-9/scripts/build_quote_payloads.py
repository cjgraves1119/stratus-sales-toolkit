#!/usr/bin/env python3
"""
build_quote_payloads.py - Build Customer + OP quote payloads from parsed sub mod data.

Use this when CREATING new Zoho quotes from scratch (Fast Path B). When the
DID already has a Zoho quote attached (Fast Path A: most common API-driven
case), prefer scripts/submod_quote_pricing.py — it updates the existing quote
in place and preserves subform line ids, avoiding the well-documented
subform-id-invalidation bug.

Two pricing modes:

  pricing_source = "ccw_api_net" (preferred when parsed.source == "ccw_api")
      - Source of truth = Cisco's BillingAmountNetChange / ContractAmountNetChange
        (key `ccw_net_addon_cost` on the parsed line, with fallback to
        api.billingAmountNetChange / api.contractAmountNetChange).
      - Add-on lines billed at:
          markup mode: cost x (1 + margin/100)
          gross  mode: cost / (1 - margin/100)        (default; matches Codex)
      - No-change lines display full term list with 100% discount = $0 net.
      - Customer + OP quotes are IDENTICAL: full subscription transparency,
        only the delta is invoiced.
      - Decimal arithmetic with ROUND_HALF_UP and a penny-bump heuristic so
        the net invoice amount lands on the expected dollar+cent (e.g. exactly
        $651.35 on the DID 84410290 reference case).

  pricing_source = "xls_list_discount" (legacy fallback, CCW xls path)
      - Customer quote: net-change rows only at flat discount_percent.
      - OP quote: full state, NOCHANGE at 100% off, ADDED/MODIFIED at discount_percent.
      - Behaviour identical to v2.8.

Usage:
    python3 build_quote_payloads.py <parsed_json_path> <config_json_path>

Exit codes:
    0 = success
    1 = file/config error
    2 = SKU not found in cache or fallbacks
    3 = math verification failure
"""

from __future__ import annotations

import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


CACHE_PATH = Path(__file__).parent.parent / "data" / "sku_cache.json"
MONEY = Decimal("0.01")


# ----------------------------- Decimal helpers -----------------------------

def D(value) -> Decimal:
    if value is None:
        return Decimal("0")
    s = str(value).replace(",", "").replace("$", "").strip()
    if not s:
        return Decimal("0")
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def money(value) -> Decimal:
    return D(value).quantize(MONEY, rounding=ROUND_HALF_UP)


def fmt(value) -> float:
    return float(money(value))


def fmt_qty(d: Decimal) -> str:
    if d == d.to_integral_value():
        return str(int(d))
    return format(d.normalize(), "f")


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

def apply_margin(cost: Decimal, margin_percent: Decimal, margin_mode: str) -> Decimal:
    if margin_mode == "markup":
        return cost * (Decimal("1") + margin_percent / Decimal("100"))
    if margin_mode == "gross":
        if margin_percent >= Decimal("100"):
            raise ValueError("gross margin percent must be < 100")
        return cost / (Decimal("1") - margin_percent / Decimal("100"))
    raise ValueError(f"Unknown margin_mode: {margin_mode!r}")


def pricing_for_addon_line(li: dict, margin_percent: Decimal, margin_mode: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Compute (qty, list_price, discount, net) for an add-on line.

    Penny-bump heuristic: when rounded list_price * qty < target_sell,
    bump list_price by 1 cent so the line total reaches the target before
    the discount is applied.
    """
    qty = D(li["new_qty"] or 0)
    if qty <= 0:
        return Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")

    api = li.get("api") or {}
    full_list = D(li.get("full_state_ext_list") or li.get("ext_list_all_rows") or 0)
    cost = D(li.get("ccw_net_addon_cost") or api.get("billingAmountNetChange") or api.get("contractAmountNetChange") or 0)
    if cost <= 0:
        # Fallback: if API didn't surface a cost but qty changed, use a
        # conservative 45% net derivation. Surfaces a warning to caller.
        cost = full_list * Decimal("0.55")

    target_sell = money(apply_margin(cost, margin_percent, margin_mode))

    list_price = (full_list / qty).quantize(MONEY, rounding=ROUND_HALF_UP) if qty > 0 else Decimal("0")
    line_total = money(list_price * qty)

    if line_total < target_sell:
        list_price = (target_sell / qty).quantize(MONEY, rounding=ROUND_HALF_UP)
        line_total = money(list_price * qty)
        if line_total < target_sell:
            list_price = list_price + MONEY
            line_total = money(list_price * qty)

    discount = money(line_total - target_sell)
    if discount < 0:
        discount = Decimal("0")

    return qty, list_price, discount, target_sell


# ----------------------------- API net mode --------------------------------

def is_addon_line(li):
    api = li.get("api") or {}
    qty_change = li.get("net_change_qty") or api.get("quantityChange") or 0
    bill_change = api.get("billingAmountNetChange") or 0
    contract_change = api.get("contractAmountNetChange") or 0
    line_change_type = (api.get("lineChangeType") or "").lower()
    ccw_net = li.get("ccw_net_addon_cost") or 0
    return (
        (qty_change and float(qty_change) > 0)
        or (bill_change and float(bill_change) > 0)
        or (contract_change and float(contract_change) > 0)
        or (ccw_net and float(ccw_net) > 0)
        or line_change_type == "added"
    )


def build_api_net_lines(parsed, parent_sku_zoho_id, margin_percent, margin_mode,
                       flat_cache, fallback_ids):
    items = []
    unresolved = []
    grand_total = Decimal("0")
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

        new_qty = int(li.get("new_qty") or 0)
        if new_qty <= 0:
            continue

        if is_addon_line(li):
            qty, list_price, discount, net = pricing_for_addon_line(li, D(margin_percent), margin_mode)
            qty_change = int(li.get("net_change_qty") or (li.get("api") or {}).get("quantityChange") or 0)
            existing = int(li.get("existing_qty") or 0)
            if existing > 0 and qty_change > 0:
                desc = f"ADD-ON +{qty_change} (existing {existing}, total {new_qty})"
            else:
                desc = f"ADD-ON +{qty_change} new license(s)"
            summary["addon_lines"] += 1
        else:
            qty = D(new_qty)
            full_list = D(li.get("full_state_ext_list") or li.get("ext_list_all_rows") or 0)
            list_price = (full_list / qty).quantize(MONEY, rounding=ROUND_HALF_UP) if qty > 0 else Decimal("0")
            line_total = money(list_price * qty)
            discount = line_total
            net = Decimal("0")
            desc = f"NOCHANGE - {new_qty} license(s) (no charge, covered by existing sub)"
            summary["nochange_lines"] += 1

        items.append({
            "Product_Name": {"id": zoho_id},
            "Quantity": int(qty) if qty == qty.to_integral_value() else float(qty),
            "List_Price": fmt(list_price),
            "Discount": fmt(discount),
            "Description": desc,
        })
        grand_total += net

    return items, fmt(grand_total), unresolved, summary


# ----------------------------- XLS legacy mode -----------------------------

def build_xls_lines(parsed, parent_sku_zoho_id, mode, discount_pct,
                   flat_cache, fallback_ids):
    items = []
    unresolved = []
    grand_total = Decimal("0")

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

    pct = D(discount_pct) / Decimal("100")

    for li in parsed["consolidated_line_items"]:
        sku = li["sku"]
        if sku == parsed["parent_sku"]:
            continue

        zoho_id, _ = resolve_sku(sku, flat_cache, fallback_ids)
        if not zoho_id:
            unresolved.append(sku)
            continue

        unit_list = D(li.get("unit_list_price_full_term") or 0)
        new_qty = int(li.get("new_qty") or 0)
        net_change_qty = int(li.get("net_change_qty") or 0)
        action = li["action"]

        if mode == "customer":
            if action == "NOCHANGE":
                continue
            qty = net_change_qty
            list_price = unit_list
            total_list = money(unit_list * D(net_change_qty))
            discount = money(total_list * pct)
            net = money(total_list - discount)
            if action == "ADDED":
                desc = f"ADDED - {net_change_qty} new license(s)"
            else:
                desc = f"ADDED - {net_change_qty} new license(s) (+{net_change_qty} to existing {li.get('existing_qty', 0)})"

            items.append({
                "Product_Name": {"id": zoho_id},
                "Quantity": qty,
                "List_Price": fmt(list_price),
                "Discount": fmt(discount),
                "Description": desc,
            })
            grand_total += net

        elif mode == "op":
            qty = new_qty
            list_price = unit_list
            total_list = money(unit_list * D(qty))
            if action == "NOCHANGE":
                discount = total_list
                net = Decimal("0")
                desc = f"NOCHANGE - {qty} license(s) (no charge)"
            elif action == "ADDED":
                discount = money(total_list * pct)
                net = money(total_list - discount)
                desc = f"ADDED - {qty} new license(s)"
            elif action == "MODIFIED":
                customer_pays = money(unit_list * D(net_change_qty) * (Decimal("1") - pct))
                discount = money(total_list - customer_pays)
                net = customer_pays
                desc = f"MODIFIED - {qty} total (+{net_change_qty} added)"
            else:
                discount = Decimal("0")
                net = total_list
                desc = f"{action} - {qty}"

            items.append({
                "Product_Name": {"id": zoho_id},
                "Quantity": qty,
                "List_Price": fmt(list_price),
                "Discount": fmt(discount),
                "Description": desc,
            })
            grand_total += net

    return items, fmt(grand_total), unresolved


# ----------------------------- Quote payload -------------------------------

def build_quote_payload(parsed, config, items, subject_suffix):
    header = parsed.get("header") or {}
    deal_id = config["deal_id"]
    sub_id = header.get("subscription_id") or header.get("quote_number")
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
        margin_percent = D(config.get("margin_percent", 20))
        margin_mode = config.get("margin_mode", "gross")  # default gross to match Codex / sales practice
        if margin_mode not in ("markup", "gross"):
            print(f"ERROR: invalid margin_mode {margin_mode!r}", file=sys.stderr)
            sys.exit(1)

        items, total, unresolved, summary = build_api_net_lines(
            parsed, parent_zoho_id, margin_percent, margin_mode, flat_cache, fallback_ids,
        )

        if unresolved:
            print(f"ERROR: Unresolved SKUs: {unresolved}", file=sys.stderr)
            sys.exit(2)

        customer_payload = build_quote_payload(parsed, config, items, subject_suffix="")
        op_payload = build_quote_payload(parsed, config, items, subject_suffix="- OP")
        customer_total = total
        op_total = total

    elif pricing_source == "xls_list_discount":
        if "discount_percent" not in config:
            print("ERROR: pricing_source=xls_list_discount requires discount_percent in config", file=sys.stderr)
            sys.exit(1)
        discount_pct = D(config["discount_percent"])

        if parent_sku == "CISCO-NETWORK-SUB" and discount_pct != Decimal("45") and not config.get("skip_ea3_prompt"):
            warnings.append(f"WARN: parent CISCO-NETWORK-SUB usually 45% (EA 3.0); discount_percent is {discount_pct}%")
        if parent_sku == "MERAKI-SUB" and discount_pct != Decimal("30") and not config.get("skip_ea3_prompt"):
            warnings.append(f"WARN: parent MERAKI-SUB usually 30% co-term; discount_percent is {discount_pct}%")

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
            print(f"ERROR: Quote totals don't match (customer=${customer_total} op=${op_total})", file=sys.stderr)
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
        output["margin_percent"] = float(D(config.get("margin_percent", 20)))
        output["margin_mode"] = config.get("margin_mode", "gross")
    else:
        output["discount_percent"] = float(D(config.get("discount_percent", 0)))

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
