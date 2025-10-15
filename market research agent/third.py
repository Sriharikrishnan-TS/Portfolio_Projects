# -*- coding: utf-8 -*-
"""
This is a SIMPLIFIED Flask endpoint for the LangGraph AI interviewer.

Workflow:
1. Frontend calls GET /interview to start and get the first question.
2. Frontend calls POST /interview/{thread_id} with the user's answer.
"""

import uuid
from flask import Flask, request,jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage
from agent import app

# --- 1. App Initialization ---
api = Flask(__name__)
# Enable CORS to allow your frontend to call this API
CORS(api)

# --- 2. Hardcoded Client Prompt ---
# The client prompt is constant and defined here.
CLIENT_PROMPT = "A sleek, affordable Fire-tablet built for reading, streaming and light productivity. Features a vibrant 10.1″ full-HD display, fast octa-core processor, 4 GB RAM, 64 GB internal storage (expandable via microSD), solid 12-hour battery life, and seamless deep integration with the Amazon ecosystem (Kindle, Prime Video, Alexa, etc.). I need a good marketing strategy and competitive market landscape analysis."

# --- 3. Flask API Endpoints ---

@api.route("/interview", methods=["GET","POST"])
def handle_interview():
    """
    Handles the entire interview flow using only GET requests.
    - If no 'thread_id' is in the query, starts a new interview.
    - If 'thread_id' is present, continues the interview with the 'message'.
    """
    thread_id = request.args.get('thread_id', default='')
    print("10")

    # CASE 1: Start a new interview if no thread_id is provided
    if not thread_id:
        print(thread_id)
        print("11")
        new_thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": new_thread_id}}
        
        initial_input = {
            "client_prompt": CLIENT_PROMPT,
            "messages": [],
            "transcript": "",
            "summary":''
        }
        response = app.invoke(initial_input, config)
        first_question = response['messages'][-1].content
        
        # Return the NEW thread_id so the frontend can use it
        return jsonify({
            "thread_id": new_thread_id, 
            "ai_message": first_question,
            "status": "in_progress"
        })

    # CASE 2: Continue an existing interview
    else:
        print(thread_id)
        print("12")
        # Keeping your original logic for parsing thread_id and message
        user_message_content = thread_id[36:]
        thread_id = thread_id[:36]
        
        if not user_message_content:
            return jsonify({"error": "A message is required to continue."}), 400

        config = {"configurable": {"thread_id": thread_id}}
        user_message = HumanMessage(content=user_message_content)
        
        response = app.invoke({"messages": [user_message]}, config)

        # --- MODIFIED LOGIC TO FIX THE "FINISH" BEHAVIOR ---
        # Instead of 'if response is None', we check if the 'summary' key
        # exists in the final state returned by app.invoke()
        if response["summary"]:
            print('summary')
            summary = response["summary"]
            final_message = f"Thank you for your time.\n\n**Interview Summary:**\n{summary}"
            
            # The interview is over, return the summary
            return jsonify({"ai_message": final_message, "status": "finished"})
        
        # If no summary, the interview is still in progress
        else:
            next_question = response['messages'][-1].content
            return jsonify({"ai_message": next_question, "status": "in_progress"})


# --- 4. Running the Flask Server ---
if __name__ == "__main__":
    # Use the built-in Flask development server
    # debug=True enables auto-reloading when you save the file
    api.run(host="0.0.0.0", port=8000, debug=True)