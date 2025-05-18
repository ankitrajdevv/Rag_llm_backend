import React, { useState } from "react";
import axios from "axios";
import ChatBar from "./components/ChatBar";
import Spinner from "./components/Spinner";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    if (selectedFile) {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const res = await axios.post("http://localhost:8000/upload/", formData);
      setFilename(res.data.filename);
      alert("PDF uploaded successfully");
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

    const res = await axios.post("http://localhost:8000/ask/", formData);

    setChatHistory((prev) => {
      const updated = [...prev];
      updated[currentIndex] = {
        question: query,
        answer: res.data.answer,
      };
      return updated;
    });
  };

  return (
    <div className="app-container">
      <div className="top-bar">
        <h2>RAG LLM</h2>
      </div>

      <div className="chat-area">
        {chatHistory.map((item, index) => (
          <div key={index} className="chat-pair">
            <div className="question-wrapper">
              <div className="question">{item.question}</div>
            </div>
            {item.answer === null ? (
              <Spinner />
            ) : (
              <div className="answer-wrapper">
                <div className="answer">{item.answer}</div>
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
          />
        </div>
      </div>
    </div>
  );
}

export default App;
