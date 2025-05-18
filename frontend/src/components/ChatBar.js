import React from "react";
import { FaPlus, FaArrowUp } from "react-icons/fa";
import "./ChatBar.css";

const ChatBar = ({
  query,
  setQuery,
  askQuestion,
  handleFileChange,
  isPdfUploaded
}) => {
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && query.trim() && isPdfUploaded) {
      askQuestion();
    }
  };

  const isButtonDisabled = !query.trim() || !isPdfUploaded;

  return (
    <div className="chat-bar">
      <label htmlFor="file-upload" className="icon-button" title="Upload PDF">
        <FaPlus />
      </label>
      <input
        id="file-upload"
        type="file"
        accept=".pdf"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder={isPdfUploaded ? "Ask a question..." : "Upload a PDF first"}
        className="chat-input"
        disabled={!isPdfUploaded}  // Disable input if no PDF uploaded
      />
      <button
        onClick={askQuestion}
        className={`icon-button ${isButtonDisabled ? "disabled" : ""}`}
        disabled={isButtonDisabled}
        title={isButtonDisabled ? "Upload a PDF and enter question" : "Ask"}
      >
        <FaArrowUp />
      </button>
    </div>
  );
};

export default ChatBar;
