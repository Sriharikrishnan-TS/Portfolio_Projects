# -*- coding: utf-8 -*-
"""
This file defines the LangGraph structure for the conversational AI interviewer.
It includes the state, nodes, and edges that manage the interview flow.
"""

import os
import requests
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

# Set up the environment variable for the Google API key for Gemini
# Replace 'YOUR_GOOGLE_API_KEY' with your actual key

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
base_url = os.getenv('BASE_URL')

# --- 1. Define the State ---
class InterviewerState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: The list of messages that have been exchanged in the conversation.
        transcript: The full transcript of the conversation.
        emotional_status: The perceived emotional state of the SME.
        client_prompt: The initial prompt from the client.
        selected_framework: The framework chosen based on the client's prompt.
    """
    messages: Annotated[List[AnyMessage], lambda x, y: x + y]
    transcript: str
    emotional_status: str
    client_prompt: str
    selected_framework: dict
    summary: str

# --- 2. Define The Graph Nodes ---

# Initialize the models
# Using a smaller, local model for classification and a more powerful one for generation
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
generative_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.75)
# For the classifier, a smaller model would be used in a real scenario.
# Here, we simulate this with a specific prompt for Gemini.
classifier_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

def select_framework(state: InterviewerState):
    """
    Selects the most relevant framework from the dataset based on the client's prompt.
    """
    client_prompt = state['client_prompt']
    get_data = {'text': 'initial__'+client_prompt}
    def smthn():
        try:
            # requests automatically URL-encodes the data in the 'params' dictionary
            response = requests.get(base_url, params=get_data)
            return (response.json() if response.json() else None)

        except requests.exceptions.ConnectionError:
            return None
    selected_framework = smthn()
    return {"selected_framework": selected_framework}

def generate_question(state: InterviewerState):
    """Generates a question based on the selected framework and conversation history."""
    framework = state['selected_framework']
    conversation_history = "\n".join([msg.content for msg in state['messages'] if isinstance(msg, (HumanMessage, SystemMessage))])
    
    last_response = state['messages'][-4:]

    # This is our "black-box" function. In a real scenario, this could be another LLM call
    # or a rule-based system.
    get_data = {'text': 'probe____'+'\n'.join([msg.content for msg in last_response])}
    def smthn():
        try:
            # requests automatically URL-encodes the data in the 'params' dictionary
            response = requests.get(base_url, params=get_data)
            return (response.json() if response.json() else None)

        except requests.exceptions.ConnectionError:
            return None
        
    context = smthn()
    context = context if context else 'N/A'

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert market research interviewer. Your goal is to ask insightful, open-ended questions to an industry expert (SME). You have to brief to them, in maximum 2-3 lines, about all the info you are provided about client's product. Then ask them for suggestions / their thoughts on the product obeying following prompts. They are indstry expert officials so have a serious tone."
                   "You need to be conversational and human-like. Avoid robotic questions. Do not re-explain the product if already explained earlier."
                   "Based on the following framework and conversation history, generate the next question. "
                   "Info provided by the Client:{Client}\n"
                   "Framework Title: {title}\n"
                   "Points to Cover: {points_to_cover}\n"
                   "Goals: {goals}\n"
                   "Conversation History:\n{history}\n"
                   "Also consider this provided context, if it's not N/A, into consideration while framing the question:\n{context}\n"
                   "Your question should be natural and flow from the conversation."
                   "Do not put placeholders and use ONLY the info you are provided with.If they divert from topic, try to steer them back on track."),
        ("user", "Generate the next question.")
    ])

    chain = prompt | generative_llm | StrOutputParser()
    question = chain.invoke({
        "Client":state['client_prompt'],
        "title": framework.get('title', 'N/A'),
        "points_to_cover": ", ".join(framework.get('points_to_consider', [])),
        "goals": ", ".join(framework.get('goals', [])),
        "history": conversation_history if conversation_history else "This is the start of the conversation.",
        "context": context
    })

    return {"messages": [SystemMessage(content=question)]}

def update_transcript_and_classify(state: InterviewerState):
    """
    Updates the transcript with the latest exchange and then classifies the response
    to decide the next step.
    """
    # The last message is the human's response, the one before is the AI's question.
    last_question = state['messages'][-2].content
    last_response = state['messages'][-1].content
    if len(state["messages"]) >= 3:
        print("Wow")
        return "FINISH"
    
    # Update transcript
    transcript = state['transcript'] + f"\n\nInterviewer: {last_question}\nSME: {last_response}"
    
    # Now classify the response
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a conversation analyst. Your task is to analyze the last response from an SME in the context of the entire conversation and decide the next action.

The objective of the conversation is to gather as much relevant information as possible, but once 5 to 8 questions have been asked or enough useful information has been collected, the process should stop.

If the SME drifts off-topic, treat it as incomplete information and steer toward PROBE unless enough total info has been gathered (then use FINISH).

Possible Actions:

CONTINUE: The SME has answered well and seems open to continue — proceed to the next relevant question.

PROBE: The SME's answer is unclear, incomplete, or off-topic — ask a follow-up to gather more detail, but avoid over-questioning.

FINISH: The SME appears tired, annoyed, or enough information (5-8 meaningful responses) has already been gathered — end the conversation. IF THE NUMBER OF QUESTIONS IN THE TRANSCRIPT IS EQUAL TO OR GREATER THAN 2, THEN JUST RETURN FINISH,  regardless of whatever.

Also, briefly assess the SME's emotional state: Engaged, Neutral, Annoyed, or Confused.

Output Format:
ACTION | EMOTIONAL_STATE

Here's the history:{history}
"""),
        ("user", "Analyze the last response and provide the action and emotional state.")
    ])
    chain = prompt | classifier_llm | StrOutputParser()
    result = chain.invoke({"history":transcript})

    action = "CONTINUE" # Default action
    try:
        action_part, _ = result.strip().split('|')
        action = action_part.strip().upper()
    except ValueError:
        pass
    state['transcript'] = transcript 
    if action not in ["PROBE", "FINISH"]:
        return "CONTINUE"
    
    return action

