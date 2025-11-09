# CAPM PDF → JSON Extractor

This project automates extraction of CAPM practice test questions and answers from PDFs into
standardized JSON batches for an exam-prep application.

OpenSpec is used to plan and track changes. See `openspec/`.

## Quickstart

1. (Optional) Create/activate the Python venv
2. Install dependencies
3. Place PDFs under `input/questions/` and `input/answers/`
4. Run the extractor

```bash
# 1) (Optional) create venv
# python3 -m venv .venv && source .venv/bin/activate

# 2) install deps
pip install -r requirements.txt

# 3) run extractor (uses config.json)
python scripts/extract_questions.py --config config.json

# or use the provided local config pointing to the included sample files
python scripts/extract_questions.py --config config.local.json --skip-tests

# to avoid auto-resolving missing paths (only process tests whose paths exist)
python scripts/extract_questions.py --config config.json --strict-paths
```

## Config

See `config.json`. Update `tests` array with your actual question/answer PDF paths.

- A convenience `config.local.json` is provided that points to the sample Practice Test 2 PDFs that
  are present in `input/`.

Naming tips for best auto-resolution when paths are missing:
- Place question PDFs under `input/questions/` with names containing `practice_test` or `test` and the test number.
- Place answer PDFs under `input/answers/` with names containing `answers` or `rationale` and the test number.

## OpenSpec

- Proposal and tasks: `openspec/changes/add-capm-pdf-extraction/`
- Project context: `openspec/project.md`

Use `openspec validate --strict` to validate proposals/specs.

## Notes

- The initial extractor is implemented in Python (`scripts/extract_questions.py`).
- PDF parsers are imported lazily; the script will work even without the PDF libs when using sample
  text fixtures or dry runs.

## Testing

Run unit tests (uses monkeypatched pdfplumber, no real PDFs required):

```bash
pytest -q

## Publishing to GitHub

1. Create a new GitHub repository and copy the HTTPS URL.

2. Initialize git (if not already), add remote, and push:

```bash
git init
git add .
git commit -m "Initial CAPM PDF→JSON extractor"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

3. CI will run on push (runs pytest). Large PDFs and outputs are ignored by `.gitignore`.

## Contributing

Please open issues or PRs for:
- Adding CI validation for produced JSON (validator currently local)
- Caching and parallel processing improvements
- Additional PDF edge case handling

```

## Combining outputs

Combine all batches for a single test into one file:

```bash
python scripts/combine_outputs.py --test "Practice Test 2"
```

Auto-detect tests present in `output/` and combine them into a single file with a `testName` field:

```bash
python scripts/combine_outputs.py --all-tests
```

Or specify multiple tests explicitly:

```bash
python scripts/combine_outputs.py --tests "Practice Test 1" "Practice Test 2" "Practice Test 3"
```