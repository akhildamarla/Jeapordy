"""
Jeopardy Game - Configuration
----------------------------
This file contains configuration settings for the Jeopardy game.
"""

import os

# Application settings
APP_TITLE = "Python Jeopardy Game"
APP_SIZE = (1280, 800)

# Game settings
DEFAULT_TEAMS = [
    {"name": "Team 1", "score": 0, "color": "#3498db"},  # Blue
    {"name": "Team 2", "score": 0, "color": "#e74c3c"},  # Red
    {"name": "Team 3", "score": 0, "color": "#2ecc71"},  # Green
]

# Round settings
ROUND_NAMES = ["Jeopardy", "Double Jeopardy", "Final Jeopardy"]
JEOPARDY_VALUES = [200, 400, 600, 800, 1000]
DOUBLE_JEOPARDY_VALUES = [400, 800, 1200, 1600, 2000]

# Timer settings (in seconds)
QUESTION_TIMER = 30
FINAL_JEOPARDY_TIMER = 60

# Excel file settings
DEFAULT_TEMPLATE_PATH = os.path.join("templates", "jeopardy_template.xlsx")
EXCEL_SHEET_NAMES = ["Jeopardy Round", "Double Jeopardy Round", "Final Jeopardy"]

# UI Settings
FONT_FAMILY = "Arial"
CATEGORY_FONT = (FONT_FAMILY, 14, "bold")
QUESTION_FONT = (FONT_FAMILY, 18)
ANSWER_FONT = (FONT_FAMILY, 16)
SCORE_FONT = (FONT_FAMILY, 16, "bold")
BUTTON_FONT = (FONT_FAMILY, 16)
TEAM_FONT = (FONT_FAMILY, 14, "bold")
VALUE_FONT = (FONT_FAMILY, 18, "bold")

# Colors
BG_COLOR = "#060CE9"  # Classic Jeopardy blue
TEXT_COLOR = "#FFFFFF"  # White
SELECTED_COLOR = "#FFD700"  # Gold
PLAYED_COLOR = "#2C3E50"  # Dark blue-gray
CORRECT_COLOR = "#27AE60"  # Green
INCORRECT_COLOR = "#C0392B"  # Red
DAILY_DOUBLE_COLOR = "#F39C12"  # Orange

# Sounds
TIMER_SOUND = os.path.join("resources", "sounds", "timer.wav")
DAILY_DOUBLE_SOUND = os.path.join("resources", "sounds", "daily_double.wav")
FINAL_JEOPARDY_SOUND = os.path.join("resources", "sounds", "final_jeopardy.wav")

# Special settings
DAILY_DOUBLE_CHANCE = 0.1  # Probability of a question being a Daily Double