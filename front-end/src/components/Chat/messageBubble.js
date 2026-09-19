import React from "react";
import ReactMarkdown from "react-markdown"; 
import "./chatBox.css";

function MessageBubble({ sender, text, timestamp, agentUsed }) {
  const isUser = sender === "user";

  return (
    <div className={`message-row ${isUser ? "message-row-user" : "message-row-agent"}`}>
      {!isUser && <div className="agent-avatar">🤖</div>}
      <div className={`message-bubble ${isUser ? "message-user" : "message-agent"}`}>
        {!isUser && agentUsed && (
          <span className="agent-tag">{agentUsed}</span>
        )}
        <div className="message-text">
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>
        <span className="message-time">{timestamp}</span>
      </div>
    </div>
  );
}

export default MessageBubble;