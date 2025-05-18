import React from "react";
import { FaPlus, FaArrowUp } from "react-icons/fa";

const ChatBar = ({ query, setQuery, askQuestion, handleFileChange }) => {
  return (
    <div style={styles.chatBar}>
      <label htmlFor="file-upload" style={styles.iconButton}>
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
        placeholder="Ask a question..."
        style={styles.input}
      />
      <button onClick={askQuestion} style={styles.iconButton}>
        <FaArrowUp />
      </button>
    </div>
  );
};

const styles = {
  chatBar: {
    backgroundColor: "#2c2c2c",
    borderRadius: "25px",
    padding: "10px 15px",
    display: "flex",
    alignItems: "center",
    position: "relative"
  },
  iconButton: {
    backgroundColor: "#3a3a3a",
    color: "#fff",
    border: "none",
    borderRadius: "50%",
    width: "40px",
    height: "40px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    marginRight: "10px"
  },
  input: {
    flex: 1,
    backgroundColor: "transparent",
    border: "none",
    color: "#fff",
    fontSize: "16px",
    outline: "none"
  }
};

export default ChatBar;
