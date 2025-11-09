#!/usr/bin/env python3
"""
CAPM PDF → JSON Extractor (skeleton)

Spec-driven by OpenSpec. See:
- Project context: openspec/project.md
- Proposal/tasks: openspec/changes/add-capm-pdf-extraction/
- Detailed functional prompt: `# 🤖 AI Coding Assistant Automation Prom.md`

This skeleton provides function signatures and docstrings as specified. Implementations will be added
incrementally following the OpenSpec tasks.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple

# Note: PDF libraries are imported lazily inside functions to avoid hard dependency for dry runs.


def extract_questions(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract questions from PDF maintaining:
    1. Question number
    2. Full question text (handle multi-line)
    3. All options (A, B, C, D, sometimes E, F, G)
    4. Handle special formatting (bold, newlines)

    Returns a list of question dicts:
    {
      'number': int,
      'text': str,
      'options': { 'A': str, 'B': str, ... }
    }

    Implementation notes (to be completed):
    - Use pdfplumber or pypdf to extract text per page
    - Detect question blocks via regex
      * Question: r"^(\d+)\s*\)\s*(.*)" (number followed by close paren)
      * Options: r"^([A-G])\)\s*(.+)"
    - Accumulate multi-line question text until first option
    - Continue collecting options until next question starts or block ends
    - Preserve special characters and normalize whitespace carefully
    """
    # Attempt to read PDF and produce structured questions list.
    # Safe behavior: if file missing or parser unavailable, return [].
    if not os.path.exists(pdf_path):
        print(f"(extract_questions) File not found: {pdf_path}")
        return []

    lines: List[str] = []
    text: Optional[str] = None

    # Prefer pdfplumber; fallback to pypdf text extraction
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    lines.extend(page_text.splitlines())
    except Exception as e:
        # Fallback to pypdf
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    lines.extend(page_text.splitlines())
        except Exception as e2:
            print(f"(extract_questions) Could not parse PDF using pdfplumber or pypdf: {e} / {e2}")
            return []

    # Normalize whitespace
    norm_lines = [re.sub(r"\s+", " ", ln).strip() for ln in lines]

    questions: List[Dict[str, Any]] = []
    current_q: Optional[Dict[str, Any]] = None
    collecting_options = False
    current_option_letter: Optional[str] = None

    # Regexes
    # Allow optional leading page/line numbers and different delimiters for questions
    # Examples matched: "18) ...", "18 . ...", "18- ...", and lines like "18 18) ..."
    q_re = re.compile(r"^\s*(?:\d+\s+)?(\d+)\s*[\)\.-]\s*(.*)")
    # Accept A) A. A: variants, with optional leading spaces
    opt_re = re.compile(r"^\s*([A-G])\s*[\)\.:]\s*(.+)")

    # Cleanup helper to strip page footer artifacts like "41/117" at end of line
    page_footer_re = re.compile(r"\b\d{1,4}\s*/\s*\d{1,4}\b$")
    def clean_line(s: str) -> str:
        s2 = s.strip()
        s2 = re.sub(page_footer_re, "", s2).strip()
        return s2

    def finalize_current():
        nonlocal current_q
        if current_q is not None:
            # Trim text
            current_q["text"] = re.sub(r"\s+", " ", current_q.get("text", "").strip())
            # Trim options
            opts = current_q.get("options", {})
            for k, v in list(opts.items()):
                opts[k] = re.sub(r"\s+", " ", v.strip())
            questions.append(current_q)
            current_q = None

    for raw in norm_lines:
        raw = clean_line(raw)
        if not raw:
            # Ignore blank lines
            continue

        # Skip common non-content headers that sometimes appear between question text and options
        if raw.lower() in {"options", "option", "answer choices", "answers"}:
            continue

        m_q = q_re.match(raw)
        if m_q:
            # New question starts; finalize previous
            finalize_current()
            num = int(m_q.group(1))
            q_text_initial = m_q.group(2).strip()
            current_q = {
                "number": num,
                "text": q_text_initial,
                "options": {},
            }
            collecting_options = False
            current_option_letter = None
            continue

        if current_q is None:
            # Not inside a question block; skip
            continue

        m_opt = opt_re.match(raw)
        if m_opt:
            collecting_options = True
            current_option_letter = m_opt.group(1)
            current_q["options"][current_option_letter] = m_opt.group(2).strip()
            continue

        # If we are collecting options, treat non-matching lines as continuation of last option
        if collecting_options and current_option_letter is not None:
            prev = current_q["options"].get(current_option_letter, "")
            # Join with space
            current_q["options"][current_option_letter] = (prev + " " + raw).strip()
        else:
            # Otherwise, it's additional question text
            prev_q_text = current_q.get("text", "")
            current_q["text"] = (prev_q_text + " " + raw).strip()

    # finalize tail
    finalize_current()

    # Post-process: handle special cases flags
    for q in questions:
        q_text = q.get("text", "")
        if "<<IMAGE>>" in q_text or "drag and drop" in q_text.lower():
            q.setdefault("requires_manual_review", True)
            q.setdefault("note", "Contains image or interactive element")

        # Detect choose two/three for downstream validation
        if re.search(r"\(choose\s+(two|three)\)", q_text, re.IGNORECASE):
            q.setdefault("choose_multi", True)

    return questions


