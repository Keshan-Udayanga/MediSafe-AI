import React, { useState } from "react";
import "./dashboard.css";

function AdminDashboard({ user, onLogout }) {
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div className={`admin-dashboard ${darkMode ? "dark" : ""}`}>

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">M</div>

          <div>
            <h2>MediSafe</h2>
            <span>AI Admin</span>
          </div>
        </div>

        <nav className="sidebar-nav">

          <button className="nav-item active">
            <span>⌂</span>
            Dashboard
          </button>

          <button className="nav-item">
            <span>🤖</span>
            Chatbot
          </button>

          <button className="nav-item">
            <span>📄</span>
            Drug Information
          </button>

          <button className="nav-item">
            <span>🛡️</span>
            Safety Documents
          </button>

        </nav>

        <div className="sidebar-bottom">

          <button
            className="theme-btn"
            onClick={() => setDarkMode(!darkMode)}
          >
            <span>{darkMode ? "☀️" : "🌙"}</span>
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>

          <button className="logout-btn" onClick={onLogout}>
            <span>↪</span>
            Logout
          </button>

        </div>

      </aside>


      {/* Main Content */}
      <main className="dashboard-main">

        {/* Header */}
        <header className="dashboard-header">

          <div>
            <p className="welcome-small">WELCOME BACK 👋</p>

            <h1>Admin Dashboard</h1>

            <p className="header-description">
              Manage MediSafe AI knowledge and safety resources.
            </p>
          </div>

          <div className="profile">

            <div className="profile-avatar">
              {user?.username?.charAt(0)?.toUpperCase() || "A"}
            </div>

            <div>
              <strong>{user?.username || "Admin"}</strong>
              <span>Administrator</span>
            </div>

          </div>

        </header>


        {/* Statistics */}
        <section className="stats-grid">

          <div className="stat-card">
            <div className="stat-icon purple">🤖</div>

            <div>
              <span>Chatbot</span>
              <h3>Active</h3>
            </div>

            <div className="status-dot"></div>
          </div>


          <div className="stat-card">
            <div className="stat-icon blue">📄</div>

            <div>
              <span>Drug Documents</span>
              <h3>Manage</h3>
            </div>
          </div>


          <div className="stat-card">
            <div className="stat-icon green">🛡️</div>

            <div>
              <span>Safety Documents</span>
              <h3>Manage</h3>
            </div>
          </div>

        </section>


        {/* Main Cards */}
        <section className="section-title">

          <div>
            <h2>System Management</h2>
            <p>Select an area to manage the MediSafe AI system.</p>
          </div>

        </section>


        <section className="management-grid">

          {/* Chatbot */}
          <div className="management-card chatbot-card">

            <div className="card-top">

              <div className="large-icon purple-bg">
                🤖
              </div>

              <span className="available">
                ● Available
              </span>

            </div>

            <h2>AI Chatbot</h2>

            <p>
              Access the MediSafe AI chatbot and test
              information retrieval and safety responses.
            </p>

            <button className="primary-btn">
              Open Chatbot
              <span>→</span>
            </button>

          </div>


          {/* Drug Information */}
          <div className="management-card">

            <div className="card-top">

              <div className="large-icon blue-bg">
                📄
              </div>

              <span className="document-label">
                Knowledge Base
              </span>

            </div>

            <h2>Drug Information</h2>

            <p>
              Add, remove and manage PDF documents
              used by the Information Agent.
            </p>

            <button className="secondary-btn">
              Manage Documents
              <span>→</span>
            </button>

          </div>


          {/* Safety */}
          <div className="management-card">

            <div className="card-top">

              <div className="large-icon green-bg">
                🛡️
              </div>

              <span className="document-label">
                Safety Knowledge
              </span>

            </div>

            <h2>Safety Documents</h2>

            <p>
              Manage safety-related PDF documents used
              by the Safety Agent.
            </p>

            <button className="secondary-btn">
              Manage Documents
              <span>→</span>
            </button>

          </div>

        </section>


        {/* Bottom Info */}
        <section className="info-panel">

          <div className="info-icon">
            💡
          </div>

          <div>
            <h3>How MediSafe AI works</h3>

            <p>
              The Orchestrator receives the user's question
              and routes it to the appropriate AI agent.
              Agents use information from the available
              knowledge documents.
            </p>
          </div>

        </section>

      </main>

    </div>
  );
}

export default AdminDashboard;