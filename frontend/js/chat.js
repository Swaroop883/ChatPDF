let selectedChatMode = null;

async function initChatPage() {
  const token = requireAuth();
  if (!token) return;

  const sessionId   = sessionStorage.getItem("chatpdf_session_id");
  const sessionName = sessionStorage.getItem("chatpdf_session_name");

  if (!sessionId) {
    showToast("No active session. Redirecting…", "error");
    setTimeout(() => { window.location.href = "dashboard.html"; }, 1500);
    return;
  }

  const docName = document.getElementById("chat-doc-name");
  if (docName) docName.textContent = sessionName || "Chat Session";

  const closeBtn = document.getElementById("btn-close-chat");
  if (closeBtn) closeBtn.addEventListener("click", () => closeChat(sessionId));

  const ragBtn     = document.getElementById("btn-mode-rag");
  const summaryBtn = document.getElementById("btn-mode-summary");
  const indicator  = document.getElementById("mode-indicator");

  if (ragBtn) {
    ragBtn.addEventListener("click", () => {
      selectedChatMode = "rag";
      ragBtn.classList.add("active");
      summaryBtn.classList.remove("active");
      if (indicator) {
        indicator.textContent = "🔍 Search inside PDF selected";
        indicator.style.color = "var(--accent-green)";
      }
      document.getElementById("chat-question").focus();
    });
  }

  if (summaryBtn) {
    summaryBtn.addEventListener("click", () => {
      selectedChatMode = "summary";
      summaryBtn.classList.add("active");
      ragBtn.classList.remove("active");
      if (indicator) {
        indicator.textContent = "🧠 Analytical Question selected";
        indicator.style.color = "var(--accent-amber)";
      }
      document.getElementById("chat-question").focus();
    });
  }

  const sendBtn     = document.getElementById("btn-send");
  const questionBox = document.getElementById("chat-question");

  if (sendBtn) sendBtn.addEventListener("click", () => sendChatMessage(sessionId));

  if (questionBox) {
    questionBox.addEventListener("input", () => {
      questionBox.style.height = "auto";
      questionBox.style.height = `${questionBox.scrollHeight}px`;
    });
    questionBox.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey) {
        e.preventDefault();
        sendChatMessage(sessionId);
      }
    });
  }

  await loadChatHistory(sessionId);
}

async function loadChatHistory(sessionId) {
  try {
    const data = await apiRequest(`/history/${sessionId}`);
    const messages = data.messages || [];
    if (messages.length === 0) {
      showWelcomeMessage();
      return;
    }
    messages.forEach(renderMessagePair);
    scrollToBottom();
  } catch (err) {
    showToast("Could not load history: " + err.message, "error");
    showWelcomeMessage();
  }
}

function showWelcomeMessage() {
  const area = document.getElementById("chat-messages");
  if (!area) return;
  area.innerHTML = `
    <div class="empty-state">
      <span class="empty-state-icon">💬</span>
      <h3>Start your conversation</h3>
      <p>Select a mode above, then type your question and press Enter.</p>
      <p style="margin-top:12px;font-size:0.85rem;">
        <span style="color:var(--accent-green)">🔍 Search inside PDF</span> — specific facts<br>
        <span style="color:var(--accent-amber)">🧠 Analytical Question</span> — broad analysis
      </p>
    </div>`;
}

async function sendChatMessage(sessionId) {
  const questionBox = document.getElementById("chat-question");
  const sendBtn     = document.getElementById("btn-send");
  const text        = questionBox ? questionBox.value.trim() : "";

  if (!selectedChatMode) {
    showToast("Please select a mode first.", "info");
    return;
  }
  if (!text) {
    showToast("Please type a question.", "info");
    return;
  }

  if (questionBox) { questionBox.value = ""; questionBox.style.height = "auto"; }
  if (sendBtn) sendBtn.disabled = true;

  const emptyState = document.querySelector(".empty-state");
  if (emptyState) emptyState.remove();

  renderUserQuestion(text, selectedChatMode);
  const typingId = showTypingIndicator();

  try {
    const result = await apiRequest("/chat", "POST", {
      session_id: parseInt(sessionId),
      question: text,
      mode: selectedChatMode,
    });
    removeTypingIndicator(typingId);
    renderAssistantAnswer(result);
    scrollToBottom();
  } catch (err) {
    removeTypingIndicator(typingId);
    renderErrorAnswer(err.message);
    showToast("Error: " + err.message, "error");
  } finally {
    if (sendBtn) sendBtn.disabled = false;
  }
}

