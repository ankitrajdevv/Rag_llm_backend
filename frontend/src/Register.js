import React, { useState } from "react";
import axios from "axios";

function Register({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:8000/register/", { username, password });
      setSuccess(true);
    } catch (err) {
      setError("Username already exists");
    }
  };

  return (
    <form onSubmit={handleRegister} className="auth-form">
      <h2>Register</h2>
      <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" required />
      <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Password" required />
      <button type="submit">Register</button>
      {success && <div className="success">Registration successful! You can now log in.</div>}
      {error && <div className="error">{error}</div>}
    </form>
  );
}

export default Register;