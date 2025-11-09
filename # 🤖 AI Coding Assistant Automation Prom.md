# 🤖 AI Coding Assistant Automation Prompt

## **Project Goal**
Automate the extraction and structuring of CAPM practice test questions from PDF files into standardized JSON format for exam preparation application.

---

## **Step-by-Step Implementation Guide**

### **STEP 1: Project Setup & File Structure**

```
project/
├── input/
│   ├── questions/
│   │   └── [PDF files with questions numbered 1-150]
│   └── answers/
│       └── [PDF files with answers and rationales]
├── output/
│   └── [Generated JSON files]
├── scripts/
│   └── extract_questions.py (or .js/.ts)
└── config.json
```

**Task:** Set up the directory structure and install required libraries.

**Libraries needed:**
- **Python:** `PyPDF2`, `pdfplumber`, or `pypdf` for PDF extraction
- **Node.js:** `pdf-parse` or `pdf.js`
- **Data processing:** `json`, `re` (regex)

---

### **STEP 2: Extract Questions from PDF**

**Input Format:**
```
Questions appear as:
1 ) Question text here spanning
multiple lines?
A) Option A text
B) Option B text
C) Option C text
D) Option D text

2 ) Next question...
```

**Extraction Logic:**
```python
def extract_questions(pdf_path):
    """
    Extract questions from PDF maintaining:
    1. Question number
    2. Full question text (handle multi-line)
    3. All options (A, B, C, D, sometimes E, F, G)
    4. Handle special formatting (bold, newlines)
    """
    questions = []
    
    # Regex patterns:
    # Question: r"^(\d+)\s*\)"  # Matches "1 )", "23 )", etc.
    # Options: r"^([A-G])\)\s*(.+)"  # Matches "A) text"
    
    # Key challenges:
    # - Questions span multiple lines until options start
    # - Some questions have (Choose two/three)
    # - Some have images/tables (note these for manual review)
    
    return questions
```

**Critical Details:**
- Question numbers are NOT always sequential in PDF (pages may split questions)
- Stop reading question text when you hit first option pattern `^[A-G])\s*`
- Preserve special characters and formatting
- Handle edge case: "Choose two" or "Choose three" in question text

---

### **STEP 3: Extract Answers & Explanations from PDF**

**Input Format:**
```
51 C The question describes a role, which is responsible...
[Multiple paragraphs of explanation]

52 B The correct answer is: Prepare a detailed business case...
[Explanation continues]
```

**Extraction Logic:**
```python
def extract_answers(pdf_path):
    """
    Extract answers and match to question numbers.
    
    Pattern: NUMBER LETTER(s) Explanation text...
    
    Handle:
    1. Single answers: "51 C"
    2. Multiple answers: "56 A,B,C" or "62 A,E"
    3. Multi-line explanations
    4. References to PMBOK/Agile Practice Guide
    """
    answers = {}
    
    # Regex: r"^(\d+)\s+([A-G,]+)\s+(.+)"
    # Group 1: Question number
    # Group 2: Answer letter(s) - may include commas
    # Group 3: Explanation (continues until next question number)
    
    return answers
```

**Critical Details:**
- Answers may be: single letter (A), multiple letters (A,B,C), or (A,E)
- Explanation continues until next question number pattern
- Some explanations reference other questions
- Clean up escape characters: `\r\n`, `''` (double quotes), etc.

---

### **STEP 4: Match Questions with Answers**

```python
def match_questions_answers(questions, answers):
    """
    Combine extracted questions with their answers.
    
    Validate:
    - Every question has an answer
    - Answer letter exists in question options
    - Flag mismatches for review
    """
    matched_data = []
    
    for q in questions:
        q_num = q['number']
        if q_num not in answers:
            print(f"WARNING: No answer found for Q{q_num}")
            continue
            
        # Validate answer letter exists in options
        answer_letters = answers[q_num]['correct']
        for letter in answer_letters.split(','):
            if letter not in q['options']:
                print(f"ERROR: Q{q_num} answer {letter} not in options")
        
        matched_data.append({
            'question': q,
            'answer': answers[q_num]
        })
    
    return matched_data
```

---

### **STEP 5: Structure Data into Target JSON Format**

