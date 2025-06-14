import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Register({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await axios.post("http://localhost:8000/register/", { username, password });
      setSuccess(true);
      setTimeout(() => navigate("/login", { replace: true }), 1200);
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
      {success && <div className="success">Registration successful! Redirecting to login...</div>}
      {error && <div className="error">{error}</div>}
      <button
        type="button"
        className="switch-link"
        onClick={() => navigate("/login")}
      >
        Already have an account? Login
      </button>
    </form>
  );
}

export default Register;