# GitHub Copilot Instructions for CAPM PDF→JSON Extractor

## Project Overview
This project extracts CAPM (Certified Associate in Project Management) practice test questions and answers from PDF files into standardized JSON batches for exam preparation applications.

**Core Technologies:**
- Python 3.9+
- PDF parsing: `pdfplumber` (preferred), `pypdf` (fallback)
- Testing: `pytest` with mocked fixtures
- Spec-driven development: OpenSpec framework

**Key Files:**
- `scripts/extract_questions.py` - Main extraction pipeline
- `scripts/combine_outputs.py` - Batch combiner
- `scripts/ci_validate_outputs.py` - CI validation helper
- `tests/test_parsing.py` - Unit tests with synthetic fixtures

---

## Code Style & Conventions

### Python Style
- Follow PEP 8 conventions
- Use type hints where helpful (especially function signatures)
- Write clear docstrings for all functions with Args/Returns sections
- Keep functions small and focused (<50 lines when possible)
- Use descriptive variable names: `questions_pdf`, `batch_size`, not `qp`, `bs`

### Naming Conventions
```python
# Functions: snake_case with verb prefix
def extract_questions(pdf_path: str) -> List[Dict[str, Any]]:
def validate_json_output(json_file: str) -> bool:

# Variables: descriptive snake_case
matched_data = []
batch_start = 1
question_text = ""

# Constants: UPPER_SNAKE_CASE
VALID_TOPICS = ["Project Management Fundamentals and Core Concepts", ...]
DEFAULT_BATCH_SIZE = 15
```

### Error Handling
```python
# Prefer explicit error handling with informative messages
if not os.path.exists(pdf_path):
    print(f"(extract_questions) File not found: {pdf_path}")
    return []

# Use try/except for external library calls with fallback
try:
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        # extraction logic
except Exception as e:
    # Fallback to pypdf
    try:
        from pypdf import PdfReader
        # fallback logic
    except Exception as e2:
        print(f"Could not parse PDF: {e} / {e2}")
        return []
```

---

## PDF Parsing Patterns

### Question Extraction
Questions follow this pattern in PDFs:
```
18 ) What is project management?
Options
  A) Managing projects
  B) Leading teams
  C) Both
  D) Neither
```

**Key Challenges:**
1. **Multi-line questions:** Accumulate text until first option marker
2. **Indented options:** Accept varying spaces before A), B), etc.
3. **Duplicate page numbers:** Handle "18 18) Question" format
4. **Page footers:** Strip "41/117" patterns at line end
5. **Header noise:** Skip "Options", "Option", "Answer choices"

**Regex Patterns:**
```python
# Question with optional leading number artifact
q_re = re.compile(r"^\s*(?:\d+\s+)?(\d+)\s*[\)\.-]\s*(.*)")

# Options with variant markers: A) A. A:
opt_re = re.compile(r"^\s*([A-G])\s*[\)\.:]\s*(.+)")

# Page footer cleanup
page_footer_re = re.compile(r"\b\d{1,4}\s*/\s*\d{1,4}\b$")
```

### Answer Extraction
Answers appear as:
```
76 C This is an explanation that continues
and has more detail on next line.
77) A Explanation starts right after.
78 A, B, C Multi-answer with spaced commas
```

**Pattern:**
```python
# Allows standalone headers ("33 C") with optional explanation
head_re = re.compile(r"^(\d+)\s*[\.)-]?\s+([A-G](?:\s*,\s*[A-G])*)(?:\s+(.+))?$")
```

**Accumulation Logic:**
- Capture answer letter(s) and optional initial explanation
- Continue collecting lines until next question number
- Join multi-line explanations with spaces

---

## JSON Schema & Validation

### Output Format
Each question item must include:
```json
{
  "text": "[Practice Test N] Q#) Question text...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "correctAnswer": "C" or "A,B,C",
  "explanation": "Rationale text (>=100 chars preferred)",
  "topic": "One of 4 CAPM ECO domains",
  "difficulty": "easy|medium|hard"
}
```

### Topic Classification
Map questions to CAPM exam content outline domains:
1. **Project Management Fundamentals and Core Concepts** (default)
2. **Predictive, Plan-Based Methodologies**
3. **Agile Frameworks/Methodologies**
4. **Business Analysis Frameworks**

**Keyword-based Classification:**
```python
# Check question + explanation text for domain keywords
agile_keywords = ['scrum', 'sprint', 'kanban', 'retrospective', ...]
predictive_keywords = ['waterfall', 'wbs', 'gantt', 'critical path', ...]
ba_keywords = ['requirements', 'business case', 'roi', 'swot', ...]
```

