#!/usr/bin/env python3
"""
Jeopardy Game - Main Application
--------------------------------
This is the main entry point for the Jeopardy game application.
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui import JeopardyUI
from game_logic import JeopardyGame
from file_handler import ExcelHandler
from config import DEFAULT_TEAMS, APP_TITLE, APP_SIZE


def main():
    """Main function to run the Jeopardy application."""
    
    # Create the main application window
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry(f"{APP_SIZE[0]}x{APP_SIZE[1]}")
    root.resizable(True, True)
    
    # Set up the Excel handler for loading game data
    excel_handler = ExcelHandler()
    
    # Initialize the game logic with default teams
    game = JeopardyGame(teams=DEFAULT_TEAMS)
    
    # Create the UI and connect it to the game logic
    ui = JeopardyUI(root, game, excel_handler)
    
    # Set up protocol for closing the application
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    
    # Start the main event loop
    root.mainloop()


def on_closing(root):
    """Handle the application closing event."""
    if messagebox.askokcancel("Quit", "Do you want to quit the game?"):
        root.destroy()


if __name__ == "__main__":
    main()