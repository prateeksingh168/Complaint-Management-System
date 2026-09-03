/* ============================================
   ComplaintCare AI
   Understands input (any language) → English reply
============================================ */

let pendingTicket = null;

const CHATBOT_API_BASE_URL = "http://127.0.0.1:8000/api/v1";


/* ============================================
   BACKEND API HELPER
============================================ */

async function chatbotApiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("cms_access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = "Bearer " + token;
  }

  const response = await fetch(
    CHATBOT_API_BASE_URL + endpoint,
    {
      ...options,
      headers
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "API request failed");
  }

  return data;
}


/* ============================================
   CHAT WINDOW
============================================ */

function toggleChat() {
  document
    .getElementById("chatbot-window")
    .classList.toggle("open");

  if (
    document
      .getElementById("chatbot-window")
      .classList
      .contains("open")
  ) {
    setTimeout(() => {
      document
        .getElementById("chat-input")
        .focus();
    }, 100);
  }
}


/* ============================================
   MESSAGE HELPERS
============================================ */

function addBotMessage(html) {
  const body = document.getElementById("chat-body");

  const div = document.createElement("div");

  div.className = "chat-msg bot";

  div.innerHTML = html;

  body.appendChild(div);

  body.scrollTop = body.scrollHeight;
}


function addUserMessage(text) {
  const body = document.getElementById("chat-body");

  const div = document.createElement("div");

  div.className = "chat-msg user";

  div.textContent = text;

  body.appendChild(div);

  body.scrollTop = body.scrollHeight;
}


/* ============================================
   LOCAL SMART ANALYSIS
   Kept for compatibility with existing project
============================================ */

function smartAnalyze(inputText) {

  const low = inputText.toLowerCase();

  const tech = [
    "internet",
    "wifi",
    "wi-fi",
    "broadband",
    "network",
    "connection",
    "down",
    "not working",
    "slow",
    "speed",
    "outage",
    "error",
    "login",
    "website",
    "server",
    "router",
    "technical",
    "issue"
  ];

  const bill = [
    "bill",
    "billing",
    "charge",
    "payment",
    "refund",
    "money",
    "amount",
    "invoice",
    "extra",
    "wrong",
    "paid"
  ];

  const svc = [
    "plan",
    "upgrade",
    "service",
    "sim",
    "activation",
    "request",
    "new connection",
    "installation"
  ];

  let cat = "General";

  let pri = "Medium";

  let team = "Customer Support";


  if (tech.some(w => low.includes(w))) {

    cat = "Technical";

    team = "Network & Technical Team";

  }

  else if (bill.some(w => low.includes(w))) {

    cat = "Billing";

    team = "Billing & Payments Team";

  }

  else if (svc.some(w => low.includes(w))) {

    cat = "Service";

    team = "Customer Service Team";

  }


  if (
    [
      "urgent",
      "emergency",
      "critical",
      "fraud",
      "hacked",
      "stolen",
      "business loss",
      "asap"
    ].some(w => low.includes(w))
  ) {

    pri = "Urgent";

  }

  else if (
    [
      "not working",
      "down",
      "outage",
      "failed",
      "important",
      "delayed",
      "wrong charge",
      "extra charge",
      "no response"
    ].some(w => low.includes(w))
  ) {

    pri = "High";

  }

  else if (
    [
      "suggestion",
      "feedback",
      "query",
      "information",
      "please explain"
    ].some(w => low.includes(w))
  ) {

    pri = "Low";

  }


  return {
    category: cat,
    priority: pri,
    assignedTo: team
  };
}


/* ============================================
   QUICK ADVICE
============================================ */

function quickAdvice(inputText) {

  const t = inputText.toLowerCase();


  if (
    (
      t.includes("internet") ||
      t.includes("wifi") ||
      t.includes("network")
    ) &&
    !t.includes("bill") &&
    !t.includes("charge")
  ) {

    return {
      found: true,
      reply:
        "Quick Fix: Restart router, disconnect WiFi, reconnect, wait 2 minutes. " +
        "If still down, reply <b>YES</b> to create a <b>High Priority Technical</b> ticket."
    };

  }


  if (
    t.includes("bill") ||
    t.includes("charge") ||
    t.includes("refund") ||
    t.includes("payment") ||
    t.includes("invoice")
  ) {

    return {
      found: true,
      reply:
        "Billing issue detected. Check invoice details. " +
        "Reply <b>YES</b> to create a <b>Billing</b> complaint with correct priority."
    };

  }


  if (
    t.includes("plan") ||
    t.includes("upgrade") ||
    t.includes("service") ||
    t.includes("sim") ||
    t.includes("activation")
  ) {

    return {
      found: true,
      reply:
        "Service request noted. Specify your need. " +
        "Reply <b>YES</b> to create a <b>Service</b> ticket."
    };

  }


  if (
    t.includes("urgent") ||
    t.includes("emergency") ||
    t.includes("critical") ||
    t.includes("fraud") ||
    t.includes("hack") ||
    t.includes("stolen")
  ) {

    return {
      found: true,
      reply:
        "Critical issue detected. This will receive <b>URGENT</b> priority. " +
        "Confirm with <b>YES</b>."
    };

  }


  return {
    found: false,
    reply: ""
  };
}


