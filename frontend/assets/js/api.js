const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function getAccessToken() {
  return localStorage.getItem("cms_access_token");
}

function saveAuthTokens(tokens) {
  localStorage.setItem("cms_access_token", tokens.access_token);
  localStorage.setItem("cms_refresh_token", tokens.refresh_token);
}

function clearAuthTokens() {
  localStorage.removeItem("cms_access_token");
  localStorage.removeItem("cms_refresh_token");
}

async function apiRequest(endpoint, options = {}) {
  const token = getAccessToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "API request failed");
  }

  return data;
}
