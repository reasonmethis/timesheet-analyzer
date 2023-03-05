import pandas as pd

TIMESHEET_FILE = 'WC_Clockify_Time_Report_Detailed_01_29_2023-02_04_2023.csv'
# TIMESHEET_FILE = 'test.csv'
N_LINES_FOR_TERMINAL_PROMPT = 37

def clean_and_categorize_raw_timesheet(save=True):
    """
    Reads the raw timesheet csv file, cleans it up and categorizes the items.
    :param save: Whether to save the cleaned and categorized timesheet as a new csv file.
    :return: Cleaned and categorized timesheet as a pandas dataframe.
    """
    df = pd.read_csv(TIMESHEET_FILE)
    df = clean_up(df)
    df, item_categories = categorize_items(df)
    if save:
        save_df(df, 'timesheet-with-categories.csv')
    return df

def save_hours_by_category(categorized_timesheet_df):
    """
    Saves the total hours worked by category as a new csv file.
    :param categorized_timesheet_df: Cleaned and categorized timesheet as a pandas dataframe.
    :return: None
    """
    total_hours_by_category = calculate_hours_by_category(categorized_timesheet_df)
    print(total_hours_by_category)
    print(f"Total hours: {total_hours_by_category['Hours'].sum()}")
    save_df(total_hours_by_category, 'hours-by-category.csv')

def fix():
    """
    Reads the cleaned and categorized timesheet, filters it to only include items with an empty category, and prints them.
    :return: None
    """
    # df = pd.read_csv("timesheet-with-categories.csv", dtype={'Category': str})#still parses '' as NaN
    df = pd.read_csv("timesheet-with-categories.csv", keep_default_na=False)
    filtered_df = df[df.Category == '']
    print(filtered_df)
    print(f'"{filtered_df.Category}"')

def clean_up(df):
    """
    Cleans up the raw timesheet dataframe by renaming columns and only keeping relevant columns.
    :param df: Raw timesheet dataframe.
    :return: Cleaned up timesheet dataframe.
    """
    df = df.rename(columns={'Duration (decimal)': 'Hours', 'Start Date': 'Date'})
    return df[['Description', 'Date', 'Hours']]

def categorize_items(df):
    """
    Categorize the items in the timesheet dataframe based on user input.
    Saves the mapping from task description to category in a dictionary.
    Returns the categorized dataframe and the dictionary.

    :param df: pandas DataFrame, the raw timesheet data
    :return: tuple, categorized dataframe and task to category dictionary
    """
    task_to_cat_d = {}  # Dictionary to store mapping from task to category
    df['Category'] = ''  # Initialize the category column

    # Iterate through the items in the dataframe
    for index, row in df.iterrows():
        item = row['Description']  # Get the task description

        # Check if the task description is already in the task to category dictionary
        if item in task_to_cat_d:
            category = task_to_cat_d[item]
        else:
            # If the task description is not in the dictionary, prompt the user for a category
            print(f"Provide the category for item:\n{item}")
            category_list = get_category_list(task_to_cat_d)  # Get the list of existing categories

            # Print the existing categories
            for i, category in enumerate(category_list):
                print(f'{i + 1}. {category}')

            # Prompt the user to select an existing category or enter a new one
            print(
                '\nEnter a number for one of the above categories or enter a new category: ', end=''
            )
            n_empty_lines = N_LINES_FOR_TERMINAL_PROMPT - (len(category_list) + 3)
            if n_empty_lines > 0:
                print('\n' * n_empty_lines)

            # Keep prompting the user until they enter a non-empty string
            while True:
                category = input()
                if category.strip():
                    break
            print()

            # If the user entered a number, convert it to the corresponding category
            try:
                num = int(category)
                if num > 0 and num <= len(category_list):
                    category = category_list[num - 1]
            except ValueError:
                pass

            # Assign the category to the current item in the task to category dictionary 
            task_to_cat_d[item] = category

        # Assign the category to the current item in the dataframe
        df.at[index, 'Category'] = category

    return df, task_to_cat_d


def review_and_edit_categories(categorized_timesheet_df):
    task_to_cat_d = extract_task_to_category_dict(categorized_timesheet_df)
    ind_to_task_d = {}
    while True:
        ind = 0
        for task, category in task_to_cat_d.items():
            ind += 1
            print(f'{ind}. {category} - {task}')
            ind_to_task_d[ind] = task

        while True:
            ans = input(
                '\nEnter a comma-separated list of numbers indicating entries you want to change (or "done"):'
            )
            if ans == 'done':
                return assign_categories(categorized_timesheet_df, task_to_cat_d)

            if not ans:
                continue
            try:
                inds = [int(x.strip()) for x in ans.split(',')]
            except ValueError:
                continue
            break

        # Now we have a list of entries to re-categorize
        for ind in inds:
            category_list = get_category_list(task_to_cat_d)
            task = ind_to_task_d[ind]
            print(f"\nProvide the category for item:\n{task}")
            print(f"(Currently it's assigned {task_to_cat_d[task]})")
            for i, category in enumerate(category_list):
                print(f'{i + 1}. {category}')

            print(
                '\nEnter a number for one of the above categories or enter a new category: ', end=''
            )
            n_empty_lines = N_LINES_FOR_TERMINAL_PROMPT - (len(category_list) + 3)
            if n_empty_lines > 0:
                print('\n' * n_empty_lines)

            while True:
                category = input()
                if category.strip():
                    break
            print()

            try:
                num = int(category)
                if num > 0 and num <= len(category_list):
                    category = category_list[num - 1]
            except ValueError:
                pass
            task_to_cat_d[task] = category


def get_category_list(task_to_cat_d):
    return sorted(list(set(task_to_cat_d.values())))


def assign_categories(timesheet_df, task_to_cat_d):
    categorized_timesheet_df = timesheet_df.copy()
    categorized_timesheet_df['Category'] = ''
    for ind, row in categorized_timesheet_df.iterrows():
        categorized_timesheet_df.at[ind, 'Category'] = task_to_cat_d[
            row.Description
        ]  # will throw if unassigned task
    return categorized_timesheet_df


def calculate_hours_by_category(df):
    total_hours_by_category = df.groupby('Category')['Hours'].sum().round(4)
    # create an index with 0, 1, 2 - since we drop index when saving
    return total_hours_by_category.reset_index(drop=False)


def filter_by_category(df, category):
    filtered_df = df[df['Category'] == category]
    return filtered_df


def save_df(df, fname):
    df.to_csv(fname, index=False)


def aggregate_by_task_and_date(df):
    grouped_df = df.groupby(by=['Description', 'Category', 'Date'])['Hours'].sum().reset_index()
    return grouped_df


def extract_categories(categorized_timesheet_df):
    distinct_categories = categorized_timesheet_df['Category'].unique().tolist()
    return sorted(distinct_categories)


def extract_task_to_category_dict(categorized_timesheet_df):
    task_to_cat_d = {}
    for index, row in categorized_timesheet_df.iterrows():
        item = row['Description']
        category = row['Category']
        task_to_cat_d[item] = category
    return task_to_cat_d


if __name__ == '__main__':
    categorized_timesheet_df = pd.read_csv('timesheet-with-categories.csv')
    # print(df := filter_by_category(categorized_timesheet_df, 'Communication and planning'))
    # print(aggregate_by_task_and_date(categorized_timesheet_df))
    # new_df = review_and_edit_categories(categorized_timesheet_df)
    # save_df(new_df, "new.csv")
    save_hours_by_category(categorized_timesheet_df)
