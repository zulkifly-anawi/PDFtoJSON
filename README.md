# CAPM PDF → JSON Extractor

A specialized Python tool that automates the extraction and transformation of CAPM (Certified Associate in Project Management) practice test questions and answers from PDF files into standardized, machine-readable JSON format for exam preparation applications.

## Overview

This tool eliminates the manual, error-prone process of extracting practice test data from PDFs by:
- **Parsing dual PDF sources**: Extracting questions/options from one PDF and answers/explanations from another
- **Intelligent matching**: Automatically combining questions with their corresponding answers and rationales
- **Smart classification**: Categorizing questions into CAPM knowledge domains and estimating difficulty levels
- **Quality validation**: Ensuring output integrity through comprehensive validation checks
- **Batch processing**: Organizing questions into configurable batches for efficient consumption

OpenSpec is used to plan and track changes. See `openspec/`.

## Key Features

### PDF Processing
- **Dual PDF extraction**: Processes separate question and answer PDFs
- **Multi-line text handling**: Correctly accumulates questions, options, and explanations spanning multiple lines
- **Extended option support**: Handles up to 7 answer choices (A-G), not just standard 4-option formats
- **Multi-select questions**: Supports questions with multiple correct answers (e.g., "A,B,C")
- **Robust parsing**: Uses pdfplumber as primary parser with pypdf as fallback for reliability
- **Artifact cleaning**: Removes page numbers and formatting artifacts automatically

### Intelligence Layer
- **Topic classification**: Automatically categorizes questions into 4 CAPM ECO domains:
  - Project Management Fundamentals and Core Concepts
  - Predictive, Plan-Based Methodologies
  - Agile Frameworks/Methodologies
  - Business Analysis Frameworks
- **Difficulty estimation**: Analyzes question complexity, length, and keywords to estimate difficulty (easy/medium/hard)
- **Special case detection**: Flags questions with images, drag-and-drop, or other special requirements

### Quality & Reliability
- **Comprehensive validation**: Checks for required fields, answer consistency, explanation quality, and more
- **Path auto-resolution**: Intelligently finds missing PDF files based on naming conventions
- **Batch organization**: Configurable batch sizes (default: 15 questions per batch)
- **Error handling**: Detailed logging and graceful failure recovery
- **Testing**: Unit tests with mocked PDF fixtures (no real PDFs required)

### Production Ready
- **CI/CD integration**: GitHub Actions workflow with automated testing
- **Dependency management**: Automated updates via Dependabot
- **Flexible configuration**: JSON-based config supporting multiple practice tests
- **Combining outputs**: Tools to merge batches into single or multi-test collections

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

## Output Format

Each extracted question is formatted as a JSON object with the following structure:

```json
{
  "text": "[Practice Test 2] Q18) What is the primary benefit of using an Agile approach?",
  "options": {
    "A": "Reduced project costs",
    "B": "Early and continuous delivery of value",
    "C": "Elimination of all project risks",
    "D": "Guaranteed project success"
  },
  "correctAnswer": "B",
  "explanation": "Agile methodologies focus on early and continuous delivery of valuable software through iterative development cycles. This allows stakeholders to see working increments regularly and provide feedback, ensuring the product meets their evolving needs...",
  "topic": "Agile Frameworks/Methodologies",
  "difficulty": "medium"
}
```

**Output Files:**
- Batches are saved to `output/<test_name>/<test_name>_batch_N.json`
- Combined outputs can be generated with `combine_outputs.py`
- All output files include comprehensive validation metadata

## How It Works

The extraction pipeline follows these steps:

1. **Configuration Loading**: Reads test definitions from `config.json` (PDF paths, batch sizes)
2. **Question Extraction**:
   - Opens question PDF using pdfplumber (or pypdf fallback)
   - Uses regex patterns to identify question numbers, options (A-G), and text
   - Accumulates multi-line content until next question boundary
   - Cleans formatting artifacts and page numbers
3. **Answer Extraction**:
   - Parses answer PDF with format: "NUMBER LETTER(s) Explanation"
   - Handles single answers (e.g., "51 C") and multiple answers (e.g., "56 A,B,C")
   - Accumulates multi-line explanations
4. **Matching**: Combines questions with corresponding answers and validates consistency
5. **Classification**:
   - Categorizes questions into CAPM knowledge domains using keyword matching
   - Estimates difficulty based on length, complexity, and multi-answer factors
6. **JSON Generation**: Creates batched output files with standardized structure
7. **Validation**: Performs comprehensive checks on required fields, answer consistency, and explanation quality

## Technical Stack

