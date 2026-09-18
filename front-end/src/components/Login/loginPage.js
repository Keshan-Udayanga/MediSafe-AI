import React, { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { loginWithGoogle } from "../Services/authService";
import "./loginPage.css";

function LoginPage({ onLoginSuccess }) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGoogleSuccess = async (credentialResponse) => {
    setError("");
    setLoading(true);

    try {
      if (!credentialResponse?.credential) {
        throw new Error("Google credential not received");
      }

      const result = await loginWithGoogle(credentialResponse.credential);

      onLoginSuccess(result);
    } catch (err) {
      console.error("Google login error:", err);
      setError("Google login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    setLoading(false);
    setError("Google login failed. Please try again.");
  };

  return (
    <div className="login-container">
      {/* Animated background */}
      <div className="login-bg-glow login-bg-glow-one"></div>
      <div className="login-bg-glow login-bg-glow-two"></div>
      <div className="login-grid"></div>

      <div className="login-layout">
        {/* ================= LEFT SIDE ================= */}
        <section className="login-brand-panel">
          <div className="brand-content">
            <div className="brand-icon">
              <span>✚</span>
            </div>

            <p className="brand-label">AI-POWERED HEALTHCARE</p>

            <h1 className="brand-title">
              Medi<span>Safe</span> AI
            </h1>

            <p className="brand-tagline">
              Smarter decisions.
              <br />
              Safer medication.
            </p>

            <p className="brand-description">
              Intelligent medication information, interaction safety, and
              healthcare assistance in one place.
            </p>

            <div className="feature-list">
              <div className="feature-item">
                <div className="feature-icon">💊</div>

                <div>
                  <h3>Drug Information</h3>
                  <p>Access essential medication information quickly.</p>
                </div>
              </div>

              <div className="feature-item">
                <div className="feature-icon">🛡️</div>

                <div>
                  <h3>Interaction Safety</h3>
                  <p>Identify potential drug interaction risks.</p>
                </div>
                <div className="safety-highlights">
  <div className="safety-highlight">
    <span>⚠️</span>
    <div>
      <strong>Drug Interaction Checks</strong>
      <p>Detect potential risks between medications.</p>
    </div>
  </div>

  <div className="safety-highlight">
    <span>🔍</span>
    <div>
      <strong>Clear Safety Insights</strong>
      <p>Understand medication risks in simple terms.</p>
    </div>
  </div>

  <div className="safety-highlight">
    <span>✦</span>
    <div>
      <strong>AI-Powered Assistance</strong>
      <p>Get intelligent support for medication questions.</p>
    </div>
  </div>
</div>
              </div>
            </div>
          </div>

          <div className="brand-footer">
            <span className="status-dot"></span>
            Secure AI Healthcare Platform
          </div>
        </section>

        {/* ================= RIGHT SIDE ================= */}
        <section className="login-form-panel">
          <div className="login-card">
            {/* Mobile brand */}
            <div className="mobile-brand">
              <div className="mobile-brand-icon">✚</div>
              <span>MediSafe AI</span>
            </div>

            {/* Header */}
            <div className="login-header">
              <p className="login-welcome">WELCOME BACK</p>

              <h2>Sign in to MediSafe AI</h2>

              <p>
                Continue with your Google account to access your healthcare
                assistant.
              </p>
            </div>

            {/* Error */}
            {error && (
              <div className="error-message">
                <span>!</span>
                <p>{error}</p>
              </div>
            )}

            {/* Google Login */}
            <div className="google-login-section">
              <div className="auth-label">
                <span>Continue with</span>
              </div>

              <div className="google-button-wrapper">
                {loading ? (
                  <div className="login-loading">
                    <span className="loading-spinner"></span>
                    <span>Signing you in...</span>
                  </div>
                ) : (
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={handleGoogleError}
                    theme="filled_black"
                    shape="pill"
                    size="large"
                    width="100%"
                    text="continue_with"
                  />
                )}
              </div>
            </div>

            {/* Security */}
            <div className="security-note">
              <div className="security-icon">🔒</div>

              <div>
                <strong>Secure authentication</strong>

                <p>Your login is protected using Google OAuth.</p>
              </div>
            </div>

            {/* Other login options */}
            <div className="alternative-login">
              <div className="alternative-divider">
                <span>OTHER SIGN-IN OPTIONS</span>
              </div>

              <button
                type="button"
                className="microsoft-login-btn"
                disabled
                title="Microsoft authentication is not available yet"
              >
                <span className="microsoft-icon">
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                </span>

                <span>Continue with Microsoft</span>

                <span className="coming-soon">Coming Soon</span>
              </button>
            </div>

            {/* Disclaimer */}
            <p className="login-disclaimer">
              By continuing, you acknowledge that MediSafe AI provides
              informational assistance and does not replace professional
              medical advice.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

export default LoginPage;