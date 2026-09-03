/* ============================================
   ComplaintCare - auth.js
   Register / Login / Logout (localStorage)
============================================ */

// ---------- Storage Keys ----------
const USERS_KEY = "cms_users";
const SESSION_KEY = "cms_currentUser";

// ---------- Helpers ----------
function getUsers() {
  return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function showMessage(boxId, text, type) {
  const box = document.getElementById(boxId);
  box.textContent = text;
  box.className = "message " + type; // "error" ya "success"
}

// ---------- Default Admin Seed (auto ek baar banta hai) ----------
(function seedAdmin() {
  const users = getUsers();
  if (!users.some((u) => u.email === "admin@cms.com")) {
    users.push({
      id: 1,
      name: "Admin",
      email: "admin@cms.com",
      phone: "0000000000",
      password: "admin123",
      role: "admin",
      createdAt: new Date().toISOString(),
    });
    saveUsers(users);
  }
})();

// ---------- REGISTER ----------
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const name = document.getElementById("regName").value.trim();
    const email = document.getElementById("regEmail").value.trim().toLowerCase();
    const phone = document.getElementById("regPhone").value.trim();
    const password = document.getElementById("regPassword").value;
    const confirm = document.getElementById("regConfirm").value;

    // ---- Validations ----
    if (name.length < 3)
      return showMessage("reg-message", "Name kam se kam 3 letters ka hona chahiye ❌", "error");
    if (!/^\S+@\S+\.\S+$/.test(email))
      return showMessage("reg-message", "Valid email daalo ❌", "error");
    if (!/^\d{10}$/.test(phone))
      return showMessage("reg-message", "Phone exactly 10 digits ka hona chahiye ❌", "error");
    if (password.length < 6)
      return showMessage("reg-message", "Password kam se kam 6 characters ka ❌", "error");
    if (password !== confirm)
      return showMessage("reg-message", "Passwords match nahi kar rahe ❌", "error");

    const users = getUsers();
    if (users.some((u) => u.email === email))
      return showMessage("reg-message", "Ye email already registered hai! Login karo ❌", "error");

    // ---- New User Save ----
    const newUser = {
      id: users.length ? users[users.length - 1].id + 1 : 2,
      name: name,
      email: email,
      phone: phone,
      password: password,
      role: "user",
      createdAt: new Date().toISOString(),
    };

    users.push(newUser);
    saveUsers(users);
    localStorage.setItem(SESSION_KEY, JSON.stringify(newUser)); // auto login

    showMessage("reg-message", "Account ban gaya! Redirect ho raha hai... ✅", "success");
    setTimeout(() => (window.location.href = "user-dashboard.html"), 1200);
  });
}

// ---------- LOGIN ----------
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value.trim().toLowerCase();
    const password = document.getElementById("loginPassword").value;

    if (password.length < 8) {
      return showMessage(
        "login-message",
        "Password must be at least 8 characters.",
        "error"
      );
    }

    try {
      const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      saveAuthTokens(data);

      const profile = await apiRequest("/auth/profile");

      localStorage.setItem(SESSION_KEY, JSON.stringify(profile));

      showMessage(
        "login-message",
        "Login successful! Redirecting...",
        "success"
      );

      setTimeout(() => {
        window.location.href =
          profile.role === "admin"
            ? "admin-dashboard.html"
            : "user-dashboard.html";
      }, 1200);
    } catch (error) {
      showMessage(
        "login-message",
        error.message || "Login failed. Please try again.",
        "error"
      );
    }
  });
}
// ---------- LOGOUT (dashboard pages me use hoga) ----------
function logout() {
  localStorage.removeItem(SESSION_KEY);
  window.location.href = "../index.html";
}

// ---------- Page Protect (dashboard pages me call karenge) ----------
function checkAuth() {
  const user = JSON.parse(localStorage.getItem(SESSION_KEY));
  if (!user) window.location.href = "login.html";
  return user;
}