/* ============================================
   OLD LOCAL TICKET FUNCTION
   Kept for compatibility.
   NOT USED by YES confirmation.
============================================ */

function createRealTicket(complaintText, analysis) {

  const user = getCurrentUser();

  const tickets = getTickets();

  let maxId = 1000;


  tickets.forEach(x => {

    const clean = String(x.id).replace(/\D/g, "");

    const num = parseInt(clean, 10);

    if (!isNaN(num) && num > maxId) {
      maxId = num;
    }

  });


  const ticket = {

    id: maxId + 1,

    userId: user ? user.id : 0,

    userEmail: user
      ? user.email
      : "guest@test.com",

    userName: user
      ? user.name
      : "Guest User",

    subject:
      complaintText.length > 60
        ? complaintText.substring(0, 60) + "..."
        : complaintText,

    description: complaintText,

    category: analysis.category,

    priority: analysis.priority,

    status: "Registered",

    assignedTo: analysis.assignedTo,

    createdAt: new Date().toISOString(),

    updatedAt: new Date().toISOString(),

    source: "AI Chatbot"

  };


  tickets.unshift(ticket);

  saveTickets(tickets);


  const notifications = getNotifications();


  notifications.unshift({

    id: Date.now(),

    userId: user ? user.id : 0,

    ticketId: ticket.id,

    title:
      "Ticket #" + ticket.id + " Created",

    message:
      "Category: " +
      ticket.category +
      " | Priority: " +
      ticket.priority +
      " | Team: " +
      ticket.assignedTo,

    type: "ticket-created",

    read: false,

    createdAt: new Date().toISOString()

  });


  saveNotifications(notifications);


  if (
    typeof updateNotificationCount === "function"
  ) {
    updateNotificationCount();
  }


  return ticket;
}


/* ============================================
   MAIN SEND MESSAGE
============================================ */

