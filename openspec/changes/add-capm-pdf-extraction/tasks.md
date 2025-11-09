## 1. Implementation
- [x] 1.1 Create project scaffold: `input/questions`, `input/answers`, `output`, `scripts/` and README
- [x] 1.2 Add `requirements.txt` with `pdfplumber`, `pypdf`, `tqdm`, and `pytest`
- [x] 1.3 Add `scripts/extract_questions.py` with function signatures and top-of-file prompt comment
- [x] 1.4 Implement `extract_questions()` parsing logic and unit tests for sample text
	- Robust regex handles leading spaces, duplicate page numbers (e.g., "18 18)"), variant markers (A) A. A:), and header cleanup; unit tests with mocked pdfplumber pass.
- [x] 1.5 Implement `extract_answers()` parsing logic and tests
	- Supports variants `51 C`, `51) C`, standalone headers ("33 C"), and multi-line explanations; unit tests added.
- [x] 1.6 Implement `match_questions_answers()` and JSON emitter
	- Batches output by question number ranges; handles gaps (e.g., missing Q33 answer).
- [x] 1.7 Implement `classify_topic()` and `estimate_difficulty()` helpers
	- Keyword-based topic classifier (4 CAPM ECO domains); heuristic difficulty scorer.
- [x] 1.8 Implement `validate_json_output()` and local validation
	- Post-extraction validator checks schema, short explanations, answer-option consistency; CI wiring pending.
- [x] 1.9 Add `scripts/combine_outputs.py` to merge batches
	- Supports `--test`, `--tests`, `--all-tests` for single-test, multi-test, and auto-detect combining; adds `testName` field in multi-test mode.

## 2. QA & Validation
- [x] 2.1 Create sample text fixtures / small sample PDFs for iterative testing
	- Synthetic-text fixtures via monkeypatched `pdfplumber` in unit tests (`tests/test_parsing.py`).
- [x] 2.2 Run extraction on sample and iterate to fix edge cases
	- Practice Test 2 and 3 processed end-to-end (150 questions each); resolved duplicate leading numbers, standalone answer headers, page footer artifacts.
- [x] 2.3 Review flagged mismatches and image/manual-review cases
	- Validator flags short explanations (source PDF has terse rationale for some items); no blocking errors for available PDFs.
	- Manual-review flags added for <<IMAGE>> and "drag and drop" questions.

## 3. Documentation
- [x] 3.1 Document how to run the script locally (README) and how to add new PDFs
	- README includes quickstart, config usage, `--strict-paths` flag, naming tips for auto-resolution, testing instructions, and combiner usage.
- [x] 3.2 Add a short note in `openspec/project.md` referencing the change and usage
	- Project context updated with tech stack, dependencies, and testing strategy.

## 4. Follow-ups (post-merge)
- [ ] 4.1 Add caching of raw extracted text for faster re-runs
- [ ] 4.2 Add progress bars and parallel processing for larger runs
- [ ] 4.3 Optionally add a Node.js version or wrapper if required
