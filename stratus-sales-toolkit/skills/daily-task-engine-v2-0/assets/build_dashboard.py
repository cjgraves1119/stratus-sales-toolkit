#!/usr/bin/env python3
"""
Pre-built dashboard injector for Daily Task Engine.

Reads task JSON from a file and injects it into the HTML dashboard template
using string find/replace (not regex, which fails on JSON with \\u escapes).

Usage:
    python build_dashboard.py <template_path> <data_path> <output_path>

Arguments:
    template_path  Path to assets/task-dashboard.html
    data_path      Path to JSON file containing the task data array
    output_path    Path where the populated dashboard HTML should be written

Example:
    python assets/build_dashboard.py assets/task-dashboard.html /tmp/task_data.json /mnt/outputs/task-dashboard.html
"""
import sys
import json


def build_dashboard(template_path: str, data_path: str, output_path: str) -> None:
    """Inject task data into dashboard template using string operations."""

    # Read template
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Read task data JSON
    with open(data_path, "r", encoding="utf-8") as f:
        task_json = f.read().strip()

    # Validate JSON is parseable (catches malformed data early)
    try:
        json.loads(task_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {data_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Find injection point using string search (no regex needed)
    marker = "const SAMPLE_DATA = ["
    pos = template.find(marker)

    if pos == -1:
        print(f"ERROR: Marker '{marker}' not found in template.", file=sys.stderr)
        sys.exit(1)

    # Build injection: set window.TASK_DATA_INJECT before the SAMPLE_DATA line
    inject_line = f"\n    window.TASK_DATA_INJECT = {task_json};\n    "

    # Insert the injection right before the marker
    modified = template[:pos] + inject_line + template[pos:]

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(modified)

    print(f"Dashboard written to {output_path} ({len(modified):,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python build_dashboard.py <template_path> <data_path> <output_path>")
        sys.exit(1)

    build_dashboard(sys.argv[1], sys.argv[2], sys.argv[3])