### Difficulty Estimation
Heuristic scoring based on:
- Question length (>200 chars → +1)
- Explanation length (>500 chars → +1)
- Multi-answer (comma-separated → +2)
- Complex keywords ('root cause', 'best practice', 'hybrid' → +1)

**Scoring:**
- 0-1 → "easy"
- 2-3 → "medium"
- 4+ → "hard"

---

## Testing Strategy

### Unit Tests (pytest)
Use mocked `pdfplumber` to avoid real PDF dependencies:
```python
class FakePage:
    def __init__(self, text):
        self._text = text
    def extract_text(self):
        return self._text

class FakePDF:
    def __init__(self, pages_texts):
        self.pages = [FakePage(t) for t in pages_texts]
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

def test_extract_questions_indented_options(monkeypatch):
    lines = [
        "76) What doc?",
        "  A) One",
        "    B) Two"
    ]
    fake_text = "\n".join(lines)
    fake_mod = types.SimpleNamespace(open=lambda path: FakePDF([fake_text]))
    monkeypatch.setitem(sys.modules, 'pdfplumber', fake_mod)
    # ... test assertions
```

### Validation Rules
Post-extraction validation checks:
1. All required fields present and non-empty
2. `text` starts with `[Practice Test X]`
3. `correctAnswer` letters exist in `options`
4. `explanation` length >= 100 chars (warn if shorter)
5. `topic` is one of 4 valid domains
6. `difficulty` is "easy", "medium", or "hard"

**Validation Function:**
```python
def validate_json_output(json_file: str) -> bool:
    # Load JSON, check schema, log issues
    # Return True if all valid, False otherwise
```

---

## CLI Design Patterns

### Script Arguments
```python
parser = argparse.ArgumentParser(description="CAPM PDF → JSON extractor")
parser.add_argument('--config', default='config.json', help='Path to config.json')
parser.add_argument('--skip-tests', action='store_true', help='Skip quick test_extraction()')
parser.add_argument('--strict-paths', action='store_true', 
                    help='Do not resolve missing paths; skip tests if PDFs absent')
```

### Combiner Modes
```bash
# Single test
python scripts/combine_outputs.py --test "Practice Test 2"

# Multiple tests with testName field
python scripts/combine_outputs.py --tests "Test 1" "Test 2" "Test 3"

# Auto-detect all tests in output/
python scripts/combine_outputs.py --all-tests
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Missing Questions in Output
**Cause:** Batching by count instead of number ranges  
**Solution:** Batch by question number ranges (e.g., 1-15, 16-30) to handle gaps

```python
# WRONG: Uses matched count (misses Q33 if answer missing)
for i in range(0, len(matched), batch_size):
    batch = matched[i:i+batch_size]

# CORRECT: Uses question number ranges
nums = sorted(item["question"]["number"] for item in matched)
for start in range(nums[0], nums[-1] + 1, batch_size):
    end = min(start + batch_size - 1, nums[-1])
    batch = [item for item in matched if start <= item["question"]["number"] <= end]
```

### Pitfall 2: Import Errors in CI
**Cause:** `scripts` module not in PYTHONPATH  
**Solution:** Set job-level env in GitHub Actions

```yaml
jobs:
  test:
    env:
      PYTHONPATH: ${{ github.workspace }}
    steps:
      - run: pytest -q
```

### Pitfall 3: Explanation Too Short Warnings
**Cause:** Source PDFs have terse rationale for some items  
**Solution:** Log warning but include item; flag for manual review

```python
if len(item['explanation']) < 100:
    issues.append(f"Q{q_num}: Explanation too short")
    # Still include in output, just warn
```

---

## OpenSpec Integration

### When to Create Proposals
Create a change proposal (`openspec/changes/<id>/`) when:
- Adding new features (e.g., progress bars, caching)
- Making breaking changes (API, schema modifications)
- Changing architecture (parallel processing, new dependencies)

**Skip proposals for:**
- Bug fixes (restore intended behavior)
- Typos, formatting, comments
- Non-breaking dependency updates

### Proposal Structure
```
openspec/changes/add-feature/
├── proposal.md       # Why, what, impact
├── tasks.md          # Implementation checklist
├── design.md         # (Optional) Technical decisions
└── specs/
    └── capability/
        └── spec.md   # ADDED/MODIFIED/REMOVED Requirements
```

### Workflow
1. Review `openspec/project.md` and `openspec list`
2. Scaffold proposal: `openspec/changes/<verb-led-id>/`
3. Write spec deltas with `## ADDED|MODIFIED|REMOVED Requirements`
4. Include at least one `#### Scenario:` per requirement
5. Validate: `openspec validate <id> --strict`
6. Implement tasks sequentially, mark `- [x]` when complete
7. Archive after deployment: `openspec archive <id> --yes`

---

## CI/CD Patterns

