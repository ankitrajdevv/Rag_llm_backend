import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Register from "./Register";
import ChatApp from "./ChatApp";
import "./App.css";

// Helper to wrap form in styled box
const AuthPage = ({ children }) => (
  <div className="auth-container">
    <div className="auth-box">
      {children}
    </div>
  </div>
);

function App() {
  const [user, setUser] = useState("");

  const handleLogout = () => {
    setUser("");
    // Optional: navigate to login page if needed
    // window.location.href = "/login";
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            !user ? (
              <AuthPage>
                <Login setUser={setUser} />
              </AuthPage>
            ) : (
              <Navigate to="/chat" replace />
            )
          }
        />
        <Route
          path="/register"
          element={
            !user ? (
              <AuthPage>
                <Register setUser={setUser} />
              </AuthPage>
            ) : (
              <Navigate to="/chat" replace />
            )
          }
        />
        <Route
          path="/chat"
          element={
            user ? (
              <ChatApp user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/"
          element={
            user ? <Navigate to="/chat" replace /> : <Navigate to="/login" replace />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;