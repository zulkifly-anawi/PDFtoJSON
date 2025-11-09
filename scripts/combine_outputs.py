#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
from typing import List, Dict, Any, Iterable


def combine_batches(test_name: str, output_dir: str = "output") -> str:
    """Combine batch JSONs for given test into a single JSON file.

    Returns the path to the combined JSON file.
    """
    prefix = f"CAPM_{test_name.replace(' ', '_')}_Questions_"
    pattern = os.path.join(output_dir, f"{prefix}*.json")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No files matched pattern: {pattern}")

    # Extract numeric ranges and sort by start
    def parse_range(path: str):
        name = os.path.basename(path)
        m = re.search(r"Questions_(\d+)-(\d+)\.json$", name)
        if not m:
            return (10**9, 10**9)
        return (int(m.group(1)), int(m.group(2)))

    files.sort(key=parse_range)

    combined: List[Dict[str, Any]] = []
    for p in files:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"Unexpected JSON root in {p}, expected a list")
            combined.extend(data)

    out_path = os.path.join(output_dir, f"CAPM_{test_name.replace(' ', '_')}_All.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"Combined {len(files)} files -> {out_path} ({len(combined)} items)")
    return out_path


def detect_tests_in_output(output_dir: str = "output") -> List[str]:
    """Auto-detect test names based on existing batch files in output/.

    Looks for files like: CAPM_<TEST_NAME_WITH_UNDERSCORES>_Questions_*.json
    Returns a de-underscored list of test names (with spaces).
    """
    paths = glob.glob(os.path.join(output_dir, "CAPM_*_Questions_*.json"))
    names = set()
    for p in paths:
        base = os.path.basename(p)
        m = re.match(r"CAPM_(.+?)_Questions_\d+-\d+\.json$", base)
        if m:
            underscored = m.group(1)
            names.add(underscored.replace('_', ' '))
    return sorted(names)


def combine_all_tests(test_names: Iterable[str], output_dir: str = "output") -> str:
    """Combine batches across multiple tests into a single JSON file.

    Adds a `testName` field to each item.
    """
    all_items: List[Dict[str, Any]] = []
    total_files = 0

    for test_name in test_names:
        prefix = f"CAPM_{test_name.replace(' ', '_')}_Questions_"
        pattern = os.path.join(output_dir, f"{prefix}*.json")
        files = glob.glob(pattern)
        if not files:
            continue

        def parse_range(path: str):
            name = os.path.basename(path)
            m = re.search(r"Questions_(\d+)-(\d+)\.json$", name)
            if not m:
                return (10**9, 10**9)
            return (int(m.group(1)), int(m.group(2)))

        files.sort(key=parse_range)
        total_files += len(files)

        for p in files:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError(f"Unexpected JSON root in {p}, expected a list")
                for item in data:
                    item_with_test = dict(item)
                    item_with_test['testName'] = test_name
                    all_items.append(item_with_test)

    if not all_items:
        raise FileNotFoundError("No batch files found for the specified tests.")

    out_path = os.path.join(output_dir, "CAPM_All_Tests.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
    print(f"Combined {total_files} files across {len(list(test_names))} tests -> {out_path} ({len(all_items)} items)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Combine batch JSON files into consolidated JSON(s)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--test', help='Single test name, e.g. "Practice Test 2"')
    group.add_argument('--tests', nargs='+', help='Multiple test names to combine into one file')
    group.add_argument('--all-tests', action='store_true', help='Auto-detect tests from output files and combine all')
    parser.add_argument('--output-dir', default='output', help='Directory containing batch JSON files')
    args = parser.parse_args()

    if args.test:
        combine_batches(args.test, args.output_dir)
    elif args.tests:
        combine_all_tests(args.tests, args.output_dir)
    elif args.all_tests:
        detected = detect_tests_in_output(args.output_dir)
        if not detected:
            raise SystemExit("No tests detected in output/. Generate batches first.")
        print(f"Detected tests: {', '.join(detected)}")
        combine_all_tests(detected, args.output_dir)


if __name__ == '__main__':
    main()
