"""
Jeopardy Game - Game Logic
-------------------------
This module contains the game logic for the Jeopardy game.
"""

import random
from config import ROUND_NAMES, JEOPARDY_VALUES, DOUBLE_JEOPARDY_VALUES

class Question:
    """Represents a Jeopardy question."""
    
    def __init__(self, category, value, text, answer, is_daily_double=False):
        """Initialize a Question object.
        
        Args:
            category (str): The category of the question
            value (int): The point value of the question
            text (str): The text of the question
            answer (str): The answer to the question
            is_daily_double (bool, optional): Whether this is a Daily Double. Defaults to False.
        """
        self.category = category
        self.value = value
        self.text = text
        self.answer = answer
        self.is_daily_double = is_daily_double
        self.played = False
    
    def play(self):
        """Mark the question as played."""
        self.played = True
    
    def __str__(self):
        """Return a string representation of the question."""
        return f"{self.category} for {self.value}: {self.text}"


class JeopardyRound:
    """Represents a round in the Jeopardy game."""
    
    def __init__(self, name, categories=None, questions=None):
        """Initialize a JeopardyRound object.
        
        Args:
            name (str): The name of the round (e.g., "Jeopardy", "Double Jeopardy")
            categories (list, optional): List of category names. Defaults to None.
            questions (dict, optional): Dictionary of questions by category and value. Defaults to None.
        """
        self.name = name
        self.categories = categories or []
        self.questions = questions or {}  # Dict of form {category: {value: Question}}
        self.completed = False
    
    def add_category(self, category):
        """Add a category to the round.
        
        Args:
            category (str): The name of the category
        """
        if category not in self.categories:
            self.categories.append(category)
            self.questions[category] = {}
    
    def add_question(self, question):
        """Add a question to the round.
        
        Args:
            question (Question): The Question object to add
        """
        if question.category not in self.categories:
            self.add_category(question.category)
        
        self.questions[question.category][question.value] = question
    
    def get_question(self, category, value):
        """Get a question by category and value.
        
        Args:
            category (str): The category name
            value (int): The value of the question
            
        Returns:
            Question: The Question object, or None if not found
        """
        return self.questions.get(category, {}).get(value)
    
    def is_complete(self):
        """Check if all questions in the round have been played.
        
        Returns:
            bool: True if all questions have been played, False otherwise
        """
        for category in self.questions:
            for value in self.questions[category]:
                if not self.questions[category][value].played:
                    return False
        
        self.completed = True
        return True


class FinalJeopardyRound(JeopardyRound):
    """Represents the Final Jeopardy round."""
    
    def __init__(self, category=None, question=None, answer=None):
        """Initialize a FinalJeopardyRound object.
        
        Args:
            category (str, optional): The category for Final Jeopardy. Defaults to None.
            question (str, optional): The Final Jeopardy question. Defaults to None.
            answer (str, optional): The Final Jeopardy answer. Defaults to None.
        """
        super().__init__("Final Jeopardy", [category] if category else [])
        
        if category and question and answer:
            final_question = Question(category, 0, question, answer)
            self.questions[category] = {0: final_question}
    
    def set_question(self, category, question, answer):
        """Set the Final Jeopardy question.
        
        Args:
            category (str): The category for Final Jeopardy
            question (str): The Final Jeopardy question
            answer (str): The Final Jeopardy answer
        """
        self.categories = [category]
        final_question = Question(category, 0, question, answer)
        self.questions = {category: {0: final_question}}