async function sendMsg() {

  const input =
    document.getElementById("chat-input");

  const text =
    input.value.trim();


  if (!text) {
    return;
  }


  addUserMessage(text);

  input.value = "";


  const lower =
    text.toLowerCase();

  const words =
    lower.split(" ");


  /* ============================================
     GREETING
  ============================================ */

  if (
    [
      "hi",
      "hello",
      "hey",
      "hii",
      "namaste",
      "good morning",
      "good evening",
      "good afternoon",
      "hello there"
    ].some(
      w => words.some(x => x.includes(w))
    )
  ) {

    setTimeout(() => {

      addBotMessage(
        "👋 <b>Hello! I'm ComplaintCare AI Assistant.</b><br>" +
        "I help with complaints, tracking, and explain both user and admin functions. " +
        "Describe your issue clearly in any language — I'll reply in English."
      );

    }, 300);

    return;
  }


  /* ============================================
     HOW TO FILE COMPLAINT
  ============================================ */

  if (
    lower.includes("how to file") ||
    lower.includes("how to make") ||
    lower.includes("how to complain") ||
    lower.includes("how to create") ||
    lower.includes("process") ||
    (
      lower.includes("how") &&
      (
        lower.includes("complaint") ||
        lower.includes("ticket")
      )
    )
  ) {

    setTimeout(() => {

      addBotMessage(
        "📋 <b>How to File a Complaint:</b><br>" +
        "1. Describe your issue clearly.<br>" +
        "2. Confirm with <b>YES</b>.<br>" +
        "3. Receive a <b>Ticket ID</b> instantly.<br>" +
        "4. Track anytime via <b>Track Ticket</b>.<br>" +
        "5. Admin updates reflect in real-time for both sides."
      );

    }, 300);

    return;
  }


  /* ============================================
     ADMIN FUNCTIONS
  ============================================ */

  if (
    lower.includes("admin") ||
    lower.includes("administrator") ||
    lower.includes("admin side") ||
    lower.includes("admin work") ||
    (
      lower.includes("what") &&
      lower.includes("admin")
    )
  ) {

    setTimeout(() => {

      addBotMessage(
        "🛠️ <b>Admin Functions:</b><br>" +
        "• View all tickets in real-time.<br>" +
        "• Filter by Category, Priority, Status.<br>" +
        "• Assign team and update status.<br>" +
        "• Save changes instantly.<br>" +
        "• Both user and admin see updates immediately."
      );

    }, 300);

    return;
  }


  /* ============================================
     TRACKING
  ============================================ */

  if (
    lower.includes("track") ||
    lower.includes("tracking") ||
    lower.includes("where is") ||
    lower.includes("check status") ||
    lower.includes("find my") ||
    lower.includes("ticket status") ||
    lower.includes("status check")
  ) {

    setTimeout(() => {

      addBotMessage(
        "📍 <b>Tracking Process:</b><br>" +
        "Go to <b>Track Ticket</b> page → Enter Ticket ID or select from list → " +
        "View timeline: Registered → In Progress → Under Review → Resolved. " +
        "Admin updates reflect instantly."
      );

    }, 300);

    return;
  }


  /* ============================================
     DATASET
  ============================================ */

  if (
    lower.includes("dataset") ||
    (
      lower.includes("csv") &&
      lower.includes("data")
    )
  ) {

    setTimeout(() => {

      addBotMessage(
        "📊 The system loads complaint data from the dataset file. " +
        "Once loaded, all tickets are stored locally and visible to the admin in real-time."
      );

    }, 300);

    return;
  }


  /* ============================================
     CONFIRM YES
     IMPORTANT:
     Backend has already created the real ticket
     during the /chat request.
  ============================================ */

  if (
    pendingTicket &&
    [
      "yes",
      "haan",
      "ok",
      "confirm",
      "create",
      "ticket bana",
      "ticket banao",
      "sahi",
      "correct",
      "right"
    ].some(
      w => lower.includes(w)
    )
  ) {

    const ticket =
      pendingTicket.ticket;


    pendingTicket = null;


    setTimeout(() => {

      addBotMessage(

        "✅ <b>Complaint Registered Successfully!</b><br><br>" +

        "🎫 <b>Ticket:</b> " +
        (ticket.ticket_number || "N/A") +
        "<br>" +

        "📂 <b>Category:</b> " +
        (ticket.category || "N/A") +
        "<br>" +

        "⚡ <b>Priority:</b> " +
        (ticket.priority || "N/A") +
        "<br>" +

        "🧩 <b>Complexity:</b> " +
        (ticket.complexity || "N/A") +
        "<br>" +

        "👥 <b>Recommended Team:</b> " +
        (ticket.recommended_team || "N/A") +
        "<br>" +

        "📌 <b>Status:</b> " +
        (ticket.status || "Registered") +

        "<br><br>" +

        "You can track your ticket from the <b>Track Ticket</b> page."

      );

    }, 400);


    return;
  }


  /* ============================================
     CANCEL / NO / THANKS
  ============================================ */

  if (
    pendingTicket &&
    [
      "no",
      "nahi",
      "thanks",
      "thank you",
      "resolved",
      "solve",
      "cancel",
      "not needed"
    ].some(
      w => lower.includes(w)
    )
  ) {

    pendingTicket = null;


    setTimeout(() => {

      addBotMessage(
        "Noted. I'm fully trained for complaints, tracking, admin functions, and dataset understanding. Ask anything else."
      );

    }, 300);


    return;
  }


  /* ============================================
     MAIN ANALYSIS
     REAL BACKEND + AI SERVICE
  ============================================ */

  addBotMessage(
    "🤖 <b>Analyzing your complaint...</b>"
  );


  try {

    const data =
      await chatbotApiRequest(
        "/chat",
        {
          method: "POST",

          body: JSON.stringify({

            message: text,

            session_id:
              "chatbot-" +
              Date.now()

          })
        }
      );


    const ticket =
      data.ticket;


    if (!ticket) {

      addBotMessage(
        data.reply ||
        "I could not process your complaint."
      );

      return;
    }


    /* ============================================
       STORE REAL BACKEND TICKET
    ============================================ */

    pendingTicket = {

      text: text,

      ticket: ticket

    };


    /* ============================================
       AI ANALYSIS RESULT
    ============================================ */

    addBotMessage(

      "🤖 <b>AI Analysis Complete:</b><br>" +

      "📂 <b>Category:</b> " +
      (ticket.category || "N/A") +
      "<br>" +

      "⚡ <b>Priority:</b> " +
      (ticket.priority || "N/A") +
      "<br>" +

      "🧩 <b>Complexity:</b> " +
      (ticket.complexity || "N/A") +
      "<br>" +

      "👥 <b>Recommended Team:</b> " +
      (ticket.recommended_team || "N/A") +

      "<br><br>" +

      "Reply <b>YES</b> to confirm this complaint."

    );

  }


  /* ============================================
     ERROR HANDLING
  ============================================ */

  catch (error) {

    console.error(
      "ComplaintCare AI error:",
      error
    );


    addBotMessage(

      "❌ <b>AI service error:</b> " +

      (
        error.message ||
        "Unable to process your complaint."
      )

    );

  }

}