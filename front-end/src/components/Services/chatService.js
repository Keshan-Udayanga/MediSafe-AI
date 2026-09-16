// chatService.js
// Sends the complete user query to the Orchestrator Agent

const API_BASE_URL = "http://127.0.0.1:8000";

export async function askOrchestrator(question) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE_URL}/api/orchestrate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token && {
        Authorization: `Bearer ${token}`,
      }),
    },
    body: JSON.stringify({
      query: question,
      target_drugs: [],
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    throw new Error(
      errorData.detail || "Failed to get a response. Please try again."
    );
  }

  const data = await response.json();

  return {
    answer: data.final_consolidated_answer,
    agent_used:
      data.detailed_steps
        ?.map((step) => step.agent)
        .join(", ") || "Orchestrator",
  };
}