class JeopardyGame:
    """Main game logic for Jeopardy."""
    
    def __init__(self, teams=None):
        """Initialize a JeopardyGame object.
        
        Args:
            teams (list, optional): List of team dictionaries. Defaults to None.
        """
        self.teams = teams or []
        self.current_team_index = 0
        self.rounds = {
            ROUND_NAMES[0]: JeopardyRound(ROUND_NAMES[0]),
            ROUND_NAMES[1]: JeopardyRound(ROUND_NAMES[1]),
            ROUND_NAMES[2]: FinalJeopardyRound()
        }
        self.current_round_name = ROUND_NAMES[0]
        self.daily_doubles = []
        self.game_over = False
    
    @property
    def current_round(self):
        """Get the current round of the game.
        
        Returns:
            JeopardyRound: The current round
        """
        return self.rounds[self.current_round_name]
    
    @property
    def current_team(self):
        """Get the current team.
        
        Returns:
            dict: The current team dictionary
        """
        if not self.teams:
            return None
        return self.teams[self.current_team_index]
    
    def add_team(self, name, color="#3498db"):
        """Add a team to the game.
        
        Args:
            name (str): The name of the team
            color (str, optional): The color associated with the team. Defaults to "#3498db".
        """
        self.teams.append({"name": name, "score": 0, "color": color})
    
    def next_team(self):
        """Move to the next team's turn.
        
        Returns:
            dict: The new current team
        """
        if not self.teams:
            return None
        
        self.current_team_index = (self.current_team_index + 1) % len(self.teams)
        return self.current_team
    
    def update_score(self, team_index, points, correct=True):
        """Update a team's score.
        
        Args:
            team_index (int): The index of the team to update
            points (int): The points to add (or subtract if correct is False)
            correct (bool, optional): Whether the answer was correct. Defaults to True.
        """
        if 0 <= team_index < len(self.teams):
            if correct:
                self.teams[team_index]["score"] += points
            else:
                self.teams[team_index]["score"] -= points
    
    def setup_round(self, round_name, categories, questions_data):
        """Set up a round with categories and questions.
        
        Args:
            round_name (str): The name of the round to set up
            categories (list): List of category names
            questions_data (dict): Dictionary of questions data by category and value
        """
        if round_name not in self.rounds:
            return
        
        round_obj = self.rounds[round_name]
        
        # Clear existing data
        round_obj.categories = []
        round_obj.questions = {}
        
        # Add categories
        for category in categories:
            round_obj.add_category(category)
        
        # Add questions
        for category in questions_data:
            for value, data in questions_data[category].items():
                question = Question(
                    category=category,
                    value=value,
                    text=data["question"],
                    answer=data["answer"],
                    is_daily_double=data.get("is_daily_double", False)
                )
                round_obj.add_question(question)
                
                if question.is_daily_double:
                    self.daily_doubles.append((round_name, category, value))
    
    def setup_final_jeopardy(self, category, question, answer):
        """Set up the Final Jeopardy round.
        
        Args:
            category (str): The Final Jeopardy category
            question (str): The Final Jeopardy question
            answer (str): The Final Jeopardy answer
        """
        final_round = self.rounds[ROUND_NAMES[2]]
        if isinstance(final_round, FinalJeopardyRound):
            final_round.set_question(category, question, answer)
    
    def next_round(self):
        """Move to the next round.
        
        Returns:
            str: The name of the new current round, or None if game is over
        """
        current_index = ROUND_NAMES.index(self.current_round_name)
        if current_index < len(ROUND_NAMES) - 1:
            self.current_round_name = ROUND_NAMES[current_index + 1]
            return self.current_round_name
        else:
            self.game_over = True
            return None
    
    def get_winners(self):
        """Get the team(s) with the highest score.
        
        Returns:
            list: A list of winning team dictionaries
        """
        if not self.teams:
            return []
        
        max_score = max(team["score"] for team in self.teams)
        return [team for team in self.teams if team["score"] == max_score]
    
    def reset_game(self):
        """Reset the game to its initial state."""
        for team in self.teams:
            team["score"] = 0
        
        self.current_team_index = 0
        self.current_round_name = ROUND_NAMES[0]
        self.daily_doubles = []
        self.game_over = False
        
        for round_name in self.rounds:
            if round_name == ROUND_NAMES[2]:
                self.rounds[round_name] = FinalJeopardyRound()
            else:
                self.rounds[round_name] = JeopardyRound(round_name)
    
    def set_daily_doubles(self, round_name, num_daily_doubles=1):
        """Randomly assign Daily Doubles to questions in a round.
        
        Args:
            round_name (str): The name of the round to set Daily Doubles for
            num_daily_doubles (int, optional): Number of Daily Doubles to set. Defaults to 1.
        """
        if round_name not in self.rounds:
            return
        
        round_obj = self.rounds[round_name]
        available_questions = []
        
        for category in round_obj.categories:
            for value in round_obj.questions.get(category, {}):
                question = round_obj.questions[category][value]
                if not question.is_daily_double:
                    available_questions.append((category, value, question))
        
        # Make sure we don't try to set more Daily Doubles than there are questions
        num_daily_doubles = min(num_daily_doubles, len(available_questions))
        
        # Remove any existing Daily Doubles for this round
        self.daily_doubles = [dd for dd in self.daily_doubles if dd[0] != round_name]
        
        # Randomly select questions to be Daily Doubles
        for _ in range(num_daily_doubles):
            if not available_questions:
                break
                
            idx = random.randrange(len(available_questions))
            category, value, question = available_questions.pop(idx)
            
            question.is_daily_double = True
            self.daily_doubles.append((round_name, category, value))