### GitHub Actions Workflow
```yaml
name: CI
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      PYTHONPATH: ${{ github.workspace }}
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
      - name: Run tests
        run: pytest -q
      - name: Run CI validation on combined outputs
        run: python scripts/ci_validate_outputs.py
```

### Dependabot Configuration
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"  # Repo root
    schedule:
      interval: "weekly"
```

---

## Performance Optimization

### Future Enhancements
1. **Caching:** Save raw extracted text to avoid re-parsing PDFs
2. **Progress bars:** Use `tqdm` for long-running extractions
3. **Parallel processing:** Process multiple tests concurrently
4. **Incremental output:** Save batches immediately, don't wait for all 150

### Memory Efficiency
```python
# Don't load all pages at once
for page in pdf.pages:
    text = page.extract_text()
    # Process immediately
    
# Clean up large objects
del large_list
import gc; gc.collect()
```

---

## Special Cases

### Image/Interactive Questions
Flag for manual review:
```python
if "<<IMAGE>>" in question_text or "drag and drop" in question_text.lower():
    item['requires_manual_review'] = True
    item['note'] = "Contains image or interactive element"
```

### Multi-Select Questions
Detect "choose two/three" pattern:
```python
if re.search(r"\(choose\s+(two|three)\)", question_text, re.IGNORECASE):
    item['choose_multi'] = True
    # Ensure correctAnswer is comma-separated: "A,B,C"
```

### Resolver Pattern
Auto-locate PDFs when configured paths missing:
```python
def _resolve_pdf_path(kind: str, configured: str) -> str:
    if os.path.exists(configured):
        return configured
    
    # Score candidates by keywords and index
    candidates = glob.glob(os.path.join('input', kind, "*.pdf"))
    
    def score(path: str) -> int:
        basename = os.path.basename(path).lower()
        s = 0
        if idx in basename: s += 2
        if kind == 'questions' and any(k in basename for k in ['question', 'test']):
            s += 1
        # ... similar for answers
        return s
    
    return max(candidates, key=score) if candidates else configured
```

---

## Code Review Checklist

Before committing extraction code:
- [ ] Handles multi-line questions and options
- [ ] Cleans page footers and duplicate numbers
- [ ] Validates answer letters exist in options
- [ ] Classifies topic and difficulty
- [ ] Includes docstrings with Args/Returns
- [ ] Has unit tests (or uses existing fixtures)
- [ ] Logs warnings for short explanations
- [ ] Batches by question number ranges (not count)
- [ ] Uses lazy imports for PDF libraries
- [ ] Follows PEP 8 style

---

## Quick Reference

### Key Regex Patterns
```python
# Question (with optional leading artifact)
r"^\s*(?:\d+\s+)?(\d+)\s*[\)\.-]\s*(.*)"

# Option (indented, variant markers)
r"^\s*([A-G])\s*[\)\.:]\s*(.+)"

# Answer header (optional explanation)
r"^(\d+)\s*[\.)-]?\s+([A-G](?:\s*,\s*[A-G])*)(?:\s+(.+))?$"

# Page footer cleanup
r"\b\d{1,4}\s*/\s*\d{1,4}\b$"
```

### Validation Thresholds
- Explanation min length: 100 chars (warn if shorter)
- Question length for difficulty: >200 chars → +1 score
- Explanation length for difficulty: >500 chars → +1 score
- Multi-answer difficulty: +2 score

### File Naming
```
# Batch outputs
CAPM_{test_name}_Questions_{start}-{end}.json

# Combined outputs
CAPM_{test_name}_All.json
CAPM_All_Tests.json  # Multi-test with testName field
```

---

## Resources & Documentation

- **OpenSpec Guide:** `openspec/AGENTS.md`
- **Project Context:** `openspec/project.md`
- **Task Tracker:** `openspec/changes/add-capm-pdf-extraction/tasks.md`
- **Original Spec:** `# 🤖 AI Coding Assistant Automation Prom.md`
- **README:** Full usage instructions and examples

**Testing:**
```bash
# Run unit tests
pytest -q

# Run with local config
python scripts/extract_questions.py --config config.local.json

# Combine outputs
python scripts/combine_outputs.py --all-tests

# Validate
python scripts/ci_validate_outputs.py
```

---

## Summary

This is a **PDF parsing + validation + batching pipeline** for CAPM exam questions. Focus on:
1. **Robust parsing** (multi-line, indents, artifacts)
2. **Validation** (schema, answer consistency)
3. **Clear logging** (warnings, errors)
4. **Testability** (mocked fixtures)
5. **OpenSpec workflow** (proposals before features)

When in doubt, check existing code patterns in `scripts/extract_questions.py` and follow the testing approach in `tests/test_parsing.py`.
