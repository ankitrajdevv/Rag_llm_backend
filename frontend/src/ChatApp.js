import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ChatBar from "./components/ChatBar";
import Spinner from "./components/Spinner";
import "./ChatApp.css";

function ChatApp({ user, onLogout }) {
  // eslint-disable-next-line
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [isPdfUploaded, setIsPdfUploaded] = useState(false);
  const [speakingIndex, setSpeakingIndex] = useState(null);

  // For auto-scroll to latest answer
  const latestMsgRef = useRef(null);

  // Fetch user's chat history when component mounts or user changes
  useEffect(() => {
    const fetchHistory = async () => {
      if (user) {
        try {
          const res = await axios.get("http://localhost:8000/history/", {
            params: { username: user },
          });
          setChatHistory(res.data.history.reverse());
        } catch (err) {
          setChatHistory([]);
        }
      }
    };
    fetchHistory();
  }, [user]);

  useEffect(() => {
    if (latestMsgRef.current) {
      latestMsgRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatHistory]);

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setIsPdfUploaded(false);

      const formData = new FormData();
      formData.append("file", selectedFile);

      try {
        const res = await axios.post("http://localhost:8000/upload/", formData);
        setFilename(res.data.filename);
        setIsPdfUploaded(true);
        alert("PDF uploaded successfully");
      } catch (error) {
        alert("Failed to upload PDF");
        setIsPdfUploaded(false);
      }
    } else {
      alert("Please upload a valid PDF file");
      setIsPdfUploaded(false);
    }
  };

  const askQuestion = async () => {
    if (!query || !filename) return;

    const currentIndex = chatHistory.length;
    setChatHistory([...chatHistory, { question: query, answer: null }]);
    setQuery("");

    const formData = new FormData();
    formData.append("filename", filename);
    formData.append("query", query);
    formData.append("username", user);

    try {
      const res = await axios.post("http://localhost:8000/ask/", formData);
      setChatHistory((prev) => {
        const updated = [...prev];
        updated[currentIndex] = {
          question: query,
          answer: res.data.answer,
        };
        return updated;
      });
    } catch (error) {
      alert("Failed to get answer");
      setChatHistory((prev) => {
        const updated = [...prev];
        updated[currentIndex] = {
          question: query,
          answer: "Error fetching answer.",
        };
        return updated;
      });
    }
  };

  // Copy answer to clipboard
  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
  };

  // Speak answer using Web Speech API
  const speakText = (text, idx) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // stop any ongoing speech
      const utterance = new window.SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;
      utterance.onend = () => setSpeakingIndex(null);
      setSpeakingIndex(idx);
      window.speechSynthesis.speak(utterance);
    } else {
      alert("Speech synthesis not supported in your browser.");
    }
  };

  // Stop speech synthesis
  const stopSpeech = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
    }
  };

  return (
    <div className="app-container">
      <div className="top-bar" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ display: "inline-block" }}>RAG LLM</h2>
        {user && (
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div className="user-info" style={{
              color: "#90caf9",
              fontWeight: "bold",
              fontSize: "1.1em",
              letterSpacing: "1px",
              background: "#222d",
              padding: "7px 16px",
              borderRadius: "20px"
            }}>{user}</div>
            <button
              onClick={onLogout}
              style={{
                background: "#23272f",
                color: "#fff",
                border: "none",
                borderRadius: "12px",
                padding: "7px 18px",
                fontWeight: "bold",
                cursor: "pointer",
                fontSize: "1em",
                transition: "background 0.2s"
              }}
              onMouseOver={e => e.currentTarget.style.background="#1976d2"}
              onMouseOut={e => e.currentTarget.style.background="#23272f"}
            >
              Logout
            </button>
          </div>
        )}
      </div>

      <div className="chat-area">
        {chatHistory.map((item, index) => (
          <div
            key={index}
            className="chat-pair"
            ref={index === chatHistory.length - 1 ? latestMsgRef : null}
          >
            <div className="question-wrapper">
              <div className="question">{item.question}</div>
            </div>
            {item.answer === null ? (
              <Spinner />
            ) : (
              <div className="answer-wrapper">
                <div
                  className={`answer answer-with-copy${speakingIndex === index ? " speaking-answer" : ""}`}
                  style={speakingIndex === index ? { background: "#314062" } : {}}
                >
                  <div className="answer-text">{item.answer}</div>
                  <div className="answer-actions">
                    <button
                      className="copy-btn"
                      onClick={() => handleCopy(item.answer)}
                      title="Copy answer"
                    >
                      <span role="img" aria-label="Copy to clipboard">📋</span> Copy
                    </button>
                    {speakingIndex === index ? (
                      <button
                        className="speak-btn stop-btn"
                        onClick={stopSpeech}
                        title="Stop speaking"
                      >
                        <span role="img" aria-label="Stop">⏹️</span> Stop
                      </button>
                    ) : (
                      <button
                        className="speak-btn"
                        onClick={() => speakText(item.answer, index)}
                        title="Read aloud"
                      >
                        <span role="img" aria-label="Speak">🔊</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="chat-bar-wrapper">
        <div className="chat-bar-container">
          <ChatBar
            query={query}
            setQuery={setQuery}
            askQuestion={askQuestion}
            handleFileChange={handleFileChange}
            isPdfUploaded={isPdfUploaded}
          />
        </div>
      </div>
    </div>
  );
}

export default ChatApp;