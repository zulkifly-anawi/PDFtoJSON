#!/usr/bin/env python3
"""CI validation helper: run validate_json_output() on combined outputs and fail if issues found."""
from __future__ import annotations
import glob
import json
import os
import sys

from scripts.extract_questions import validate_json_output


def main():
    # Prefer the combined all-tests file if present
    candidates = glob.glob(os.path.join('output', 'CAPM_*_All.json'))
    if not candidates:
        print('(ci-validate) No combined JSON files found in output/; skipping validation.')
        return 0

    all_ok = True
    for p in sorted(candidates):
        ok = validate_json_output(p)
        if not ok:
            all_ok = False

    return 0 if all_ok else 2


if __name__ == '__main__':
    sys.exit(main())