**Target JSON Schema:**
```json
[
  {
    "text": "[Practice Test 1] 1) Question text here?",
    "options": {
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    },
    "correctAnswer": "C",
    "explanation": "Full explanation with rationale. Why this is correct. Why others are wrong. Reference: PMBOK Guide section.",
    "topic": "One of: Project Management Fundamentals and Core Concepts | Predictive, Plan-Based Methodologies | Agile Frameworks/Methodologies | Business Analysis Frameworks",
    "difficulty": "easy | medium | hard"
  }
]
```

**Transformation Logic:**
```python
def create_json_structure(matched_data, test_name, batch_start, batch_end):
    """
    Transform matched data into target JSON format.
    
    Args:
        test_name: "Practice Test 1", "Practice Test 2", etc.
        batch_start: Starting question number for this batch
        batch_end: Ending question number for this batch
    """
    json_output = []
    
    for item in matched_data:
        if batch_start <= item['question']['number'] <= batch_end:
            json_output.append({
                "text": f"[{test_name}] {item['question']['number']}) {item['question']['text']}",
                "options": item['question']['options'],
                "correctAnswer": item['answer']['correct'],
                "explanation": item['answer']['explanation'],
                "topic": classify_topic(item),  # See STEP 6
                "difficulty": estimate_difficulty(item)  # See STEP 7
            })
    
    return json_output
```

**Formatting Rules:**
- Text starts with: `[Practice Test X] NUMBER)`
- Remove extra whitespace but preserve intentional formatting
- Clean escape characters: `\r\n` → space, `''` → proper quotes
- Ensure explanations are complete sentences

---

### **STEP 6: Topic Classification**

**Topic Mapping Logic:**
```python
def classify_topic(item):
    """
    Classify question into CAPM ECO domains based on keywords.
    
    CAPM Domains:
    1. Project Management Fundamentals and Core Concepts
    2. Predictive, Plan-Based Methodologies  
    3. Agile Frameworks/Methodologies
    4. Business Analysis Frameworks
    """
    question_text = item['question']['text'].lower()
    explanation = item['answer']['explanation'].lower()
    combined = question_text + " " + explanation
    
    # Keyword matching (order matters - check most specific first)
    
    # Agile keywords
    agile_keywords = [
        'scrum', 'sprint', 'agile', 'kanban', 'retrospective', 
        'product owner', 'scrum master', 'user story', 'backlog',
        'iteration', 'adaptive', 'daily standup', 'velocity',
        'burndown', 'mvp', 'minimum viable product'
    ]
    
    # Predictive keywords
    predictive_keywords = [
        'waterfall', 'predictive', 'wbs', 'work breakdown',
        'gantt', 'critical path', 'baseline', 'change control board',
        'traditional', 'plan-driven'
    ]
    
    # Business Analysis keywords
    ba_keywords = [
        'requirements', 'business case', 'roi', 'stakeholder analysis',
        'swot', 'traceability matrix', 'elicitation', 'moscow',
        'weighted ranking', 'business analyst', 'feasibility'
    ]
    
    # Check matches and return most specific domain
    if any(keyword in combined for keyword in agile_keywords):
        return "Agile Frameworks/Methodologies"
    
    if any(keyword in combined for keyword in predictive_keywords):
        return "Predictive, Plan-Based Methodologies"
    
    if any(keyword in combined for keyword in ba_keywords):
        return "Business Analysis Frameworks"
    
    # Default
    return "Project Management Fundamentals and Core Concepts"
```

---

### **STEP 7: Difficulty Estimation**

```python
def estimate_difficulty(item):
    """
    Estimate difficulty based on:
    1. Question complexity
    2. Explanation length
    3. Number of options
    4. Keywords indicating complexity
    """
    q_text = item['question']['text']
    explanation = item['answer']['explanation']
    
    difficulty_score = 0
    
    # Length indicators
    if len(q_text) > 200:
        difficulty_score += 1
    if len(explanation) > 500:
        difficulty_score += 1
    
    # Multiple correct answers
    if ',' in item['answer']['correct']:
        difficulty_score += 2
    
    # Complexity keywords
    complex_keywords = [
        'root cause', 'best practice', 'most appropriate',
        'complex', 'integrate', 'conflict', 'hybrid'
    ]
    if any(keyword in q_text.lower() for keyword in complex_keywords):
        difficulty_score += 1
    
    # Classify
    if difficulty_score <= 1:
        return "easy"
    elif difficulty_score <= 3:
        return "medium"
    else:
        return "hard"
```

