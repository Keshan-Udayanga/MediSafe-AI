import React, { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { loginWithGoogle } from "../Services/authService";
import "./loginPage.css";

function LoginPage({ onLoginSuccess }) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Google Login Success
  const handleGoogleSuccess = async (credentialResponse) => {
    setError("");
    setLoading(true);

    try {
      if (!credentialResponse?.credential) {
        throw new Error("Google credential not received");
      }

      const result = await loginWithGoogle(
        credentialResponse.credential
      );

      onLoginSuccess(result);

    } catch (err) {
      console.error("Google login error:", err);

      setError(
        err.message || "Google login failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  // Google Login Error
  const handleGoogleError = () => {
    console.error("Google Login failed");

    setError("Google login failed. Please try again.");
    setLoading(false);
  };

  return (
    <div className="login-container">

      {/* Animated background */}
      <div className="login-bg-glow login-bg-glow-one"></div>
      <div className="login-bg-glow login-bg-glow-two"></div>
      <div className="login-grid"></div>

      <div className="login-layout">

        {/* ================= RIGHT SIDE ================= */}

        <section className="login-form-panel">

          <div className="login-card">

            {/* Mobile brand */}

            <div className="mobile-brand">

              <div className="mobile-brand-icon">
                ✚
              </div>

              <span>
                MediSafe AI
              </span>

            </div>


            {/* Header */}

            <div className="login-header">

              <p className="login-welcome">
                WELCOME BACK
              </p>

              <h2>
                Sign in to MediSafe AI
              </h2>

              <p>
                Continue with your Google account to access
                your healthcare assistant.
              </p>

            </div>


            {/* Error */}

            {error && (

              <div className="error-message">

                <span>!</span>

                <p>
                  {error}
                </p>

              </div>

            )}


            {/* Google Login */}

            <div className="google-login-section">

              <div className="auth-label">
                <span>
                  Continue with
                </span>
              </div>


              <div className="google-button-wrapper">

                {loading ? (

                  <div className="login-loading">

                    <span className="loading-spinner"></span>

                    <span>
                      Signing you in...
                    </span>

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




            {/* Other login options */}

            <div className="alternative-login">

              <div className="alternative-divider">

                <span>
                  OTHER SIGN-IN OPTIONS
                </span>

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

                <span>
                  Continue with Microsoft
                </span>

                <span className="coming-soon">
                  Coming Soon
                </span>

              </button>

            </div>


            {/* Disclaimer */}

            <p className="login-disclaimer">

              By continuing, you acknowledge that MediSafe AI
              provides informational assistance and does not
              replace professional medical advice.

            </p>

          </div>

        </section>

      </div>

    </div>
  );
}

export default LoginPage;