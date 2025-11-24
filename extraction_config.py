"""
Configuration constants for CAPM PDF extraction.

Centralized configuration for thresholds, classification keywords,
and extraction parameters. Modify these values to tune extraction behavior.
"""

# Batch Processing
DEFAULT_BATCH_SIZE = 15

# Validation Thresholds
MIN_EXPLANATION_LENGTH = 100  # Minimum characters for explanation
LONG_QUESTION_THRESHOLD = 200  # Question length for difficulty +1
LONG_EXPLANATION_THRESHOLD = 500  # Explanation length for difficulty +1

# Valid CAPM ECO Domains
VALID_TOPICS = [
    "Project Management Fundamentals and Core Concepts",
    "Predictive, Plan-Based Methodologies",
    "Agile Frameworks/Methodologies",
    "Business Analysis Frameworks",
]

# Topic Classification Keywords
AGILE_KEYWORDS = [
    'scrum', 'sprint', 'agile', 'kanban', 'retrospective',
    'product owner', 'scrum master', 'user story', 'backlog',
    'iteration', 'adaptive', 'daily standup', 'velocity',
    'burndown', 'mvp', 'minimum viable product', 'story points',
    'sprint planning', 'sprint review', 'incremental',
]

PREDICTIVE_KEYWORDS = [
    'waterfall', 'predictive', 'wbs', 'work breakdown',
    'gantt', 'critical path', 'baseline', 'change control board',
    'traditional', 'plan-driven', 'earned value', 'pert',
    'schedule compression', 'fast tracking', 'crashing',
]

BUSINESS_ANALYSIS_KEYWORDS = [
    'requirements', 'business case', 'roi', 'stakeholder analysis',
    'swot', 'traceability matrix', 'elicitation', 'moscow',
    'weighted ranking', 'business analyst', 'feasibility',
    'benefit-cost ratio', 'payback period', 'npv', 'irr',
]

# Difficulty Estimation Keywords
COMPLEX_KEYWORDS = [
    'root cause', 'best practice', 'most appropriate',
    'complex', 'integrate', 'conflict', 'hybrid',
    'negotiate', 'optimize', 'prioritize', 'balance',
]

# Difficulty Score Thresholds
DIFFICULTY_EASY_MAX = 1
DIFFICULTY_MEDIUM_MAX = 3
# Score > DIFFICULTY_MEDIUM_MAX is 'hard'

# Regex Patterns (for reference/documentation)
QUESTION_PATTERN = r"^\s*(?:\d+\s+)?(\d+)\s*[\)\.-]\s*(.*)"
OPTION_PATTERN = r"^\s*([A-G])\s*[\)\.:]\s*(.+)"
ANSWER_PATTERN = r"^(\d+)\s*[\.)-]?\s+([A-G](?:\s*,\s*[A-G])*)(?:\s+(.+))?$"
PAGE_FOOTER_PATTERN = r"\b\d{1,4}\s*/\s*\d{1,4}\b$"

# Special Case Detection
HEADER_SKIP_PATTERNS = ["options", "option", "answer choices", "answers"]
IMAGE_MARKERS = ["<<IMAGE>>", "drag and drop", "image", "diagram"]
MULTI_SELECT_PATTERN = r"\(choose\s+(two|three)\)"
