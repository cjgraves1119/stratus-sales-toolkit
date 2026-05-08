#!/usr/bin/env python3
"""
verify_quotes.py - Compare expected vs actual Zoho quote totals after creation.

Usage:
    python3 verify_quotes.py <expected_json> <actual_json>

Where:
    expected_json = output from build_quote_payloads.py (has expected totals)
    actual_json   = {
        "customer_quote": <result of ZohoCRM_getRecord for customer quote>,
        "op_quote":       <result of ZohoCRM_getRecord for op quote>
    }

Outputs a clear pass/fail report with line-level diff if mismatch.

Exit codes:
    0 = both quotes match expectations
    1 = mismatch (details printed)
    2 = input error
"""

import json
import sys


def extract_quote_totals(quote_record):
    """
    Pull pre-tax Sub_Total and other fields from a Zoho getRecord response.

    IMPORTANT: We verify against Sub_Total (pre-tax), NOT Grand_Total. Taxable
    accounts (Tax_Type: Regular) have sales tax auto-added by Zoho; comparing
    Grand_Total would falsely flag these quotes as mismatched even when the
    underlying pricing is correct.
    """
    if "data" in quote_record and isinstance(quote_record["data"], list) and quote_record["data"]:
        q = quote_record["data"][0]
    else:
        q = quote_record
    return {
        "id": q.get("id"),
        "quote_number": q.get("Quote_Number"),
        "subject": q.get("Subject"),
        "grand_total": q.get("Grand_Total"),
        "sub_total": q.get("Sub_Total"),
        "all_taxes_total": q.get("All_Taxes_Total") or 0,
        "tax_type": q.get("Tax_Type"),
        "line_count": len(q.get("Quoted_Items", [])),
        "line_items": q.get("Quoted_Items", []),
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: verify_quotes.py <expected_json> <actual_json>", file=sys.stderr)
        sys.exit(2)

    expected = json.load(open(sys.argv[1]))
    actual = json.load(open(sys.argv[2]))

    expected_total = expected["totals"]["customer_total"]

    customer = extract_quote_totals(actual["customer_quote"])
    op = extract_quote_totals(actual["op_quote"])

    # Verify against Sub_Total (pre-tax) — Grand_Total includes auto-tax for taxable accounts
    cust_sub = float(customer["sub_total"] or 0)
    op_sub = float(op["sub_total"] or 0)

    customer_match = abs(cust_sub - expected_total) < 0.02
    op_match = abs(op_sub - expected_total) < 0.02
    totals_equal = abs(cust_sub - op_sub) < 0.02

    lines_expected_customer = len(expected["customer_quote"]["Quoted_Items"])
    lines_expected_op = len(expected["op_quote"]["Quoted_Items"])

    customer_line_count_match = customer["line_count"] == lines_expected_customer
    op_line_count_match = op["line_count"] == lines_expected_op

    all_good = customer_match and op_match and totals_equal and customer_line_count_match and op_line_count_match

    tax_note = ""
    if customer["all_taxes_total"] or op["all_taxes_total"]:
        tax_note = f"  (tax auto-applied: customer=${customer['all_taxes_total']:.2f}, op=${op['all_taxes_total']:.2f})"

    print("=" * 60)
    print("QUOTE VERIFICATION REPORT")
    print(f"(comparing Sub_Total pre-tax; Tax_Type: {customer['tax_type']}){tax_note}")
    print("=" * 60)
    print(f"Expected total:   ${expected_total:.2f}")
    print(f"Customer quote:   ${cust_sub:.2f} pre-tax (grand=${float(customer['grand_total'] or 0):.2f})  ({customer['quote_number']})  lines: {customer['line_count']}/{lines_expected_customer}  {'PASS' if customer_match and customer_line_count_match else 'FAIL'}")
    print(f"OP quote:         ${op_sub:.2f} pre-tax (grand=${float(op['grand_total'] or 0):.2f})  ({op['quote_number']})  lines: {op['line_count']}/{lines_expected_op}  {'PASS' if op_match and op_line_count_match else 'FAIL'}")
    print(f"Customer == OP:   {'YES' if totals_equal else 'NO'}")
    print()

    if not all_good:
        print("=== MISMATCHES ===")
        if not customer_match:
            print(f"  Customer Sub_Total wrong: got ${cust_sub:.2f}, expected ${expected_total:.2f}")
        if not op_match:
            print(f"  OP Sub_Total wrong: got ${op_sub:.2f}, expected ${expected_total:.2f}")
        if not totals_equal:
            print(f"  Customer and OP Sub_Totals don't match each other: customer=${cust_sub:.2f}, op=${op_sub:.2f}")
        if not customer_line_count_match:
            print(f"  Customer quote line count wrong: got {customer['line_count']}, expected {lines_expected_customer}")
        if not op_line_count_match:
            print(f"  OP quote line count wrong: got {op['line_count']}, expected {lines_expected_op}")
        print()
        print("=== LINE-LEVEL DIFF (OP quote) ===")
        for i, exp_item in enumerate(expected["op_quote"]["Quoted_Items"]):
            if i < len(op["line_items"]):
                act_item = op["line_items"][i]
                exp_list = exp_item["List_Price"]
                act_list = act_item.get("List_Price", 0)
                exp_disc = exp_item["Discount"]
                act_disc = act_item.get("Discount", 0)
                exp_qty = exp_item["Quantity"]
                act_qty = act_item.get("Quantity", 0)
                if abs(exp_list - act_list) > 0.01 or abs(exp_disc - act_disc) > 0.01 or exp_qty != act_qty:
                    print(f"  Line {i+1}: EXPECTED qty={exp_qty} list=${exp_list} disc=${exp_disc}  |  ACTUAL qty={act_qty} list=${act_list} disc=${act_disc}")

    print("=" * 60)
    print("RESULT:", "PASS" if all_good else "FAIL")
    print("=" * 60)

    sys.exit(0 if all_good else 1)


if __name__ == "__main__":
    main()
