## Why

The project needs an automated, repeatable, and auditable pipeline to extract CAPM practice test questions
and answers from vendor-provided PDFs and emit validated JSON batches compatible with our exam-prep app.

Manual extraction is slow, error-prone, and hard to review. A spec-driven change proposal will allow
clear requirements, review, and incremental implementation with testing and validation.

## What changes

- Add a new capability: `capm-pdf-extraction` that ingests questions and answers PDFs and produces
  batched JSON files following the agreed schema.

- Provide CLI/script `scripts/extract_questions.py` (Python) with modular functions for extraction,
  matching, classification, difficulty estimation, batching, and validation.

- Populate `input/` and `output/` scaffolding and a `requirements.txt` for dependencies.

## Impact

- Affects: file layout (`scripts/`, `input/`, `output/`), CI test harness, and documentation.
- New dependencies: `pdfplumber` or `pypdf` (Python) and dev tooling for OpenSpec (already installed).
- Non-breaking: This change adds a new capability and does not modify existing features.

## Acceptance criteria

- [x] `scripts/extract_questions.py` exists and contains the documented functions and docstrings.
- [x] Running the script with a small sample (or sample text-mode fixture) produces at least one validated JSON file in `output/` matching the target schema.
- [x] `openspec/changes/add-capm-pdf-extraction/tasks.md` is complete and checked off when implementation done.
- [x] End-to-end extraction for Practice Test 2 and Practice Test 3 (150 questions each) produces batched and combined JSON outputs.
- [x] Unit tests pass (`pytest -q`) with mocked pdfplumber fixtures.
- [x] Combiner (`scripts/combine_outputs.py`) supports single-test, multi-test, and auto-detect modes.
- [ ] CI wiring: GitHub Actions workflow to run pytest and validator on sample outputs (pending).

## Timeline / Priority

- Priority: High (automates a manual and time-consuming task)
- Target: scaffold and skeleton implementation in the next iteration (this change proposal)
