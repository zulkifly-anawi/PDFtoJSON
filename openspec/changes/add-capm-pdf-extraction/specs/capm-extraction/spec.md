## ADDED Requirements

### Requirement: PDF extraction
The system SHALL extract questions and options from a questions PDF file and preserve question numbers,
all option texts (A..G), and multi-line question text.

#### Scenario: Extract simple question block
- **GIVEN** a question page containing `1 )` followed by question text and `A)`..`D)` options
- **WHEN** the extractor runs
- **THEN** it returns a question object with `number`, `text` and `options` containing keys `A`..`D`.

### Requirement: Answer extraction
The system SHALL extract correct answer letter(s) and explanation text from the answers/rationales PDF
and associate them with the question number.

#### Scenario: Single answer
- **GIVEN** an answers PDF line `51 C Explanation...`
- **WHEN** the answers extractor runs
- **THEN** it returns `{ 51: { correct: "C", explanation: "Explanation..." } }`.

### Requirement: Matching and validation
The system SHALL match questions with answers and flag missing answers or answer letters not found in options.

#### Scenario: Missing answer
- **GIVEN** a question with number `10` and no corresponding answer
- **WHEN** match runs
- **THEN** the system logs a WARNING and includes the question in a review list.

### Requirement: Output JSON schema
The system SHALL emit JSON files in batches (configurable batch size) where each item follows the target
schema: text, options (map), correctAnswer (string/comma-separated), explanation, topic, difficulty.

#### Scenario: Batch output
- **GIVEN** 15 matched questions and batch_size=15
- **WHEN** create_json_structure runs
- **THEN** it writes one JSON file containing 15 items following the schema above.
