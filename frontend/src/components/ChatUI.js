import React, { useState } from 'react';
import './ChatUI.css';

const ChatUI = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const newMessages = [
            ...messages,
            { type: 'user', text: input },
            { type: 'bot', text: 'Hello! 😊\nHow can I help you today?' }
        ];
        setMessages(newMessages);
        setInput('');
    };

    return (
        <div className="chat-wrapper">
            <header className="chat-header">
                <h2>ChatBot Project</h2>
            </header>

            <main className="chat-container">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`chat-message ${msg.type}`}
                    >
                        <p><strong>{msg.type === 'user' ? 'You' : 'Bot'}:</strong> {msg.text}</p>
                    </div>
                ))}
            </main>

            <footer className="chat-footer">
                <form onSubmit={handleSubmit} className="chat-form">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask anything..."
                        required
                    />
                    <button type="submit">Send</button>
                </form>
            </footer>
        </div>
    );
};

export default ChatUI;
