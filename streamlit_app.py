import openai
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO

# Function to call OpenAI API and generate tasks from input text using ChatCompletion
def generate_tasklist(api_key, input_text):
    openai.api_key = api_key
    prompt = f"""Extract a meaningful task list from the following text and format it as a structured tabular output with the following columns:

TASKLIST, TASK, DESCRIPTION, ASSIGN TO, START DATE, DUE DATE, PRIORITY, ESTIMATED TIME, TAGS, STATUS.

For each task or subtask, include details under each column. Leave "ASSIGN TO", "START DATE", "DUE DATE", "PRIORITY", "ESTIMATED TIME", "TAGS", and "STATUS" empty.

Text to extract tasks from:

{input_text}

Provide the output in the exact tabular structure, with clear headings matching the specified columns."""


    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip().split("\n")

# Function to create an Excel file with the task list using predefined headers
def create_excel(task_list):
    # Define the headers from the provided Excel template
    headers = ['Tasklist Name', 'Task Name', 'Description', 'Start Date', 'Due Date', 'Assigned To', 'Priority']

    # Add today's date and time as the Tasklist name
    tasklist_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a DataFrame for the task list
    task_data = {
        'Tasklist Name': [tasklist_name] * len(task_list),
        'Task Name': task_list,
        'Description': [''] * len(task_list),  # Empty description for now
        'Start Date': [''] * len(task_list),  # Empty start date for now
        'Due Date': [''] * len(task_list),  # Empty due date for now
        'Assigned To': [''] * len(task_list),  # Empty assigned to for now
        'Priority': [''] * len(task_list)  # Empty priority for now
    }

    task_df = pd.DataFrame(task_data, columns=headers)

    # Save the dataframe to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        task_df.to_excel(writer, index=False)
    return output.getvalue()

# Streamlit UI
st.title("Task List Generator")

# Input text for generating tasks
input_text = st.text_area("Enter text to generate task list")

if st.button("Generate Task List"):
    if input_text:
        # Use Streamlit Secrets to get the OpenAI API key
        api_key = st.secrets["api_key"]

        # Generate task list using the updated function
        tasks = generate_tasklist(api_key, input_text)
        st.write("Generated Task List:")
        st.write(tasks)

        # Create Excel file
        excel_data = create_excel(tasks)

        # Download button for the Excel file
        st.download_button(
            label="Download Task List as Excel",
            data=excel_data,
            file_name=f"tasklist_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Please enter text to generate a task list.")

