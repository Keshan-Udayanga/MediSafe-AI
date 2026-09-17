import React, { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { loginWithCredentials, loginWithGoogle } from "../Services/authService";
import "./loginPage.css";

function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Username/Password login handle කරනවා
  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!username || !password) {
      setError("Please enter both username and password");
      setLoading(false);
      return;
    }

    try {
      const result = await loginWithCredentials(username, password);
      onLoginSuccess(result);
    } catch (err) {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  // Google Login Success handle කරනවා
  const handleGoogleSuccess = async (credentialResponse) => {
    setError("");

    if (!credentialResponse?.credential) {
      console.error("Google login returned no credential", credentialResponse);
      setError("Google login failed: no credential was returned.");
      return;
    }

    try {
      const result = await loginWithGoogle(credentialResponse.credential);
      onLoginSuccess(result);
    } catch (err) {
      console.error("Google login request failed", err);
      setError(err.message || "Google login failed. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">MediSafe AI</h1>
        <p className="login-subtitle">Sign in to continue</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              className="text-input"
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="text-input"
            />
          </div>

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="divider">
          <span>OR</span>
        </div>

        <div className="google-login-wrapper">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError("Google login failed")}
            theme="filled_black"
            shape="pill"
            width="100%"
          />
        </div>
      </div>
    </div>
  );
}

export default LoginPage;