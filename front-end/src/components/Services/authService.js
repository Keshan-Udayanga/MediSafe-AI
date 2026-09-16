// authService.js
// Backend එකට authentication requests යවනවා

const API_BASE_URL = "http://127.0.0.1:8000";

// Username/Password login
export async function loginWithCredentials(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      password,
    }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  return await response.json();
}

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
    throw new Error("Google login failed");
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