function renderMessagePair({ question, answer, mode_used, source_chunk }) {
  const area = document.getElementById("chat-messages");
  if (!area) return;

  const modeLabel = mode_used === "rag" ? "🔍 Search inside PDF" : "🧠 Analytical Question";
  const modeColor = mode_used === "rag" ? "var(--accent-green)" : "var(--accent-amber)";
  const sourceHtml = source_chunk
    ? `<div class="source-chunk-wrapper">
         <button class="source-chunk-toggle" onclick="toggleSourceChunk(this)">📎 View source passage ▾</button>
         <div class="source-chunk-content">${escapeHtml(source_chunk)}</div>
       </div>`
    : `<div class="summary-note">📊 Summary mode was used</div>`;

  const el = document.createElement("div");
  el.className = "chat-message-pair";
  el.innerHTML = `
    <div class="message-question">${escapeHtml(question)}</div>
    <div class="message-mode-badge" style="color:${modeColor}">${modeLabel}</div>
    <div class="message-answer">${escapeHtml(answer)}</div>
    ${sourceHtml}`;
  area.appendChild(el);
}

function renderUserQuestion(text, mode) {
  const area = document.getElementById("chat-messages");
  if (!area) return;
  const modeLabel = mode === "rag" ? "🔍 Search inside PDF" : "🧠 Analytical Question";
  const modeColor = mode === "rag" ? "var(--accent-green)" : "var(--accent-amber)";
  const el = document.createElement("div");
  el.className = "chat-message-pair";
  el.id = "pending-question";
  el.innerHTML = `
    <div class="message-question">${escapeHtml(text)}</div>
    <div class="message-mode-badge" style="color:${modeColor}">${modeLabel}</div>`;
  area.appendChild(el);
  scrollToBottom();
}

function renderAssistantAnswer({ answer, mode_used, source_chunk }) {
  const pending = document.getElementById("pending-question");
  if (!pending) return;
  const sourceHtml = source_chunk
    ? `<div class="source-chunk-wrapper">
         <button class="source-chunk-toggle" onclick="toggleSourceChunk(this)">📎 View source passage ▾</button>
         <div class="source-chunk-content">${escapeHtml(source_chunk)}</div>
       </div>`
    : `<div class="summary-note">📊 Summary mode was used</div>`;
  const answerEl = document.createElement("div");
  answerEl.className = "message-answer";
  answerEl.textContent = answer;
  pending.appendChild(answerEl);
  pending.insertAdjacentHTML("beforeend", sourceHtml);
  pending.removeAttribute("id");
}

function renderErrorAnswer(message) {
  const pending = document.getElementById("pending-question");
  if (!pending) return;
  const el = document.createElement("div");
  el.className = "message-answer";
  el.style.cssText = "border-color:var(--accent-red);color:var(--accent-red)";
  el.textContent = `⚠️ Error: ${message}`;
  pending.appendChild(el);
  pending.removeAttribute("id");
}

function showTypingIndicator() {
  const area = document.getElementById("chat-messages");
  if (!area) return null;
  const id = `typing-${Date.now()}`;
  const el = document.createElement("div");
  el.id = id;
  el.className = "typing-indicator";
  el.innerHTML = "<span></span><span></span><span></span>";
  area.appendChild(el);
  scrollToBottom();
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function toggleSourceChunk(btn) {
  const content = btn.nextElementSibling;
  const isOpen = content.classList.contains("open");
  content.classList.toggle("open", !isOpen);
  btn.textContent = isOpen ? "📎 View source passage ▾" : "📎 Hide source passage ▴";
}

async function closeChat(sessionId) {
  try {
    await apiRequest(`/session/close/${sessionId}`, "DELETE");
    showToast("Chat closed.", "success");
  } catch (err){
    console.log(err);
    showToast("Unable to notify server. Returning to dashboard.", "info");
  }
  sessionStorage.removeItem("chatpdf_session_id");
  sessionStorage.removeItem("chatpdf_session_name");
  window.location.href = "dashboard.html";
}