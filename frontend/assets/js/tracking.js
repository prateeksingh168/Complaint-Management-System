/* ============================================
   ComplaintCare - Ticket Tracking
   Backend / PostgreSQL Integration
============================================ */

const TRACKING_API_BASE_URL = "http://127.0.0.1:8000/api/v1";


/* ============================================
   API REQUEST
============================================ */

async function trackingApiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("cms_access_token");

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers.Authorization = "Bearer " + token;
    }

    const response = await fetch(
        TRACKING_API_BASE_URL + endpoint,
        {
            ...options,
            headers
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Unable to fetch ticket data"
        );
    }

    return data;
}


/* ============================================
   LOAD USER TICKETS
============================================ */

async function loadUserTickets() {

    const ticketContainer =
        document.querySelector(".ticket-list") ||
        document.querySelector("#ticket-list");

    if (!ticketContainer) {
        console.warn("Ticket list container not found.");
        return;
    }

    ticketContainer.innerHTML =
        "<p>Loading tickets...</p>";

    try {

        const data =
            await trackingApiRequest(
                "/tickets?page=1&page_size=100"
            );

        const tickets =
            data.items || [];

        if (!tickets.length) {

            ticketContainer.innerHTML =
                "<p>No tickets found.</p>";

            return;
        }

        renderTicketList(
            tickets,
            ticketContainer
        );

    } catch (error) {

        console.error(
            "Ticket loading error:",
            error
        );

        ticketContainer.innerHTML =
            "<p>Unable to load tickets. Please login again.</p>";
    }
}


/* ============================================
   RENDER TICKET LIST
============================================ */

function renderTicketList(
    tickets,
    container
) {

    container.innerHTML = "";

    tickets.forEach(ticket => {

        const item =
            document.createElement("div");

        item.className =
            "ticket-item";

        item.innerHTML = `
            <div>
                <strong>
                    ${escapeHtml(ticket.ticket_number || "N/A")}
                </strong>
                <div>
                    ${escapeHtml(ticket.category || "General")}
                </div>
            </div>

            <div>
                <span>
                    ${escapeHtml(ticket.status || "Registered")}
                </span>
            </div>
        `;

        item.style.cursor = "pointer";

        item.addEventListener(
            "click",
            () => showTicketDetails(ticket)
        );

        container.appendChild(item);
    });
}


/* ============================================
   SHOW TICKET DETAILS
============================================ */

function showTicketDetails(ticket) {

    const detailsContainer =
        document.querySelector(".ticket-details") ||
        document.querySelector("#ticket-details");

    if (!detailsContainer) {
        console.warn(
            "Ticket details container not found."
        );
        return;
    }

    detailsContainer.innerHTML = `
        <h3>Ticket Details</h3>

        <div class="ticket-detail-row">
            <strong>Ticket:</strong>
            <span>
                ${escapeHtml(ticket.ticket_number || "N/A")}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Complaint:</strong>
            <span>
                ${escapeHtml(ticket.complaint_id || "N/A")}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Category:</strong>
            <span>
                ${escapeHtml(ticket.category || "N/A")}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Priority:</strong>
            <span>
                ${escapeHtml(ticket.priority || "N/A")}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Status:</strong>
            <span>
                ${escapeHtml(ticket.status || "Registered")}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Assigned Team ID:</strong>
            <span>
                ${ticket.assigned_team_id ?? "Not assigned"}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Assigned Agent ID:</strong>
            <span>
                ${ticket.assigned_agent_id ?? "Not assigned"}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Created:</strong>
            <span>
                ${formatDate(ticket.created_at)}
            </span>
        </div>

        <div class="ticket-detail-row">
            <strong>Updated:</strong>
            <span>
                ${formatDate(ticket.updated_at)}
            </span>
        </div>

        ${ticket.history && ticket.history.length
            ? renderHistory(ticket.history)
            : ""
        }
    `;
}


/* ============================================
   SEARCH TICKET
============================================ */

async function trackTicket() {

    const input =
        document.querySelector(
            'input[placeholder*="Ticket ID"]'
        );

    if (!input) {
        console.warn(
            "Ticket ID input not found."
        );
        return;
    }

    const ticketId =
        input.value.trim();

    if (!ticketId) {

        alert(
            "Please enter a Ticket ID."
        );

        return;
    }

    try {

        const numericId =
            ticketId.replace(/\D/g, "");

        let endpoint;

        /*
         * Backend endpoint expects database ticket ID.
         * If user enters TKT-10010, extract 10010.
         */

        endpoint =
            "/tickets/" + numericId;

        const ticket =
            await trackingApiRequest(
                endpoint
            );

        showTicketDetails(ticket);

    } catch (error) {

        console.error(
            "Ticket tracking error:",
            error
        );

        const detailsContainer =
            document.querySelector(".ticket-details") ||
            document.querySelector("#ticket-details");

        if (detailsContainer) {

            detailsContainer.innerHTML = `
                <h3>Ticket Details</h3>
                <p>
                    ❌ Ticket not found or you do not
                    have permission to view it.
                </p>
            `;
        }
    }
}


/* ============================================
   TICKET HISTORY
============================================ */

function renderHistory(history) {

    let html = `
        <div class="ticket-history">
            <h4>Ticket Timeline</h4>
    `;

    history.forEach(item => {

        html += `
            <div class="history-item">
                <strong>
                    ${escapeHtml(item.new_status || "Updated")}
                </strong>

                ${item.old_status
                ? `
                            <span>
                                ${escapeHtml(item.old_status)}
                                →
                                ${escapeHtml(item.new_status)}
                            </span>
                          `
                : ""
            }

                <small>
                    ${formatDate(item.changed_at)}
                </small>
            </div>
        `;
    });

    html += "</div>";

    return html;
}


/* ============================================
   HELPERS
============================================ */

function formatDate(value) {

    if (!value) {
        return "N/A";
    }

    try {

        return new Date(value)
            .toLocaleString();

    } catch {

        return value;
    }
}


function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ============================================
   INITIALIZE
============================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadUserTickets();

        const buttons =
            document.querySelectorAll("button");

        buttons.forEach(button => {

            const text =
                button.textContent
                    .trim()
                    .toLowerCase();

            if (text === "track") {

                button.addEventListener(
                    "click",
                    trackTicket
                );
            }
        });

        const input =
            document.querySelector(
                'input[placeholder*="Ticket ID"]'
            );

        if (input) {

            input.addEventListener(
                "keydown",
                event => {

                    if (event.key === "Enter") {
                        trackTicket();
                    }

                }
            );
        }
    }
);