def probe_question(state: InterviewerState):
    """Calls a black-box function to get a probing question."""
    last_response = state['messages'][-4:]

    # This is our "black-box" function. In a real scenario, this could be another LLM call
    # or a rule-based system.
    def get_next_probe(response: str) -> str:
        get_data = {'text': 'probe____'+'\n'.join('\n'.join([msg.content for msg in response]))}
        def smthn():
            try:
                # requests automatically URL-encodes the data in the 'params' dictionary
                response = requests.get(base_url, params=get_data)
                return (response.json() if response.json() else None)

            except requests.exceptions.ConnectionError:
                return None
        selected_framework = smthn()
        return (ChatPromptTemplate.from_messages([
            f"The expert said: '{response}'. This is not clear enough, please ask them a question to either dig-deeper or probe them for question."
            "Here's some additional context : {context}"
            "Please focus on the context unless the context is empty. Use only the info provided. If they divert from topic, try to steer them back on track."]) | generative_llm | StrOutputParser()).invoke({"context":selected_framework})

    probe_q = get_next_probe(last_response)
    return {"messages": [SystemMessage(content=probe_q)]}


def summarize(state: InterviewerState):
    """Summarizes the conversation and provides key insights."""
    print("Wow!")
    transcript = state['transcript']
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert market research analyst. Based on the following interview transcript,"
                   "provide a concise summary of the key insights, findings, and any notable information."),
        ("user", "Transcript:\n{transcript}\n\nSummary:")
    ])

    chain = prompt | generative_llm | StrOutputParser()
    summary = chain.invoke({"transcript": transcript})
    return {"summary": summary}


# --- 3. Build the Graph ---

workflow = StateGraph(InterviewerState)
workflow.add_node("select_framework", select_framework)
workflow.add_node("generate_question", generate_question)
workflow.add_node("probe_question", probe_question)
workflow.add_node("classify", update_transcript_and_classify)
workflow.add_node("summarize", summarize)

workflow.set_entry_point("select_framework")
workflow.add_edge("select_framework", "generate_question")
workflow.add_edge("generate_question", "classify")
workflow.add_edge("probe_question", "classify")
workflow.add_conditional_edges(
    "classify",
    lambda x: x,
    {
        "CONTINUE": "generate_question",
        "PROBE": "probe_question",
        "FINISH": "summarize",
    },
)
workflow.add_edge("summarize", END)

memory = MemorySaver()
# The 'interrupt_after' tells the graph to pause at these steps, waiting for the front-end to continue
app = workflow.compile(
    checkpointer=memory, 
    interrupt_after=["generate_question", "probe_question"]
)