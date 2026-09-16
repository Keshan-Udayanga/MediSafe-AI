import React, { useState, useRef, useEffect } from "react";
import MessageBubble from "./messageBubble.js";
import { askOrchestrator } from "../Services/chatService.js";
import "./chatBox.css";

function ChatBox({ user, onLogout }) {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const getCurrentTime = () => {
        return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    };

    const handleSend = async () => {
        if (!inputText.trim()) return;

        const userMessage = { sender: "user", text: inputText, timestamp: getCurrentTime() };
        setMessages((prev) => [...prev, userMessage]);

        const questionText = inputText;
        setInputText("");
        setLoading(true);

        try {
            // ← Query එක කෙලින්ම Orchestrator Agent එකට යනවා
            // Orchestrator ම බලනවා: Drug Info ද, Safety ද කියලා, ඕන agent එකට route කරනවා
            const response = await askOrchestrator(questionText);

            const agentMessage = {
                sender: "agent",
                text: response.answer,
                agentUsed: response.agent_used, // orchestrator ම return කරන "මොන agent එකද handle කළේ" කියන label එක
                timestamp: getCurrentTime(),
            };
            setMessages((prev) => [...prev, agentMessage]);
        } catch (err) {
            const errorMessage = {
                sender: "agent",
                text: err.message || "Something went wrong. Please try again.",
                timestamp: getCurrentTime(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // ChatBox.jsx - return statement එකේ මේ කොටස වෙනස් කරන්න

    return (
        <div className="chat-container">
            <div className="chat-main">
                <div className="chat-header">
                    <h3 className="header-title">💊 MediSafe AI Assistant</h3>
                    <div className="header-user">
                        <div className="user-avatar">{user?.username?.charAt(0).toUpperCase()}</div>
                        <div className="user-text">
                            <p className="user-name">{user?.username}</p>
                            <p className="user-email">{user?.email}</p>
                        </div>
                    </div>
                </div>

                {/* ← අලුත් wrapper div එකක් - Messages + Input දෙකම මේකට ඇතුලේ */}
                <div className="chat-card">
                    <div className="messages-area">
                        {messages.length === 0 && (
                            <div className="empty-state">
                                <p>Ask me anything about drugs, side effects, or drug interactions</p>
                            </div>
                        )}

                        {messages.map((msg, index) => (
                            <MessageBubble
                                key={index}
                                sender={msg.sender}
                                text={msg.text}
                                timestamp={msg.timestamp}
                                agentUsed={msg.agentUsed}
                            />
                        ))}

                        {loading && (
                            <div className="message-row message-row-agent">
                                <div className="agent-avatar">🤖</div>
                                <div className="message-bubble message-agent typing-indicator">
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    <div className="input-area">
                        <textarea
                            className="chat-input"
                            placeholder="Ask about a drug, or check interactions (e.g. Metformin and Lisinopril)..."
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={handleKeyDown}
                            rows={1}
                        />
                        <button className="send-btn" onClick={handleSend} disabled={loading || !inputText.trim()}>
                            ➤
                        </button>
                    </div>
                </div>
                {/* ← wrapper div එක මෙතන ඉවර වෙනවා */}
            </div>
        </div>
    );
}

export default ChatBox;