---

### **STEP 8: Batch Processing & Output**

```python
def process_test(test_name, questions_pdf, answers_pdf, batch_size=15):
    """
    Main processing pipeline.
    
    Args:
        test_name: "Practice Test 1"
        questions_pdf: Path to questions PDF
        answers_pdf: Path to answers PDF
        batch_size: Questions per JSON file (default: 15)
    """
    print(f"Processing {test_name}...")
    
    # Extract
    questions = extract_questions(questions_pdf)
    answers = extract_answers(answers_pdf)
    
    # Match
    matched = match_questions_answers(questions, answers)
    
    # Generate batches
    total_questions = len(matched)
    for start in range(1, total_questions + 1, batch_size):
        end = min(start + batch_size - 1, total_questions)
        
        # Create JSON
        batch_data = create_json_structure(matched, test_name, start, end)
        
        # Save file
        filename = f"CAPM_{test_name.replace(' ', '_')}_Questions_{start}-{end}.json"
        output_path = os.path.join('output', filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created: {filename} ({len(batch_data)} questions)")
    
    print(f"✅ {test_name} complete!\n")
```

---

### **STEP 9: Validation & Quality Checks**

```python
def validate_json_output(json_file):
    """
    Validate generated JSON for quality and completeness.
    
    Checks:
    1. All required fields present
    2. Correct answer exists in options
    3. No empty fields
    4. Proper formatting
    5. Text starts with correct prefix
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues = []
    
    for idx, item in enumerate(data):
        q_num = idx + 1
        
        # Required fields
        required_fields = ['text', 'options', 'correctAnswer', 'explanation', 'topic', 'difficulty']
        for field in required_fields:
            if field not in item or not item[field]:
                issues.append(f"Q{q_num}: Missing or empty {field}")
        
        # Text format
        if not item['text'].startswith('[Practice Test'):
            issues.append(f"Q{q_num}: Text doesn't start with [Practice Test X]")
        
        # Answer validation
        answer = item['correctAnswer']
        for letter in answer.split(','):
            if letter.strip() not in item['options']:
                issues.append(f"Q{q_num}: Answer {letter} not in options")
        
        # Explanation length (should be substantial)
        if len(item['explanation']) < 100:
            issues.append(f"Q{q_num}: Explanation too short")
        
        # Valid topic
        valid_topics = [
            "Project Management Fundamentals and Core Concepts",
            "Predictive, Plan-Based Methodologies",
            "Agile Frameworks/Methodologies",
            "Business Analysis Frameworks"
        ]
        if item['topic'] not in valid_topics:
            issues.append(f"Q{q_num}: Invalid topic '{item['topic']}'")
        
        # Valid difficulty
        if item['difficulty'] not in ['easy', 'medium', 'hard']:
            issues.append(f"Q{q_num}: Invalid difficulty '{item['difficulty']}'")
    
    # Report
    if issues:
        print(f"❌ Validation failed for {json_file}:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"✅ {json_file} validation passed!")
        return True
```

---

### **STEP 10: Main Execution Script**

