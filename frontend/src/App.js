import React, { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import ChatApp from "./ChatApp";
import "./App.css";

function App() {
  const [user, setUser] = useState("");
  const [showRegister, setShowRegister] = useState(false);

  if (!user) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          {showRegister ? (
            <>
              <Register setUser={setUser} />
              <button className="switch-link" onClick={() => setShowRegister(false)}>
                Already have an account? Login
              </button>
            </>
          ) : (
            <>
              <Login setUser={setUser} />
              <button className="switch-link" onClick={() => setShowRegister(true)}>
                New user? Register
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  return <ChatApp user={user} />;
}
export default App;