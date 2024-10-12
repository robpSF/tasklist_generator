import openai
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO

# Set up OpenAI API key
openai.api_key = st.secrets["openai"]["api_key"]

# Function to call OpenAI API and generate tasks from input text using ChatCompletion
def generate_tasklist(input_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Turn this text into a task list: {input_text}"}
        ],
        max_tokens=200,
        temperature=0.7
    )
    task_list = response.choices[0].message['content'].strip().split("\n")
    return task_list

# Function to create an Excel file with the task list
def create_excel(task_list, uploaded_file):
    # Load the uploaded file to get the headers
    df = pd.read_excel(uploaded_file)

    # Add today's date and time as the Tasklist name
    tasklist_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a DataFrame for the task list
    task_data = {
        'Tasklist Name': [tasklist_name] * len(task_list),
        'Task Name': task_list,
        # Add other necessary columns from your Excel template here, for example:
        # 'Task Description': [''] * len(task_list),
        # 'Task Due Date': [''] * len(task_list),
        # More columns can be added as per the structure of the uploaded file
    }
    task_df = pd.DataFrame(task_data)

    # Concatenate the new task list with the sample data from the uploaded file
    new_df = pd.concat([df, task_df], ignore_index=True)

    # Save the dataframe to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        new_df.to_excel(writer, index=False)
    return output.getvalue()

# Streamlit UI
st.title("Task List Generator")

# File uploader to upload the Excel template
uploaded_file = st.file_uploader("Upload the Excel file template", type=["xlsx"])

# Input text for generating tasks
input_text = st.text_area("Enter text to generate task list")

if st.button("Generate Task List"):
    if uploaded_file and input_text:
        tasks = generate_tasklist(input_text)
        st.write("Generated Task List:")
        st.write(tasks)

        # Create Excel file
        excel_data = create_excel(tasks, uploaded_file)

        # Download button for the Excel file
        st.download_button(
            label="Download Task List as Excel",
            data=excel_data,
            file_name=f"tasklist_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    elif not uploaded_file:
        st.warning("Please upload an Excel file template.")
    elif not input_text:
        st.warning("Please enter text to generate a task list.")
