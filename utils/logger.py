"""
Logging utilities for CAPM PDF extraction.

Provides consistent logging across extraction scripts with structured output.
"""

import sys
from typing import Optional


class ExtractionLogger:
    """Lightweight logger for extraction operations."""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize logger.
        
        Args:
            verbose: If True, print detailed debug messages
        """
        self.verbose = verbose
        self.warnings = []
        self.errors = []
    
    def info(self, message: str, prefix: str = "") -> None:
        """Print info message."""
        prefix_str = f"({prefix}) " if prefix else ""
        print(f"{prefix_str}{message}")
    
    def debug(self, message: str, prefix: str = "") -> None:
        """Print debug message if verbose enabled."""
        if self.verbose:
            prefix_str = f"({prefix}) " if prefix else ""
            print(f"DEBUG: {prefix_str}{message}", file=sys.stderr)
    
    def warning(self, message: str, prefix: str = "") -> None:
        """Print warning and store for summary."""
        prefix_str = f"({prefix}) " if prefix else ""
        msg = f"WARNING: {prefix_str}{message}"
        print(msg)
        self.warnings.append(msg)
    
    def error(self, message: str, prefix: str = "") -> None:
        """Print error and store for summary."""
        prefix_str = f"({prefix}) " if prefix else ""
        msg = f"ERROR: {prefix_str}{message}"
        print(msg, file=sys.stderr)
        self.errors.append(msg)
    
    def summary(self) -> None:
        """Print summary of warnings and errors."""
        if self.warnings or self.errors:
            print("\n" + "=" * 50)
            print("SUMMARY")
            print("=" * 50)
            
            if self.warnings:
                print(f"\nWarnings ({len(self.warnings)}):")
                for w in self.warnings[:10]:  # Show first 10
                    print(f"  - {w}")
                if len(self.warnings) > 10:
                    print(f"  ... and {len(self.warnings) - 10} more")
            
            if self.errors:
                print(f"\nErrors ({len(self.errors)}):")
                for e in self.errors[:10]:  # Show first 10
                    print(f"  - {e}")
                if len(self.errors) > 10:
                    print(f"  ... and {len(self.errors) - 10} more")
            print()
    
    def has_errors(self) -> bool:
        """Check if any errors were logged."""
        return len(self.errors) > 0
    
    def reset(self) -> None:
        """Clear warning and error lists."""
        self.warnings.clear()
        self.errors.clear()
