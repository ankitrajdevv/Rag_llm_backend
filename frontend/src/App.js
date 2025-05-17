import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post("http://localhost:8000/upload/", formData);
    setFilename(res.data.filename);
  };

  const askQuestion = async () => {
    const formData = new FormData();
    formData.append("filename", filename);
    formData.append("query", query);
    const res = await axios.post("http://localhost:8000/ask/", formData);
    setAnswer(res.data.answer);
  };

  return (
    <div style={{ padding: 30 }}>
      <h2>RAG LLM PDF QA</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={uploadFile}>Upload PDF</button>
      <br /><br />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
        style={{ width: "60%" }}
      />
      <button onClick={askQuestion}>Ask</button>
      <br /><br />
      <h3>Answer:</h3>
      <p>{answer}</p>
    </div>
  );
}

export default App;
