function adminGuard() {
  const user = getCurrentUser();
  if (!user) { window.location.href = "login.html"; return null; }
  if (user.role !== "admin") { alert("Admin only"); window.location.href = "user-dashboard.html"; return null; }
  return user;
}

function getAllTickets() {
  // All tickets including dataset + user created
  return getTickets().sort((a,b) => {
    const p = {Urgent:1, High:2, Medium:3, Low:4};
    return (p[a.priority]||5) - (p[b.priority]||5);
  });
}

function updateTicket(ticketId, newStatus, newAgent) {
  const tickets = getTickets();
  const idx = tickets.findIndex(t => Number(t.id) === Number(ticketId));
  if (idx === -1) return null;

  const oldStatus = tickets[idx].status;
  tickets[idx].status = newStatus;
  tickets[idx].assignedTo = newAgent || tickets[idx].assignedTo;
  tickets[idx].updatedAt = new Date().toISOString();

  saveTickets(tickets); // ✅ REAL-TIME SAVE

  // Add admin notification
  const notifications = getNotifications();
  notifications.unshift({
    id: Date.now(),
    userId: tickets[idx].userId || 0,
    ticketId: tickets[idx].id,
    title: "Ticket #" + tickets[idx].id + " Updated (Admin)",
    message: "Status changed: " + oldStatus + " → " + newStatus + ". Team: " + (newAgent || tickets[idx].assignedTo),
    type: "ticket-update",
    read: false,
    createdAt: new Date().toISOString()
  });
  saveNotifications(notifications);

  return tickets[idx];
}

function addNotificationForTicket(ticket, title, message) {
  const notifications = getNotifications();
  notifications.unshift({
    id: Date.now(),
    userId: ticket.userId || 0,
    ticketId: ticket.id,
    title: title,
    message: message,
    type: "ticket-created",
    read: false,
    createdAt: new Date().toISOString()
  });
  saveNotifications(notifications);
}