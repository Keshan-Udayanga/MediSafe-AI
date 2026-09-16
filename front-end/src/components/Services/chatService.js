// chatService.js - Orchestrator Agent එකට Query එක යවනවා

const API_BASE_URL = "http://127.0.0.1:8000";

export async function askOrchestrator(question) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE_URL}/agent/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Failed to get a response. Please try again.");
  }

  return await response.json(); // { answer: "...", agent_used: "Drug Info Agent" }
}