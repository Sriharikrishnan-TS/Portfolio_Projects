# main.py
import json
import httpx
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import whisper
import torch
from pydub import AudioSegment
import io
import tempfile
import requests



# ----------------- App Setup -----------------
app = FastAPI(
    title="Analytics Dashboard API",
    description="API for fetching analytics data for the dashboard front-end.",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Pydantic Models -----------------
class Metric(BaseModel):
    current: float
    change: float

class ProductMetric(BaseModel):
    name: str
    change: float

class SummaryMetrics(BaseModel):
    totalInterviews: Metric
    positiveSentiment: Metric
    avgDuration: Metric
    topProduct: ProductMetric

class Dataset(BaseModel):
    label: str
    data: List[int]

class SentimentAnalysis(BaseModel):
    labels: List[str]
    datasets: List[Dataset]

class InterviewDurationDistribution(BaseModel):
    labels: List[str]
    data: List[int]

class MostUsedProduct(BaseModel):
    name: str
    value: int

class SpiderChartData(BaseModel):
    productName: str
    scores: List[int]

class DashboardResponse(BaseModel):
    lastUpdated: datetime
    summaryMetrics: SummaryMetrics
    sentimentAnalysis: SentimentAnalysis
    interviewDurationDistribution: InterviewDurationDistribution
    mostUsedProducts: List[MostUsedProduct]
    SpiderChart: SpiderChartData

class Message(BaseModel):
    sender: str
    text: str

class ConversationPayload(BaseModel):
    messages: List[Message]

class StartChatResponse(BaseModel):
    thread_id: str
    ai_message: str

class LLMChatRequest(BaseModel):
    thread_id:str
    text:str


class LLMChatResponse(BaseModel):
    ai_message:str
    status:str

# ----------------- Existing Endpoints -----------------
@app.get("/api/dashboard/analytics", response_model=DashboardResponse)
async def get_dashboard_data():
    """
    Retrieves dashboard data by fetching it from an external database URL.
    """
    # The URL for your  database
    DATABASE_URL = "https://vbzml093-5000.inc1.devtunnels.ms/db?text=front_end"

    try:
        # Use an async client to make the network request
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(DATABASE_URL)

            # This will automatically raise an error for non-200 responses (like 404, 500)
            response.raise_for_status()

            # Parse the JSON data from the response
            live_data = response.json()
            
            # Return the live data
            return live_data

    except httpx.RequestError as exc:
        # This catches network errors, like being unable to connect
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"Error communicating with the database service: {exc}"
        )
    except httpx.HTTPStatusError as exc:
        # This catches error responses from the database (e.g., 404 Not Found)
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Database service returned an error: {exc.response.text}"
        )

LLM_URL = "https://5s1c40lz-8000.inc1.devtunnels.ms/interview"

@app.post("/api/llm/start", response_model=StartChatResponse)
async def start_llm_conversation():
    """
    Starts a new conversation with the external LLM by sending an empty payload.
    Returns the initial message and a new thread_id.
    """
    try:
        async with httpx.AsyncClient(verify=False) as client:
            # Send an empty JSON to the external LLM to start the chat
            response = await client.post(LLM_URL, json={}, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            # The external LLM is expected to return {"thread_id": "...", "message": "..."}

            print("llm response:",data)
            return data
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"LLM service error: {exc.response.text}")


@app.post("/api/llm/chat", response_model=LLMChatResponse)
async def continue_llm_conversation(request: LLMChatRequest):
    """
    Continues a conversation using an existing thread_id.
    Formats the payload as { "thread": "thread_id+text" } for the external LLM.
    """
    try:
        # Format the payload as required by the external LLM
        payload = {"thread_id": f"{request.thread_id}+{request.text}"}
        print(payload)
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(LLM_URL, params=payload, timeout=60.0)
            response.raise_for_status()
            # We expect the LLM to return a simple response like {"response": "..."}
            data = response.json()
            print(data)
            return data
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"LLM service error: {exc.response.text}")
    
CONVERSATIONS_FILE = "conversations.json"
@app.post("/api/conversations")
def save_conversation(payload: ConversationPayload):
    try:
        new_conversation = {
            "conversation_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "messages": [msg.dict() for msg in payload.messages],
        }

        try:
            with open(CONVERSATIONS_FILE, "r") as f:
                conversations = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            conversations = []

        conversations.append(new_conversation)
        with open(CONVERSATIONS_FILE, "w") as f:
            json.dump(conversations, f, indent=2)

        return {"status": "success", "conversation_id": new_conversation["conversation_id"]}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# ----------------- Whisper Transcription Endpoint -----------------
# Load Whisper once (recommended)
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = whisper.load_model("base", device=device)

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Receives an audio file (webm/mp3/wav) and returns transcribed text using Whisper.
    Converts to WAV automatically.
    """
    try:
        audio_bytes = await file.read()

        # Convert to WAV using pydub
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(tmp_wav.name, format="wav")

            # Now pass to Whisper
            result = whisper_model.transcribe(tmp_wav.name)

        return {"transcript": result["text"].strip()}

    except Exception as e:
        print("Transcription error:", e)
        return {"error": str(e)}

