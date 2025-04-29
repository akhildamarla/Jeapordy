"""
Jeopardy Game - File Handler
---------------------------
This module handles loading and parsing Excel files for the Jeopardy game.
"""

import os
import pandas as pd
import random
from tkinter import filedialog, messagebox
from config import EXCEL_SHEET_NAMES, ROUND_NAMES, JEOPARDY_VALUES, DOUBLE_JEOPARDY_VALUES, DEFAULT_TEMPLATE_PATH


class ExcelHandler:
    """Handles loading and parsing Excel files for the Jeopardy game."""
    
    def __init__(self):
        """Initialize an ExcelHandler object."""
        self.file_path = None
    
    def create_template(self, save_path=None):
        """Create a template Excel file for Jeopardy game.
        
        Args:
            save_path (str, optional): Path to save the template file. Defaults to None.
            
        Returns:
            str: Path to the created template file, or None if creation failed
        """
        if not save_path:
            save_path = filedialog.asksaveasfilename(
                title="Save Jeopardy Template",
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")]
            )
            
            if not save_path:
                return None
        
        try:
            # Create DataFrames for each sheet
            jeopardy_df = pd.DataFrame(columns=['Category'] + [f'Question {i+1}' for i in range(5)])
            double_jeopardy_df = pd.DataFrame(columns=['Category'] + [f'Question {i+1}' for i in range(5)])
            final_jeopardy_df = pd.DataFrame({
                'Item': ['Category', 'Question', 'Answer'],
                'Value': ['', '', '']
            })
            daily_doubles_df = pd.DataFrame({
                'Round': ['Jeopardy', 'Double Jeopardy', 'Double Jeopardy'],
                'Category': ['', '', ''],
                'Value': ['', '', '']
            })
            
            # Create a sample row with instructions
            jeopardy_sample = ['Category Name']
            for i, value in enumerate(JEOPARDY_VALUES):
                jeopardy_sample.append(f'Question: Sample question for ${value} | Answer: Sample answer')
            jeopardy_df.loc[0] = jeopardy_sample
            
            double_sample = ['Category Name']
            for i, value in enumerate(DOUBLE_JEOPARDY_VALUES):
                double_sample.append(f'Question: Sample question for ${value} | Answer: Sample answer')
            double_jeopardy_df.loc[0] = double_sample
            
            # Create the Excel writer and write each sheet
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                jeopardy_df.to_excel(writer, sheet_name=EXCEL_SHEET_NAMES[0], index=False)
                double_jeopardy_df.to_excel(writer, sheet_name=EXCEL_SHEET_NAMES[1], index=False)
                final_jeopardy_df.to_excel(writer, sheet_name=EXCEL_SHEET_NAMES[2], index=False)
                daily_doubles_df.to_excel(writer, sheet_name='Daily Doubles', index=False)
                
                # Add a help sheet
                help_df = pd.DataFrame({
                    'Instructions': [
                        'How to use this template:',
                        '1. For Jeopardy and Double Jeopardy rounds, add categories in the Category column.',
                        '2. Add questions and answers in the format "Question: [text] | Answer: [text]"',
                        '3. For Final Jeopardy, fill in the Category, Question, and Answer in the Value column.',
                        '4. For Daily Doubles, specify the Round, Category, and Value of each Daily Double.',
                        '5. You can add as many categories as needed by adding more rows.',
                        '6. Save the file and load it in the Jeopardy Game application.'
                    ]
                })
                help_df.to_excel(writer, sheet_name='Help', index=False)
            
            return save_path
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating template: {str(e)}")
            return None
    
    def load_file(self):
        """Show a file dialog to select an Excel file.
        
        Returns:
            str: Path to the selected file, or None if no file was selected
        """
        file_path = filedialog.askopenfilename(
            title="Select Jeopardy Questions File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            return file_path
        
        return None
    
    def parse_file(self, file_path=None):
        """Parse the Excel file and extract game data.
        
        Args:
            file_path (str, optional): Path to the Excel file. Defaults to None.
            
        Returns:
            dict: Dictionary containing game data, or None if parsing failed
        """
        if not file_path and not self.file_path:
            return None
            
        file_path = file_path or self.file_path
        
        try:
            # Initialize game data structure
            game_data = {
                "rounds": {
                    ROUND_NAMES[0]: {"categories": [], "questions": {}},
                    ROUND_NAMES[1]: {"categories": [], "questions": {}},
                    ROUND_NAMES[2]: {"category": "", "question": "", "answer": ""}
                },
                "daily_doubles": []
            }
            
            # Read Excel file
            xl = pd.ExcelFile(file_path)
            
            # Check if the required sheets are present
            for sheet_name in EXCEL_SHEET_NAMES:
                if sheet_name not in xl.sheet_names:
                    messagebox.showerror("Error", f"Sheet '{sheet_name}' not found in the Excel file.")
                    return None
            
            # Parse Jeopardy round
            jeopardy_df = pd.read_excel(file_path, sheet_name=EXCEL_SHEET_NAMES[0])
            self._parse_jeopardy_round(jeopardy_df, game_data, ROUND_NAMES[0], JEOPARDY_VALUES)
            
            # Parse Double Jeopardy round
            double_df = pd.read_excel(file_path, sheet_name=EXCEL_SHEET_NAMES[1])
            self._parse_jeopardy_round(double_df, game_data, ROUND_NAMES[1], DOUBLE_JEOPARDY_VALUES)
            
            # Parse Final Jeopardy
            final_df = pd.read_excel(file_path, sheet_name=EXCEL_SHEET_NAMES[2])
            self._parse_final_jeopardy(final_df, game_data)
            
            # Parse Daily Doubles if the sheet exists
            if 'Daily Doubles' in xl.sheet_names:
                dd_df = pd.read_excel(file_path, sheet_name='Daily Doubles')
                self._parse_daily_doubles(dd_df, game_data)
            else:
                # Automatically assign Daily Doubles if not specified
                self._assign_random_daily_doubles(game_data)
            
            return game_data
            
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing Excel file: {str(e)}")
            return None
    
    def _parse_jeopardy_round(self, df, game_data, round_name, values):
        """Parse a regular Jeopardy round from a DataFrame.
        
        Args:
            df (DataFrame): The DataFrame containing round data
            game_data (dict): The game data dictionary to update
            round_name (str): The name of the round
            values (list): The point values for the round
        """
        # Get categories (first column)
        categories = df['Category'].dropna().tolist()
        game_data["rounds"][round_name]["categories"] = categories
        
        # Initialize questions dictionary
        questions = {}
        for category in categories:
            questions[category] = {}
        
        # Process each row (category)
        for _, row in df.iterrows():
            category = row['Category']
            if pd.isna(category) or category == '':
                continue
                
            # Process each question column
            for i, value in enumerate(values):
                col_name = f'Question {i+1}'
                if col_name not in row or pd.isna(row[col_name]) or row[col_name] == '':
                    continue
                    
                # Parse question and answer
                qa_text = row[col_name]
                question, answer = self._parse_qa_text(qa_text)
                
                if question and answer:
                    if category not in questions:
                        questions[category] = {}
                        
                    questions[category][value] = {
                        "question": question,
                        "answer": answer,
                        "is_daily_double": False
                    }
        
        game_data["rounds"][round_name]["questions"] = questions
    
    def _parse_final_jeopardy(self, df, game_data):
        """Parse the Final Jeopardy round from a DataFrame.
        
        Args:
            df (DataFrame): The DataFrame containing Final Jeopardy data
            game_data (dict): The game data dictionary to update
        """
        # Find the rows for category, question, and answer
        category_row = df[df['Item'] == 'Category']
        question_row = df[df['Item'] == 'Question']
        answer_row = df[df['Item'] == 'Answer']
        
        if not category_row.empty and 'Value' in category_row.columns:
            game_data["rounds"][ROUND_NAMES[2]]["category"] = str(category_row['Value'].iloc[0])
            
        if not question_row.empty and 'Value' in question_row.columns:
            game_data["rounds"][ROUND_NAMES[2]]["question"] = str(question_row['Value'].iloc[0])
            
        if not answer_row.empty and 'Value' in answer_row.columns:
            game_data["rounds"][ROUND_NAMES[2]]["answer"] = str(answer_row['Value'].iloc[0])
    
    def _parse_daily_doubles(self, df, game_data):
        """Parse the Daily Doubles from a DataFrame.
        
        Args:
            df (DataFrame): The DataFrame containing Daily Doubles data
            game_data (dict): The game data dictionary to update
        """
        daily_doubles = []
        
        for _, row in df.iterrows():
            round_name = row.get('Round')
            category = row.get('Category')
            value = row.get('Value')
            
            if pd.isna(round_name) or pd.isna(category) or pd.isna(value):
                continue
                
            round_name = str(round_name).strip()
            category = str(category).strip()
            
            try:
                value = int(value)
            except (ValueError, TypeError):
                continue
                
            if round_name in ROUND_NAMES and round_name != ROUND_NAMES[2]:  # No Daily Doubles in Final Jeopardy
                # Verify the category and value exist
                if category in game_data["rounds"][round_name]["categories"]:
                    if category in game_data["rounds"][round_name]["questions"]:
                        if value in game_data["rounds"][round_name]["questions"][category]:
                            # Mark this question as a Daily Double
                            game_data["rounds"][round_name]["questions"][category][value]["is_daily_double"] = True
                            daily_doubles.append((round_name, category, value))
        
        game_data["daily_doubles"] = daily_doubles
        
        # If no valid Daily Doubles were found, assign them randomly
        if not daily_doubles:
            self._assign_random_daily_doubles(game_data)
    
    def _assign_random_daily_doubles(self, game_data):
        """Assign Daily Doubles randomly if none were specified.
        
        Args:
            game_data (dict): The game data dictionary to update
        """
        daily_doubles = []
        
        # One Daily Double in Jeopardy round
        self._add_random_daily_double(game_data, ROUND_NAMES[0], daily_doubles)
        
        # Two Daily Doubles in Double Jeopardy round
        self._add_random_daily_double(game_data, ROUND_NAMES[1], daily_doubles)
        self._add_random_daily_double(game_data, ROUND_NAMES[1], daily_doubles)
        
        game_data["daily_doubles"] = daily_doubles
    
    def _add_random_daily_double(self, game_data, round_name, daily_doubles):
        """Add a random Daily Double to a round.
        
        Args:
            game_data (dict): The game data dictionary to update
            round_name (str): The name of the round to add the Daily Double to
            daily_doubles (list): The list of current Daily Doubles to update
        """
        round_data = game_data["rounds"][round_name]
        categories = round_data["categories"]
        if not categories:
            return
            
        # Get all available questions
        available_questions = []
        for category in categories:
            if category in round_data["questions"]:
                for value, question_data in round_data["questions"][category].items():
                    if not question_data.get("is_daily_double", False):
                        available_questions.append((category, value))
        
        if not available_questions:
            return
            
        # Randomly select a question
        category, value = random.choice(available_questions)
        
        # Mark it as a Daily Double
        round_data["questions"][category][value]["is_daily_double"] = True
        daily_doubles.append((round_name, category, value))
    
    def _parse_qa_text(self, text):
        """Parse question and answer from text in the format "Question: X | Answer: Y".
        
        Args:
            text (str): The text to parse
            
        Returns:
            tuple: A tuple containing (question, answer), or (None, None) if parsing failed
        """
        if pd.isna(text) or not isinstance(text, str):
            return None, None
            
        try:
            # Split by the '|' character
            parts = text.split('|')
            
            if len(parts) < 2:
                # Try to split by newline as an alternative
                parts = text.split('\n')
                
            if len(parts) < 2:
                # Simple fallback: assume the text is the question and there is no answer
                return text.strip(), "No answer provided"
            
            # Extract question and answer
            question_part = parts[0].strip()
            answer_part = parts[1].strip()
            
            # Remove "Question:" and "Answer:" prefixes if present
            if question_part.lower().startswith("question:"):
                question_part = question_part[9:].strip()
                
            if answer_part.lower().startswith("answer:"):
                answer_part = answer_part[7:].strip()
            
            return question_part, answer_part
            
        except Exception:
            return text.strip(), "No answer provided"
    
    def ensure_template_exists(self):
        """Ensure that the template Excel file exists.
        
        Returns:
            str: Path to the template file
        """
        if not os.path.exists(DEFAULT_TEMPLATE_PATH):
            # Create the templates directory if it doesn't exist
            os.makedirs(os.path.dirname(DEFAULT_TEMPLATE_PATH), exist_ok=True)
            
            # Create the template file
            return self.create_template(DEFAULT_TEMPLATE_PATH)
        
        return DEFAULT_TEMPLATE_PATH