"""
Jeopardy Game - User Interface
-----------------------------
This module contains the user interface for the Jeopardy game.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import time
import threading
import random
from PIL import Image, ImageTk
import pygame

from config import (
    ROUND_NAMES, JEOPARDY_VALUES, DOUBLE_JEOPARDY_VALUES,
    BG_COLOR, TEXT_COLOR, SELECTED_COLOR, PLAYED_COLOR,
    CORRECT_COLOR, INCORRECT_COLOR, DAILY_DOUBLE_COLOR,
    CATEGORY_FONT, QUESTION_FONT, ANSWER_FONT, SCORE_FONT,
    BUTTON_FONT, TEAM_FONT, VALUE_FONT,
    TIMER_SOUND, DAILY_DOUBLE_SOUND, FINAL_JEOPARDY_SOUND,
    QUESTION_TIMER, FINAL_JEOPARDY_TIMER
)


class JeopardyUI:
    """Main UI class for the Jeopardy game."""
    
    def __init__(self, root, game, excel_handler):
        """Initialize the UI.
        
        Args:
            root (Tk): The root Tkinter window
            game (JeopardyGame): The game logic object
            excel_handler (ExcelHandler): The Excel file handler
        """
        self.root = root
        self.game = game
        self.excel_handler = excel_handler
        
        # Initialize pygame for sound
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except:
            self.sound_enabled = False
        
        # Create UI elements
        self._create_menu()
        self._create_frames()
        self._create_scoreboard()
        self._create_game_board()
        self._create_status_bar()
        
        # Game state variables
        self.current_question = None
        self.timer_running = False
        self.timer_thread = None
        self.timer_value = 0
        self.wagering = False
        self.wager_amount = 0
        
        # Show welcome screen
        self._show_welcome_screen()
    
    def _create_menu(self):
        """Create the application menu."""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Game", command=self._new_game)
        file_menu.add_command(label="Load Questions", command=self._load_questions)
        file_menu.add_command(label="Create Template", command=self._create_template)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Game menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="Manage Teams", command=self._manage_teams)
        game_menu.add_command(label="Reset Scores", command=self._reset_scores)
        game_menu.add_separator()
        game_menu.add_command(label="Next Round", command=self._next_round)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Play", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _create_frames(self):
        """Create the main frames for the UI."""
        # Main container frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for scoreboard
        self.scoreboard_frame = ttk.Frame(self.main_frame, padding="5")
        self.scoreboard_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Middle frame for game board
        self.gameboard_frame = ttk.Frame(self.main_frame, padding="5")
        self.gameboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Question display frame (initially hidden)
        self.question_frame = ttk.Frame(self.main_frame, padding="10")
        
        # Bottom frame for status
        self.status_frame = ttk.Frame(self.main_frame, padding="5")
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
    
    def _create_scoreboard(self):
        """Create the scoreboard UI."""
        self.team_frames = []
        self.score_labels = []
        
        # Create a frame for each team
        for i, team in enumerate(self.game.teams):
            team_frame = ttk.Frame(self.scoreboard_frame, padding="5", style=f"Team{i+1}.TFrame")
            team_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.team_frames.append(team_frame)
            
            # Team name label
            name_label = ttk.Label(
                team_frame, 
                text=team["name"],
                font=TEAM_FONT,
                background=team["color"],
                foreground=TEXT_COLOR,
                anchor=tk.CENTER
            )
            name_label.pack(fill=tk.X)
            
            # Score label
            score_label = ttk.Label(
                team_frame,
                text=f"${team['score']}",
                font=SCORE_FONT,
                background=team["color"],
                foreground=TEXT_COLOR,
                anchor=tk.CENTER
            )
            score_label.pack(fill=tk.X)
            self.score_labels.append(score_label)
            
            # Current turn indicator
            if i == self.game.current_team_index:
                indicator = ttk.Label(
                    team_frame,
                    text="Current Turn",
                    font=(TEAM_FONT[0], 10, "italic"),
                    background=team["color"],
                    foreground=TEXT_COLOR,
                    anchor=tk.CENTER
                )
                indicator.pack(fill=tk.X)
                team_frame.indicator = indicator
    
    def _create_game_board(self):
        """Create the game board UI."""
        self.board_frame = ttk.Frame(self.gameboard_frame)
        self.board_frame.pack(fill=tk.BOTH, expand=True)
        
        # We'll create the actual board when questions are loaded
        self.category_labels = []
        self.question_buttons = []
    
    def _create_status_bar(self):
        """Create the status bar UI."""
        # Round label
        self.round_label = ttk.Label(
            self.status_frame,
            text=f"Round: {self.game.current_round_name}",
            font=(TEAM_FONT[0], 12)
        )
        self.round_label.pack(side=tk.LEFT)
        
        # Current team label
        team = self.game.current_team
        if team:
            team_text = f"Current Team: {team['name']}"
        else:
            team_text = "No teams"
            
        self.current_team_label = ttk.Label(
            self.status_frame,
            text=team_text,
            font=(TEAM_FONT[0], 12)
        )
        self.current_team_label.pack(side=tk.RIGHT)
    
    def _show_welcome_screen(self):
        """Show the welcome screen."""
        # Clear the game board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        # Create welcome message
        welcome_frame = ttk.Frame(self.board_frame, padding="20")
        welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        welcome_label = ttk.Label(
            welcome_frame,
            text="Welcome to Python Jeopardy!",
            font=(CATEGORY_FONT[0], 24, "bold"),
            justify=tk.CENTER
        )
        welcome_label.pack(pady=(20, 10))
        
        instructions = (
            "To start a new game:\n\n"
            "1. Load questions from an Excel file using File > Load Questions\n"
            "2. Customize teams using Game > Manage Teams\n\n"
            "If you don't have a questions file, you can create a template "
            "using File > Create Template"
        )
        
        instructions_label = ttk.Label(
            welcome_frame,
            text=instructions,
            font=(CATEGORY_FONT[0], 14),
            justify=tk.CENTER
        )
        instructions_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(welcome_frame)
        buttons_frame.pack(pady=20)
        
        load_button = ttk.Button(
            buttons_frame,
            text="Load Questions",
            command=self._load_questions
        )
        load_button.pack(side=tk.LEFT, padx=10)
        
        template_button = ttk.Button(
            buttons_frame,
            text="Create Template",
            command=self._create_template
        )
        template_button.pack(side=tk.LEFT, padx=10)
    
    def _build_game_board(self):
        """Build the game board based on the current round."""
        # Clear existing board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        current_round = self.game.current_round
        categories = current_round.categories
        
        if not categories:
            messagebox.showinfo("Information", "No categories found. Please load questions first.")
            self._show_welcome_screen()
            return
        
        # Determine grid dimensions
        num_categories = len(categories)
        
        # If we're in Final Jeopardy, show a special screen
        if self.game.current_round_name == ROUND_NAMES[2]:
            self._show_final_jeopardy_board()
            return
        
        # Determine point values for this round
        values = JEOPARDY_VALUES if self.game.current_round_name == ROUND_NAMES[0] else DOUBLE_JEOPARDY_VALUES
        
        # Create a grid of categories and questions
        self.category_labels = []
        self.question_buttons = [[] for _ in range(num_categories)]
        
        # Create the board grid
        board_grid = ttk.Frame(self.board_frame)
        board_grid.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid layout (make all columns equal width)
        for i in range(num_categories):
            board_grid.columnconfigure(i, weight=1)
        
        # Add categories
        for i, category in enumerate(categories):
            category_frame = ttk.Frame(board_grid, padding="5")
            category_frame.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            
            category_label = tk.Label(
                category_frame,
                text=category,
                font=CATEGORY_FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                wraplength=150,
                height=2,
                justify=tk.CENTER
            )
            category_label.pack(fill=tk.BOTH, expand=True)
            self.category_labels.append(category_label)
        
        # Add question buttons
        for i, category in enumerate(categories):
            for j, value in enumerate(values):
                question_frame = ttk.Frame(board_grid, padding="5")
                question_frame.grid(row=j+1, column=i, sticky="nsew", padx=2, pady=2)
                
                question = current_round.get_question(category, value)
                if question and not question.played:
                    question_button = tk.Button(
                        question_frame,
                        text=f"${value}",
                        font=VALUE_FONT,
                        bg=BG_COLOR,
                        fg=TEXT_COLOR,
                        command=lambda cat=category, val=value: self._select_question(cat, val),
                        relief=tk.RAISED,
                        bd=2
                    )
                    
                    # Mark Daily Doubles with a different color
                    if question.is_daily_double:
                        question_button.configure(bg=DAILY_DOUBLE_COLOR)
                        
                    question_button.pack(fill=tk.BOTH, expand=True)
                    self.question_buttons[i].append(question_button)
                else:
                    # Empty or played question
                    empty_label = tk.Label(
                        question_frame,
                        bg=PLAYED_COLOR,
                        relief=tk.FLAT
                    )
                    empty_label.pack(fill=tk.BOTH, expand=True)
                    self.question_buttons[i].append(None)
    
    def _show_final_jeopardy_board(self):
        """Show the Final Jeopardy board."""
        final_frame = ttk.Frame(self.board_frame, padding="20")
        final_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(
            final_frame,
            text="FINAL JEOPARDY",
            font=(CATEGORY_FONT[0], 36, "bold"),
            foreground=BG_COLOR
        )
        title_label.pack(pady=(20, 40))
        
        # Get Final Jeopardy data
        final_round = self.game.rounds[ROUND_NAMES[2]]
        if not final_round.categories:
            messagebox.showinfo("Information", "No Final Jeopardy question found.")
            return
            
        category = final_round.categories[0]
        
        category_frame = ttk.Frame(final_frame)
        category_frame.pack(pady=20)
        
        category_label = ttk.Label(
            category_frame,
            text="Category:",
            font=(CATEGORY_FONT[0], 18)
        )
        category_label.pack(side=tk.LEFT, padx=(0, 10))
        
        category_name = ttk.Label(
            category_frame,
            text=category,
            font=(CATEGORY_FONT[0], 24, "bold"),
            foreground=BG_COLOR
        )
        category_name.pack(side=tk.LEFT)
        
        # Create buttons for wagering and showing the question
        buttons_frame = ttk.Frame(final_frame)
        buttons_frame.pack(pady=40)
        
        wager_button = ttk.Button(
            buttons_frame,
            text="Make Wagers",
            command=self._make_final_wagers
        )
        wager_button.pack(side=tk.LEFT, padx=10)
        
        question_button = ttk.Button(
            buttons_frame,
            text="Show Question",
            command=self._show_final_question
        )
        question_button.pack(side=tk.LEFT, padx=10)
    
    def _select_question(self, category, value):
        """Handle selecting a question from the board.
        
        Args:
            category (str): The selected category
            value (int): The point value of the question
        """
        current_round = self.game.current_round
        question = current_round.get_question(category, value)
        
        if not question or question.played:
            return
        
        self.current_question = question
        
        # If this is a Daily Double, show the wager screen
        if question.is_daily_double:
            self._play_sound(DAILY_DOUBLE_SOUND)
            self._show_daily_double(question)
        else:
            # Otherwise show the question directly
            self._show_question(question)
    
    def _show_daily_double(self, question):
        """Show the Daily Double screen and prompt for a wager.
        
        Args:
            question (Question): The Daily Double question
        """
        # Clear the game board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        daily_double_frame = ttk.Frame(self.board_frame, padding="20")
        daily_double_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show "Daily Double" title
        title_label = ttk.Label(
            daily_double_frame,
            text="DAILY DOUBLE",
            font=(CATEGORY_FONT[0], 36, "bold"),
            foreground=DAILY_DOUBLE_COLOR
        )
        title_label.pack(pady=(20, 40))
        
        # Show category
        category_label = ttk.Label(
            daily_double_frame,
            text=f"Category: {question.category}",
            font=(CATEGORY_FONT[0], 18)
        )
        category_label.pack(pady=10)
        
        # Team making the wager
        team = self.game.current_team
        team_label = ttk.Label(
            daily_double_frame,
            text=f"{team['name']}, make your wager:",
            font=(TEAM_FONT[0], 16)
        )
        team_label.pack(pady=10)
        
        # Create a wager entry
        wager_frame = ttk.Frame(daily_double_frame)
        wager_frame.pack(pady=20)
        
        wager_label = ttk.Label(
            wager_frame,
            text="$",
            font=(VALUE_FONT[0], 18)
        )
        wager_label.pack(side=tk.LEFT)
        
        # Calculate maximum wager
        max_wager = max(team['score'], 1000) if self.game.current_round_name == ROUND_NAMES[0] else max(team['score'], 2000)
        
        self.wager_entry = ttk.Entry(
            wager_frame,
            font=(VALUE_FONT[0], 18),
            width=8
        )
        self.wager_entry.pack(side=tk.LEFT, padx=5)
        self.wager_entry.insert(0, str(question.value))  # Default wager is the question value
        
        # Add a note about maximum wager
        max_wager_label = ttk.Label(
            daily_double_frame,
            text=f"Maximum wager: ${max_wager}",
            font=(TEAM_FONT[0], 12, "italic")
        )
        max_wager_label.pack(pady=5)
        
        # Submit button
        submit_button = ttk.Button(
            daily_double_frame,
            text="Submit Wager",
            command=self._submit_daily_double_wager
        )
        submit_button.pack(pady=20)
    
    def _submit_daily_double_wager(self):
        """Handle submitting a Daily Double wager."""
        if not self.current_question:
            return
            
        # Get the wager amount
        try:
            wager = int(self.wager_entry.get())
            
            # Validate wager
            team = self.game.current_team
            max_wager = max(team['score'], 1000) if self.game.current_round_name == ROUND_NAMES[0] else max(team['score'], 2000)
            
            if wager <= 0:
                messagebox.showerror("Invalid Wager", "Wager must be positive.")
                return
                
            if wager > max_wager:
                messagebox.showerror("Invalid Wager", f"Maximum wager is ${max_wager}.")
                return
                
            # Store the wager and show the question
            self.wager_amount = wager
            self._show_question(self.current_question)
            
        except ValueError:
            messagebox.showerror("Invalid Wager", "Please enter a valid number.")
    
    def _show_question(self, question):
        """Show a question on the screen.
        
        Args:
            question (Question): The question to display
        """
        # Clear the game board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        question_display = ttk.Frame(self.board_frame, padding="20")
        question_display.pack(fill=tk.BOTH, expand=True)
        
        # Category
        category_label = ttk.Label(
            question_display,
            text=f"Category: {question.category}",
            font=(CATEGORY_FONT[0], 16)
        )
        category_label.pack(pady=(10, 20))
        
        # Value
        if question.is_daily_double:
            value_text = f"Daily Double: ${self.wager_amount}"
        else:
            value_text = f"${question.value}"
            
        value_label = ttk.Label(
            question_display,
            text=value_text,
            font=(VALUE_FONT[0], 16)
        )
        value_label.pack(pady=(0, 20))
        
        # Question text
        question_label = ttk.Label(
            question_display,
            text=question.text,
            font=QUESTION_FONT,
            wraplength=600,
            justify=tk.CENTER
        )
        question_label.pack(pady=30)
        
        # Timer
        self.timer_label = ttk.Label(
            question_display,
            text=f"Time remaining: {QUESTION_TIMER} seconds",
            font=(TEAM_FONT[0], 12)
        )
        self.timer_label.pack(pady=10)
        
        # Controls frame
        controls_frame = ttk.Frame(question_display)
        controls_frame.pack(pady=20)
        
        # Show answer button
        show_answer_button = ttk.Button(
            controls_frame,
            text="Show Answer",
            command=self._show_answer
        )
        show_answer_button.pack(side=tk.LEFT, padx=10)
        
        # Correct/Incorrect buttons
        if not question.is_daily_double:
            # For regular questions, we need to know which team is answering
            team_frame = ttk.Frame(question_display)
            team_frame.pack(pady=10)
            
            team_label = ttk.Label(
                team_frame,
                text="Select answering team:",
                font=(TEAM_FONT[0], 12)
            )
            team_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Team selector
            self.answering_team_var = tk.StringVar()
            self.answering_team_var.set(self.game.current_team["name"])
            
            team_dropdown = ttk.Combobox(
                team_frame,
                textvariable=self.answering_team_var,
                values=[team["name"] for team in self.game.teams],
                state="readonly",
                width=15
            )
            team_dropdown.pack(side=tk.LEFT)
            
            # Correct/Incorrect buttons frame
            answer_buttons_frame = ttk.Frame(question_display)
            answer_buttons_frame.pack(pady=10)
            
            correct_button = ttk.Button(
                answer_buttons_frame,
                text="Correct",
                command=lambda: self._handle_answer(True)
            )
            correct_button.pack(side=tk.LEFT, padx=10)
            
            incorrect_button = ttk.Button(
                answer_buttons_frame,
                text="Incorrect",
                command=lambda: self._handle_answer(False)
            )
            incorrect_button.pack(side=tk.LEFT, padx=10)
        else:
            # For Daily Doubles, only the selecting team can answer
            answer_buttons_frame = ttk.Frame(question_display)
            answer_buttons_frame.pack(pady=10)
            
            correct_button = ttk.Button(
                answer_buttons_frame,
                text="Correct",
                command=lambda: self._handle_daily_double_answer(True)
            )
            correct_button.pack(side=tk.LEFT, padx=10)
            
            incorrect_button = ttk.Button(
                answer_buttons_frame,
                text="Incorrect",
                command=lambda: self._handle_daily_double_answer(False)
            )
            incorrect_button.pack(side=tk.LEFT, padx=10)
        
        # Start the timer
        self._start_timer(QUESTION_TIMER)
    
    def _show_answer(self):
        """Show the answer to the current question."""
        if not self.current_question:
            return
            
        # Stop the timer
        self._stop_timer()
        
        # Create a top-level window for the answer
        answer_window = tk.Toplevel(self.root)
        answer_window.title("Answer")
        answer_window.geometry("500x300")
        answer_window.transient(self.root)
        answer_window.grab_set()
        
        # Add padding and styling
        answer_frame = ttk.Frame(answer_window, padding="20")
        answer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Answer label
        answer_label = ttk.Label(
            answer_frame,
            text="The correct answer is:",
            font=(CATEGORY_FONT[0], 14)
        )
        answer_label.pack(pady=(10, 20))
        
        # The answer itself
        the_answer = ttk.Label(
            answer_frame,
            text=self.current_question.answer,
            font=ANSWER_FONT,
            wraplength=400,
            justify=tk.CENTER
        )
        the_answer.pack(pady=20)
        
        # Close button
        close_button = ttk.Button(
            answer_frame,
            text="Close",
            command=answer_window.destroy
        )
        close_button.pack(pady=20)
    
    def _handle_answer(self, correct):
        """Handle a regular question being answered.
        
        Args:
            correct (bool): Whether the answer was correct
        """
        if not self.current_question:
            return
            
        # Stop the timer
        self._stop_timer()
        
        # Find the team that answered
        team_name = self.answering_team_var.get()
        team_index = -1
        
        for i, team in enumerate(self.game.teams):
            if team["name"] == team_name:
                team_index = i
                break
                
        if team_index == -1:
            return
            
        # Update score
        points = self.current_question.value
        self.game.update_score(team_index, points, correct)
        
        # Mark question as played
        self.current_question.play()
        
        # Update the next team's turn (if correct, the answering team gets to choose next)
        if correct:
            self.game.current_team_index = team_index
        else:
            self.game.next_team()
            
        # Update the UI
        self._update_scoreboard()
        self._update_status_bar()
        
        # Show a message
        if correct:
            messagebox.showinfo("Correct", f"{team_name} gets ${points}!")
        else:
            messagebox.showinfo("Incorrect", f"{team_name} loses ${points}!")
            
        # Return to the game board
        self._build_game_board()
        
        # Check if the round is complete
        if self.game.current_round.is_complete():
            messagebox.showinfo("Round Complete", f"{self.game.current_round_name} round is complete!")
            self._next_round()
    
    def _handle_daily_double_answer(self, correct):
        """Handle a Daily Double question being answered.
        
        Args:
            correct (bool): Whether the answer was correct
        """
        if not self.current_question:
            return
            
        # Stop the timer
        self._stop_timer()
        
        # Update score
        team_index = self.game.current_team_index
        team_name = self.game.current_team["name"]
        
        self.game.update_score(team_index, self.wager_amount, correct)
        
        # Mark question as played
        self.current_question.play()
        
        # Update the UI
        self._update_scoreboard()
        
        # Show a message
        if correct:
            messagebox.showinfo("Correct", f"{team_name} wins ${self.wager_amount}!")
        else:
            messagebox.showinfo("Incorrect", f"{team_name} loses ${self.wager_amount}!")
            
        # Return to the game board
        self._build_game_board()
        
        # Check if the round is complete
        if self.game.current_round.is_complete():
            messagebox.showinfo("Round Complete", f"{self.game.current_round_name} round is complete!")
            self._next_round()
    
    def _make_final_wagers(self):
        """Handle making wagers for Final Jeopardy."""
        # Create a top-level window for wagers
        wager_window = tk.Toplevel(self.root)
        wager_window.title("Final Jeopardy Wagers")
        wager_window.geometry("500x400")
        wager_window.transient(self.root)
        wager_window.grab_set()
        
        # Add padding and styling
        wager_frame = ttk.Frame(wager_window, padding="20")
        wager_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            wager_frame,
            text="Final Jeopardy Wagers",
            font=(CATEGORY_FONT[0], 18, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Instructions
        instructions = ttk.Label(
            wager_frame,
            text="Enter wager for each team (wagers cannot exceed current score):",
            font=(TEAM_FONT[0], 12)
        )
        instructions.pack(pady=(0, 20))
        
        # Create entries for each team
        team_entries = []
        
        for team in self.game.teams:
            team_frame = ttk.Frame(wager_frame)
            team_frame.pack(fill=tk.X, pady=5)
            
            team_label = ttk.Label(
                team_frame,
                text=f"{team['name']} (Current score: ${team['score']}):",
                font=TEAM_FONT,
                width=30,
                anchor=tk.W
            )
            team_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Wager entry
            wager_entry = ttk.Entry(team_frame, width=10)
            wager_entry.pack(side=tk.LEFT)
            wager_entry.insert(0, str(team['score']))  # Default to current score
            
            team_entries.append((team, wager_entry))
        
        # Submit button
        submit_frame = ttk.Frame(wager_frame)
        submit_frame.pack(pady=20)
        
        submit_button = ttk.Button(
            submit_frame,
            text="Submit Wagers",
            command=lambda: self._submit_final_wagers(team_entries, wager_window)
        )
        submit_button.pack()
    
    def _submit_final_wagers(self, team_entries, window):
        """Submit wagers for Final Jeopardy.
        
        Args:
            team_entries (list): List of (team, entry) tuples
            window (Toplevel): The wager window to close
        """
        # Store wagers
        self.final_wagers = {}
        
        for team, entry in team_entries:
            try:
                wager = int(entry.get())
                
                # Validate wager
                if wager < 0:
                    messagebox.showerror("Invalid Wager", f"Wager for {team['name']} must be non-negative.")
                    return
                    
                if wager > team['score']:
                    messagebox.showerror("Invalid Wager", f"Wager for {team['name']} cannot exceed current score (${team['score']}).")
                    return
                    
                self.final_wagers[team['name']] = wager
                
            except ValueError:
                messagebox.showerror("Invalid Wager", f"Please enter a valid number for {team['name']}.")
                return
        
        # Close the window
        window.destroy()
        
        # Show a confirmation
        messagebox.showinfo("Wagers Submitted", "All wagers have been submitted for Final Jeopardy.")
    
    def _show_final_question(self):
        """Show the Final Jeopardy question."""
        if self.game.current_round_name != ROUND_NAMES[2]:
            return
            
        # Make sure wagers have been submitted
        if not hasattr(self, 'final_wagers'):
            messagebox.showinfo("Wagers Required", "Please submit wagers before showing the question.")
            self._make_final_wagers()
            return
            
        # Get the Final Jeopardy question
        final_round = self.game.rounds[ROUND_NAMES[2]]
        if not final_round.categories:
            messagebox.showinfo("Error", "No Final Jeopardy question found.")
            return
            
        category = final_round.categories[0]
        question = final_round.questions[category][0]
        
        # Play the Final Jeopardy sound
        self._play_sound(FINAL_JEOPARDY_SOUND)
        
        # Clear the game board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        final_question_frame = ttk.Frame(self.board_frame, padding="20")
        final_question_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            final_question_frame,
            text="FINAL JEOPARDY",
            font=(CATEGORY_FONT[0], 24, "bold"),
            foreground=BG_COLOR
        )
        title_label.pack(pady=(10, 20))
        
        # Category
        category_label = ttk.Label(
            final_question_frame,
            text=f"Category: {category}",
            font=(CATEGORY_FONT[0], 18)
        )
        category_label.pack(pady=(0, 20))
        
        # Question
        question_label = ttk.Label(
            final_question_frame,
            text=question.text,
            font=QUESTION_FONT,
            wraplength=600,
            justify=tk.CENTER
        )
        question_label.pack(pady=30)
        
        # Timer
        self.timer_label = ttk.Label(
            final_question_frame,
            text=f"Time remaining: {FINAL_JEOPARDY_TIMER} seconds",
            font=(TEAM_FONT[0], 12)
        )
        self.timer_label.pack(pady=10)
        
        # Start the timer
        self._start_timer(FINAL_JEOPARDY_TIMER)
        
        # Buttons
        buttons_frame = ttk.Frame(final_question_frame)
        buttons_frame.pack(pady=20)
        
        show_answer_button = ttk.Button(
            buttons_frame,
            text="Show Answer",
            command=lambda: self._show_final_answer(question)
        )
        show_answer_button.pack(side=tk.LEFT, padx=10)
    
    def _show_final_answer(self, question):
        """Show the Final Jeopardy answer and process results.
        
        Args:
            question (Question): The Final Jeopardy question
        """
        # Stop the timer
        self._stop_timer()
        
        # Create a top-level window for the answer and results
        answer_window = tk.Toplevel(self.root)
        answer_window.title("Final Jeopardy Answer")
        answer_window.geometry("600x500")
        answer_window.transient(self.root)
        answer_window.grab_set()
        
        # Add padding and styling
        answer_frame = ttk.Frame(answer_window, padding="20")
        answer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Answer label
        answer_label = ttk.Label(
            answer_frame,
            text="The correct Final Jeopardy answer is:",
            font=(CATEGORY_FONT[0], 16)
        )
        answer_label.pack(pady=(10, 20))
        
        # The answer itself
        the_answer = ttk.Label(
            answer_frame,
            text=question.answer,
            font=ANSWER_FONT,
            wraplength=500,
            justify=tk.CENTER
        )
        the_answer.pack(pady=20)
        
        # Create checkboxes for each team
        team_responses = []
        
        teams_frame = ttk.Frame(answer_frame)
        teams_frame.pack(fill=tk.X, pady=20)
        
        response_label = ttk.Label(
            teams_frame,
            text="Select teams with correct answers:",
            font=(TEAM_FONT[0], 14)
        )
        response_label.pack(pady=(0, 10))
        
        for team in self.game.teams:
            team_frame = ttk.Frame(teams_frame)
            team_frame.pack(fill=tk.X, pady=5)
            
            correct_var = tk.BooleanVar(value=False)
            
            team_check = ttk.Checkbutton(
                team_frame,
                text=f"{team['name']} (Wagered: ${self.final_wagers.get(team['name'], 0)})",
                variable=correct_var
            )
            team_check.pack(side=tk.LEFT)
            
            team_responses.append((team, correct_var))
        
        # Submit button
        submit_button = ttk.Button(
            answer_frame,
            text="Submit Results",
            command=lambda: self._process_final_results(team_responses, answer_window)
        )
        submit_button.pack(pady=20)
    
    def _process_final_results(self, team_responses, window):
        """Process the Final Jeopardy results.
        
        Args:
            team_responses (list): List of (team, correct_var) tuples
            window (Toplevel): The window to close
        """
        # Update scores
        for team, correct_var in team_responses:
            wager = self.final_wagers.get(team['name'], 0)
            
            for i, game_team in enumerate(self.game.teams):
                if game_team['name'] == team['name']:
                    self.game.update_score(i, wager, correct_var.get())
                    break
        
        # Close the window
        window.destroy()
        
        # Update the scoreboard
        self._update_scoreboard()
        
        # Show final results
        self._show_game_results()
    
    def _show_game_results(self):
        """Show the final game results."""
        # Clear the game board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        results_frame = ttk.Frame(self.board_frame, padding="20")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            results_frame,
            text="FINAL RESULTS",
            font=(CATEGORY_FONT[0], 36, "bold"),
            foreground=BG_COLOR
        )
        title_label.pack(pady=(20, 40))
        
        # Get winners
        winners = self.game.get_winners()
        
        if winners:
            if len(winners) == 1:
                winner_text = f"The winner is {winners[0]['name']} with ${winners[0]['score']}!"
            else:
                winner_names = ", ".join(winner['name'] for winner in winners)
                winner_text = f"It's a tie between {winner_names} with ${winners[0]['score']}!"
                
            winner_label = ttk.Label(
                results_frame,
                text=winner_text,
                font=(CATEGORY_FONT[0], 20),
                foreground=CORRECT_COLOR
            )
            winner_label.pack(pady=20)
        
        # Final scores
        scores_frame = ttk.Frame(results_frame)
        scores_frame.pack(pady=20)
        
        scores_label = ttk.Label(
            scores_frame,
            text="Final Scores:",
            font=(CATEGORY_FONT[0], 16)
        )
        scores_label.pack(pady=(0, 10))
        
        # Sort teams by score
        sorted_teams = sorted(self.game.teams, key=lambda t: t['score'], reverse=True)
        
        for team in sorted_teams:
            team_score = ttk.Label(
                scores_frame,
                text=f"{team['name']}: ${team['score']}",
                font=SCORE_FONT
            )
            team_score.pack(pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(results_frame)
        buttons_frame.pack(pady=30)
        
        new_game_button = ttk.Button(
            buttons_frame,
            text="New Game",
            command=self._new_game
        )
        new_game_button.pack(side=tk.LEFT, padx=10)
        
        exit_button = ttk.Button(
            buttons_frame,
            text="Exit",
            command=self.root.quit
        )
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # Mark game as over
        self.game.game_over = True
    
    def _start_timer(self, seconds):
        """Start a countdown timer.
        
        Args:
            seconds (int): The number of seconds for the timer
        """
        self.timer_value = seconds
        self.timer_running = True
        
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_running = False
            self.timer_thread.join()
            
        self.timer_thread = threading.Thread(target=self._timer_countdown)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        # Play the timer sound
        self._play_sound(TIMER_SOUND)
    
    def _timer_countdown(self):
        """Countdown timer thread function."""
        while self.timer_running and self.timer_value > 0:
            # Update the timer label
            self.root.after(0, self._update_timer_label)
            
            # Wait 1 second
            time.sleep(1)
            self.timer_value -= 1
            
        # Timer finished
        if self.timer_running and self.timer_value <= 0:
            self.root.after(0, self._timer_finished)
    
    def _update_timer_label(self):
        """Update the timer label with current value."""
        if hasattr(self, 'timer_label'):
            self.timer_label.config(text=f"Time remaining: {self.timer_value} seconds")
    
    def _timer_finished(self):
        """Handle timer finished event."""
        if hasattr(self, 'timer_label'):
            self.timer_label.config(text="Time's up!")
            
        # Play a sound or show a message
        messagebox.showinfo("Time's Up", "The time has expired!")
    
    def _stop_timer(self):
        """Stop the countdown timer."""
        self.timer_running = False
        
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(0.1)
    
    def _play_sound(self, sound_file):
        """Play a sound effect.
        
        Args:
            sound_file (str): Path to the sound file
        """
        if not self.sound_enabled:
            return
            
        try:
            if os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
        except Exception:
            # Silently fail if sound can't be played
            pass
    
    def _update_scoreboard(self):
        """Update the scoreboard display."""
        for i, team in enumerate(self.game.teams):
            if i < len(self.score_labels):
                self.score_labels[i].config(text=f"${team['score']}")
        
        # Update current turn indicator
        for i, frame in enumerate(self.team_frames):
            if hasattr(frame, 'indicator'):
                frame.indicator.destroy()
                delattr(frame, 'indicator')
                
            if i == self.game.current_team_index:
                indicator = ttk.Label(
                    frame,
                    text="Current Turn",
                    font=(TEAM_FONT[0], 10, "italic"),
                    background=self.game.teams[i]["color"],
                    foreground=TEXT_COLOR,
                    anchor=tk.CENTER
                )
                indicator.pack(fill=tk.X)
                frame.indicator = indicator
    
    def _update_status_bar(self):
        """Update the status bar."""
        # Update round label
        self.round_label.config(text=f"Round: {self.game.current_round_name}")
        
        # Update current team label
        team = self.game.current_team
        if team:
            self.current_team_label.config(text=f"Current Team: {team['name']}")
    
    def _load_questions(self):
        """Load questions from an Excel file."""
        file_path = self.excel_handler.load_file()
        if not file_path:
            return
            
        # Parse the file
        game_data = self.excel_handler.parse_file(file_path)
        if not game_data:
            return
            
        # Set up the game with the loaded data
        
        # Jeopardy round
        jeopardy_data = game_data["rounds"][ROUND_NAMES[0]]
        self.game.setup_round(
            ROUND_NAMES[0],
            jeopardy_data["categories"],
            jeopardy_data["questions"]
        )
        
        # Double Jeopardy round
        double_data = game_data["rounds"][ROUND_NAMES[1]]
        self.game.setup_round(
            ROUND_NAMES[1],
            double_data["categories"],
            double_data["questions"]
        )
        
        # Final Jeopardy
        final_data = game_data["rounds"][ROUND_NAMES[2]]
        self.game.setup_final_jeopardy(
            final_data["category"],
            final_data["question"],
            final_data["answer"]
        )
        
        # Set Daily Doubles
        self.game.daily_doubles = game_data["daily_doubles"]
        
        # Reset the game state
        self.game.current_round_name = ROUND_NAMES[0]
        self.game.current_team_index = 0
        self.game.game_over = False
        
        for team in self.game.teams:
            team["score"] = 0
            
        # Update the UI
        self._update_scoreboard()
        self._update_status_bar()
        self._build_game_board()
        
        messagebox.showinfo("Success", "Questions loaded successfully!")
    
    def _create_template(self):
        """Create a template Excel file."""
        # Make sure the templates directory exists
        file_path = self.excel_handler.ensure_template_exists()
        if file_path:
            messagebox.showinfo("Template Created", f"Template file created at:\n{file_path}")
    
    def _new_game(self):
        """Start a new game."""
        if messagebox.askyesno("New Game", "Start a new game? All scores will be reset."):
            self.game.reset_game()
            self._update_scoreboard()
            self._update_status_bar()
            self._build_game_board()
    
    def _manage_teams(self):
        """Open the team management dialog."""
        # Create a top-level window
        teams_window = tk.Toplevel(self.root)
        teams_window.title("Manage Teams")
        teams_window.geometry("500x400")
        teams_window.transient(self.root)
        teams_window.grab_set()
        
        # Add padding and styling
        teams_frame = ttk.Frame(teams_window, padding="20")
        teams_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            teams_frame,
            text="Manage Teams",
            font=(CATEGORY_FONT[0], 18, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Team list
        teams_list_frame = ttk.Frame(teams_frame)
        teams_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Team entries
        team_entries = []
        team_colors = []
        
        for i, team in enumerate(self.game.teams):
            team_frame = ttk.Frame(teams_list_frame)
            team_frame.pack(fill=tk.X, pady=5)
            
            # Team number
            number_label = ttk.Label(
                team_frame,
                text=f"Team {i+1}:",
                width=8
            )
            number_label.pack(side=tk.LEFT, padx=(0, 5))
            
            # Team name entry
            name_entry = ttk.Entry(team_frame, width=20)
            name_entry.insert(0, team["name"])
            name_entry.pack(side=tk.LEFT, padx=5)
            team_entries.append(name_entry)
            
            # Team color picker (simplified)
            color_var = tk.StringVar(value=team["color"])
            team_colors.append(color_var)
            
            color_options = [
                ("#3498db", "Blue"),
                ("#e74c3c", "Red"),
                ("#2ecc71", "Green"),
                ("#f39c12", "Orange"),
                ("#9b59b6", "Purple"),
                ("#1abc9c", "Teal"),
                ("#d35400", "Brown"),
                ("#34495e", "Navy")
            ]
            
            color_dropdown = ttk.Combobox(
                team_frame,
                textvariable=color_var,
                values=[color[1] for color in color_options],
                state="readonly",
                width=10
            )
            color_dropdown.pack(side=tk.LEFT, padx=5)
            
            # Set the current selection
            for j, (color_code, color_name) in enumerate(color_options):
                if color_code == team["color"]:
                    color_dropdown.current(j)
                    break
            
            # Delete button
            delete_button = ttk.Button(
                team_frame,
                text="✕",
                width=3,
                command=lambda frame=team_frame, idx=i: self._remove_team_entry(frame, idx, team_entries, team_colors)
            )
            delete_button.pack(side=tk.LEFT, padx=5)
        
        # Add team button
        add_frame = ttk.Frame(teams_frame)
        add_frame.pack(fill=tk.X, pady=10)
        
        add_button = ttk.Button(
            add_frame,
            text="Add Team",
            command=lambda: self._add_team_entry(teams_list_frame, team_entries, team_colors)
        )
        add_button.pack(side=tk.LEFT)
        
        # Buttons frame
        buttons_frame = ttk.Frame(teams_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        save_button = ttk.Button(
            buttons_frame,
            text="Save",
            command=lambda: self._save_teams(team_entries, team_colors, teams_window)
        )
        save_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=teams_window.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def _add_team_entry(self, parent, entries, colors):
        """Add a new team entry to the team management dialog.
        
        Args:
            parent (Frame): The parent frame
            entries (list): List of team name entries
            colors (list): List of team color variables
        """
        team_frame = ttk.Frame(parent)
        team_frame.pack(fill=tk.X, pady=5)
        
        # Team number
        number_label = ttk.Label(
            team_frame,
            text=f"Team {len(entries)+1}:",
            width=8
        )
        number_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Team name entry
        name_entry = ttk.Entry(team_frame, width=20)
        name_entry.insert(0, f"Team {len(entries)+1}")
        name_entry.pack(side=tk.LEFT, padx=5)
        entries.append(name_entry)
        
        # Team color picker (simplified)
        color_var = tk.StringVar(value="#3498db")
        colors.append(color_var)
        
        color_options = [
            ("#3498db", "Blue"),
            ("#e74c3c", "Red"),
            ("#2ecc71", "Green"),
            ("#f39c12", "Orange"),
            ("#9b59b6", "Purple"),
            ("#1abc9c", "Teal"),
            ("#d35400", "Brown"),
            ("#34495e", "Navy")
        ]
        
        color_dropdown = ttk.Combobox(
            team_frame,
            textvariable=color_var,
            values=[color[1] for color in color_options],
            state="readonly",
            width=10
        )
        color_dropdown.current(0)
        color_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_button = ttk.Button(
            team_frame,
            text="✕",
            width=3,
            command=lambda frame=team_frame, idx=len(entries)-1: self._remove_team_entry(frame, idx, entries, colors)
        )
        delete_button.pack(side=tk.LEFT, padx=5)
    
    def _remove_team_entry(self, frame, index, entries, colors):
        """Remove a team entry from the team management dialog.
        
        Args:
            frame (Frame): The team frame to remove
            index (int): The index of the team entry
            entries (list): List of team name entries
            colors (list): List of team color variables
        """
        frame.destroy()
        
        # Remove from lists
        if 0 <= index < len(entries):
            entries.pop(index)
            colors.pop(index)
    
    def _save_teams(self, entries, colors, window):
        """Save the teams from the team management dialog.
        
        Args:
            entries (list): List of team name entries
            colors (list): List of team color variables
            window (Toplevel): The team management window to close
        """
        if not entries:
            messagebox.showerror("Error", "You must have at least one team.")
            return
            
        # Map color names back to color codes
        color_map = {
            "Blue": "#3498db",
            "Red": "#e74c3c",
            "Green": "#2ecc71",
            "Orange": "#f39c12",
            "Purple": "#9b59b6",
            "Teal": "#1abc9c",
            "Brown": "#d35400",
            "Navy": "#34495e"
        }
        
        # Create new teams
        new_teams = []
        
        for i, entry in enumerate(entries):
            name = entry.get().strip()
            if not name:
                name = f"Team {i+1}"
                
            color_name = colors[i].get()
            color_code = color_map.get(color_name, "#3498db")
            
            new_teams.append({"name": name, "score": 0, "color": color_code})
        
        # Update the game's teams
        self.game.teams = new_teams
        self.game.current_team_index = 0
        
        # Rebuild the scoreboard
        for widget in self.scoreboard_frame.winfo_children():
            widget.destroy()
            
        self._create_scoreboard()
        self._update_status_bar()
        
        # Close the window
        window.destroy()
    
    def _reset_scores(self):
        """Reset all team scores."""
        if messagebox.askyesno("Reset Scores", "Reset all scores to zero?"):
            for team in self.game.teams:
                team["score"] = 0
                
            self._update_scoreboard()
    
    def _next_round(self):
        """Move to the next round."""
        if self.game.game_over:
            return
            
        if self.game.current_round_name == ROUND_NAMES[2]:
            # If in Final Jeopardy, show results
            self._show_game_results()
            return
            
        # Confirm with the user
        message = f"Move to the {self.game.current_round_name} round?"
        if self.game.current_round_name == ROUND_NAMES[0]:
            message = f"Move to the {ROUND_NAMES[1]} round?"
        elif self.game.current_round_name == ROUND_NAMES[1]:
            message = f"Move to the {ROUND_NAMES[2]} round (Final Jeopardy)?"
            
        if not messagebox.askyesno("Next Round", message):
            return
            
        # Move to the next round
        next_round = self.game.next_round()
        if next_round:
            self._update_status_bar()
            self._build_game_board()
    
    def _show_help(self):
        """Show the help information."""
        help_text = """
        How to Play Python Jeopardy
        ---------------------------
        
        1. Load questions from an Excel file using File > Load Questions
        
        2. Set up teams using Game > Manage Teams
        
        3. Game Play:
           - Teams take turns selecting questions
           - The current team is highlighted in the scoreboard
           - After selecting a question, the team attempts to answer
           - Correct answers earn points, incorrect answers lose points
           - Daily Doubles allow the team to wager points
           
        4. After completing a round, move to the next round using Game > Next Round
        
        5. Final Jeopardy:
           - All teams make wagers based on their current scores
           - Everyone answers the same final question
           - Correct answers add the wagered points, incorrect answers subtract them
           
        6. The team with the highest score at the end wins!
        """
        
        # Create a top-level window
        help_window = tk.Toplevel(self.root)
        help_window.title("How to Play")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        # Add padding and styling
        help_frame = ttk.Frame(help_window, padding="20")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            help_frame,
            text="How to Play Python Jeopardy",
            font=(CATEGORY_FONT[0], 18, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Help text
        text_widget = tk.Text(
            help_frame,
            wrap=tk.WORD,
            font=(CATEGORY_FONT[0], 12),
            padx=10,
            pady=10,
            width=60,
            height=20
        )
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(help_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        close_button = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy
        )
        close_button.pack(pady=10)
    
    def _show_about(self):
        """Show the about information."""
        # Create a top-level window
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        
        # Add padding and styling
        about_frame = ttk.Frame(about_window, padding="20")
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            about_frame,
            text="Python Jeopardy Game",
            font=(CATEGORY_FONT[0], 18, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Version
        version_label = ttk.Label(
            about_frame,
            text="Version 1.0",
            font=(CATEGORY_FONT[0], 12)
        )
        version_label.pack(pady=5)
        
        # Description
        description = (
            "A customizable Jeopardy game created with Python and Tkinter.\n\n"
            "Features:\n"
            "- Multiple categories and questions\n"
            "- Team score tracking\n"
            "- Daily Doubles and Final Jeopardy\n"
            "- Custom questions via Excel files"
        )
        
        desc_label = ttk.Label(
            about_frame,
            text=description,
            font=(CATEGORY_FONT[0], 12),
            justify=tk.CENTER,
            wraplength=300
        )
        desc_label.pack(pady=10)
        
        # Close button
        close_button = ttk.Button(
            about_frame,
            text="Close",
            command=about_window.destroy
        )
        close_button.pack(pady=10)