def extract_answers(pdf_path: str) -> Dict[int, Dict[str, str]]:
    """
    Extract answers and match to question numbers.

    Pattern: NUMBER LETTER(s) Explanation text...

    Handle:
    1. Single answers: "51 C"
    2. Multiple answers: "56 A,B,C" or "62 A,E"
    3. Multi-line explanations
    4. References to PMBOK/Agile Practice Guide

    Returns a dict keyed by question number:
    { 51: { 'correct': 'C', 'explanation': '...' }, ... }

    Implementation notes (to be completed):
    - Use pdfplumber or pypdf
    - Regex root: r"^(\d+)\s+([A-G,]+)\s+(.+)" (explanation continues to next match)
    - Merge lines until next question number
    - Clean CRLF and normalize quotes
    """
    if not os.path.exists(pdf_path):
        print(f"(extract_answers) File not found: {pdf_path}")
        return {}

    lines: List[str] = []

    # Prefer pdfplumber; fallback to pypdf
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    lines.extend(page_text.splitlines())
    except Exception as e:
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    lines.extend(page_text.splitlines())
        except Exception as e2:
            print(f"(extract_answers) Could not parse PDF using pdfplumber or pypdf: {e} / {e2}")
            return {}

    norm_lines = [re.sub(r"\s+", " ", ln).strip() for ln in lines]

    # Pattern: number, letters (comma-separated), explanation start
    # Allow: "51 C ...", "51) C ...", "51. C ...", and multi answers with optional spaces: "A, B, C"
    # Allow head lines without immediate explanation text (e.g., "33 C")
    head_re = re.compile(r"^(\d+)\s*[\.)-]?\s+([A-G](?:\s*,\s*[A-G])*)(?:\s+(.+))?$")
    page_footer_re = re.compile(r"\b\d{1,4}\s*/\s*\d{1,4}\b$")
    def _clean_answer_line(s: str) -> str:
        s2 = s.strip()
        s2 = re.sub(page_footer_re, "", s2).strip()
        return s2

    answers: Dict[int, Dict[str, str]] = {}
    current_num: Optional[int] = None
    current_correct: str = ""
    current_expl_lines: List[str] = []

    def flush_current():
        nonlocal current_num, current_correct, current_expl_lines
        if current_num is not None:
            explanation = re.sub(r"\s+", " ", " ".join(current_expl_lines).strip())
            answers[current_num] = {
                "correct": current_correct,
                "explanation": explanation,
            }
        current_num = None
        current_correct = ""
        current_expl_lines = []

    for raw in norm_lines:
        raw = _clean_answer_line(raw)
        if not raw:
            continue

        m = head_re.match(raw)
        if m:
            # New answer block
            flush_current()
            current_num = int(m.group(1))
            current_correct = m.group(2).upper().replace(" ", "")
            expl_start = (m.group(3) or "").strip()
            current_expl_lines = [expl_start] if expl_start else []
            continue

        # Continuation of explanation until next head
        if current_num is not None:
            current_expl_lines.append(raw)

    # Flush tail
    flush_current()

    return answers


