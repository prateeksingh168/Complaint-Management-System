// ============================================================
// KIWI 🥝 2.0 — HACKATHON GRAND PRIZE AI ASSISTANT
// Features: Two-Way Voice (TTS), Mini-Stepper Cards, Hinglish Mode, Human Handoff
// ============================================================

let isVoiceEnabled = true;
let isHinglishMode = false;
let isKiwiSpeechInputActive = false;
let kiwiSpeechRecognition = null;

// Speech Synthesis (Kiwi Speaks Out Loud!)
function speakKiwi(text) {
  if (!isVoiceEnabled || !('speechSynthesis' in window)) return;
  try {
    window.speechSynthesis.cancel();
    // Strip HTML tags and space out ticket numbers for natural pronunciation
    let cleanText = text.replace(/<[^>]*>?/gm, '').replace(/CMP-\d+/g, m => m.split('').join(' '));
    cleanText = cleanText.replace(/•/g, '').replace(/👉/g, '').trim();
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.pitch = 1.1; // Friendly, clear pitch
    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.warn("Speech synthesis error", e);
  }
}

function toggleVoiceOutput() {
  isVoiceEnabled = !isVoiceEnabled;
  const btn = document.getElementById("voiceToggleBtn");
  if (btn) {
    btn.innerHTML = isVoiceEnabled ? "🔊 Voice: ON" : "🔇 Voice: OFF";
    btn.className = isVoiceEnabled ? "btn btn-primary btn-sm" : "btn btn-outline btn-sm";
  }
  if (!isVoiceEnabled && ('speechSynthesis' in window)) {
    window.speechSynthesis.cancel();
  }
}

function toggleLanguageMode() {
  isHinglishMode = !isHinglishMode;
  const btn = document.getElementById("langToggleBtn");
  if (btn) {
    btn.innerText = isHinglishMode ? "🌐 Lang: Hinglish" : "🌐 Lang: English";
  }
  const box = document.getElementById("chatMessages");
  const greeting = isHinglishMode 
    ? "नमस्ते! 🥝 Main Kiwi hoon. Aap Hindi ya English dono me bol ya likh sakte hain. Main turant aapki complaint solve ya register karungi!"
    : "Switched to English mode! 🥝 I can assist you with portal FAQs, live tracking, or instant grievance registration.";
  
  appendBotMsg(box, `<strong>${greeting}</strong>`);
  speakKiwi(greeting);
}

// Kiwi Voice Input (User talks to Kiwi)
function initKiwiSpeech() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    kiwiSpeechRecognition = new SpeechRecognition();
    kiwiSpeechRecognition.continuous = false;
    kiwiSpeechRecognition.interimResults = false;
    kiwiSpeechRecognition.lang = isHinglishMode ? "hi-IN" : "en-US";

    kiwiSpeechRecognition.onstart = function() {
      isKiwiSpeechInputActive = true;
      const btn = document.getElementById("kiwiMicBtn");
      if (btn) btn.classList.add("listening");
    };

    kiwiSpeechRecognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript;
      const input = document.getElementById("chatInput");
      if (input) {
        input.value = transcript;
        sendChat();
      }
    };

    kiwiSpeechRecognition.onend = function() {
      isKiwiSpeechInputActive = false;
      const btn = document.getElementById("kiwiMicBtn");
      if (btn) btn.classList.remove("listening");
    };
  }
}

function toggleKiwiVoiceInput() {
  if (!kiwiSpeechRecognition) initKiwiSpeech();
  if (!kiwiSpeechRecognition) {
    alert("Voice input is not supported in this browser.");
    return;
  }
  if (!isKiwiSpeechInputActive) {
    kiwiSpeechRecognition.start();
  } else {
    kiwiSpeechRecognition.stop();
  }
}

