/**
 * SafeSpace Frontend Client
 * Handles real-time SSE streaming, Web Speech API voice input,
 * SpeechSynthesis TTS, interactive breathing visualizer, and session management.
 */

// Application State
const state = {
  sessionId: localStorage.getItem("safespace_session_id") || `sess_${Math.random().toString(36).substr(2, 9)}`,
  ttsEnabled: false,
  isStreaming: false,
  isListening: false,
  currentGroundingStep: 1,
  breathingInterval: null,
};

localStorage.setItem("safespace_session_id", state.sessionId);

// DOM Elements
const messagesContainer = document.getElementById("messagesContainer");
const messagesList = document.getElementById("messagesList");
const welcomeCard = document.getElementById("welcomeCard");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const voiceInputBtn = document.getElementById("voiceInputBtn");
const micIcon = document.getElementById("micIcon");
const ttsToggleBtn = document.getElementById("ttsToggleBtn");
const ttsIcon = document.getElementById("ttsIcon");
const newChatBtn = document.getElementById("newChatBtn");
const sessionList = document.getElementById("sessionList");
const crisisBanner = document.getElementById("crisisBanner");
const closeCrisisBanner = document.getElementById("closeCrisisBanner");
const sosHeaderBtn = document.getElementById("sosHeaderBtn");
const confirmSosBtn = document.getElementById("confirmSosBtn");
const mobileToggleBtn = document.getElementById("mobileToggleBtn");
const sidebar = document.getElementById("sidebar");

// Modals
const breathingModal = document.getElementById("breathingModal");
const groundingModal = document.getElementById("groundingModal");
const cbtModal = document.getElementById("cbtModal");
const sosModal = document.getElementById("sosModal");

// ---------------------------------------------------------
// Initialization
// ---------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadSessions();
  setupVoiceRecognition();
  feather.replace();
});

function setupEventListeners() {
  // Sending messages
  sendBtn.addEventListener("click", handleSend);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  // Auto-grow textarea
  chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
  });

  // New Chat
  newChatBtn.addEventListener("click", startNewChat);

  // Suggestions
  document.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      chatInput.value = prompt;
      handleSend();
    });
  });

  // Mood chips
  document.querySelectorAll(".mood-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".mood-chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      const mood = chip.getAttribute("data-mood");
      sendAutomatedMessage(`I'm checking in right now. I am feeling ${mood}.`);
    });
  });

  // Voice output toggle
  ttsToggleBtn.addEventListener("click", toggleTTS);

  // SOS Triggers
  sosHeaderBtn.addEventListener("click", () => openModal(sosModal));
  confirmSosBtn.addEventListener("click", triggerSosDispatch);
  closeCrisisBanner.addEventListener("click", () => {
    crisisBanner.style.display = "none";
  });

  // Mobile menu toggle
  mobileToggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  // Modals open
  document.getElementById("openBreathingModal").addEventListener("click", () => openModal(breathingModal));
  document.getElementById("openGroundingModal").addEventListener("click", () => openModal(groundingModal));
  document.getElementById("openCbtModal").addEventListener("click", () => openModal(cbtModal));

  // Modals close
  document.querySelectorAll("[data-close]").forEach(btn => {
    btn.addEventListener("click", () => {
      const modalId = btn.getAttribute("data-close");
      closeModal(document.getElementById(modalId));
    });
  });

  // Toolkit: Breathing
  document.getElementById("startBreathingBtn").addEventListener("click", startBreathingCycle);
  document.getElementById("stopBreathingBtn").addEventListener("click", stopBreathingCycle);

  // Toolkit: Grounding
  document.getElementById("nextGroundingBtn").addEventListener("click", nextGroundingStep);
  document.getElementById("prevGroundingBtn").addEventListener("click", prevGroundingStep);

  // Toolkit: CBT Thought Reframer
  document.getElementById("sendCbtToChatBtn").addEventListener("click", submitCbtReframer);
}

// ---------------------------------------------------------
// Messaging & Real-Time Streaming
// ---------------------------------------------------------
async function handleSend() {
  const text = chatInput.value.trim();
  if (!text || state.isStreaming) return;

  chatInput.value = "";
  chatInput.style.height = "auto";
  welcomeCard.style.display = "none";

  // Append user bubble
  appendMessage("user", text);

  // Append assistant typing placeholder
  const assistantBubble = appendMessage("assistant", "", true);
  state.isStreaming = true;

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: state.sessionId
      })
    });

    if (!response.ok) throw new Error("Backend stream request failed");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let accumulatedText = "";

    // Remove typing dots
    assistantBubble.querySelector(".typing-bubble")?.remove();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.replace("data: ", ""));
            if (data.token) {
              accumulatedText += data.token;
              assistantBubble.querySelector(".message-bubble").textContent = accumulatedText;
              scrollToBottom();
            }
          } catch (err) {
            // Non-JSON SSE ping, skip
          }
        }
      }
    }

    // Check for crisis trigger in response
    if (accumulatedText.includes("988") || accumulatedText.includes("Crisis Text Line")) {
      crisisBanner.style.display = "block";
    }

    // TTS playback if voice enabled
    if (state.ttsEnabled && accumulatedText) {
      speakText(accumulatedText);
    }

    loadSessions();

  } catch (err) {
    console.error("Streaming error:", err);
    assistantBubble.querySelector(".message-bubble").textContent = 
      "I am here with you, but I experienced a connection interruption. Please know your feelings matter, and feel free to try again shortly.";
  } finally {
    state.isStreaming = false;
  }
}

