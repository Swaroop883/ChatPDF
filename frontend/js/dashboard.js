async function initDashboardPage() {
  const token = requireAuth();
  if (!token) return;

  const params = new URLSearchParams(window.location.search);
  const tokenFromUrl = params.get("token");
  if (tokenFromUrl) {
    saveAuthData(tokenFromUrl, params.get("username") || "User");
    window.history.replaceState({}, document.title, "dashboard.html");
  }

  const greetingEl = document.getElementById("greeting-name");
  if (greetingEl) greetingEl.textContent = `Hello, ${getUsername()}!`;

  const logoutBtn = document.getElementById("btn-logout");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);

  await loadSessionList();
  setupUploadZone();
}

async function loadSessionList() {
  const grid       = document.getElementById("sessions-grid");
  const emptyState = document.getElementById("sessions-empty");
  const title      = document.getElementById("sessions-title");
  if (!grid) return;

  try {
    const sessions = await apiRequest("/session/list");

    if (sessions.length === 0) {
      if (emptyState) emptyState.style.display = "block";
      if (title) title.style.display = "none";
      return;
    }

    if (emptyState) emptyState.style.display = "none";
    if (title) title.style.display = "flex";

    grid.innerHTML = sessions.map((s) => {
      const date = s.created_at
        ? new Date(s.created_at).toLocaleDateString("en-US", {
            year: "numeric", month: "short", day: "numeric",
          })
        : "Unknown date";
      return `
        <div class="session-card" onclick="openSession(${s.session_id}, '${escapeHtml(s.session_name)}')">
          <div class="session-card-icon">📄</div>
          <div class="session-card-title" title="${escapeHtml(s.document_filename)}">
            ${escapeHtml(s.document_filename)}
          </div>
          <div class="session-card-date">📅 ${date}</div>
        </div>`;
    }).join("");
  } catch (err) {
    showToast("Could not load sessions: " + err.message, "error");
  }
}

function openSession(sessionId, sessionName) {
  sessionStorage.setItem("chatpdf_session_id", sessionId);
  sessionStorage.setItem("chatpdf_session_name", sessionName);
  window.location.href = "chat.html";
}

function setupUploadZone() {
  const zone    = document.getElementById("upload-zone");
  const input   = document.getElementById("file-input");
  const wrapper = document.getElementById("progress-wrapper");
  const bar     = document.getElementById("upload-progress");
  const label   = document.getElementById("progress-label");
  if (!zone || !input) return;

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("drag-over");
  });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    if (e.dataTransfer.files[0]) handleFileUpload(e.dataTransfer.files[0], wrapper, bar, label);
  });

  input.addEventListener("change", (e) => {
    if (e.target.files[0]) handleFileUpload(e.target.files[0], wrapper, bar, label);
  });
}

async function handleFileUpload(file, wrapper, bar, label) {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Please select a PDF file.", "error");
    return;
  }

  if (wrapper) wrapper.style.display = "block";
  if (label)   label.textContent = "Uploading PDF…";

  let progress = 0;
  const interval = setInterval(() => {
    if (progress < 85) {
      progress += Math.random() * 8;
      if (bar) bar.style.width = `${Math.min(progress, 85)}%`;
    }
  }, 300);

  try {
    const formData = new FormData();
    formData.append("file", file);
    if (label) label.textContent = "Processing and embedding PDF…";

    const uploadResult = await apiUpload("/document/upload", formData);

    clearInterval(interval);
    if (bar)   bar.style.width = "90%";
    if (label) label.textContent = "Creating chat session…";

    const sessionResult = await apiRequest("/session/create", "POST", {
      document_id: uploadResult.document_id,
    });

    if (bar)   bar.style.width = "100%";
    if (label) label.textContent = "Done! Opening chat…";

    sessionStorage.setItem("chatpdf_session_id", sessionResult.session_id);
    sessionStorage.setItem("chatpdf_session_name", uploadResult.filename);

    showToast("PDF processed successfully!", "success");
    setTimeout(() => { window.location.href = "chat.html"; }, 800);
  } catch (err) {
    clearInterval(interval);
    if (wrapper) wrapper.style.display = "none";
    if (bar)     bar.style.width = "0%";
    showToast(err.message, "error");
  }
}