def match_questions_answers(
    questions: List[Dict[str, Any]], answers: Dict[int, Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Combine extracted questions with their answers.

    Validate:
    - Every question has an answer
    - Answer letter exists in question options
    - Flag mismatches for review
    """
    matched_data: List[Dict[str, Any]] = []

    for q in questions:
        q_num = q.get("number")
        if q_num not in answers:
            print(f"WARNING: No answer found for Q{q_num}")
            continue

        # Validate answer letter exists in options
        answer_letters = answers[q_num].get("correct", "")
        for letter in [l.strip() for l in answer_letters.split(',') if l.strip()]:
            if letter not in q.get("options", {}):
                print(f"ERROR: Q{q_num} answer {letter} not in options")

        matched_data.append({
            "question": q,
            "answer": answers[q_num],
        })

    return matched_data


def classify_topic(item: Dict[str, Any]) -> str:
    """
    Classify question into CAPM ECO domains based on keywords.
    Returns one of:
    - Project Management Fundamentals and Core Concepts
    - Predictive, Plan-Based Methodologies
    - Agile Frameworks/Methodologies
    - Business Analysis Frameworks
    """
    question_text = item["question"]["text"].lower()
    explanation = item["answer"].get("explanation", "").lower()
    combined = f"{question_text} {explanation}"

    agile_keywords = [
        'scrum', 'sprint', 'agile', 'kanban', 'retrospective',
        'product owner', 'scrum master', 'user story', 'backlog',
        'iteration', 'adaptive', 'daily standup', 'velocity',
        'burndown', 'mvp', 'minimum viable product'
    ]

    predictive_keywords = [
        'waterfall', 'predictive', 'wbs', 'work breakdown',
        'gantt', 'critical path', 'baseline', 'change control board',
        'traditional', 'plan-driven'
    ]

    ba_keywords = [
        'requirements', 'business case', 'roi', 'stakeholder analysis',
        'swot', 'traceability matrix', 'elicitation', 'moscow',
        'weighted ranking', 'business analyst', 'feasibility'
    ]

    if any(k in combined for k in agile_keywords):
        return "Agile Frameworks/Methodologies"
    if any(k in combined for k in predictive_keywords):
        return "Predictive, Plan-Based Methodologies"
    if any(k in combined for k in ba_keywords):
        return "Business Analysis Frameworks"
    return "Project Management Fundamentals and Core Concepts"


def estimate_difficulty(item: Dict[str, Any]) -> str:
    """
    Estimate difficulty based on:
    1. Question complexity
    2. Explanation length
    3. Number of options
    4. Keywords indicating complexity
    """
    q_text = item["question"]["text"]
    explanation = item["answer"].get("explanation", "")

    difficulty_score = 0

    if len(q_text) > 200:
        difficulty_score += 1
    if len(explanation) > 500:
        difficulty_score += 1

    if "," in item["answer"].get("correct", ""):
        difficulty_score += 2

    complex_keywords = [
        'root cause', 'best practice', 'most appropriate',
        'complex', 'integrate', 'conflict', 'hybrid'
    ]
    if any(keyword in q_text.lower() for keyword in complex_keywords):
        difficulty_score += 1

    if difficulty_score <= 1:
        return "easy"
    elif difficulty_score <= 3:
        return "medium"
    else:
        return "hard"


def create_json_structure(
    matched_data: List[Dict[str, Any]], test_name: str, batch_start: int, batch_end: int
) -> List[Dict[str, Any]]:
    """
    Transform matched data into target JSON format.
    """
    json_output: List[Dict[str, Any]] = []

    for item in matched_data:
        num = item["question"].get("number", 0)
        if batch_start <= num <= batch_end:
            json_output.append({
                "text": f"[{test_name}] {num}) {item['question']['text']}",
                "options": item["question"].get("options", {}),
                "correctAnswer": item["answer"].get("correct", ""),
                "explanation": item["answer"].get("explanation", ""),
                "topic": classify_topic(item),
                "difficulty": estimate_difficulty(item),
            })

    return json_output


def validate_json_output(json_file: str) -> bool:
    """
    Validate generated JSON for quality and completeness.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues: List[str] = []

    for idx, item in enumerate(data):
        q_num = idx + 1
        required_fields = ['text', 'options', 'correctAnswer', 'explanation', 'topic', 'difficulty']
        for field in required_fields:
            if field not in item or not item[field]:
                issues.append(f"Q{q_num}: Missing or empty {field}")
        if not item.get('text', '').startswith('[Practice Test'):
            issues.append(f"Q{q_num}: Text doesn't start with [Practice Test X]")
        answer = item.get('correctAnswer', '')
        for letter in [l.strip() for l in answer.split(',') if l.strip()]:
            if letter not in item.get('options', {}):
                issues.append(f"Q{q_num}: Answer {letter} not in options")
        if len(item.get('explanation', '')) < 100:
            issues.append(f"Q{q_num}: Explanation too short")
        valid_topics = [
            "Project Management Fundamentals and Core Concepts",
            "Predictive, Plan-Based Methodologies",
            "Agile Frameworks/Methodologies",
            "Business Analysis Frameworks",
        ]
        if item.get('topic') not in valid_topics:
            issues.append(f"Q{q_num}: Invalid topic '{item.get('topic')}'")
        if item.get('difficulty') not in ['easy', 'medium', 'hard']:
            issues.append(f"Q{q_num}: Invalid difficulty '{item.get('difficulty')}'")

    if issues:
        print(f"❌ Validation failed for {json_file}:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"✅ {json_file} validation passed!")
        return True


def process_test(
    test_name: str,
    questions_pdf: str,
    answers_pdf: str,
    batch_size: int = 15,
    strict_paths: bool = False,
) -> None:
    """
    Main processing pipeline for a single test.
    """
    print(f"Processing {test_name}...")

    def _resolve_pdf_path(kind: str, configured: str) -> str:
        """Resolve a PDF path. If the configured path doesn't exist, try to find a sensible fallback.
        kind: 'questions' | 'answers'
        """
        if os.path.exists(configured):
            return configured

        # Derive index from test_name (first number)
        m = re.search(r"(\d+)", test_name)
        idx = m.group(1) if m else ""

        # Base directory from configured path or default
        base_dir = os.path.dirname(configured)
        if not base_dir:
            base_dir = os.path.join('input', kind)
        if not os.path.isdir(base_dir):
            base_dir = os.path.join('input', kind)

        candidates = sorted(glob.glob(os.path.join(base_dir, "*.pdf")))
        if not candidates:
            # Nothing to resolve
            return configured

        def score(p: str) -> int:
            b = os.path.basename(p).lower()
            s = 0
            if idx and idx in b:
                s += 2
            # keyword hints
            if kind == 'questions' and any(k in b for k in ['question', 'practice_test', 'test']):
                s += 1
            if kind == 'answers' and any(k in b for k in ['answer', 'rationale', 'rationales']):
                s += 1
            return s

        best = max(candidates, key=score)
        if score(best) > 0:
            print(f"(resolver) Using fallback for {kind}: {best}")
            return best
        # Fallback to first candidate with a warning
        print(f"(resolver) No exact match for {kind}; using {best}")
        return best

    # Respect strict mode: do not attempt fallback resolution
    if strict_paths:
        q_path = questions_pdf
        a_path = answers_pdf
        # Skip if configured paths are missing
        missing = []
        if not os.path.exists(q_path):
            missing.append(f"questions: {q_path}")
        if not os.path.exists(a_path):
            missing.append(f"answers: {a_path}")
        if missing:
            print(f"(strict) Skipping {test_name} due to missing path(s): {', '.join(missing)}")
            return
    else:
        q_path = _resolve_pdf_path('questions', questions_pdf)
        a_path = _resolve_pdf_path('answers', answers_pdf)

    questions = extract_questions(q_path)
    answers = extract_answers(a_path)

    matched = match_questions_answers(questions, answers)

    # Build batches based on actual question numbers, not matched count.
    if not matched:
        print(f"No matched questions for {test_name}; skipping JSON emission.")
        print()
        return

    nums = sorted(item["question"].get("number", 0) for item in matched)
    min_num = nums[0]
    max_num = nums[-1]

    for start in range(min_num, max_num + 1, batch_size):
        end = min(start + batch_size - 1, max_num)
        batch_data = create_json_structure(matched, test_name, start, end)
        filename = f"CAPM_{test_name.replace(' ', '_')}_Questions_{start}-{end}.json"
        output_path = os.path.join('output', filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
        print(f"Created: {filename} ({len(batch_data)} questions)")

    print(f"✅ {test_name} complete!\n")


def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_extraction(sample_pdf: str = 'input/test_sample.pdf') -> None:
    """Test with small sample first. Skips if sample not found."""
    if not os.path.exists(sample_pdf):
        print("(test_extraction) No sample PDF found; skipping quick test.")
        return
    questions = extract_questions(sample_pdf)
    assert len(questions) >= 10, "Expected at least 10 questions in sample"
    assert all('text' in q for q in questions), "Every question should have text"
    print("✅ Extraction test passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="CAPM PDF → JSON extractor (skeleton)")
    parser.add_argument('--config', default='config.json', help='Path to config.json')
    parser.add_argument('--skip-tests', action='store_true', help='Skip quick test_extraction()')
    parser.add_argument('--strict-paths', action='store_true', help='Do not resolve missing paths; skip tests if configured PDFs are absent')
    args = parser.parse_args()

    if not args.skip_tests:
        test_extraction()

    if not os.path.exists(args.config):
        print(f"Config not found: {args.config}. Nothing to do.")
        return

    cfg = load_config(args.config)
    tests = cfg.get('tests', [])
    if not tests:
        print("No tests configured in config.json")
        return

    for test in tests:
        try:
            process_test(
                test_name=test['name'],
                questions_pdf=test['questions'],
                answers_pdf=test['answers'],
                batch_size=int(test.get('batch_size', 15)),
                strict_paths=bool(args.strict_paths),
            )
        except Exception as e:
            print(f"❌ Error processing {test.get('name', 'UNKNOWN')}: {e}")
            continue

    print("\n" + "=" * 50)
    print("VALIDATION PHASE")
    print("=" * 50 + "\n")

    output_files = glob.glob('output/*.json')
    all_valid = True

    for json_file in sorted(output_files):
        if not validate_json_output(json_file):
            all_valid = False

    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 ALL TESTS PROCESSED AND VALIDATED SUCCESSFULLY!")
    else:
        print("⚠️  Some validation issues found. Review output above.")
    print("=" * 50)


if __name__ == "__main__":
    main()