function sendAutomatedMessage(text) {
  chatInput.value = text;
  handleSend();
}

function appendMessage(role, content, isTyping = false) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "👤" : "👩‍⚕️";

  const wrapper = document.createElement("div");
  wrapper.className = "message-content-wrapper";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  if (isTyping) {
    bubble.innerHTML = `
      <div class="typing-bubble">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    `;
  } else {
    bubble.textContent = content;
  }

  const meta = document.createElement("div");
  meta.className = "message-meta";
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  meta.innerHTML = `<span>${time}</span>`;

  if (role === "assistant") {
    meta.innerHTML += `<span class="citation-chip">Clinical Attunement</span>`;
  }

  wrapper.appendChild(bubble);
  wrapper.appendChild(meta);
  row.appendChild(avatar);
  row.appendChild(wrapper);

  messagesList.appendChild(row);
  scrollToBottom();
  return row;
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ---------------------------------------------------------
// Sessions & Memory
// ---------------------------------------------------------
async function loadSessions() {
  try {
    const res = await fetch("/api/sessions");
    const data = await res.json();
    sessionList.innerHTML = "";

    data.sessions.forEach(s => {
      const item = document.createElement("div");
      item.className = `session-item ${s.session_id === state.sessionId ? "active" : ""}`;
      item.innerHTML = `
        <span class="session-title"><i data-feather="message-circle" style="width: 14px; height: 14px; margin-right: 6px;"></i>${s.title}</span>
        <button class="delete-session-btn" title="Delete conversation"><i data-feather="trash-2" style="width: 13px; height: 13px;"></i></button>
      `;

      item.querySelector(".session-title").addEventListener("click", () => switchSession(s.session_id));
      item.querySelector(".delete-session-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        deleteSession(s.session_id);
      });

      sessionList.appendChild(item);
    });
    feather.replace();
  } catch (err) {
    console.warn("Failed to load sessions:", err);
  }
}

async function switchSession(sid) {
  state.sessionId = sid;
  localStorage.setItem("safespace_session_id", sid);
  messagesList.innerHTML = "";
  welcomeCard.style.display = "none";

  try {
    const res = await fetch(`/api/sessions/${sid}/history`);
    const data = await res.json();
    data.messages.forEach(msg => appendMessage(msg.role, msg.content));
    loadSessions();
  } catch (err) {
    console.error("Failed to load session history:", err);
  }
}

function startNewChat() {
  state.sessionId = `sess_${Math.random().toString(36).substr(2, 9)}`;
  localStorage.setItem("safespace_session_id", state.sessionId);
  messagesList.innerHTML = "";
  welcomeCard.style.display = "block";
  loadSessions();
}

async function deleteSession(sid) {
  await fetch(`/api/sessions/${sid}`, { method: "DELETE" });
  if (state.sessionId === sid) {
    startNewChat();
  } else {
    loadSessions();
  }
}

// ---------------------------------------------------------
// Multimodal Voice (Speech-to-Text & Text-to-Speech)
// ---------------------------------------------------------
function setupVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    voiceInputBtn.style.display = "none";
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  voiceInputBtn.addEventListener("click", () => {
    if (state.isListening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  });

  recognition.onstart = () => {
    state.isListening = true;
    voiceInputBtn.classList.add("listening");
  };

  recognition.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      transcript += event.results[i][0].transcript;
    }
    chatInput.value = transcript;
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
  };

  recognition.onend = () => {
    state.isListening = false;
    voiceInputBtn.classList.remove("listening");
  };
}

function toggleTTS() {
  state.ttsEnabled = !state.ttsEnabled;
  ttsToggleBtn.classList.toggle("active", state.ttsEnabled);
  ttsToggleBtn.querySelector(".btn-label").textContent = state.ttsEnabled ? "Voice On" : "Voice Off";
  if (!state.ttsEnabled) {
    window.speechSynthesis.cancel();
  }
}

