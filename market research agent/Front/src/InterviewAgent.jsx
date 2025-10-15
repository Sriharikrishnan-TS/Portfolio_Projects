import React, { useState, useRef, useEffect } from "react";
import "./App.css";

const InterviewAgent = ({ userRole, onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [threadId, setThreadId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messageEndRef = useRef(null); // 👈 for auto-scroll

  // 👇 Auto-scroll to bottom when messages or typing changes
  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  // Start conversation on mount
  useEffect(() => {
    const startConversation = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/llm/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        if (!response.ok) throw new Error("Failed to start conversation");

        const data = await response.json();
        setThreadId(data.thread_id);
        setMessages([{ id: 1, text: data.ai_message, sender: "agent" }]);
      } catch (err) {
        console.error(err);
        setMessages([
          {
            id: 1,
            text: "Sorry, I couldn't connect to the interview agent. Please try again later.",
            sender: "agent",
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    startConversation();
  }, []);

  // Send message
  const handleSendMessage = async () => {
    const trimmedInput = inputValue.trim();
    if (!threadId || !trimmedInput || isLoading) return;

    const newUserMessage = {
      id: Date.now(),
      text: trimmedInput,
      sender: "user",
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/llm/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: threadId, text: trimmedInput }),
      });
      if (!response.ok) throw new Error("Chat API failed");

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, text: data.ai_message, sender: "agent" },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: "Something went wrong. Try again.",
          sender: "agent",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => e.key === "Enter" && handleSendMessage();

  // 🎤 Recording + transcription
  const handleMicClick = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        const formData = new FormData();
        formData.append("file", audioBlob, "speech.webm");

        try {
          const res = await fetch("http://127.0.0.1:8000/transcribe", {
            method: "POST",
            body: formData,
          });
          if (!res.ok) throw new Error("Transcription failed");
          const data = await res.json();
          setInputValue(data.transcript || "");
        } catch (err) {
          console.error("Transcription Error:", err);
          alert("Failed to transcribe audio.");
        } finally {
          stream.getTracks().forEach((t) => t.stop());
        }
      };

      recorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Microphone access denied. Please enable mic permissions.");
    }
  };

  // 💾 Save conversation
  const handleSaveConversation = async () => {
    if (messages.length <= 1) {
      alert("No conversation to save yet.");
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8000/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages }),
      });
      const result = await response.json();
      alert(`Conversation saved! ID: ${result.conversation_id}`);
    } catch (err) {
      console.error("Save failed:", err);
      alert("Could not save conversation.");
    }
  };

  return (
    <div className="chat-container">
      <header className="header">
        <div className="header-left">
          <div className="agent-icon"></div>
          <div>
            <h1 className="header-title">Interview Agent</h1>
            <p className="header-subtitle">Conversational Intelligence</p>
          </div>
        </div>

        <div className="header-right">
          {userRole === "admin" && (
            <button className="header-button admin-button">
              Admin Dashboard
            </button>
          )}
          <button onClick={handleSaveConversation} className="header-button">
            Summary
          </button>
          <button className="header-button">Help</button>
          <button
            onClick={onLogout}
            className="logout-button-agent"
            style={{ backgroundColor: "black" }}
          >
            Logout
          </button>
        </div>
      </header>

      <div className="message-list">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message-bubble ${
              msg.sender === "agent" ? "agent-bubble" : "user-bubble"
            }`}
          >
            {msg.sender === "agent" && <div className="bubble-icon">💬</div>}
            <p className="message-text">{msg.text}</p>
          </div>
        ))}

        {isLoading && (
          <div className="message-bubble agent-bubble">
            <div className="bubble-icon">💬</div>
            <p className="message-text typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </p>
          </div>
        )}

        {/* 👇 Auto-scroll anchor */}
        <div ref={messageEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={inputValue}
          placeholder="Type or speak..."
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          className="input-box"
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading}
          className="send-button"
        >
          ➤
        </button>

        <button
          className={`mic-button ${isRecording ? "recording" : ""}`}
          onClick={handleMicClick}
          disabled={isLoading}
          style={{
            background: isRecording ? "#E63946" : "#007bff",
            color: "white",
            transition: "0.3s",
          }}
        >
          🎤 {isRecording && <span style={{ fontSize: "12px" }}>Recording...</span>}
        </button>
      </div>

      <div
        style={{
          textAlign: "center",
          color: "#777",
          fontSize: "13px",
          marginTop: "8px",
        }}
      >
        Click 🎤 to record and transcribe with Whisper (FastAPI backend).
      </div>
    </div>
  );
};

export default InterviewAgent;
