# Jeopardy Excel Template Guide

## Overview
The Python Jeopardy game loads questions and categories from an Excel file. Here's how to structure your Excel file for a complete game.

## Sheet Structure
Your Excel file should contain the following sheets:

1. **Jeopardy Round** - First round questions ($200-$1000)
2. **Double Jeopardy Round** - Second round questions ($400-$2000)
3. **Final Jeopardy** - The final question
4. **Daily Doubles** (Optional) - Specify which questions are Daily Doubles

## Jeopardy & Double Jeopardy Sheets Format

Each regular round sheet should be structured like this:

| Category      | Question 1                               | Question 2                               | Question 3                               | Question 4                               | Question 5                               |
|---------------|------------------------------------------|------------------------------------------|------------------------------------------|------------------------------------------|------------------------------------------|
| Science       | Question: What is H2O? \| Answer: Water  | Question: What is the largest planet? \| Answer: Jupiter | Question: Who developed the theory of relativity? \| Answer: Einstein | Question: What is the nearest star to Earth? \| Answer: The Sun | Question: What gas do plants absorb? \| Answer: Carbon Dioxide |
| History       | Question: Who was the first U.S. president? \| Answer: George Washington | Question: Which empire built the pyramids? \| Answer: Egyptian | ... | ... | ... |
| Geography     | ... | ... | ... | ... | ... |
| Literature    | ... | ... | ... | ... | ... |
| Pop Culture   | ... | ... | ... | ... | ... |

- Each row represents a category
- Column A contains the category names
- Columns B-F contain the questions and answers
- For the Jeopardy Round, questions are worth $200, $400, $600, $800, and $1000 respectively
- For the Double Jeopardy Round, questions are worth $400, $800, $1200, $1600, and $2000 respectively

## Final Jeopardy Sheet Format

| Item     | Value                                               |
|----------|-----------------------------------------------------|
| Category | Famous Inventions                                   |
| Question | This device, patented in 1876, revolutionized communication |
| Answer   | What is the telephone?                              |

## Daily Doubles Sheet Format (Optional)

| Round           | Category      | Value |
|-----------------|---------------|-------|
| Jeopardy        | Science       | 600   |
| Double Jeopardy | History       | 1200  |
| Double Jeopardy | Pop Culture   | 2000  |

- The Round column should contain either "Jeopardy" or "Double Jeopardy"
- The Category column should match a category name exactly
- The Value column should contain the dollar value of the question

## Tips for Creating Questions

1. **Format** - Always use the format "Question: [text] | Answer: [text]"
2. **Categories** - You can add as many categories as you want by adding more rows
3. **Daily Doubles** - If you don't specify Daily Doubles, they will be assigned randomly
4. **Final Jeopardy** - The answer in Final Jeopardy should ideally be in the form of a question

## Example
You can generate a template file from the application by selecting "File > Create Template" which will provide you with a pre-formatted Excel file to fill in.