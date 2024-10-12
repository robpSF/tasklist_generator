import openai
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO

# Function to call OpenAI API and generate tasks from input text using ChatCompletion
def generate_tasklist(api_key, input_text):
    openai_api_key = st.secrets["api_key"]

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
    generated_tasks = response['choices'][0]['message']['function_call']['arguments']
    
    return generated_tasks

# Assuming input text and API key are already provided for demonstration purposes
api_key = "YOUR_OPENAI_API_KEY"
input_text = "James wishes to create pre-scenario materials, including usernames, passwords, and a video..."

# Generate the task list
tasks = generate_tasklist(api_key, input_text)
print(tasks)
