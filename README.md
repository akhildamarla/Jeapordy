# Python Jeopardy Game

A full-featured Jeopardy game implementation with a graphical user interface, built with Python and Tkinter.

## Features

- **Complete Jeopardy gameplay** including Jeopardy Round, Double Jeopardy Round, and Final Jeopardy
- **Multiple categories** - add as many topic columns as you want
- **Team management** with score tracking and turn alternation
- **Daily Doubles** with wager functionality
- **Excel integration** for loading custom questions and categories
- **Template creation** to help you format your question files
- **Full game flow** from start to finish

## Installation

### Requirements

- Python 3.6 or higher
- Required packages: pandas, openpyxl, pygame, Pillow

### Setup

1. Clone or download this repository
2. Install the required packages:

```bash
pip install pandas openpyxl pygame Pillow
```

3. Create the directory structure:

```
jeopardy_game/
│
├── main.py
├── game_logic.py
├── ui.py
├── file_handler.py
├── config.py
├── resources/
│   ├── sounds/
│   │   ├── timer.wav
│   │   ├── daily_double.wav
│   │   └── final_jeopardy.wav
│   └── images/
│       ├── logo.png
│       └── background.png
└── templates/
```

4. Copy all the Python files from this project into their respective files
5. Create the resource directories for sounds and images (optional)

## Usage

1. Run the game by executing the main.py file:

```bash
python main.py
```

2. From the application:
   - Create a template Excel file by selecting **File > Create Template**
   - Fill in your questions in the Excel template
   - Load your questions by selecting **File > Load Questions**
   - Manage teams by selecting **Game > Manage Teams**
   - Start playing!

## Creating Question Files

The game loads questions from an Excel file with a specific format:

- Sheet 1: "Jeopardy Round" - First round questions ($200-$1000)
- Sheet 2: "Double Jeopardy Round" - Second round questions ($400-$2000)
- Sheet 3: "Final Jeopardy" - The final question
- Sheet 4 (optional): "Daily Doubles" - Specify which questions are Daily Doubles

See the Excel Template Guide for more detailed information on how to format your question files.

## Gameplay Instructions

1. **Starting a Game**:
   - Load questions from an Excel file
   - Set up your teams

2. **Regular Gameplay**:
   - Teams take turns selecting questions
   - The current team is highlighted in the scoreboard
   - After selecting a question, answer it verbally
   - Mark it correct or incorrect using the buttons
   - Correct answers earn points and the team keeps control
   - Incorrect answers lose points and control passes to the next team

3. **Daily Doubles**:
   - Only the selecting team can answer
   - They must wager before seeing the question
   - Correct answers add the wagered points, incorrect answers subtract them

4. **Final Jeopardy**:
   - All teams make wagers based on their current scores
   - Each team answers the same final question
   - Correct answers add the wagered points, incorrect answers subtract them

5. **Winning**:
   - The team with the highest score at the end wins!

## Customization

You can customize the game by modifying the `config.py` file:
- Change the default teams
- Adjust point values
- Modify timer durations
- Change colors and fonts
- Add or remove sounds

## License

This project is available for personal and educational use.

## Acknowledgments

- Inspired by the classic Jeopardy game show created by Merv Griffin