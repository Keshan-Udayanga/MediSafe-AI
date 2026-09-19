import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  getDrugInformationDocuments,
  uploadDrugInformationDocument,
  deleteDrugInformationDocument,
  getSafetyDocuments,
  uploadSafetyDocument,
  deleteSafetyDocument,
  fetchDocumentPdfBlob,
} from "../Services/documentService";
import "./documentTablePage.css";

function DocumentTablePage({ type = "drug", user }) {
  const isSafety = type === "safety";
  const title = isSafety ? "Safety Documents" : "Drug Information Documents";
  const eyebrow = isSafety ? "SAFETY KNOWLEDGE BASE" : "DRUG INFORMATION KNOWLEDGE BASE";
  const description = isSafety
    ? "Manage, view, and upload safety-related PDF documents used by the AI Safety Agent."
    : "Manage, view, and upload drug information PDF documents used by the AI Information Agent.";
  const icon = isSafety ? "🛡️" : "📄";
  const accentClass = isSafety ? "safety-accent" : "drug-accent";

  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const fileInputRef = useRef(null);

  // PDF Viewer State
  const [pdfViewer, setPdfViewer] = useState({
    open: false,
    title: "",
    blobUrl: null,
    loading: false,
    error: "",
  });

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await (isSafety ? getSafetyDocuments() : getDrugInformationDocuments());
      setDocuments(data || []);
    } catch (err) {
      setError(err.message || "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  }, [isSafety]);

  useEffect(() => {
    loadDocuments();
    setSearchQuery("");
    setError("");
    setSuccess("");
  }, [loadDocuments]);

  // Close viewer and release blob URL on unmount
  useEffect(() => {
    return () => {
      if (pdfViewer.blobUrl) {
        URL.revokeObjectURL(pdfViewer.blobUrl);
      }
    };
  }, [pdfViewer.blobUrl]);

  // Close PDF viewer on Escape key
  useEffect(() => {
    if (!pdfViewer.open) return;
    const handleKey = (e) => {
      if (e.key === "Escape") {
        if (pdfViewer.blobUrl) URL.revokeObjectURL(pdfViewer.blobUrl);
        setPdfViewer({ open: false, title: "", blobUrl: null, loading: false, error: "" });
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [pdfViewer.open, pdfViewer.blobUrl]);

  const openPdfViewer = async (doc) => {
    // Release previous blob
    if (pdfViewer.blobUrl) URL.revokeObjectURL(pdfViewer.blobUrl);

    setPdfViewer({ open: true, title: doc.title, blobUrl: null, loading: true, error: "" });

    try {
      const blob = await fetchDocumentPdfBlob(doc.id, isSafety);
      const blobUrl = URL.createObjectURL(blob);
      setPdfViewer((prev) => ({ ...prev, blobUrl, loading: false }));
    } catch (err) {
      setPdfViewer((prev) => ({
        ...prev,
        loading: false,
        error: err.message || "Failed to load PDF.",
      }));
    }
  };

  const closePdfViewer = () => {
    if (pdfViewer.blobUrl) URL.revokeObjectURL(pdfViewer.blobUrl);
    setPdfViewer({ open: false, title: "", blobUrl: null, loading: false, error: "" });
  };

  const handleFileSelected = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";

    if (!file) return;
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are accepted.");
      return;
    }

    setActionLoading(true);
    setError("");
    setSuccess("");

    try {
      await (isSafety ? uploadSafetyDocument(file) : uploadDrugInformationDocument(file));
      await loadDocuments();
      setSuccess(`"${file.name}" was uploaded successfully and indexed.`);
    } catch (err) {
      setError(err.message || "Failed to upload document.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async (docId, docTitle) => {
    if (
      !window.confirm(
        `Are you sure you want to delete "${docTitle}"? This will remove it from the AI knowledge base.`
      )
    ) {
      return;
    }

    setActionLoading(true);
    setError("");
    setSuccess("");

    try {
      await (isSafety ? deleteSafetyDocument(docId) : deleteDrugInformationDocument(docId));
      await loadDocuments();
      setSuccess(`"${docTitle}" was deleted successfully.`);
    } catch (err) {
      setError(err.message || "Failed to delete document.");
    } finally {
      setActionLoading(false);
    }
  };

  const filteredDocs = documents.filter((doc) =>
    (doc.title || "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={`doc-table-page ${accentClass}`}>
      {/* Page Header */}
      <header className="doc-page-header">
        <div className="doc-header-text">
          <span className="doc-eyebrow">{eyebrow}</span>
          <h1>
            <span className="doc-title-icon">{icon}</span> {title}
          </h1>
          <p className="doc-header-desc">{description}</p>
        </div>

        <div className="doc-header-profile">
          <div className="doc-avatar">
            {user?.username?.charAt(0)?.toUpperCase() || "A"}
          </div>
          <div>
            <strong>{user?.username || "Admin"}</strong>
            <span>Administrator</span>
          </div>
        </div>
      </header>

      {/* Status Alerts */}
      {error && (
        <div className="doc-alert error" role="alert">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
          <button
            type="button"
            className="alert-close"
            onClick={() => setError("")}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {success && (
        <div className="doc-alert success" role="alert">
          <span className="alert-icon">✓</span>
          <span>{success}</span>
          <button
            type="button"
            className="alert-close"
            onClick={() => setSuccess("")}
            aria-label="Dismiss success message"
          >
            ×
          </button>
        </div>
      )}

      {/* Action Toolbar */}
      <section className="doc-toolbar">
        <div className="doc-search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search documents by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="doc-search-input"
          />
          {searchQuery && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={() => setSearchQuery("")}
            >
              ×
            </button>
          )}
        </div>

        <div className="doc-toolbar-actions">
          <span className="doc-count-badge">
            <strong>{filteredDocs.length}</strong> of{" "}
            <strong>{documents.length}</strong>{" "}
            {documents.length === 1 ? "document" : "documents"}
          </span>

          <button
            type="button"
            className="doc-upload-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={actionLoading}
          >
            <span className="btn-icon">{actionLoading ? "⏳" : "⬆️"}</span>
            {actionLoading ? "Processing..." : "+ Upload New PDF"}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,.pdf"
            onChange={handleFileSelected}
            hidden
          />
        </div>
      </section>

      {/* Table Container */}
      <main className="doc-table-card">
        {loading ? (
          <div className="doc-loading-state">
            <div className="loading-spinner"></div>
            <p>Loading documents from knowledge base...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="doc-empty-state">
            <div className="empty-icon">{searchQuery ? "🔎" : "📂"}</div>
            <h3>{searchQuery ? "No matching documents" : "No documents found"}</h3>
            <p>
              {searchQuery
                ? `No documents match "${searchQuery}". Try a different keyword.`
                : `No ${isSafety ? "safety" : "drug information"} PDF documents have been uploaded yet.`}
            </p>
            {!searchQuery && (
              <button
                type="button"
                className="doc-empty-upload-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={actionLoading}
              >
                + Upload your first PDF
              </button>
            )}
          </div>
        ) : (
          <div className="table-responsive">
            <table className="doc-table">
              <thead>
                <tr>
                  <th className="col-id">#</th>
                  <th className="col-title">Document Name</th>
                  <th className="col-type">Format</th>
                  <th className="col-status">Status</th>
                  <th className="col-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc, index) => (
                  <tr
                    key={doc.id}
                    className="doc-row doc-row-clickable"
                    onClick={() => openPdfViewer(doc)}
                    title={`Click to view "${doc.title}"`}
                  >
                    <td className="col-id">{index + 1}</td>
                    <td className="col-title">
                      <div className="doc-file-info">
                        <span className="pdf-tag">PDF</span>
                        <span className="doc-name" title={doc.title}>
                          {doc.title}
                        </span>
                        <span className="doc-view-hint">👁 View</span>
                      </div>
                    </td>
                    <td className="col-type">
                      <span className="format-badge">PDF Document</span>
                    </td>
                    <td className="col-status">
                      <span className="status-badge active">
                        <span className="dot"></span> Indexed &amp; Active
                      </span>
                    </td>
                    <td
                      className="col-actions"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <button
                        type="button"
                        className="doc-delete-btn"
                        onClick={() => handleDelete(doc.id, doc.title)}
                        disabled={actionLoading}
                        title={`Delete ${doc.title}`}
                      >
                        <span>🗑️</span> Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {/* ======== PDF VIEWER MODAL ======== */}
      {pdfViewer.open && (
        <div
          className="pdf-modal-backdrop"
          role="presentation"
          onClick={closePdfViewer}
        >
          <div
            className="pdf-modal"
            role="dialog"
            aria-modal="true"
            aria-label={`Viewing: ${pdfViewer.title}`}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="pdf-modal-header">
              <div className="pdf-modal-title-row">
                <span className="pdf-modal-icon">📄</span>
                <div>
                  <p className="pdf-modal-eyebrow">
                    {isSafety ? "Safety Document" : "Drug Information Document"}
                  </p>
                  <h2 className="pdf-modal-title" title={pdfViewer.title}>
                    {pdfViewer.title}
                  </h2>
                </div>
              </div>
              <button
                type="button"
                className="pdf-modal-close"
                onClick={closePdfViewer}
                aria-label="Close PDF viewer"
              >
                ×
              </button>
            </div>

            {/* Modal Body */}
            <div className="pdf-modal-body">
              {pdfViewer.loading && (
                <div className="pdf-loading">
                  <div className="loading-spinner"></div>
                  <p>Loading PDF...</p>
                </div>
              )}

              {pdfViewer.error && !pdfViewer.loading && (
                <div className="pdf-error">
                  <span>⚠️</span>
                  <p>{pdfViewer.error}</p>
                </div>
              )}

              {pdfViewer.blobUrl && !pdfViewer.loading && (
                <iframe
                  className="pdf-iframe"
                  src={pdfViewer.blobUrl}
                  title={pdfViewer.title}
                  aria-label={`PDF: ${pdfViewer.title}`}
                />
              )}
            </div>

            {/* Modal Footer */}
            <div className="pdf-modal-footer">
              <span className="pdf-modal-hint">
                Press <kbd>Esc</kbd> or click outside to close
              </span>
              {pdfViewer.blobUrl && (
                <a
                  href={pdfViewer.blobUrl}
                  download={pdfViewer.title}
                  className="pdf-download-btn"
                >
                  ⬇️ Download PDF
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentTablePage;
