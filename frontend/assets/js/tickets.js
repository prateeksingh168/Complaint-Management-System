/* ============================================
   ComplaintCare - tickets.js
   Ticket create / search / notify
============================================ */

function getNextTicketId() {
  const tickets = getTickets();
  if (!tickets.length) return 1001;
  return Math.max(...tickets.map((t) => Number(t.id) || 0)) + 1;
}

function addNotificationForTicket(ticket, title, message, type) {
  const notifications = getNotifications();
  notifications.unshift({
    id: Date.now(),
    userId: ticket.userId || 0,
    ticketId: ticket.id,
    title: title,
    message: message,
    type: type || "info",
    read: false,
    createdAt: new Date().toISOString(),
  });
  saveNotifications(notifications);
}

function addTicket(data) {
  const user = getCurrentUser();
  const tickets = getTickets();

  const newTicket = {
    id: getNextTicketId(),
    userId: user ? user.id : 0,
    userName: user ? user.name : "Guest",
    userEmail: user ? user.email : "guest@cms.com",
    subject: data.subject,
    description: data.description,
    category: data.category || "General",
    priority: data.priority || "Medium",
    status: "Registered",
    assignedTo: data.assignedTo || "Customer Support",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    source: data.source || "Manual Form",
  };

  tickets.unshift(newTicket);
  saveTickets(tickets);

  addNotificationForTicket(
    newTicket,
    "Ticket #" + newTicket.id + " Created",
    "Your " + newTicket.priority + " priority " + newTicket.category +
      " complaint has been assigned to " + newTicket.assignedTo + ".",
    "ticket-created"
  );

  return newTicket;
}

function getTicketById(id) {
  const num = Number(String(id).replace("#", "").trim());
  return getTickets().find((t) => Number(t.id) === num) || null;
}

function getMyTickets() {
  const user = getCurrentUser();
  const tickets = getTickets();
  if (!user) return tickets;

  const mine = tickets.filter(
    (t) => t.userId === user.id || t.userEmail === user.email
  );

  // Demo tickets (bina userId) bhi dikhao taaki project me data dikhe
  const demo = tickets.filter((t) => !t.userId && !t.userEmail);
  const combined = [...mine, ...demo];

  const seen = {};
  return combined.filter((t) => {
    if (seen[t.id]) return false;
    seen[t.id] = true;
    return true;
  });
}

function statusStep(status) {
  const order = ["Registered", "In Progress", "Under Review", "Resolved"];
  const i = order.indexOf(status);
  return i === -1 ? 0 : i;
}