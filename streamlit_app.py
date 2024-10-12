import openai
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO

# Function to call OpenAI API and generate tasks from input text using ChatCompletion
def generate_tasklist(api_key, input_text):
    openai.api_key = api_key

    # Define the expected JSON schema for output
    functions = [
        {
            "name": "generate_task_list",
            "description": "Generate a structured task list from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "TASKLIST": {
                        "type": "array",
                        "description": "List of task list categories.",
                        "items": {"type": "string"}
                    },
                    "TASK": {
                        "type": "array",
                        "description": "List of tasks and subtasks.",
                        "items": {"type": "string"}
                    },
                    "DESCRIPTION": {
                        "type": "array",
                        "description": "List of descriptions for each task or subtask.",
                        "items": {"type": "string"}
                    },
                    "ASSIGN TO": {
                        "type": "array",
                        "description": "List of assigned persons (leave null).",
                        "items": {"type": "null"}
                    },
                    "START DATE": {
                        "type": "array",
                        "description": "List of start dates (leave null).",
                        "items": {"type": "null"}
                    },
                    "DUE DATE": {
                        "type": "array",
                        "description": "List of due dates (leave null).",
                        "items": {"type": "null"}
                    },
                    "PRIORITY": {
                        "type": "array",
                        "description": "List of priorities (leave null).",
                        "items": {"type": "null"}
                    },
                    "ESTIMATED TIME": {
                        "type": "array",
                        "description": "List of estimated times (leave null).",
                        "items": {"type": "null"}
                    },
                    "TAGS": {
                        "type": "array",
                        "description": "List of tags (leave null).",
                        "items": {"type": "null"}
                    },
                    "STATUS": {
                        "type": "array",
                        "description": "List of statuses (leave null).",
                        "items": {"type": "null"}
                    }
                },
                "required": ["TASKLIST", "TASK", "DESCRIPTION"]
            }
        }
    ]

    # OpenAI API call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract a meaningful task list from the following text:\n\n{input_text}"}
        ],
        functions=functions,
        function_call={"name": "generate_task_list"}
    )

    # Extract the response from function_call
    generated_tasks = eval(response['choices'][0]['message']['function_call']['arguments'])
    
    return generated_tasks

# Streamlit UI
st.title("Task List Generator")

# Input for OpenAI API Key
api_key = st.secrets["api_key"]

# Text area for input text
input_text = st.text_area("Paste the text here to generate the task list:")

# Button to generate task list
if st.button("Generate Task List"):
    if api_key and input_text:
        try:
            tasks = generate_tasklist(api_key, input_text)
            task_list_df = pd.DataFrame(tasks)
            
            # Display the generated DataFrame
            st.write("Generated Task List:")
            st.dataframe(task_list_df)

            # Option to download the generated task list as an Excel file
            output = BytesIO()
            task_list_df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="Download Task List as Excel",
                data=output,
                file_name="Generated_Task_List.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please provide both an API key and input text.")
