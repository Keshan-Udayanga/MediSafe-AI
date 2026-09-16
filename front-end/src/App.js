// src/App.jsx
import React, { useState } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import LoginPage from "./components/Login/loginPage";
import ChatBox from "./components/Chat/chatBox";

import "./App.css";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID

function App() {
  const [user, setUser] = useState(null);

  const handleLoginSuccess = (result) => {
    setUser(result.user);
    localStorage.setItem("access_token", result.access_token); // token save කරගන්නවා
  };

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <div className="App">
        {!user ? (
          <LoginPage onLoginSuccess={handleLoginSuccess} />
        ) : (
          <ChatBox user={user} />
        )}
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;