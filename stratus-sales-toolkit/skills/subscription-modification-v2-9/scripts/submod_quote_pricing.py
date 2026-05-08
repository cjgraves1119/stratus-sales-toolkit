#!/usr/bin/env python3
"""
Build deterministic Zoho quote-line pricing updates for a CCW subscription mod.

This script does not talk to Zoho directly. It takes:
  1. CCW parsed JSON from pull_sub_mod_api.py
  2. A fetched Zoho Quote JSON containing Quoted_Items with subform ids

It outputs the exact Zoho update body needed to:
  - keep all subscription lines visible,
  - discount no-change lines to $0,
  - bill add-on lines only for Cisco net change plus margin,
  - preserve duplicate SKUs by matching occurrence order.

Example:
  python3 scripts/submod_quote_pricing.py \
    --ccw-parsed /tmp/ccw_84459955_parsed.json \
    --zoho-quote /tmp/zoho_fetch_quote_lines_84459955.json \
    --quote-id 2570562000405039063 \
    --margin 20 \
    --margin-mode gross \
    --output /tmp/zoho_quote_update_84459955.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


MONEY = Decimal("0.01")

def fmt_qty(d):
    """Render a Decimal quantity without scientific notation."""
    if d == d.to_integral_value():
        return str(int(d))
    return format(d.normalize(), "f")


def as_decimal(value: Any) -> Decimal:
    raw = str(value or "0").replace(",", "").replace("$", "").strip()
    return Decimal(raw or "0")


def money_decimal(value: Decimal | float | int | str) -> Decimal:
    return as_decimal(value).quantize(MONEY, rounding=ROUND_HALF_UP)


def money(value: Decimal | float | int | str) -> float:
    return float(money_decimal(value))


def load_json(path: str) -> Any:
    text = Path(path).read_text()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Codex/MCP output files can occasionally contain prose/log text around
        # the final JSON. Keep this fallback strict enough to avoid guessing.
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def first_record(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"][0] if payload["data"] else {}
    if isinstance(payload, dict):
        return payload
    raise ValueError("Expected a JSON object or a Zoho {data:[...]} response")


def quote_lines(quote: dict[str, Any]) -> list[dict[str, Any]]:
    lines = quote.get("Quoted_Items") or quote.get("quoted_items")
    if not isinstance(lines, list):
        raise ValueError("Zoho quote JSON must include Quoted_Items")
    return lines


def product_code(line: dict[str, Any]) -> str:
    for key in ("Product_Code", "product_code", "SKU", "sku"):
        if line.get(key):
            return str(line[key]).strip()
    product = line.get("Product_Name") or {}
    if isinstance(product, dict):
        for key in ("Product_Code", "product_code", "code"):
            if product.get(key):
                return str(product[key]).strip()
    return ""


def line_total(line: dict[str, Any]) -> Decimal:
    if line.get("Total") is not None:
        return as_decimal(line["Total"])
    return as_decimal(line.get("List_Price")) * as_decimal(line.get("Quantity"))


def line_discount(line: dict[str, Any]) -> Decimal:
    return as_decimal(line.get("Discount"))


def apply_margin(cost: Decimal, percent: Decimal, mode: str) -> Decimal:
    if mode == "markup":
        return cost * (Decimal("1") + percent / Decimal("100"))
    if mode == "gross":
        if percent >= Decimal("100"):
            raise ValueError("gross margin percent must be less than 100")
        return cost / (Decimal("1") - percent / Decimal("100"))
    raise ValueError(f"Unknown margin mode: {mode}")


@dataclass
class ExpectedLine:
    sku: str
    quantity: Decimal
    full_list: Decimal
    target_sell: Decimal
    discount: Decimal
    list_price: Decimal
    description: str
    ccw_net: Decimal
    action: str


def is_addon(line: dict[str, Any]) -> bool:
    qty_change = as_decimal(line.get("net_change_qty"))
    ccw_net = as_decimal(line.get("ccw_net_addon_cost"))
    action = str(line.get("action") or "").upper()
    return qty_change > 0 or ccw_net > 0 or action in {"ADDED", "MODIFIED"}


def build_expected_lines(parsed: dict[str, Any], margin: Decimal, margin_mode: str) -> list[ExpectedLine]:
    expected: list[ExpectedLine] = []
    parent = parsed.get("parent_sku")
    term = parsed.get("term") or {}

    if parent:
        expected.append(
            ExpectedLine(
                sku=parent,
                quantity=Decimal("1"),
                full_list=Decimal("0"),
                target_sell=Decimal("0"),
                discount=Decimal("0"),
                list_price=Decimal("0"),
                description=(
                    f"{parent} - {term.get('term_months')} months remaining "
                    f"({term.get('start_date')} -> {term.get('end_date')})"
                ),
                ccw_net=Decimal("0"),
                action="PARENT",
            )
        )

    for line in parsed.get("consolidated_line_items", []):
        sku = str(line.get("sku") or "").strip()
        if not sku or sku == parent:
            continue

        qty = as_decimal(line.get("new_qty"))
        qty_change = as_decimal(line.get("net_change_qty"))
        full_list = as_decimal(line.get("full_state_ext_list"))
        ccw_net = as_decimal(line.get("ccw_net_addon_cost"))
        action = str(line.get("action") or "")
        list_price = full_list / qty if qty > 0 else Decimal("0")

        if is_addon(line) and ccw_net > 0:
            target_sell = apply_margin(ccw_net, margin, margin_mode)
            description = (
                f"ADD-ON - {fmt_qty(qty)} total shown; billing only "
                f"+{fmt_qty(qty_change)} added license(s). Cisco net change "
                f"${money(ccw_net):.2f}; {money(margin):g}% {margin_mode} applied."
            )
        elif is_addon(line):
            target_sell = Decimal("0")
            description = "ADD-ON metadata present but Cisco net change is $0; shown for transparency."
        else:
            target_sell = Decimal("0")
            description = f"NOCHANGE - {fmt_qty(qty)} license(s), covered under existing subscription; no additional charge."

        discount = full_list - target_sell
        if discount < 0:
            discount = Decimal("0")
            if qty > 0:
                list_price = target_sell / qty
                full_list = target_sell

        expected.append(
            ExpectedLine(
                sku=sku,
                quantity=qty,
                full_list=full_list,
                target_sell=target_sell,
                discount=discount,
                list_price=list_price,
                description=description,
                ccw_net=ccw_net,
                action=action,
            )
        )

    return expected


def map_quote_lines_by_sku(lines: list[dict[str, Any]]) -> dict[str, deque[dict[str, Any]]]:
    by_sku: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
    for line in lines:
        sku = product_code(line)
        if sku:
            by_sku[sku].append(line)
    return by_sku


def build_update(parsed: dict[str, Any], quote: dict[str, Any], quote_id: str | None, margin: Decimal, margin_mode: str, delete_extra: bool) -> dict[str, Any]:
    expected_lines = build_expected_lines(parsed, margin, margin_mode)
    existing_lines = quote_lines(quote)
    by_sku = map_quote_lines_by_sku(existing_lines)

    update_items: list[dict[str, Any]] = []
    line_report: list[dict[str, Any]] = []
    warnings: list[str] = []
    missing: list[str] = []

    for expected in expected_lines:
        existing = by_sku.get(expected.sku, deque()).popleft() if by_sku.get(expected.sku) else None
        if not existing:
            missing.append(expected.sku)
            continue
        if not existing.get("id"):
            warnings.append(f"Quote line for {expected.sku} has no subform id; cannot update it")
            continue

        payload_qty = expected.quantity
        payload_list_price = money_decimal(expected.list_price)
        payload_target = money_decimal(expected.target_sell)
        payload_line_total = money_decimal(payload_list_price * payload_qty)

        if payload_qty > 0 and payload_line_total < payload_target:
            payload_list_price = (payload_target / payload_qty).quantize(MONEY, rounding=ROUND_HALF_UP)
            payload_line_total = money_decimal(payload_list_price * payload_qty)
            if payload_line_total < payload_target:
                payload_list_price += MONEY
                payload_line_total = money_decimal(payload_list_price * payload_qty)

        # Zoho calculates line value from rounded unit price * quantity. Let the
        # discount absorb penny rounding so no-change lines stay exactly $0.
        payload_discount = money_decimal(payload_line_total - payload_target)
        if payload_discount < 0:
            payload_discount = Decimal("0")

        update_line = {
            "id": existing["id"],
            "Quantity": float(payload_qty),
            "List_Price": money(payload_list_price),
            "Discount": money(payload_discount),
            "Description": expected.description,
        }
        update_items.append(update_line)
        line_report.append(
            {
                "line_id": existing["id"],
                "sku": expected.sku,
                "quantity": money(expected.quantity),
                "ccw_full_list": money(expected.full_list),
                "ccw_net_addon_cost": money(expected.ccw_net),
                "target_pre_tax_sell": money(expected.target_sell),
                "discount": money(payload_discount),
                "action": expected.action,
            }
        )

    extras = [line for queue in by_sku.values() for line in queue]
    if extras and delete_extra:
        update_items.extend({"id": line["id"], "_delete": None} for line in extras if line.get("id"))
    elif extras:
        warnings.append(
            "Zoho quote has extra unmatched lines: "
            + ", ".join(f"{product_code(line)}:{line.get('id')}" for line in extras)
        )

    expected_pre_tax = sum(line.target_sell for line in expected_lines)
    existing_pre_tax = sum(line_total(line) - line_discount(line) for line in existing_lines)

    payload_record: dict[str, Any] = {"Quoted_Items": update_items}
    if quote_id:
        payload_record["id"] = quote_id

    return {
        "status": "ok" if not missing else "missing_lines",
        "quote_id": quote_id or quote.get("id"),
        "ccw_deal_id": parsed.get("header", {}).get("ccw_deal_id"),
        "ccw_quote_number": parsed.get("header", {}).get("quote_number"),
        "summary": {
            "expected_pre_tax_total": money(expected_pre_tax),
            "existing_pre_tax_total": money(existing_pre_tax),
            "line_count_expected": len(expected_lines),
            "line_count_matched": len(line_report),
            "line_count_existing": len(existing_lines),
            "margin_percent": money(margin),
            "margin_mode": margin_mode,
        },
        "missing_skus": missing,
        "warnings": warnings,
        "line_report": line_report,
        "zoho_update_body": {"data": [payload_record]},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ccw-parsed", required=True, help="JSON output from pull_sub_mod_api.py")
    parser.add_argument("--zoho-quote", required=True, help="Fetched Zoho quote JSON with Quoted_Items")
    parser.add_argument("--quote-id", help="Zoho quote record id; defaults to id in --zoho-quote")
    parser.add_argument("--margin", default="20", help="Margin percent. Default: 20")
    parser.add_argument("--margin-mode", default="gross", choices=("gross", "markup"), help="Default: gross")
    parser.add_argument("--delete-extra", action="store_true", help="Include _delete entries for unmatched Zoho quote lines")
    parser.add_argument("--output", help="Write full output JSON to this path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    parsed = load_json(args.ccw_parsed)
    quote = first_record(load_json(args.zoho_quote))
    quote_id = args.quote_id or quote.get("id")

    output = build_update(
        parsed=parsed,
        quote=quote,
        quote_id=quote_id,
        margin=as_decimal(args.margin),
        margin_mode=args.margin_mode,
        delete_extra=args.delete_extra,
    )

    rendered = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n")
    print(rendered)
    return 0 if output["status"] == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
