"""
HuggingFace Spaces entry point.
Delegates to dashboard/app.py for actual application.
"""
import sys
from pathlib import Path

# Add dashboard to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard.app import main

if __name__ == "__main__":
    main()
