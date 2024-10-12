import openai
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import json

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
            {"role": "user", "content": "Extract a meaningful task list, with subtasks, from the following text (understand that the text is an email and the sender might be refering to themselves. I only want tasks and subtasks for me):\n\n" + input_text + "\n\nThe output should be in the following JSON format:\n{\n  \"TASKLIST\": [\"Heading 1\", \"Subtask 1\", \"Subtask 2\", \"Heading 2\", ...],\n  \"TASK\": [\"Main Task 1\", \"- Subtask of Task 1\", \"Main Task 2\", ...],\n  \"DESCRIPTION\": [\"Description for Task 1\", \"\", \"Description for Task 2\", ...],\n  \"ASSIGN TO\": [null, null, null, ...],\n  \"START DATE\": [null, null, null, ...],\n  \"DUE DATE\": [null, null, null, ...],\n  \"PRIORITY\": [null, null, null, ...],\n  \"ESTIMATED TIME\": [null, null, null, ...],\n  \"TAGS\": [null, null, null, ...],\n  \"STATUS\": [null, null, null, ...]\n}\n"
            }
        ],
        functions=functions,
        function_call={"name": "generate_task_list"}
    )

    # Extract and parse the JSON response
    arguments_json = response['choices'][0]['message']['function_call']['arguments']
    generated_tasks = json.loads(arguments_json)
    
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

            # Find the maximum length of any of the lists
            max_length = max(len(tasks[key]) for key in tasks)

            # Ensure all lists are of the same length by padding with None
            for key in tasks:
                tasks[key].extend([None] * (max_length - len(tasks[key])))

            # Create DataFrame
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
