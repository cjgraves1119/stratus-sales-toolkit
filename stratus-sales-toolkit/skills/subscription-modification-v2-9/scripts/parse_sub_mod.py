#!/usr/bin/env python3
"""
parse_sub_mod.py - Deterministic parser for CCW subscription modification xls files.

Usage:
    python3 parse_sub_mod.py <path_to_xls>

Outputs clean JSON to stdout with:
- Header data (customer, CCW DID, sub ID, AM, expiration, term months)
- Line items classified as NOCHANGE | MODIFIED | ADDED with correct quantities
- Parent SKU auto-detected from Line 1 (CISCO-NETWORK-SUB, MERAKI-SUB, etc.)
- Grouping across duplicate rows (CCW splits same SKU across rows based on pricing history)

This script handles:
- The "Pricing Term in months = 1" trap (that column is monthly billing period, NOT remaining term)
- True remaining term is derived from the "Requested For : X.XX Months" line under parent SKU
- Same SKU appearing on multiple rows (sums qty for NOCHANGE, keeps ADDED rows separate)
- Blank Existing Qty cells on ADDED rows

Exit codes:
    0 = success
    1 = file not found or unreadable
    2 = parse error (missing required data)
    3 = missing dependency (xlrd)
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def ensure_xlrd():
    """Auto-install xlrd if missing. Returns True if available."""
    try:
        import xlrd  # noqa: F401
        return True
    except ImportError:
        try:
            subprocess.run(
                ["pip", "install", "xlrd", "--break-system-packages", "--quiet"],
                check=True, capture_output=True,
            )
            import xlrd  # noqa: F401
            return True
        except Exception as e:
            print(f"ERROR: xlrd not installed and auto-install failed: {e}", file=sys.stderr)
            return False


def parse_header(df):
    """Extract header data from rows 0-30."""
    header = {
        "ccw_deal_id": None,
        "subscription_id": None,
        "quote_name": None,
        "deal_expiration": None,  # YYYY-MM-DD
        "cisco_am_name": None,
        "cisco_am_email": None,
        "end_customer_raw": None,
        "end_customer_name": None,
        "total_list_price": None,
    }

    for i in range(min(35, len(df))):
        row = df.iloc[i].tolist()
        # Find label cells
        for j, cell in enumerate(row):
            if not isinstance(cell, str):
                continue
            label = cell.strip().rstrip(":").lower()
            # Value is usually in next non-empty cell
            value = None
            for k in range(j + 1, len(row)):
                if row[k] is not None and str(row[k]).strip() not in ("", "nan"):
                    value = row[k]
                    break

            if label == "deal id" and value:
                header["ccw_deal_id"] = str(value).strip()
            elif label == "subscription id" and value:
                header["subscription_id"] = str(value).strip()
            elif label == "quote name" and value:
                header["quote_name"] = str(value).strip()
            elif label == "deal expiration" and value:
                header["deal_expiration"] = normalize_date(str(value).strip())
            elif label == "cisco account manager" and value:
                header["cisco_am_name"], header["cisco_am_email"] = parse_am(str(value))
            elif label == "end customer" and value:
                header["end_customer_raw"] = str(value).strip()
                header["end_customer_name"] = str(value).split("\n")[1].strip() if "\n" in str(value) else str(value).strip()
            elif label == "total list price" and value:
                try:
                    header["total_list_price"] = float(value)
                except (ValueError, TypeError):
                    pass

    return header


def parse_am(am_str):
    """Extract 'Name (email)' format."""
    m = re.match(r"(.+?)\s*\((.+?)\)", am_str)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return am_str.strip(), None


def normalize_date(date_str):
    """Convert 'DD-Mon-YYYY' -> 'YYYY-MM-DD'."""
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    m = re.match(r"(\d{1,2})-(\w{3})-(\d{4})", date_str)
    if m:
        day, mon_str, year = m.groups()
        mon = months.get(mon_str.lower())
        if mon:
            return f"{year}-{mon}-{day.zfill(2)}"
    return date_str


def extract_term_months(df):
    """
    CRITICAL: Extract TRUE remaining term months from the parent SKU row context.
    Looks for 'Requested For : X.XX Months and from YYYY-MM-DD to YYYY-MM-DD'
    This is NOT the 'Pricing Term in months' column (which is billing period = 1).
    """
    result = {"term_months": None, "start_date": None, "end_date": None}
    for i in range(60, min(80, len(df))):
        row_str = " ".join(str(c) for c in df.iloc[i].tolist() if c is not None and str(c) != "nan")
        m = re.search(r"Requested For\s*:\s*([\d.]+)\s*Months\s*and\s*from\s*(\d{1,2}-\w{3}-\d{4})\s*to\s*(\d{1,2}-\w{3}-\d{4})", row_str, re.IGNORECASE)
        if m:
            result["term_months"] = float(m.group(1))
            result["start_date"] = normalize_date(m.group(2))
            result["end_date"] = normalize_date(m.group(3))
            return result
    return result


def parse_line_items(df):
    """
    Parse line items section. Column layout is FIXED:
      0: # (line number, e.g. "1.1")
      1: Action (NOCHANGE / MODIFIED / ADDED)
      2: Subscription (SKU)
      3: Description
      4: Unit List Price (USD)         <- unit price PER MONTH
      5: Pricing Term in months        <- BILLING FREQUENCY (usually 1), NOT total term
      6: New Qty
      7: Existing Qty
      8: Net Change for Qty
      9: Ext. List Price (USD)         <- this IS the extended list for the qty in that row
      ...
      26: Item Quantity Change (NoChange / Increase / Decrease)

    Returns list of dicts, one per CCW row (pre-grouping).
    """
    line_items = []

    # Find header row (contains "#", "Action", "Subscription")
    header_row_idx = None
    for i in range(60, min(75, len(df))):
        row = df.iloc[i].tolist()
        if (len(row) > 2 and str(row[0]).strip() == "#" and
                str(row[1]).strip() == "Action" and str(row[2]).strip() == "Subscription"):
            header_row_idx = i
            break

    if header_row_idx is None:
        return line_items

    # Parse each row after the header
    for i in range(header_row_idx + 1, len(df)):
        row = df.iloc[i].tolist()
        line_no = row[0] if len(row) > 0 else None
        action = row[1] if len(row) > 1 else None
        sku = row[2] if len(row) > 2 else None

        # Stop at footer or blank rows
        if line_no is None or str(line_no).strip() in ("", "nan"):
            continue
        if not isinstance(action, str) or action not in ("NOCHANGE", "MODIFIED", "ADDED", "NEW"):
            # Might be the parent "1" row (CISCO-NETWORK-SUB) - capture but flag
            if str(line_no).strip() == "1" and sku in ("CISCO-NETWORK-SUB", "MERAKI-SUB", "SECURE-ACCESS-SUB"):
                continue  # parent row, skip - we derive parent from here separately
            continue

        def safe_float(v):
            try:
                return float(v) if v not in (None, "--", "nan") else 0.0
            except (ValueError, TypeError):
                return 0.0

        def safe_int(v):
            try:
                if v in (None, "--", "nan"):
                    return 0
                return int(float(v))
            except (ValueError, TypeError):
                return 0

        item = {
            "line_no": str(line_no).strip(),
            "action": action if action != "NEW" else "ADDED",  # normalize NEW -> ADDED
            "sku": str(sku).strip(),
            "unit_list_price_per_month": safe_float(row[4]),
            "new_qty": safe_int(row[6]),
            "existing_qty": safe_int(row[7]),
            "net_change_qty": safe_int(row[8]),
            "ext_list_price": safe_float(row[9]),
        }
        line_items.append(item)

    return line_items


def determine_parent_sku(df, line_items):
    """
    Determine parent SKU from the first line (line_no = '1').
    Usually one of: CISCO-NETWORK-SUB, MERAKI-SUB, SECURE-ACCESS-SUB.
    """
    # Search the data frame for the parent line directly
    header_row_idx = None
    for i in range(60, min(75, len(df))):
        row = df.iloc[i].tolist()
        if (len(row) > 2 and str(row[0]).strip() == "#" and
                str(row[1]).strip() == "Action" and str(row[2]).strip() == "Subscription"):
            header_row_idx = i
            break

    if header_row_idx is None:
        return None

    for i in range(header_row_idx + 1, min(header_row_idx + 5, len(df))):
        row = df.iloc[i].tolist()
        if len(row) > 2 and str(row[0]).strip() == "1":
            sku = str(row[2]).strip() if row[2] else None
            if sku in ("CISCO-NETWORK-SUB", "MERAKI-SUB", "SECURE-ACCESS-SUB"):
                return sku

    # Fallback: infer from SKU prefixes in line items
    skus = [li["sku"] for li in line_items]
    if any(s.startswith("SA-") or s.startswith("E3S-SA-") for s in skus):
        return "SECURE-ACCESS-SUB"
    if any(s.startswith("LIC-") or s.startswith("E3N-") for s in skus):
        return "MERAKI-SUB"
    return "MERAKI-SUB"  # safe default


def group_line_items(line_items):
    """
    Group duplicate rows (same SKU + same action) by summing quantities.
    CCW often splits the same SKU across multiple rows based on pricing history.

    Returns a list keyed by (sku, action) with consolidated quantities and
    extended list prices.
    """
    grouped = {}
    for li in line_items:
        key = (li["sku"], li["action"])
        if key not in grouped:
            grouped[key] = {
                "sku": li["sku"],
                "action": li["action"],
                "unit_list_price_per_month": li["unit_list_price_per_month"],
                "new_qty": 0,
                "existing_qty": 0,
                "net_change_qty": 0,
                "ext_list_price": 0.0,
                "source_rows": 0,
            }
        grouped[key]["new_qty"] += li["new_qty"]
        grouped[key]["existing_qty"] += li["existing_qty"]
        grouped[key]["net_change_qty"] += li["net_change_qty"]
        grouped[key]["ext_list_price"] += li["ext_list_price"]
        grouped[key]["source_rows"] += 1

    return list(grouped.values())


def consolidate_by_sku(grouped_items):
    """
    Further consolidate: merge NOCHANGE and ADDED for the same SKU into a single line
    that captures the final state.

    CRITICAL: We sum ext_list_price across ALL rows (NOCHANGE + ADDED) for a given SKU
    to get the TRUE total extended list for the full qty. This is the source of truth
    for per-unit pricing (more precise than unit_price_per_month * term_months_rounded).

    - A SKU with only NOCHANGE remains NOCHANGE.
    - A SKU with only ADDED remains ADDED.
    - A SKU with NOCHANGE + ADDED becomes MODIFIED (existing + new licenses).
    """
    by_sku = {}
    for g in grouped_items:
        sku = g["sku"]
        if sku not in by_sku:
            by_sku[sku] = []
        by_sku[sku].append(g)

    consolidated = []
    for sku, entries in by_sku.items():
        total_ext_list_all_rows = sum(e["ext_list_price"] for e in entries)

        if len(entries) == 1:
            e = entries[0]
            consolidated.append({
                "sku": sku,
                "action": e["action"],
                "unit_list_price_per_month": e["unit_list_price_per_month"],
                "new_qty": e["new_qty"],
                "existing_qty": e["existing_qty"],
                "net_change_qty": e["net_change_qty"],
                "ext_list_all_rows": total_ext_list_all_rows,
                "ext_list_net_change": e["ext_list_price"] if e["action"] in ("ADDED", "MODIFIED") else 0.0,
            })
        else:
            total_new_qty = sum(e["new_qty"] for e in entries if e["action"] in ("NOCHANGE", "MODIFIED")) + sum(e["new_qty"] for e in entries if e["action"] == "ADDED")
            total_existing_qty = sum(e["existing_qty"] for e in entries)
            total_net_change = sum(e["net_change_qty"] for e in entries)
            unit_price = entries[0]["unit_list_price_per_month"]
            ext_list_net_change = sum(e["ext_list_price"] for e in entries if e["action"] in ("ADDED", "MODIFIED"))

            consolidated.append({
                "sku": sku,
                "action": "MODIFIED",
                "unit_list_price_per_month": unit_price,
                "new_qty": total_new_qty,
                "existing_qty": total_existing_qty,
                "net_change_qty": total_net_change,
                "ext_list_all_rows": total_ext_list_all_rows,
                "ext_list_net_change": ext_list_net_change,
            })
    return consolidated


def compute_unit_list_full_term(ext_list_all_rows, new_qty, fallback_unit_per_month, term_months):
    """
    Compute unit list price for the full remaining subscription term.

    PRIMARY: Derive from file's ext_list / qty (precise to Cisco's actual math).
    FALLBACK: unit_price_per_month * term_months (less precise due to term rounding).
    """
    if new_qty > 0 and ext_list_all_rows > 0:
        return round(ext_list_all_rows / new_qty, 2)
    return round(fallback_unit_per_month * term_months, 2)


def main():
    if len(sys.argv) != 2:
        print("Usage: parse_sub_mod.py <path_to_xls>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not ensure_xlrd():
        sys.exit(3)

    import pandas as pd

    try:
        df = pd.read_excel(file_path, sheet_name="QUOTE", engine="xlrd", header=None)
    except Exception as e:
        print(f"ERROR: Cannot read QUOTE sheet: {e}", file=sys.stderr)
        sys.exit(2)

    header = parse_header(df)
    term_info = extract_term_months(df)
    raw_line_items = parse_line_items(df)
    parent_sku = determine_parent_sku(df, raw_line_items)
    grouped = group_line_items(raw_line_items)
    consolidated = consolidate_by_sku(grouped)

    # Build output
    output = {
        "file": str(file_path),
        "header": header,
        "term": term_info,
        "parent_sku": parent_sku,
        "raw_line_item_count": len(raw_line_items),
        "consolidated_line_items": [],
        "summary": {
            "total_skus": len(consolidated),
            "added_skus": 0,
            "modified_skus": 0,
            "nochange_skus": 0,
            "net_change_qty_total": 0,
        },
    }

    term_months = term_info.get("term_months") or 1.0

    for ci in consolidated:
        unit_list_full_term = compute_unit_list_full_term(
            ci["ext_list_all_rows"], ci["new_qty"],
            ci["unit_list_price_per_month"], term_months,
        )
        net_change_ext_list = round(unit_list_full_term * ci["net_change_qty"], 2)
        full_state_ext_list = round(unit_list_full_term * ci["new_qty"], 2)

        item = {
            "sku": ci["sku"],
            "action": ci["action"],
            "unit_list_price_per_month": ci["unit_list_price_per_month"],
            "unit_list_price_full_term": unit_list_full_term,
            "new_qty": ci["new_qty"],
            "existing_qty": ci["existing_qty"],
            "net_change_qty": ci["net_change_qty"],
            "net_change_ext_list": net_change_ext_list,
            "full_state_ext_list": full_state_ext_list,
        }
        output["consolidated_line_items"].append(item)

        if ci["action"] == "ADDED":
            output["summary"]["added_skus"] += 1
        elif ci["action"] == "MODIFIED":
            output["summary"]["modified_skus"] += 1
        elif ci["action"] == "NOCHANGE":
            output["summary"]["nochange_skus"] += 1
        output["summary"]["net_change_qty_total"] += ci["net_change_qty"]

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
