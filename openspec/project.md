# Project Context

## Purpose
[Describe your project's purpose and goals]
This project automates extraction and transformation of CAPM practice test PDFs (questions & answers)
into standardized JSON batches suitable for an exam-prep application.

## Tech Stack
- **Python 3.9+**: Primary extraction scripts (`scripts/extract_questions.py`, `scripts/combine_outputs.py`)
- **pdfplumber 0.11.4** (preferred) and **pypdf 5.0.0** (fallback): PDF text extraction
- **pytest 8.3.3**: Unit testing framework with monkeypatched fixtures for PDF parsing
- **tqdm 4.66.5**: Progress bars (prepared for future enhancements)
- **OpenSpec 0.13.0**: Spec-driven development; CLI installed globally via npm (`@fission-ai/openspec`)
- **Node.js** (optional): Used only for OpenSpec CLI; extraction runtime is pure Python

## Project Conventions

### Code Style
[Describe your code style preferences, formatting rules, and naming conventions]
- Follow PEP8 for Python. Use black for formatting where applicable.
- Use clear, small functions with docstrings and typing where helpful.

### Architecture Patterns
[Document your architectural decisions and patterns]

### Testing Strategy
- **Unit tests**: `tests/test_parsing.py` provides synthetic fixtures (mocked pdfplumber) for `extract_questions()` and `extract_answers()` to validate parsing logic without real PDFs.
- **Integration tests**: Run `python scripts/extract_questions.py --config config.local.json --skip-tests --strict-paths` for end-to-end validation on actual PDFs.
- **Post-extraction validation**: `validate_json_output()` checks schema completeness, short explanations, answer-option consistency; logs warnings/errors per batch.
- **CI**: Pytest runs on push; validator should be wired to run against sample outputs (pending).

### Git Workflow
[Describe your branching strategy and commit conventions]

## Domain Context
This repository extracts CAPM (Certified Associate in Project Management) practice test questions and answers from PDF files into JSON for an exam-prep application.

### Key challenges
- **Multi-line questions/options**: Questions and options often span multiple lines; parser accumulates continuation text.
- **Multi-select answers**: Some questions require choosing 2–3 options (e.g., "A,B,C"); parser detects and flags these.
- **Image/drag-and-drop questions**: Flagged for manual review (cannot be automated from text-only PDFs).
- **Duplicate page numbers**: Some PDFs have lines like "18 18) Question text..." where the first number is a page/line artifact; regex handles this.
- **Standalone answer headers**: Some answer entries are just "33 C" with no explanation on the same line; parser accumulates from following lines.
- **Short explanations**: Some rationale lines are terse or missing in source PDFs; validator flags these but includes them in output for manual review.

### Output schema
Each question item:
```json
{
  "text": "[Practice Test N] Q#) Question text...",
  "options": {"A": "...", "B": "...", ...},
  "correctAnswer": "A" or "A,B,C" for multi-select,
  "explanation": "Rationale text...",
  "topic": "Project Management Fundamentals and Core Concepts" | "Predictive, Plan-Based Methodologies" | "Agile Frameworks/Methodologies" | "Business Analysis Frameworks",
  "difficulty": "easy" | "medium" | "hard",
  "testName": "Practice Test N" (only in combined all-tests JSON)
}
```

## Important Constraints
[List any technical, business, or regulatory constraints]

## External Dependencies
- **Local PDF files**: Placed in `input/questions/` and `input/answers/`; no network calls or external APIs.
- **OpenSpec CLI**: Installed globally via npm (`@fission-ai/openspec@0.13.0`) for spec-driven workflow.

## Current Capabilities (as of Nov 2025)
- **Extraction**: Parses Practice Test 2 and Practice Test 3 PDFs (150 questions each) into batched JSON (10 batches per test).
- **Combining**: `scripts/combine_outputs.py` merges batches into single-test or all-tests JSON with `testName` field.
- **Validation**: Post-extraction checks for schema completeness, short explanations, and answer-option mismatches.
- **Strict mode**: `--strict-paths` flag prevents auto-resolution fallback; skips tests with missing PDFs.
- **Unit tests**: Synthetic fixtures with mocked pdfplumber; run via `pytest -q`.

## File Structure
```
PDFtoJSON/
├── input/
│   ├── questions/      # Question PDFs (e.g., Practice Test (2).pdf, (3).pdf)
│   └── answers/        # Answer PDFs with rationales
├── output/             # Generated JSON batches and combined files
├── scripts/
│   ├── extract_questions.py   # Main extractor (CLI: --config, --strict-paths, --skip-tests)
│   └── combine_outputs.py     # Combiner (CLI: --test, --tests, --all-tests)
├── tests/
│   └── test_parsing.py        # Unit tests with mocked pdfplumber
├── openspec/
│   ├── AGENTS.md
│   ├── project.md
│   └── changes/add-capm-pdf-extraction/
│       ├── proposal.md
│       ├── tasks.md
│       └── specs/capm-extraction/spec.md
├── config.json                # Multi-test config (Practice Test 1, 2, 3)
├── config.local.json          # Single-test config (Practice Test 2)
├── config.local.practice3.json # Single-test config (Practice Test 3)
├── requirements.txt
└── README.md
```

