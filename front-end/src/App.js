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

import {
  getCurrentUser
} from "./components/Services/authService.js";

import "./App.css";


const GOOGLE_CLIENT_ID =
  process.env.REACT_APP_GOOGLE_CLIENT_ID;


// ============================================
// Main Application
// ============================================

function AppContent() {

  const navigate = useNavigate();

  const [user, setUser] = useState(null);

  const [loading, setLoading] = useState(true);


  // ==========================================
  // Restore existing session
  // ==========================================

  useEffect(() => {

    const restoreSession = async () => {

      try {

        const token =
          localStorage.getItem(
            "access_token"
          );


        if (!token) {

          setLoading(false);

          return;
        }


        const currentUser =
          await getCurrentUser();


        if (currentUser) {

          setUser(currentUser);

        } else {

          localStorage.removeItem(
            "access_token"
          );

          setUser(null);
        }

      } catch (error) {

        console.error(
          "Failed to restore session:",
          error
        );

        localStorage.removeItem(
          "access_token"
        );

        setUser(null);

      } finally {

        setLoading(false);

      }

    };


    restoreSession();

  }, []);


  // ==========================================
  // Google Login Success
  // ==========================================

  const handleLoginSuccess = (result) => {

    // Save token
    localStorage.setItem(
      "access_token",
      result.access_token
    );


    // Save user
    setUser(result.user);


    // ----------------------------------------
    // Check role
    // ----------------------------------------

    if (
      result.user.role === "admin"
    ) {

      navigate(
        "/admin/dashboard"
      );

    } else {

      navigate("/home");

    }

  };


  // ==========================================
  // Logout
  // ==========================================

  const handleLogout = () => {

    localStorage.removeItem(
      "access_token"
    );

    setUser(null);

    navigate("/");

  };


  // ==========================================
  // Loading
  // ==========================================

  if (loading) {

    return (

      <div className="app-loading">

        <h2>MediSafe AI</h2>

        <p>
          Checking your session...
        </p>

      </div>

    );

  }


  // ==========================================
  // Routes
  // ==========================================

  return (

    <Routes>

      {/* ------------------------------------ */}
      {/* Login */}
      {/* ------------------------------------ */}

      <Route
        path="/"
        element={
          user
            ? (
              user.role === "admin"
                ? (
                  <Navigate
                    to="/admin/dashboard"
                    replace
                  />
                )
                : (
                  <Navigate
                    to="/home"
                    replace
                  />
                )
            )
            : (
              <LoginPage
                onLoginSuccess={
                  handleLoginSuccess
                }
              />
            )
        }
      />


      {/* ------------------------------------ */}
      {/* Normal User Home */}
      {/* ------------------------------------ */}

      <Route
        path="/home"
        element={
          user ? (
            <ChatBox
              user={user}
              onLogout={
                handleLogout
              }
            />
          ) : (
            <Navigate
              to="/"
              replace
            />
          )
        }
      />


      {/* ------------------------------------ */}
      {/* Admin Dashboard */}
      {/* ------------------------------------ */}

      <Route
        path="/admin/dashboard"
        element={
          user &&
          user.role === "admin" ? (

            <AdminDashboard
              user={user}
              onLogout={
                handleLogout
              }
            />

          ) : (

            <Navigate
              to="/home"
              replace
            />

          )
        }
      />


      {/* ------------------------------------ */}
      {/* Unknown URL */}
      {/* ------------------------------------ */}

      <Route
        path="*"
        element={
          <Navigate
            to="/"
            replace
          />
        }
      />

    </Routes>

  );

}


// ============================================
// App
// ============================================

function App() {

  return (

    <GoogleOAuthProvider
      clientId={GOOGLE_CLIENT_ID}
    >

      <BrowserRouter>

        <AppContent />

      </BrowserRouter>

    </GoogleOAuthProvider>

  );

}


export default App;