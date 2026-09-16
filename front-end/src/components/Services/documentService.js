const API_BASE_URL = "http://127.0.0.1:8000";

async function getErrorMessage(response, fallback) {
  const data = await response.json().catch(() => ({}));
  return data.detail || fallback;
}

function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function getDrugInformationDocuments() {
  const response = await fetch(`${API_BASE_URL}/api/admin/drug-information-documents`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to load documents"));
  }

  return response.json();
}

export async function uploadDrugInformationDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/admin/drug-information-documents`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to upload document"));
  }

  return response.json();
}

export async function deleteDrugInformationDocument(documentId) {
  const response = await fetch(
    `${API_BASE_URL}/api/admin/drug-information-documents/${documentId}`,
    {
      method: "DELETE",
      headers: authHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to delete document"));
  }
}

export async function getSafetyDocuments() {
  const response = await fetch(`${API_BASE_URL}/api/admin/drug-information-documents/safety`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to load safety documents"));
  }

  return response.json();
}

export async function uploadSafetyDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/admin/drug-information-documents/safety`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to upload safety document"));
  }

  return response.json();
}

export async function deleteSafetyDocument(documentId) {
  const response = await fetch(
    `${API_BASE_URL}/api/admin/drug-information-documents/safety/${documentId}`,
    {
      method: "DELETE",
      headers: authHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to delete safety document"));
  }
}