"""Hugging Face Spaces entry point.

The Gradio SDK on Spaces runs this file directly without pip-installing the
project, so the src layout has to be put on the path manually.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from meal_planning_agent.main import run  # noqa: E402

run()
