import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ChatBar from "./components/ChatBar";
import Spinner from "./components/Spinner";
import "./ChatApp.css";

function App() {
  // eslint-disable-next-line
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [isPdfUploaded, setIsPdfUploaded] = useState(false);

  // For auto-scroll to latest answer
  const latestMsgRef = useRef(null);

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

  return (
    <div className="app-container">
      <div className="top-bar">
        <h2>RAG LLM</h2>
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
                <div className="answer answer-with-copy">
                  {item.answer}
                  <button
                    className="copy-btn"
                    onClick={() => handleCopy(item.answer)}
                    title="Copy answer"
                  >
                    <span role="img" aria-label="Copy to clipboard">📋</span> Copy
                  </button>
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

export default App;