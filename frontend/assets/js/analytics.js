/* ============================================
   ComplaintCare - analytics.js
============================================ */

function countByField(tickets, field) {
  return tickets.reduce((result, ticket) => {
    const value = ticket[field] || "Unknown";
    result[value] = (result[value] || 0) + 1;
    return result;
  }, {});
}

function calculateAnalytics() {
  const tickets = getTickets();

  const resolved = tickets.filter(t => t.status === "Resolved");

  const resolutionHours = resolved.map(ticket => {
    const created = new Date(ticket.createdAt);
    const updated = new Date(ticket.updatedAt);
    const hours = (updated - created) / (1000 * 60 * 60);
    return Math.max(hours, 0);
  });

  const averageResolution = resolutionHours.length
    ? resolutionHours.reduce((sum, value) => sum + value, 0) / resolutionHours.length
    : 0;

  return {
    total: tickets.length,
    resolved: resolved.length,
    open: tickets.filter(t => t.status !== "Resolved").length,
    categories: countByField(tickets, "category"),
    priorities: countByField(tickets, "priority"),
    statuses: countByField(tickets, "status"),
    averageResolution: averageResolution.toFixed(1)
  };
}