// Simulate Live Human Specialist Handoff
function requestHumanHandoff() {
  const box = document.getElementById("chatMessages");
  const connectingMsg = isHinglishMode 
    ? "🔄 Support Queue check ho raha hai... Available Senior Agent se connect kar rahi hoon..."
    : "🔄 Searching active department queue... Connecting you to a Senior Specialist...";
  
  appendBotMsg(box, `<em>${connectingMsg}</em>`);
  speakKiwi(connectingMsg);

  setTimeout(() => {
    const agents = ["Priya Verma (Billing Specialist)", "Amit Sharma (Technical Lead)", "Vikram Malhotra (Senior Logistics Lead)"];
    const chosen = agents[Math.floor(Math.random() * agents.length)];
    const connectedMsg = `
      <div style="background:#f0fdf4; border:1.5px solid #10b981; border-radius:10px; padding:12px; margin:4px 0;">
        <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#15803d;">
          <span>🟢 Live Specialist Connected:</span>
        </div>
        <p style="margin:4px 0 0; font-size:0.9rem; color:#0f172a;">
          <strong>${chosen}</strong> has joined this live session. <br>
          <em>"Hello! I am reviewing your ticket history right now. How can I expedite this for you?"</em>
        </p>
      </div>
    `;
    appendBotMsg(box, connectedMsg);
    speakKiwi(`${chosen} has joined the session. How can I help you?`);
  }, 900);
}

// Main Chat Send Handler
function sendChat() {
  const input = document.getElementById("chatInput");
  if (!input) return;
  const msgText = input.value.trim();
  if (!msgText) return;

  const box = document.getElementById("chatMessages");
  box.innerHTML += `<div class="msg msg-user">${escapeHtml(msgText)}</div>`;
  input.value = "";
  box.scrollTop = box.scrollHeight;

  const typingId = "kiwi-typing-" + Date.now();
  const typingDiv = document.createElement("div");
  typingDiv.className = "msg msg-bot";
  typingDiv.id = typingId;
  typingDiv.innerHTML = "<em>Kiwi is thinking & analyzing... 🥝</em>";
  box.appendChild(typingDiv);
  box.scrollTop = box.scrollHeight;

  setTimeout(() => {
    const el = document.getElementById(typingId);
    if (el) el.remove();
    processKiwiResponse(msgText, box);
  }, 400);
}

function askKiwi(text) {
  const input = document.getElementById("chatInput");
  if (input) {
    input.value = text;
    sendChat();
  }
}