- **Python 3.9+**: Core language
- **pdfplumber 0.11.8**: Primary PDF text extraction library
- **pypdf 6.2.0**: Fallback PDF parser for reliability
- **pytest 8.3.3+**: Testing framework with fixture support
- **GitHub Actions**: CI/CD automation
- **OpenSpec**: Spec-driven development methodology

## OpenSpec

- Proposal and tasks: `openspec/changes/add-capm-pdf-extraction/`
- Project context: `openspec/project.md`

Use `openspec validate --strict` to validate proposals/specs.

## Repository Structure

```
PDFtoJSON/
├── scripts/
│   ├── extract_questions.py      # Main extraction engine (628 lines)
│   ├── combine_outputs.py        # Batch combiner utility
│   └── ci_validate_outputs.py    # CI validation helper
├── tests/
│   └── test_parsing.py           # Unit tests with mocked PDFs
├── input/
│   ├── questions/                # Question PDFs (gitignored)
│   └── answers/                  # Answer PDFs (gitignored)
├── output/                       # Generated JSON batches (gitignored)
├── openspec/                     # Spec-driven development docs
│   ├── project.md                # Project context
│   └── changes/                  # Change proposals and specs
├── config.json                   # Multi-test configuration
├── config.local.json             # Local development config
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Testing

Run unit tests (uses monkeypatched pdfplumber, no real PDFs required):

```bash
pytest -q
```

The test suite includes:
- Multi-option parsing tests (A-G format)
- Multi-line explanation handling
- Various answer format validation
- All tests use mocked PDF fixtures for fast, reproducible testing

## Combining Outputs

After extraction, you can combine batch files in several ways:

**Combine all batches for a single test:**
```bash
python scripts/combine_outputs.py --test "Practice Test 2"
```
Output: `output/combined_Practice_Test_2.json`

**Auto-detect and combine all tests:**
```bash
python scripts/combine_outputs.py --all-tests
```
This automatically detects all tests in `output/` and creates a combined file with `testName` field added to each question.

**Specify multiple tests explicitly:**
```bash
python scripts/combine_outputs.py --tests "Practice Test 1" "Practice Test 2" "Practice Test 3"
```

**Custom output directory:**
```bash
python scripts/combine_outputs.py --all-tests --output-dir /path/to/output
```

## Advanced Usage

### Command Line Arguments

**extract_questions.py:**
- `--config PATH`: Path to configuration file (default: `config.json`)
- `--skip-tests`: Skip running pytest validation after extraction
- `--strict-paths`: Disable auto-resolution; only process tests with existing PDF paths

**combine_outputs.py:**
- `--test NAME`: Combine batches for a single test
- `--tests NAME [NAME ...]`: Combine batches for multiple specific tests
- `--all-tests`: Auto-detect and combine all tests
- `--output-dir PATH`: Custom output directory (default: `output/`)

### Configuration Options

Edit `config.json` to customize extraction behavior:

```json
{
  "tests": [
    {
      "name": "Practice Test 1",
      "questions_pdf": "input/questions/practice_test_1_questions.pdf",
      "answers_pdf": "input/answers/practice_test_1_answers.pdf",
      "batch_size": 15
    }
  ]
}
```

- **name**: Identifier for the test (used in output filenames and question text)
- **questions_pdf**: Path to PDF containing questions and options
- **answers_pdf**: Path to PDF containing correct answers and explanations
- **batch_size**: Number of questions per batch file (default: 15)

## CI/CD Integration

The repository includes GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Installs dependencies
- Runs pytest test suite
- Validates outputs automatically
- Triggers on push and pull requests

Dependabot is configured for weekly dependency updates.

## Notes

- **Main extraction engine**: `scripts/extract_questions.py` (628 lines)
- **Lazy imports**: PDF parsers are imported lazily; the script works even without PDF libs when using sample fixtures or dry runs
- **Auto-resolution**: Missing PDF paths are automatically resolved using intelligent naming conventions
- **Strict mode**: Use `--strict-paths` flag to disable auto-resolution and only process tests with valid paths
- **Batch configuration**: Default batch size is 15 questions; configurable per test in `config.json`

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

Contributions are welcome! Please open issues or pull requests for:

**Improvements:**
- Enhanced PDF parsing for edge cases (tables, complex layouts, special characters)
- Additional CAPM topic classification keywords
- Better difficulty estimation algorithms
- Performance optimizations (caching, parallel processing)
- Support for other exam formats beyond CAPM

**Bug Reports:**
- PDF parsing failures or incorrect extractions
- Answer matching issues
- Validation false positives/negatives

**Feature Requests:**
- Additional output formats (CSV, XML, database export)
- Web UI for extraction monitoring
- Real-time validation dashboards
- Integration with exam prep platforms

Please follow existing code style and include tests for new features.

## License

MIT License - See [LICENSE](LICENSE) file for details.