function speakText(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95; // Soothing, calm cadence
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

// ---------------------------------------------------------
// Toolkit: 4-7-8 Breathing Pacer Visualizer
// ---------------------------------------------------------
function startBreathingCycle() {
  const circle = document.getElementById("breathCircle");
  const instruction = document.getElementById("breathInstruction");
  const timer = document.getElementById("breathTimer");
  const startBtn = document.getElementById("startBreathingBtn");
  const stopBtn = document.getElementById("stopBreathingBtn");

  startBtn.style.display = "none";
  stopBtn.style.display = "inline-flex";

  let step = 0; // 0 = inhale 4s, 1 = hold 7s, 2 = exhale 8s
  let secondsLeft = 4;

  circle.className = "breath-circle inhale";
  instruction.textContent = "Inhale (Nose)";
  timer.textContent = secondsLeft;

  state.breathingInterval = setInterval(() => {
    secondsLeft--;
    timer.textContent = secondsLeft;

    if (secondsLeft <= 0) {
      step = (step + 1) % 3;
      if (step === 0) {
        // Inhale 4s
        secondsLeft = 4;
        circle.className = "breath-circle inhale";
        instruction.textContent = "Inhale (Nose)";
      } else if (step === 1) {
        // Hold 7s
        secondsLeft = 7;
        circle.className = "breath-circle hold";
        instruction.textContent = "Hold Breath";
      } else {
        // Exhale 8s
        secondsLeft = 8;
        circle.className = "breath-circle exhale";
        instruction.textContent = "Exhale (Mouth)";
      }
      timer.textContent = secondsLeft;
    }
  }, 1000);
}

function stopBreathingCycle() {
  clearInterval(state.breathingInterval);
  const circle = document.getElementById("breathCircle");
  const instruction = document.getElementById("breathInstruction");
  const timer = document.getElementById("breathTimer");
  
  circle.className = "breath-circle";
  instruction.textContent = "Ready";
  timer.textContent = "";

  document.getElementById("startBreathingBtn").style.display = "inline-flex";
  document.getElementById("stopBreathingBtn").style.display = "none";
}

// ---------------------------------------------------------
// Toolkit: 5-4-3-2-1 Sensory Grounding Stepper
// ---------------------------------------------------------
function nextGroundingStep() {
  if (state.currentGroundingStep < 5) {
    state.currentGroundingStep++;
    updateGroundingView();
  } else {
    closeModal(groundingModal);
    state.currentGroundingStep = 1;
    updateGroundingView();
    sendAutomatedMessage("I just finished the 5-4-3-2-1 grounding exercise. I'm feeling a bit more centered in my body now.");
  }
}

function prevGroundingStep() {
  if (state.currentGroundingStep > 1) {
    state.currentGroundingStep--;
    updateGroundingView();
  }
}

function updateGroundingView() {
  document.querySelectorAll("#groundingStepper .step-card").forEach(c => {
    c.classList.remove("active");
    if (parseInt(c.getAttribute("data-step")) === state.currentGroundingStep) {
      c.classList.add("active");
    }
  });

  document.getElementById("prevGroundingBtn").disabled = state.currentGroundingStep === 1;
  document.getElementById("nextGroundingBtn").textContent = 
    state.currentGroundingStep === 5 ? "Finish & Reflect" : "Next Step";
}

// ---------------------------------------------------------
// Toolkit: CBT Thought Reframer
// ---------------------------------------------------------
function submitCbtReframer() {
  const thought = document.getElementById("cbtThoughtInput").value.trim();
  const distortion = document.getElementById("cbtDistortionSelect").value;
  const reframe = document.getElementById("cbtReframeInput").value.trim();

  if (!thought) return;

  closeModal(cbtModal);
  const prompt = `I am practicing CBT thought reframing:\n- Automatic Thought: "${thought}"\n- Identified Distortion: ${distortion}\n- My Rational Reframe: "${reframe || 'Still working through this...'}"\n\nCould you please review this with me from a clinical psychology perspective?`;
  
  // Clear inputs
  document.getElementById("cbtThoughtInput").value = "";
  document.getElementById("cbtReframeInput").value = "";

  sendAutomatedMessage(prompt);
}

// ---------------------------------------------------------
// Emergency 1-Click SOS Dispatch
// ---------------------------------------------------------
async function triggerSosDispatch() {
  closeModal(sosModal);
  crisisBanner.style.display = "block";

  try {
    const res = await fetch("/api/emergency/sos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason: "User triggered 1-click SOS button on web UI" })
    });
    const data = await res.json();
    appendMessage("assistant", 
      `🚨 **Emergency Safety Protocol Activated** (${data.dispatch_details.status})\n\n` +
      `We have dispatched a crisis alert notification. Please know you are not alone.\n` +
      `📞 **988 Suicide & Crisis Lifeline**: Dial 988 immediately (Free & Confidential)\n` +
      `💬 **Crisis Text Line**: Text HOME to 741741`
    );
  } catch (err) {
    console.error("SOS dispatch error:", err);
  }
}

// ---------------------------------------------------------
// Modal Helpers
// ---------------------------------------------------------
function openModal(modal) {
  modal.style.display = "flex";
}

function closeModal(modal) {
  modal.style.display = "none";
  if (modal === breathingModal) {
    stopBreathingCycle();
  }
}
