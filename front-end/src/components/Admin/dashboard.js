import React, { useRef, useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  deleteDrugInformationDocument,
  deleteSafetyDocument,
  getDrugInformationDocuments,
  getSafetyDocuments,
  uploadDrugInformationDocument,
  uploadSafetyDocument,
} from "../Services/documentService";
import "./dashboard.css";

function AdminDashboard({ user, onLogout }) {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [documents, setDocuments] = useState([]);
  const [documentsOpen, setDocumentsOpen] = useState(false);
  const [documentType, setDocumentType] = useState("drug");
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentActionLoading, setDocumentActionLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const [documentsSuccess, setDocumentsSuccess] = useState("");
  const fileInputRef = useRef(null);

  const docParam = searchParams.get("doc");

  const loadDocuments = async () => {
    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      setDocuments(
        await (documentType === "safety"
          ? getSafetyDocuments()
          : getDrugInformationDocuments())
      );
    } catch (error) {
      setDocumentsError(error.message);
    } finally {
      setDocumentsLoading(false);
    }
  };

  const openDocuments = (type = "drug") => {
    setDocumentType(type);
    setDocumentsOpen(true);
    setDocumentsSuccess("");
    setDocumentsLoading(true);
    setDocumentsError("");

    const load = type === "safety" ? getSafetyDocuments : getDrugInformationDocuments;
    load()
      .then(setDocuments)
      .catch((error) => setDocumentsError(error.message))
      .finally(() => setDocumentsLoading(false));
  };

  const handleOpenDocuments = (type = "drug") => {
    if (searchParams.get("doc") !== type) {
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set("doc", type);
      setSearchParams(nextParams);
    } else {
      openDocuments(type);
    }
  };

  const handleCloseDocuments = () => {
    setDocumentsOpen(false);
    if (searchParams.get("doc")) {
      const nextParams = new URLSearchParams(searchParams);
      nextParams.delete("doc");
      setSearchParams(nextParams, { replace: true });
    }
  };

  useEffect(() => {
    if (docParam === "drug" || docParam === "safety") {
      openDocuments(docParam);
    } else if (!docParam) {
      setDocumentsOpen(false);
    }
  }, [docParam]);

  useEffect(() => {
    const handleCustomOpen = (event) => {
      const type = event.detail;
      if (type === "drug" || type === "safety") {
        openDocuments(type);
      }
    };
    window.addEventListener("open-admin-doc", handleCustomOpen);
    return () => window.removeEventListener("open-admin-doc", handleCustomOpen);
  }, []);

  const handleFileSelected = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";

    if (!file) return;
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setDocumentsError("Only PDF files are accepted.");
      return;
    }

    setDocumentActionLoading(true);
    setDocumentsError("");
    setDocumentsSuccess("");

    try {
      await (documentType === "safety"
        ? uploadSafetyDocument(file)
        : uploadDrugInformationDocument(file));
      await loadDocuments();
      setDocumentsSuccess(`${file.name} was uploaded successfully.`);
    } catch (error) {
      setDocumentsError(error.message);
    } finally {
      setDocumentActionLoading(false);
    }
  };

  const handleDelete = async (documentId, title) => {
    if (!window.confirm(`Delete ${title}?`)) return;

    setDocumentActionLoading(true);
    setDocumentsError("");
    setDocumentsSuccess("");

    try {
      await (documentType === "safety"
        ? deleteSafetyDocument(documentId)
        : deleteDrugInformationDocument(documentId));
      await loadDocuments();
      setDocumentsSuccess(`${title} was deleted successfully.`);
    } catch (error) {
      setDocumentsError(error.message);
    } finally {
      setDocumentActionLoading(false);
    }
  };

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

          <div className="stat-card">
            <div className="stat-icon purple">🤖</div>

            <div>
              <span>Chatbot</span>
              <h3>Active</h3>
            </div>

            <div className="status-dot"></div>
          </div>


          <div className="stat-card" style={{ cursor: "pointer" }} onClick={() => handleOpenDocuments("drug")} role="button" tabIndex={0}>
            <div className="stat-icon blue">📄</div>

            <div>
              <span>Drug Documents</span>
              <h3>Manage</h3>
            </div>
          </div>


          <div className="stat-card" style={{ cursor: "pointer" }} onClick={() => handleOpenDocuments("safety")} role="button" tabIndex={0}>
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

            <button className="primary-btn" onClick={() => navigate("/admin/chat")}>
              Open Chatbox
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

            <button className="secondary-btn" onClick={() => handleOpenDocuments("drug")}>
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

            <button className="secondary-btn" onClick={() => handleOpenDocuments("safety")}>
              Manage Documents
              <span>→</span>
            </button>

          </div>

        </section>


      </main>

      {documentsOpen && (
        <div className="document-modal-backdrop" role="presentation" onClick={handleCloseDocuments}>
          <section className="document-modal" role="dialog" aria-modal="true" aria-labelledby="document-modal-title" onClick={(event) => event.stopPropagation()}>
            <div className="document-modal-header">
              <div>
                <p className="document-modal-eyebrow">
                  {documentType === "safety" ? "Safety Documents" : "Drug Information"}
                </p>
                <h2 id="document-modal-title">Manage Documents</h2>
                <p>PDF files stored in the knowledge base.</p>
              </div>
              <button className="modal-close-btn" onClick={handleCloseDocuments} aria-label="Close document manager">×</button>
            </div>

            <div className="document-modal-actions">
              <span>{documents.length} document{documents.length === 1 ? "" : "s"}</span>
              <button className="add-document-btn" onClick={() => fileInputRef.current?.click()} disabled={documentActionLoading}>
                {documentActionLoading ? "Working..." : "+ Add New PDF"}
              </button>
              <input ref={fileInputRef} type="file" accept="application/pdf,.pdf" onChange={handleFileSelected} hidden />
            </div>

            {documentsError && <div className="document-status error">{documentsError}</div>}
            {documentsSuccess && <div className="document-status success">{documentsSuccess}</div>}

            <div className="document-list" aria-live="polite">
              {documentsLoading ? (
                <div className="document-empty-state">Loading documents...</div>
              ) : documents.length === 0 ? (
                <div className="document-empty-state">
                  No {documentType === "safety" ? "safety" : "drug information"} PDFs have been uploaded yet.
                </div>
              ) : (
                documents.map((document) => (
                  <div className="document-row" key={document.id}>
                    <div className="document-file-icon">PDF</div>
                    <span className="document-title" title={document.title}>{document.title}</span>
                    <button className="delete-document-btn" onClick={() => handleDelete(document.id, document.title)} disabled={documentActionLoading}>Delete</button>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      )}

    </div>
  );
}

export default AdminDashboard;