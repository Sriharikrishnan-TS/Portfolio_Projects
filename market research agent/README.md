# 🧠 LLM Agent Market Research & Product Validation System

## 🚀 Project Overview

This system automates the initial phase of product validation by using a **Large Language Model (LLM) Agent** to conduct dynamic, in-depth market research. The agent processes a person's product pitch, generates highly specific questions based on an integrated **Knowledge Graph (KG)**, and directs those questions to Subject Matter Experts (SMEs) to gather deep market intelligence.

The architecture is built on a robust, hybrid backend for maximum performance and flexibility.

---

## ⚙️ Architecture and Technology Stack

Our system follows a microservices/hybrid architecture, leveraging the strengths of both Flask and FastAPI for API serving and task handling.

| Component | Technology | Role in System |
| :--- | :--- | :--- |
| **Frontend/UI** | **React** | Displays real-time analytics, manages the product pitch input, and visualizes the knowledge graph structure. |
| **LLM Agent/Core Logic** | **Python (LangGraph)** | **The AI core** that interprets the pitch, generates probing questions, and processes SME responses. |
| **Semantic Layer** | **Knowledge Graphs (KGs)** | Implemented from product data to provide semantic context for the LLM, enabling deeper, more dynamic, and non-generic questioning of SMEs. |
| **API Backend (Hybrid)** | **Flask** & **FastAPI** | **Flask:** Handles core application logic and state management. **FastAPI:** Used for high-performance data processing endpoints (like vector similarity searches). |
| **Database/Vector Store** | **Supabase (PostgreSQL)** | Persistent storage for user data, product pitches, and SME responses. |
| **Vector Indexing** | **pgvector** | PostgreSQL extension used to store the **vector embeddings** of the Knowledge Graph nodes, enabling fast semantic retrieval (RAG) for the LLM Agent. |
| **Voice Input** | **Whisper** |Voice input for conference with the Agent is processed by the Whisper model for highly accurate, low-latency Speech-to-Text (STT) transcription.|

---

## 📊 Key Features

* **Intelligent Question Generation:** The LLM Agent uses the Knowledge Graph to identify weak points, gaps, and technical trade-offs in a pitch, leading to highly targeted SME questions.
* **Vectorized Semantic Retrieval (RAG):** Product information (nodes/edges/properties) is converted into embeddings and stored in the database, allowing the LLM to retrieve context based on semantic similarity rather than just keyword matching.
* **Dual-API Backend:** Leverages Flask for a standard application structure and FastAPI for performance-critical tasks (e.g., embedding lookups, knowledge graph traversal).
* **Real-time Analytics:** The React frontend visualizes key market insights derived from SME responses, speeding up the market research cycle.

---

## 🛠️ Setup and Installation

### Prerequisites

* Python 3.10+
* Node.js & npm (for React frontend)
* Supabase Account or Local PostgreSQL instance with the **`pgvector` extension enabled** (`CREATE EXTENSION vector;`).

### Backend Setup (Python)

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Mevan-V/Transfinitte25
    cd Transfinitte25
    ```
2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Database:**
    * Set up environment variables for your Supabase/PostgreSQL connection string.
    * Run initial migrations to create the core tables (`product_strategy_modules`, etc.).

### Frontend Setup (React)

1.  **Navigate to Frontend Directory:**
    ```bash
    cd frontend
    ```
2.  **Install Node Modules:**
    ```bash
    npm install
    ```
3.  **Start the Frontend:**
    ```bash
    npm start
    ```

### Running the System

1.  **Start the API Server(s):** (Likely running both Flask and FastAPI instances for the hybrid system).
    ```bash
    # Start Flask files
    python app.py
    python third.py 
    
    # Start FastAPI files
    python main.py
    ```
2.  Access the application in your browser at the address shown by your React setup (typically `http://localhost:5000`).