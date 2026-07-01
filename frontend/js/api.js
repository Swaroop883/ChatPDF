const API_BASE = "http://localhost:8000";

function saveAuthData(token, username) {
    console.log("Saving token =", token);

    localStorage.setItem("chatpdf_token", token);
    localStorage.setItem("chatpdf_username", username);
}

function getAuthToken() {
  return localStorage.getItem("chatpdf_token");
}

function getUsername() {
  return localStorage.getItem("chatpdf_username") || "there";
}

function logout() {
  localStorage.removeItem("chatpdf_token");
  localStorage.removeItem("chatpdf_username");
  window.location.href = "index.html";
}

function requireAuth() {
    console.log("requireAuth called");

    const params = new URLSearchParams(window.location.search);

    console.log("URL =", window.location.href);

    if (params.get("dev") === "true") return "dev-token";

    const token = getAuthToken();

    console.log("Token from localStorage =", token);

    if (!token) {
        console.log("Redirecting to index because token is null");
        window.location.href = "index.html";
        return null;
    }

    return token;
}

async function apiRequest(path, method = "GET", body = null) {
  const token = getAuthToken();
  const opts = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  };
  const res = await fetch(`${API_BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiUpload(path, formData) {
  const token = getAuthToken();
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed ${res.status}`);
  }
  return res.json();
}