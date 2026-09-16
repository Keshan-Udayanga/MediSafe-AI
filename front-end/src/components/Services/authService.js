// authService.js - Backend එකට login requests යවනවා

const API_BASE_URL = "http://127.0.0.1:8000";

// Username/Password login
export async function loginWithCredentials(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  return await response.json(); // { access_token, user }
}

// Google login - Google token එක backend එකට verify කරන්න යවනවා
export async function loginWithGoogle(googleToken) {
  const response = await fetch(`${API_BASE_URL}/auth/google-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: googleToken }),
  });

  if (!response.ok) {
    throw new Error("Google login failed");
  }

  return await response.json();
}