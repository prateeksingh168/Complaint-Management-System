// ============================================================
// ADMIN DASHBOARD - BACKEND INTEGRATION
// ============================================================

function adminGuard() {
  const user = getCurrentUser();

  if (!user) {
    window.location.href = "login.html";
    return null;
  }

  if (user.role !== "admin") {
    alert("Admin only");
    window.location.href = "user-dashboard.html";
    return null;
  }

  return user;
}


// ============================================================
// TEAM CONFIGURATION
// Backend database team IDs
// ============================================================

const ADMIN_TEAMS = {
  1: "General Support",
  2: "Technical Support",
  3: "Delivery Support",
  4: "Billing Support",
  5: "Service Support",
  6: "Account Support"
};


// ============================================================
// LOAD ADMIN TICKETS
// ============================================================

async function getAllTickets() {
  try {
    const data = await apiRequest(
      "/admin/tickets?page=1&page_size=100"
    );

    return data.items || [];
  } catch (error) {
    console.error("Failed to load admin tickets:", error);
    showAdminMessage(
      error.message || "Failed to load tickets",
      "error"
    );
    return [];
  }
}


// ============================================================
// LOAD ADMIN ANALYTICS
// ============================================================

async function getAdminAnalytics() {
  try {
    return await apiRequest("/admin/analytics");
  } catch (error) {
    console.error("Failed to load analytics:", error);
    return null;
  }
}


// ============================================================
// LOAD ADMIN AGENTS
// ============================================================

async function getAdminAgents() {
  try {
    return await apiRequest("/admin/agents");
  } catch (error) {
    console.error("Failed to load agents:", error);
    return [];
  }
}


// ============================================================
// UPDATE TICKET STATUS
// ============================================================

async function updateTicket(ticketId, newStatus, newTeamId = null) {
  try {

    // --------------------------------------------------------
    // 1. Update status
    // --------------------------------------------------------

    const statusData = {
      status: newStatus,
      note: "Updated by administrator"
    };

    const updatedTicket = await apiRequest(
      `/tickets/${ticketId}/status`,
      {
        method: "PUT",
        body: JSON.stringify(statusData)
      }
    );


    // --------------------------------------------------------
    // 2. Assign team if selected
    // --------------------------------------------------------

    if (newTeamId) {

      await apiRequest(
        `/admin/tickets/${ticketId}/assign`,
        {
          method: "PUT",
          body: JSON.stringify({
            team_id: Number(newTeamId)
          })
        }
      );
    }


    return updatedTicket;

  } catch (error) {

    console.error("Failed to update ticket:", error);

    showAdminMessage(
      error.message || "Failed to update ticket",
      "error"
    );

    return null;
  }
}


// ============================================================
// SHOW ADMIN MESSAGE
// ============================================================

function showAdminMessage(message, type = "success") {

  let box = document.getElementById("admin-message");

  if (!box) {

    box = document.createElement("div");

    box.id = "admin-message";

    box.style.position = "fixed";
    box.style.top = "20px";
    box.style.right = "20px";
    box.style.zIndex = "9999";
    box.style.padding = "14px 20px";
    box.style.borderRadius = "8px";
    box.style.fontWeight = "600";
    box.style.maxWidth = "400px";
    box.style.boxShadow = "0 5px 20px rgba(0,0,0,0.15)";

    document.body.appendChild(box);
  }

  if (type === "error") {
    box.style.background = "#fee2e2";
    box.style.color = "#991b1b";
    box.style.border = "1px solid #fecaca";
  } else {
    box.style.background = "#dcfce7";
    box.style.color = "#166534";
    box.style.border = "1px solid #bbf7d0";
  }

  box.textContent = message;
  box.style.display = "block";

  setTimeout(() => {
    box.style.display = "none";
  }, 3000);
}


// ============================================================
// FORMAT DATE
// ============================================================

function formatAdminDate(dateString) {

  if (!dateString) {
    return "-";
  }

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return dateString;
  }

  return date.toLocaleString();
}


// ============================================================
// STATUS BADGE
// ============================================================

function getStatusBadge(status) {

  const safeStatus = status || "Unknown";

  return `
    <span class="status-badge">
      ${safeStatus}
    </span>
  `;
}


// ============================================================
// PRIORITY BADGE
// ============================================================

function getPriorityBadge(priority) {

  const safePriority = priority || "Medium";

  return `
    <span class="priority-badge priority-${safePriority.toLowerCase()}">
      ${safePriority}
    </span>
  `;
}


// ============================================================
// GET TEAM NAME
// ============================================================

function getTeamName(teamId) {

  if (!teamId) {
    return "Unassigned";
  }

  return ADMIN_TEAMS[teamId] || `Team #${teamId}`;
}


// ============================================================
// EXPORT
// ============================================================

window.adminGuard = adminGuard;
window.getAllTickets = getAllTickets;
window.getAdminAnalytics = getAdminAnalytics;
window.getAdminAgents = getAdminAgents;
window.updateTicket = updateTicket;
window.showAdminMessage = showAdminMessage;
window.formatAdminDate = formatAdminDate;
window.getStatusBadge = getStatusBadge;
window.getPriorityBadge = getPriorityBadge;
window.getTeamName = getTeamName;
window.ADMIN_TEAMS = ADMIN_TEAMS;