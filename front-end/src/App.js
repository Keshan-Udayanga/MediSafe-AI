import React, { useEffect, useState } from "react";

import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate
} from "react-router-dom";

import {
  GoogleOAuthProvider
} from "@react-oauth/google";

import LoginPage from "./components/Login/loginPage";
import ChatBox from "./components/Chat/chatBox";
import AdminDashboard from "./components/Admin/dashboard";
import DocumentTablePage from "./components/Admin/documentTablePage";

import {
  getCurrentUser
} from "./components/Services/authService.js";

import "./App.css";


const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;


function AuthenticatedLayout({ user, currentView, onLogout, children }) {
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const isAdmin = user?.role === "admin";

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest(".user-menu-container")) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navItems = isAdmin
    ? [
        { id: "admin-chat", label: "Chatbox", icon: "💬", action: () => navigate("/admin/chat") },
        { id: "admin-dashboard", label: "Dashboard", icon: "📊", action: () => navigate("/admin/dashboard") },
        { id: "admin-drug-docs", label: "Drug Information Document", icon: "📄", action: () => navigate("/admin/drug-documents") },
        { id: "admin-safety-docs", label: "Safety Document", icon: "🛡️", action: () => navigate("/admin/safety-documents") }
      ]
    : [
        { id: "chat", label: "Chat", icon: "💬", action: () => navigate("/home") },
        { id: "about", label: "About", icon: "ℹ️", action: () => navigate("/home") }
      ];

  return (
    <div className="app-shell">
      <aside className="auth-sidebar">
        <div className="auth-sidebar-header">
          <div className="brand-mark">M</div>
          <div>
            <h2>MediSafe-AI</h2>
          </div>
        </div>

        <nav className="auth-sidebar-nav" aria-label={isAdmin ? "Admin navigation" : "User navigation"}>
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-button ${currentView === item.id ? "active" : ""}`}
              onClick={item.action}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="auth-sidebar-footer">
          <div className="user-menu-container">
            <button
              type="button"
              className="user-profile-card"
              onClick={() => setShowUserMenu((prev) => !prev)}
            >
              <div className="user-profile-avatar">
                {user?.username?.charAt(0)?.toUpperCase() || "U"}
              </div>
              <div className="user-profile-text">
                <strong>{user?.username || "User"}</strong>
                <span>{user?.email || "No email"}</span>
              </div>
            </button>

            {showUserMenu && (
              <button
                type="button"
                className="auth-logout"
                onClick={() => {
                  setShowUserMenu(false);
                  onLogout();
                }}
              >
                <span>↪</span>
                Logout
              </button>
            )}
          </div>
        </div>
      </aside>

      <main className="auth-main">{children}</main>
    </div>
  );
}


// ============================================
// Main Application
// ============================================

function AppContent() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      try {
        const token = localStorage.getItem("access_token");

        if (!token) {
          setLoading(false);
          return;
        }

        const currentUser = await getCurrentUser();

        if (currentUser) {
          setUser(currentUser);
        } else {
          localStorage.removeItem("access_token");
          setUser(null);
        }
      } catch (error) {
        console.error("Failed to restore session:", error);
        localStorage.removeItem("access_token");
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    restoreSession();
  }, []);

  const handleLoginSuccess = (result) => {
    localStorage.setItem("access_token", result.access_token);
    setUser(result.user);

    if (result.user.role === "admin") {
      navigate("/admin/dashboard");
    } else {
      navigate("/home");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    navigate("/");
  };

  if (loading) {
    return (
      <div className="app-loading">
        <h2>MediSafe AI</h2>
        <p>Checking your session...</p>
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          user
            ? user.role === "admin"
              ? <Navigate to="/admin/dashboard" replace />
              : <Navigate to="/home" replace />
            : <LoginPage onLoginSuccess={handleLoginSuccess} />
        }
      />

      <Route
        path="/home"
        element={
          user ? (
            <AuthenticatedLayout user={user} currentView="chat" onLogout={handleLogout}>
              <ChatBox user={user} onLogout={handleLogout} />
            </AuthenticatedLayout>
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      <Route
        path="/admin/chat"
        element={
          user && user.role === "admin" ? (
            <AuthenticatedLayout user={user} currentView="admin-chat" onLogout={handleLogout}>
              <ChatBox user={user} onLogout={handleLogout} />
            </AuthenticatedLayout>
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      <Route
        path="/admin/dashboard"
        element={
          user && user.role === "admin" ? (
            <AuthenticatedLayout user={user} currentView="admin-dashboard" onLogout={handleLogout}>
              <AdminDashboard user={user} onLogout={handleLogout} />
            </AuthenticatedLayout>
          ) : (
            <Navigate to="/home" replace />
          )
        }
      />

      <Route
        path="/admin/drug-documents"
        element={
          user && user.role === "admin" ? (
            <AuthenticatedLayout user={user} currentView="admin-drug-docs" onLogout={handleLogout}>
              <DocumentTablePage type="drug" user={user} />
            </AuthenticatedLayout>
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      <Route
        path="/admin/safety-documents"
        element={
          user && user.role === "admin" ? (
            <AuthenticatedLayout user={user} currentView="admin-safety-docs" onLogout={handleLogout}>
              <DocumentTablePage type="safety" user={user} />
            </AuthenticatedLayout>
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}


function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </GoogleOAuthProvider>
  );
}

export default App;