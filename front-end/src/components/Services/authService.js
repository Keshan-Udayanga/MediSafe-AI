// authService.js
// Backend එකට authentication requests යවනවා

const API_BASE_URL = "http://127.0.0.1:8000";

// Google login
export async function loginWithGoogle(googleToken) {
  const response = await fetch(`${API_BASE_URL}/auth/google-login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      token: googleToken,
    }),
  });

  if (!response.ok) {
    let detail = "Google login failed";

    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch (parseError) {
      console.error("Could not read Google login error response", parseError);
    }

    console.error("Google login failed", {
      status: response.status,
      detail,
    });

    throw new Error(detail);
  }

  return await response.json();
}

// Refresh වුණාම currently logged-in user ලබාගන්නවා
export async function getCurrentUser() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    return null;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    // Token expired / invalid
    localStorage.removeItem("access_token");
    return null;
  }

  return await response.json();
}