```python
def main():
    """
    Main execution pipeline for all practice tests.
    """
    # Configuration
    tests = [
        {
            'name': 'Practice Test 1',
            'questions': 'input/questions/Certified_Associate_in_Project_Management_CAPM__2023_Update__Practice_Test_1.pdf',
            'answers': 'input/answers/SAMPLE_QUESTION_PRACTICE_1__Answers_with_Rationale.pdf',
            'batch_size': 15
        },
        {
            'name': 'Practice Test 2',
            'questions': 'input/questions/Certified_Associate_in_Project_Management_CAPM__2023_Update__Practice_Test_2.pdf',
            'answers': 'input/answers/SAMPLE_QUESTION_PRACTICE_2__Answers_with_Rationale.pdf',
            'batch_size': 15
        },
        {
            'name': 'Practice Test 3',
            'questions': 'input/questions/Certified_Associate_in_Project_Management_CAPM__2023_Update__Practice_Test_3.pdf',
            'answers': 'input/answers/SAMPLE_QUESTION_PRACTICE_3__Answers_with_Rationale.pdf',
            'batch_size': 15
        }
    ]
    
    # Process each test
    for test in tests:
        try:
            process_test(
                test_name=test['name'],
                questions_pdf=test['questions'],
                answers_pdf=test['answers'],
                batch_size=test['batch_size']
            )
        except Exception as e:
            print(f"❌ Error processing {test['name']}: {e}")
            continue
    
    # Validate all outputs
    print("\n" + "="*50)
    print("VALIDATION PHASE")
    print("="*50 + "\n")
    
    output_files = glob.glob('output/*.json')
    all_valid = True
    
    for json_file in sorted(output_files):
        if not validate_json_output(json_file):
            all_valid = False
    
    # Summary
    print("\n" + "="*50)
    if all_valid:
        print("🎉 ALL TESTS PROCESSED AND VALIDATED SUCCESSFULLY!")
    else:
        print("⚠️  Some validation issues found. Review output above.")
    print("="*50)

if __name__ == "__main__":
    main()
```

---

## **Special Handling Cases**

### **Case 1: Questions with Images/Diagrams**
```python
# Flag for manual review
if "<<IMAGE>>" in question_text or "drag and drop" in question_text.lower():
    item['requires_manual_review'] = True
    item['note'] = "Contains image or interactive element"
```

### **Case 2: Multi-part Questions**
```python
# Questions like "Choose two" or "Choose three"
if re.search(r'\(choose\s+(two|three)\)', question_text, re.IGNORECASE):
    # Ensure correctAnswer is comma-separated: "A,B,C"
    pass
```

### **Case 3: Matching/Drag-and-Drop Questions**
```python
# Options like "A:1, B:2, C:3, D:4"
if any(':' in opt for opt in options.values()):
    item['question_type'] = 'matching'
```

---

## **Usage Instructions for AI Coding Assistants**

### **For GitHub Copilot:**
1. Create the file structure above
2. Copy this entire prompt into a comment at the top of `extract_questions.py`
3. Start writing function signatures - Copilot will auto-complete based on prompt

### **For Claude Code / Cursor:**
```
# In terminal or chat:
"Using the detailed specification above, create a Python script that:
1. Extracts questions from CAPM PDF files
2. Matches them with answers
3. Outputs JSON in the specified format
4. Includes validation
5. Processes all 3 practice tests

Start with extract_questions() function."
```

### **For Manus/Windsurf:**
```
"Implement the CAPM question extraction automation described above.
Use pdfplumber for PDF parsing.
Create modular functions as specified in steps 2-10.
Include error handling and logging.
Test with Practice Test 1 first before processing all tests."
```

---

## **Testing Strategy**

```python
# Test with small sample first
def test_extraction():
    """Test with first 10 questions only"""
    questions = extract_questions('input/test_sample.pdf')
    assert len(questions) >= 10
    assert all('text' in q for q in questions)
    print("✅ Extraction test passed")

# Run before full processing
test_extraction()
```

---

## **Expected Output Structure**

```
output/
├── CAPM_Practice_Test_1_Questions_1-15.json
├── CAPM_Practice_Test_1_Questions_16-30.json
├── ... (10 files total for 150 questions)
├── CAPM_Practice_Test_2_Questions_1-15.json
├── ... (10 files)
└── CAPM_Practice_Test_3_Questions_1-15.json
    ... (10 files)
```

**Total Output:** 30 JSON files (3 tests × 10 files each)

---

## **Performance Optimization Tips**

1. **Cache extracted text:** Save raw extracted text to avoid re-parsing PDFs
2. **Parallel processing:** Process multiple tests simultaneously
3. **Incremental output:** Save each batch immediately (don't wait for all 150)
4. **Progress tracking:** Add progress bars using `tqdm`

---

This comprehensive prompt should enable any AI coding assistant to automate your JSON extraction process! Let me know if you need any clarification on specific steps. 🚀