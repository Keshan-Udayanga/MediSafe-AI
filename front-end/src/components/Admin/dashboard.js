import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  getDrugInformationDocuments,
  getSafetyDocuments,
} from "../Services/documentService";
import "./dashboard.css";

function AdminDashboard({ user }) {
  const navigate = useNavigate();
  const [drugCount, setDrugCount] = useState(null);
  const [safetyCount, setSafetyCount] = useState(null);

  useEffect(() => {
    let isMounted = true;
    getDrugInformationDocuments()
      .then((docs) => {
        if (isMounted) setDrugCount(docs.length);
      })
      .catch(() => {});

    getSafetyDocuments()
      .then((docs) => {
        if (isMounted) setSafetyCount(docs.length);
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="admin-dashboard">
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
          <div
            className="stat-card"
            style={{ cursor: "pointer" }}
            onClick={() => navigate("/admin/chat")}
            role="button"
            tabIndex={0}
          >
            <div className="stat-icon purple">🤖</div>
            <div>
              <span>Chatbot</span>
              <h3>Active</h3>
            </div>
            <div className="status-dot"></div>
          </div>

          <div
            className="stat-card"
            style={{ cursor: "pointer" }}
            onClick={() => navigate("/admin/drug-documents")}
            role="button"
            tabIndex={0}
          >
            <div className="stat-icon blue">📄</div>
            <div>
              <span>Drug Documents</span>
              <h3>{drugCount !== null ? `${drugCount} PDFs` : "Manage"}</h3>
            </div>
          </div>

          <div
            className="stat-card"
            style={{ cursor: "pointer" }}
            onClick={() => navigate("/admin/safety-documents")}
            role="button"
            tabIndex={0}
          >
            <div className="stat-icon green">🛡️</div>
            <div>
              <span>Safety Documents</span>
              <h3>{safetyCount !== null ? `${safetyCount} PDFs` : "Manage"}</h3>
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
              <div className="large-icon purple-bg">🤖</div>
              <span className="available">● Available</span>
            </div>

            <h2>AI Chatbot</h2>
            <p>
              Access the MediSafe AI chatbot and test
              information retrieval and safety responses.
            </p>

            <button
              className="primary-btn"
              onClick={() => navigate("/admin/chat")}
            >
              Open Chatbox
              <span>→</span>
            </button>
          </div>

          {/* Drug Information */}
          <div className="management-card">
            <div className="card-top">
              <div className="large-icon blue-bg">📄</div>
              <span className="document-label">Knowledge Base</span>
            </div>

            <h2>Drug Information</h2>
            <p>
              Add, remove and manage PDF documents
              used by the Information Agent.
            </p>

            <button
              className="secondary-btn"
              onClick={() => navigate("/admin/drug-documents")}
            >
              View Documents Table
              <span>→</span>
            </button>
          </div>

          {/* Safety */}
          <div className="management-card">
            <div className="card-top">
              <div className="large-icon green-bg">🛡️</div>
              <span className="document-label">Safety Knowledge</span>
            </div>

            <h2>Safety Documents</h2>
            <p>
              Manage safety-related PDF documents used
              by the Safety Agent.
            </p>

            <button
              className="secondary-btn"
              onClick={() => navigate("/admin/safety-documents")}
            >
              View Documents Table
              <span>→</span>
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default AdminDashboard;