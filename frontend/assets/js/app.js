/* ============================================
   ComplaintCare - app.js (Common / Shared)
============================================ */

// ---------- Storage Keys ----------
const USERS_KEY = "cms_users";
const SESSION_KEY = "cms_currentUser";
const TICKETS_KEY = "cms_tickets";
const NOTIFS_KEY = "cms_notifications";

// ---------- Helpers ----------
function getUsers() {
  return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
}
function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}
function getCurrentUser() {
  return JSON.parse(localStorage.getItem(SESSION_KEY));
}
function getTickets() {
  return JSON.parse(localStorage.getItem(TICKETS_KEY)) || [];
}
function saveTickets(tickets) {
  localStorage.setItem(TICKETS_KEY, JSON.stringify(tickets));
}
function getNotifications() {
  return JSON.parse(localStorage.getItem(NOTIFS_KEY)) || [];
}
function saveNotifications(notifs) {
  localStorage.setItem(NOTIFS_KEY, JSON.stringify(notifs));
}

// ---------- Seed Demo Tickets (first time only) ----------
function seedTickets() {
  if (localStorage.getItem(TICKETS_KEY)) return;
  const demoTickets = [
    {
      id: 1001,
      subject: "Internet not working since morning",
      description: "My broadband connection has been down since 8 AM. I have tried restarting the router multiple times.",
      category: "Technical",
      priority: "High",
      status: "In Progress",
      assignedTo: "Network Team",
      createdAt: new Date(Date.now() - 86400000).toISOString(),
      updatedAt: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: 1002,
      subject: "Wrong amount in billing",
      description: "I was charged ₹500 extra in my last bill. Please check and correct it.",
      category: "Billing",
      priority: "Medium",
      status: "Under Review",
      assignedTo: "Billing Team",
      createdAt: new Date(Date.now() - 172800000).toISOString(),
      updatedAt: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      id: 1003,
      subject: "Request for plan upgrade",
      description: "I want to upgrade my current 4G plan to 5G unlimited plan.",
      category: "Service",
      priority: "Low",
      status: "Resolved",
      assignedTo: "Customer Support",
      createdAt: new Date(Date.now() - 259200000).toISOString(),
      updatedAt: new Date(Date.now() - 172800000).toISOString(),
    },
  ];
  saveTickets(demoTickets);
}
seedTickets();

// ---------- Auth Guard (call at top of dashboard pages) ----------
function checkAuth() {
  const user = getCurrentUser();
  if (!user) {
    window.location.href = "login.html";
    return null;
  }
  return user;
}

// ---------- Logout ----------
function logout() {
  if (confirm("Kya aap logout karna chahte hain?")) {
    localStorage.removeItem(SESSION_KEY);
    window.location.href = "../index.html";
  }
}

// ---------- Format Date ----------
function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ---------- Priority Badge Class ----------
function priorityClass(p) {
  const map = {
    Urgent: "badge-urgent",
    High: "badge-high",
    Medium: "badge-medium",
    Low: "badge-low",
  };
  return map[p] || "badge-low";
}

// ---------- Status Badge Class ----------
function statusClass(s) {
  const map = {
    "Registered": "badge-registered",
    "In Progress": "badge-progress",
    "Under Review": "badge-review",
    "Resolved": "badge-resolved",
    "Escalated": "badge-escalated",
  };
  return map[s] || "badge-registered";
}

// ---------- Category Icon ----------
function categoryIcon(cat) {
  const map = {
    Technical: "🔧",
    Billing: "💳",
    Service: "📞",
    General: "📋",
  };
  return map[cat] || "📋";
}