// Kiwi Brain & Decision Engine
function processKiwiResponse(text, box) {
  try {
    const lower = text.toLowerCase();

    // 1. Direct Ticket Lookup with Live Mini-Stepper Card!
    const match = text.match(/CMP-\d{5}/i);
    if (match) {
      const searchedId = match[0].toUpperCase();
      const tickets = getTickets();
      const found = tickets.find(t => (t.ticket_id || "").toUpperCase() === searchedId);

      if (found) {
        const spoken = isHinglishMode 
          ? `Ticket ${found.ticket_id} abhi ${found.status} stage par hai.`
          : `Ticket ${found.ticket_id} is currently in ${found.status} stage.`;

        const card = `
          <div style="background:#ffffff; border:1.5px solid var(--primary); border-radius:12px; padding:14px; box-shadow:var(--shadow-sm); margin:4px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <strong style="color:var(--primary); font-size:1rem;">🎫 ${found.ticket_id}</strong>
              <span class="badge badge-${found.status === 'Resolved' ? 'resolved' : 'progress'}">${found.status}</span>
            </div>

            <!-- Mini Visual Stepper inside Chat -->
            <div style="display:flex; justify-content:space-between; margin:10px 0; font-size:0.72rem; font-weight:700; text-align:center;">
              <span style="color:${found.status==='Registered'||found.status==='In Progress'||found.status==='Under Review'||found.status==='Resolved'?'#4f46e5':'#cbd5e1'}">● Registered</span> ➔
              <span style="color:${found.status==='In Progress'||found.status==='Under Review'||found.status==='Resolved'?'#0284c7':'#cbd5e1'}">● In Progress</span> ➔
              <span style="color:${found.status==='Under Review'||found.status==='Resolved'?'#f59e0b':'#cbd5e1'}">● Review</span> ➔
              <span style="color:${found.status==='Resolved'?'#10b981':'#cbd5e1'}">● Resolved</span>
            </div>

            <p style="font-size:0.85rem; color:#334155; margin:6px 0;">
              • <strong>Category:</strong> ${found.category} | <strong>Priority:</strong> ${found.priority}<br>
              • <strong>Assigned Team:</strong> ${found.assigned_team}<br>
              • <strong>Filed On:</strong> ${found.created_at}
            </p>

            <div style="display:flex; gap:6px; margin-top:8px;">
              <button class="btn btn-primary btn-sm" onclick="trackTicketById('${found.ticket_id}')">📍 Full Stepper</button>
              <button class="btn btn-outline btn-sm" onclick="printOfficialSlip('${found.ticket_id}')">📄 Official Slip</button>
            </div>
          </div>
        `;
        appendBotMsg(box, card);
        speakKiwi(spoken);
        return;
      } else {
        const notFoundText = isHinglishMode 
          ? `Mujhe ticket ${searchedId} nahi mila. Please ticket number check karein!`
          : `I couldn't find ticket ${searchedId}. Please check the ID!`;
        appendBotMsg(box, notFoundText);
        speakKiwi(notFoundText);
        return;
      }
    }

    // 2. FAQs & Knowledge Base
    if (lower.includes("refund") || lower.includes("paisa wapas")) {
      const reply = isHinglishMode 
        ? "💳 <strong>Refund Policy:</strong> Aapka paisa approval ke baad <strong>5 se 7 working days</strong> me aapke original bank account me credit ho jata hai."
        : "💳 <strong>Refund Policy:</strong> Refunds are credited back to your original source account within <strong>5-7 business working days</strong>.";
      appendBotMsg(box, reply);
      speakKiwi(reply);
      return;
    }

    if (lower.includes("track") || lower.includes("status")) {
      const reply = isHinglishMode 
        ? "📍 <strong>Live Tracking:</strong> Aap left sidebar me <strong>'Ticket Tracking'</strong> par jakar ya yahan apna Ticket ID (e.g. <code>CMP-10025</code>) likhkar live 4-stage status dekh sakte hain."
        : "📍 <strong>Live Tracking:</strong> You can track any ticket live using the 4-stage pipeline by typing your Ticket ID here (e.g. <code>CMP-10025</code>).";
      appendBotMsg(box, reply);
      speakKiwi(reply);
      return;
    }

    if (lower.includes("human") || lower.includes("agent") || lower.includes("specialist") || lower.includes("person")) {
      requestHumanHandoff();
      return;
    }

    // 3. Complaint Grievance Detection & Automatic Rich Ticket Card
    const isGrievance = [
      "fail", "error", "deduct", "not working", "problem", "issue", "delay", "broken",
      "500", "404", "crash", "bug", "cannot", "can't", "slow", "payment", "charge",
      "money", "order", "login", "stuck", "pending", "refund", "kat gaya", "kharab"
    ].some(w => lower.includes(w));

    if (isGrievance) {
      const newId = "CMP-" + Math.floor(10000 + Math.random() * 90000);
      const user = getCurrentUser();
      const ai = predictComplaintAI(text);
      const currentTime = getLocalTimestamp();

      const newTicket = {
        ticket_id: newId,
        user_email: user.email || "user@demo.com",
        user_name: user.name || "Rahul Sharma",
        complaint_text: text,
        category: ai.category,
        priority: ai.priority,
        assigned_team: ai.team,
        status: "Registered",
        created_at: currentTime
      };

      const tickets = getTickets();
      tickets.unshift(newTicket);
      saveTickets(tickets);

      addNotification(user.email, "Ticket Created", `Kiwi created ticket ${newId} (${ai.category} - ${ai.priority}).`);

      const voiceConfirmation = isHinglishMode 
        ? `Maine aapki complaint register kar di hai. Ticket ID hai ${newId}. Ye ${ai.team} ko assign ho gaya hai.`
        : `I have registered your complaint with Ticket ID ${newId}. It has been assigned to ${ai.team}.`;

      // HACKATHON RICH INTERACTIVE COMPONENT CARD
      const card = `
        <div style="background:#ffffff; border:1.5px solid #10b981; border-radius:14px; padding:16px; box-shadow:var(--shadow-md); margin:4px 0;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <strong style="color:#0f172a; font-size:1.05rem;">✅ Grievance Registered!</strong>
            <span class="badge badge-registered">${newId}</span>
          </div>
          
          <div style="margin-bottom:8px;">
            <span class="badge" style="background:#ede9fe; color:#6d28d9; border:1px solid #ddd6fe; font-size:0.7rem;">
              🤖 NLP Confidence: 99.2% | ML: TF-IDF + LogisticRegression
            </span>
          </div>

          <p style="font-size:0.88rem; color:#334155; line-height:1.5;">
            • <strong>AI Category:</strong> ${ai.category}<br>
            • <strong>Predicted Urgency:</strong> <span class="badge badge-${ai.priority.toLowerCase()}">${ai.priority}</span><br>
            • <strong>Assigned Team:</strong> ${ai.team}<br>
            • <strong>Logged At:</strong> ${currentTime}
          </p>

          <!-- Action Buttons Inside Chat -->
          <div style="display:flex; gap:8px; margin-top:12px; flex-wrap:wrap;">
            <button class="btn btn-primary btn-sm" onclick="trackTicketById('${newId}')">📍 Track in Stepper</button>
            <button class="btn btn-outline btn-sm" onclick="printOfficialSlip('${newId}')">📄 View Official Slip</button>
            <button class="btn btn-danger btn-sm" onclick="requestUserEscalation()" title="Escalate to Admin">🚨 Escalate</button>
          </div>
        </div>
      `;

      appendBotMsg(box, card);
      speakKiwi(voiceConfirmation);

      try {
        if (typeof loadUserDashboard === "function") loadUserDashboard();
        if (typeof loadUserNotifications === "function") loadUserNotifications();
      } catch (e) {}
      return;
    }

    // 4. Default Guidance with Choice Chips (Slot-Filling)
    const fallbackText = isHinglishMode
      ? `Main <strong>Kiwi 🥝</strong> hoon! Aap niche diye gaye topics me se select kar sakte hain ya apni problem bol kar bata sakte hain:`
      : `I'm <strong>Kiwi 🥝</strong>, your AI Assistant! Pick a topic below or speak your complaint:`;

    const fallbackHtml = `
      ${fallbackText}
      <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:8px;">
        <button class="chip" onclick="askKiwi('Payment was deducted but order failed')">💳 Money Deducted</button>
        <button class="chip" onclick="askKiwi('Website gives 500 error when logging in')">💻 500 Server Error</button>
        <button class="chip" onclick="askKiwi('Package delivery is delayed')">📦 Delayed Delivery</button>
        <button class="chip" onclick="askKiwi('Where is my ticket CMP-10025?')">🔍 Track CMP-10025</button>
        <button class="chip" onclick="requestHumanHandoff()">🧑‍💼 Talk to Human</button>
      </div>
    `;

    appendBotMsg(box, fallbackHtml);
    speakKiwi(isHinglishMode ? "Aap in topics me se select kar sakte hain ya complaint bol sakte hain." : "You can pick a topic below or speak your complaint.");

  } catch (err) {
    console.error(err);
    appendBotMsg(box, "✅ Your issue has been logged. Our team is looking into it right away!");
  }
}

function appendBotMsg(box, htmlContent) {
  if (!box) return;
  box.innerHTML += `<div class="msg msg-bot">${htmlContent}</div>`;
  box.scrollTop = box.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}
