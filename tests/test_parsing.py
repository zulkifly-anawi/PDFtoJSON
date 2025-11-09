import types
import sys
import importlib
import scripts.extract_questions as eq

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
    # Synthesize a small two-question sample with indented options including E..G
    lines = [
        "76) What doc?",
        "Options",
        "  A) One",
        "  B) Two",
        "  C) Three",
        "    D) Four",
        "   E) Five",
        " F) Six",
        "G) Seven",
        "77) Next question text",
        "A) Alpha",
        "B) Beta",
    ]
    fake_text = "\n".join(lines)

    # Monkeypatch pdfplumber.open to return our fake PDF
    fake_mod = types.SimpleNamespace(open=lambda path: FakePDF([fake_text]))
    monkeypatch.setitem(sys.modules, 'pdfplumber', fake_mod)
    # Pretend the file exists
    monkeypatch.setattr(eq.os.path, 'exists', lambda p: True)

    # Force reload of module to pick up our fake import
    importlib.reload(eq)
    qs = eq.extract_questions("/dev/null.pdf")

    q76 = next(q for q in qs if q['number'] == 76)
    assert set(q76['options'].keys()) == set(list("ABCDEFG")), q76['options']


def test_extract_answers_parsing(monkeypatch):
    # Synthesize answers with variants and multi-line explanations
    lines = [
        "76 C This is an explanation that continues",
        "and has more detail on next line.",
        "77) A Explanation starts right after.",
        "78 A, B, C Multi-answer with spaced commas",
        "79 D - short expl should still be captured",
    ]
    fake_text = "\n".join(lines)

    # Monkeypatch pdfplumber.open to return our fake PDF
    fake_mod = types.SimpleNamespace(open=lambda path: FakePDF([fake_text]))
    monkeypatch.setitem(sys.modules, 'pdfplumber', fake_mod)
    # Pretend the file exists
    monkeypatch.setattr(eq.os.path, 'exists', lambda p: True)

    importlib.reload(eq)
    ans = eq.extract_answers("/dev/null.pdf")

    assert ans[76]['correct'] == 'C'
    assert 'continues and has more detail' in ans[76]['explanation']
    assert ans[77]['correct'] == 'A'
    assert ans[78]['correct'].replace(' ', '') == 'A,B,C'
    assert ans[79]['correct'] == 'D'
