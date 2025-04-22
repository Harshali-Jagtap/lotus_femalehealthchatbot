// ========== CHATBOT INTERACTION ==========
// Wait until the page is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    const sendButton = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatBody = document.getElementById("chat-body");

    if (sendButton && userInput && chatBody) {
        // On button click or Enter key, send a message
        console.log("Chatbot script loaded successfully.");

        sendButton.addEventListener("click", function () {
            sendMessage();
        });

        userInput.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        });
    }
});

// Send user message to server and display bot response
async function sendMessage() {
    const userInputField = document.getElementById("user-input");
    const chatBody = document.getElementById("chat-body");
    const typingIndicator = document.getElementById("typing-indicator");

    if (!userInputField || !chatBody) return;

    const userMessage = userInputField.value.trim();
    if (!userMessage) return;

    console.log("Sending message:", userMessage);

    // Show a user message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.classList.add("chat-message", "user-message");
    userMessageDiv.textContent = userMessage;
    chatBody.appendChild(userMessageDiv);

    // Scroll down and reset input
    chatBody.scrollTop = chatBody.scrollHeight;
    userInputField.value = "";

    // Show typing animation
    typingIndicator.style.display = "block";
    chatBody.scrollTop = chatBody.scrollHeight;

    // Get bot response
    const botResponse = await fetchResponse(userMessage);

    // Hide typing
    typingIndicator.style.display = "none";

    // Show bot message
    const botMessageDiv = document.createElement("div");
    botMessageDiv.classList.add("chat-message", "bot-message");
    botMessageDiv.textContent = botResponse;
    chatBody.appendChild(botMessageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Fetch bot reply from backend
async function fetchResponse(userMessage) {
    try {
        console.log("Fetching response from backend...");
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: userMessage})
        });

        const data = await response.json();
        console.log("Received response:", data);
        return data.response || "I'm here to help! Could you clarify your question?";
    } catch (error) {
        console.error("Error fetching bot response:", error);
        return "Sorry, I encountered an issue processing your request.";
    }
}

// Auto-scroll chat to bottom on page load
document.addEventListener("DOMContentLoaded", function () {
    const chatBody = document.querySelector(".chat-body");
    if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight; // Auto-scroll to bottom
    }
});

// ========== QUICK CHAT PROMPTS ==========
function sendPrompt(message, isPrompt = false) {
    const userInputField = document.getElementById("user-input");
    userInputField.value = message;

    // Store prompt flag
    userInputField.setAttribute("data-is-prompt", isPrompt ? "true" : "false");

    document.getElementById("send-btn").click();
}

// ========== DELETE CHAT HISTORY ==========
document.addEventListener("DOMContentLoaded", function () {
    const confirmDeleteBtn = document.getElementById("confirmDeleteChat");
    const toastEl = document.getElementById("deleteToast");

    if (confirmDeleteBtn && toastEl) {
        confirmDeleteBtn.addEventListener("click", () => {
            fetch("/delete_chat_history", {method: "DELETE"})
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById("deleteChatModal"));
                        if (modal) modal.hide();

                        // Show Bootstrap Toast
                        const toast = new bootstrap.Toast(toastEl);
                        toast.show();

                        // Reload after 2.5 seconds
                        setTimeout(() => location.reload(), 2500);
                    } else {
                        showTemporaryError("Error deleting chat history.");
                    }
                })
                .catch(err => {
                    console.error(err);
                    showTemporaryError("Server error while deleting history.");
                });
        });
    }

    // Optional: error fallback using toast styling
    function showTemporaryError(message) {
        const toastBody = toastEl.querySelector('.toast-body');
        toastBody.textContent = message;
        toastEl.classList.remove('text-bg-success');
        toastEl.classList.add('text-bg-danger');

        const toast = new bootstrap.Toast(toastEl);
        toast.show();

        // Reset style after 3s
        setTimeout(() => {
            toastEl.classList.remove('text-bg-danger');
            toastEl.classList.add('text-bg-success');
            toastBody.textContent = "Chat history deleted successfully.";
        }, 3000);
    }
});

// ========== INDEX PAGE ==========
document.addEventListener("DOMContentLoaded", function () {
});

// ========== MENTAL HEALTH PAGE ==========
// Expand/collapse emergency support cards
function toggleCard(card) {
    card.classList.toggle("expanded");
}

// ========== MENTAL HEALTH PAGE ==========
// Expand/collapse emergency support cards
if (typeof affirmations === 'undefined') {
    var affirmations = [
        "You are doing better than you think 🌸",
        "Healing is not linear 🧠",
        "Your feelings are valid 💖",
        "You are strong, even when you feel weak 💪",
        "You don’t need to have all the answers right now 🌼",
        "You are not alone 🤝",
        "This moment will pass ☀️",
        "Peace begins with a deep breath 🌬️",
        "You deserve rest and care 🛌",
        "I give myself permission to grow at my own pace",
        "I trust in the timing of my life",
        "I am not my thoughts, feelings, or fears",
        "My feelings are valid",
        "My wellbeing is a priority",
        "I am allowed to put my needs first",
        "I choose to be kind to myself",
        "I appreciate myself just the way I am at this moment",
        "I give myself permission to struggle",
        "I can and I will",
        "I am safe and in control",
        "I have done this before, and I can do it again",
        "This too shall pass",
        "I am strong and resilient",
        "I trust myself to navigate through this",
        "I am capable and competent",
        "I take things one day at a time",
        "I inhale peace and exhale worry",
        "This feeling is only temporary",
        "I am loved and accepted just as I am"
    ];
}

function generateAffirmation() {
    const random = affirmations[Math.floor(Math.random() * affirmations.length)];
    document.getElementById("affirmation-text").textContent = random;
}

// ========== MENTAL HEALTH: MYTH SLIDER ==========
let currentMyth = 0;

function slideMyths(direction) {
    const slides = document.querySelectorAll('.myth-slide');
    if (slides.length === 0) return;

    slides[currentMyth].classList.remove('active');
    currentMyth = (currentMyth + direction + slides.length) % slides.length;
    slides[currentMyth].classList.add('active');
}

// Auto-slide myths every 8 seconds
setInterval(() => slideMyths(1), 8000);

// ========== ABOUT PAGE: ACCORDIONS + SCROLL ANIMATION ==========
const accordions = document.querySelectorAll(".accordion-toggle");
accordions.forEach(btn => {
    btn.addEventListener("click", () => {
        const content = btn.nextElementSibling;
        content.style.display = content.style.display === "block" ? "none" : "block";
    });
});
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
            observer.unobserve(entry.target);
        }
    });
}, {threshold: 0.2});

document.querySelectorAll('.about-card').forEach(card => {
    observer.observe(card);
});

// ========== FEMALE HEALTH: SCROLL BUTTONS ==========
document.querySelectorAll(".scroll-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-target");
        const section = document.getElementById(targetId);
        if (section) {
            section.scrollIntoView({behavior: "smooth", block: "start"});
        }
    });
});

// ========== FOOTER FETCH (Optional if templated) ==========
fetch("/footer")
    .then(res => res.text())
    .then(data => {
        const footer = document.getElementById("footer-placeholder");
        if (footer) footer.innerHTML = data;
    });
