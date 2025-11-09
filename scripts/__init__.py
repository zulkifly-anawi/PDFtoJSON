"""Package marker for scripts so tests can import scripts.extract_questions

This file makes the `scripts` folder a Python package which helps pytest import
modules during CI where implicit namespace packages may not be configured.
"""
