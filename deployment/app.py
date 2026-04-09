from urllib import response

import gradio as gr
import requests
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CHECK_CODEBASE_URL = os.getenv("CHECK_CODEBASE_URL")
INSERT_CODEBASE_URL = os.getenv("INSERT_CODEBASE_URL")

# Function to query the codebase API
def process_query(query, session_id, collection_name):
    try:
        payload = {"session_id": session_id, "query": query, "collection_name": collection_name}
        response = requests.post(CHECK_CODEBASE_URL, json=payload)

        if response.status_code != 200:
            return f"⚠️ API Error [{response.status_code}]: {response.text}"

        response = response.json()
        print("response: ", response["response"])
        return response["response"]

    except Exception as e:
        return f"⚠️ Error contacting API: {e}"
    
def insert_codebase(repo_path, session_id):
    try:
        payload = {"session_id": session_id, "repo_path": repo_path}
        response = requests.post(INSERT_CODEBASE_URL, json=payload)

        if response.status_code != 200:
            return f"⚠️ API Error [{response.status_code}]: {response.text}"

        response = response.json()

        collection_name = response.get("message", "")

        return collection_name

    except Exception as e:
        return f"⚠️ Error contacting API: {e}"

# Gradio chat interface
with gr.Blocks() as chat_app:
    gr.Markdown("## 💬 Codebase RAG Chatbot")

    repo_path = gr.Textbox(
        label="Codebase Repository Path",
        placeholder="Enter the path to your codebase repository",
        lines=1
    )

    query_input = gr.Textbox(
        label="Ask your question",
        placeholder="Type your question here...",
        lines=2
    )
    session_id_state = gr.State(value=str(uuid.uuid4()))
    collection_name_state = gr.State(value="")  # To store the collection name after insertion
    chat_output = gr.Chatbot()
    submit_btn = gr.Button("Submit")  # Add a submit button
    # Add a button to insert the codebase
    insert_btn = gr.Button("Insert Codebase")

    # When clicked, insert the repo and store the collection name
    insert_btn.click(insert_codebase, inputs=[repo_path, session_id_state], outputs=[collection_name_state])

    def chat_step(query, session_id, chat_history, collection_name):
        if not collection_name:
            return chat_history, "⚠️ Please insert the codebase first."
        
        chat_history = chat_history or []
        response_text = process_query(query, session_id, collection_name)

        # Append messages in Gradio Chatbot format
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": response_text})

        return chat_history, ""  # updated history + clear input
    
    # Connect Enter key and submit button
    query_input.submit(chat_step, inputs=[query_input, session_id_state, chat_output, collection_name_state], outputs=[chat_output, query_input])
    submit_btn.click(chat_step, inputs=[query_input, session_id_state, chat_output, collection_name_state], outputs=[chat_output, query_input])

chat_app.launch(pwa=True, server_name="0.0.0.0", server_port=8501, inbrowser=True)