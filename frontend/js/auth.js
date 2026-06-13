function initAuthPage() {
  const params = new URLSearchParams(window.location.search);
  const tokenFromUrl = params.get("token");
  const usernameFromUrl = params.get("username");

  if (tokenFromUrl) {
    saveAuthData(tokenFromUrl, usernameFromUrl || "User");
    window.location.href = "dashboard.html";
    return;
  }

  if (getAuthToken()) {
    window.location.href = "dashboard.html";
    return;
  }

  const loginTab     = document.getElementById("tab-login");
  const registerTab  = document.getElementById("tab-register");
  const loginForm    = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  loginTab.addEventListener("click", () => {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");
    loginForm.style.display = "block";
    registerForm.style.display = "none";
  });

  registerTab.addEventListener("click", () => {
    registerTab.classList.add("active");
    loginTab.classList.remove("active");
    registerForm.style.display = "block";
    loginForm.style.display = "none";
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email    = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const btn      = document.getElementById("login-submit");
    btn.disabled = true;
    btn.textContent = "Signing in…";
    try {
      const data = await apiRequest("/auth/login", "POST", { email, password });
      saveAuthData(data.access_token, data.username);
      showToast("Welcome back!", "success");
      setTimeout(() => { window.location.href = "dashboard.html"; }, 500);
    } catch (err) {
      showToast(err.message, "error");
      btn.disabled = false;
      btn.textContent = "Sign In";
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("reg-username").value.trim();
    const email    = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const btn      = document.getElementById("register-submit");

    if (password.length < 8) {
      showToast("Password must be at least 8 characters.", "error");
      return;
    }
    btn.disabled = true;
    btn.textContent = "Creating account…";
    try {
      await apiRequest("/auth/register", "POST", { username, email, password });
      showToast("Account created! Please sign in.", "success");
      loginTab.click();
      document.getElementById("login-email").value = email;
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Create Account";
    }
  });

  const googleBtn = document.getElementById("btn-google");
  if (googleBtn) {
    googleBtn.addEventListener("click", () => {
      window.location.href = `${API_BASE}/auth/google`;
    });
  }
}