// src/App.jsx

import React, { useEffect, useState } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";

import LoginPage from "./components/Login/loginPage";
import ChatBox from "./components/Chat/chatBox";

import { getCurrentUser } from "./components/Services/authService.js";

import "./App.css";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // App එක load / refresh වෙන හැම වෙලාවකම
  // existing login session එක check කරනවා
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const token = localStorage.getItem("access_token");

        // Token එකක් නැත්නම් login page එකට යන්න
        if (!token) {
          setLoading(false);
          return;
        }

        // Token එක තියෙනවා නම් backend එකෙන් user verify කරගන්න
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

  // Login success
  const handleLoginSuccess = (result) => {
    localStorage.setItem("access_token", result.access_token);
    setUser(result.user);
  };

  // Logout
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  // Session check වෙනකම්
  if (loading) {
    return (
      <div className="app-loading">
        <h2>MediSafe AI</h2>
        <p>Checking your session...</p>
      </div>
    );
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <div className="App">
        {!user ? (
          <LoginPage onLoginSuccess={handleLoginSuccess} />
        ) : (
          <ChatBox user={user} onLogout={handleLogout} />
        )}
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;