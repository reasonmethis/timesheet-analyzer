# Timesheet Analyzer
This program is a simple time tracking tool that allows the user to categorize time entries in a timesheet. The timesheet is in a CSV file with columns that include 'Duration (decimal)', 'Start Date', and 'Description'. The program reads the CSV file and first extracts the above-mentioned columns and renames them to 'Hours', 'Date', and 'Description'. It then categorizes the time entries by prompting the user for a category for each unique time entry description. The user can either choose a category from a list of previously used categories, or create a new category. The categorized timesheet is then saved as a new CSV file. The program also has functionality to review and edit the categories, and to calculate the total hours for each category.## Usage

## Installation 
1. Clone the repo
2. Initialize and activate a virtual environment 
3. Install dependencies:
    pip install -r requirements.txt
