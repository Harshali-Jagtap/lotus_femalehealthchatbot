document.addEventListener("DOMContentLoaded", function () {
    console.log("Chatbot script loaded successfully.");

    const sendButton = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatBody = document.getElementById("chat-body");

    if (!sendButton || !userInput || !chatBody) {
        console.error("Error: Required elements missing in `chatbot.html`.");
        return;
    }

    sendButton.addEventListener("click", function () {
        sendMessage();
    });

    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});

async function sendMessage() {
    const userInputField = document.getElementById("user-input");
    const chatBody = document.getElementById("chat-body");

    if (!userInputField || !chatBody) return;

    const userMessage = userInputField.value.trim();
    if (!userMessage) return;

    console.log("Sending message:", userMessage);

    // Create User Message Bubble
    const userMessageDiv = document.createElement("div");
    userMessageDiv.classList.add("chat-message", "user-message");
    userMessageDiv.textContent = userMessage;
    chatBody.appendChild(userMessageDiv);

    // Auto-scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;

    // Clear input field
    userInputField.value = "";

    // Fetch bot response
    const botResponse = await fetchResponse(userMessage);

    // Create Bot Response Bubble
    const botMessageDiv = document.createElement("div");
    botMessageDiv.classList.add("chat-message", "bot-message");
    botMessageDiv.textContent = botResponse;
    chatBody.appendChild(botMessageDiv);

    // Auto-scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function fetchResponse(userMessage) {
    try {
        console.log("Fetching response from backend...");
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        console.log("Received response:", data);
        return data.response || "I'm here to help! Could you clarify your question?";
    } catch (error) {
        console.error("Error fetching bot response:", error);
        return "Sorry, I encountered an issue processing your request.";
    }
}

//Dashaboard.html
document.addEventListener("DOMContentLoaded", function () {
    const toggleHealthTips = document.getElementById("toggleHealthTips");
    const healthTipsContainer = document.getElementById("healthTipsContainer");

    toggleHealthTips.addEventListener("click", function () {
        fetch("/toggle_health_tips", {method: "POST"})
            .then(response => response.json())
            .then(data => {
                healthTipsContainer.style.display = data.show_health_tips ? "block" : "none";
            })
            .catch(error => console.error("Error toggling health tips:", error));
    });
});

// Dashboard Calendar
document.addEventListener("DOMContentLoaded", function () {
    let calendarEl = document.getElementById("calendar");

    let eventFormContainer = document.getElementById("eventFormContainer");
    let eventForm = document.getElementById("eventForm");
    let cancelEventBtn = document.getElementById("cancelEventBtn");
    let eventDateInput = document.getElementById("eventDate");
    let eventTitleInput = document.getElementById("eventTitle");

    let eventDetailsContainer = document.getElementById("eventDetailsContainer");
    let eventTitleDisplay = document.getElementById("eventTitleDisplay");
    let eventDateDisplay = document.getElementById("eventDateDisplay");
    let closeDetailsBtn = document.getElementById("closeDetailsBtn");

    let editEventContainer = document.getElementById("editEventContainer");
    let editEventTitle = document.getElementById("editEventTitle");
    let editEventBtn = document.getElementById("editEventBtn");
    let saveEditEventBtn = document.getElementById("saveEditEventBtn");

    let deleteEventContainer = document.getElementById("deleteEventContainer");
    let deleteEventBtn = document.getElementById("deleteEventBtn");
    let confirmDeleteEventBtn = document.getElementById("confirmDeleteEventBtn");
    let cancelDeleteEventBtn = document.getElementById("cancelDeleteEventBtn");

    let selectedEvent = null;

    // Function to Hide All Forms
    function hideAllForms() {
        eventFormContainer.style.display = "none";
        eventDetailsContainer.style.display = "none";
        editEventContainer.style.display = "none";
        deleteEventContainer.style.display = "none";
    }

    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth", selectable: true, editable: true, events: "/get_events",

        // Open Add Event Form When Clicking a Date
        dateClick: function (info) {
            hideAllForms(); // Close all other forms
            eventDateInput.value = info.dateStr;
            eventFormContainer.style.display = "block"; // Show add event form
            eventTitleInput.focus();
        },

        // Show Event Details When Clicking an Event
        eventClick: function (info) {
            hideAllForms(); // Close all other forms
            selectedEvent = info.event;
            eventTitleDisplay.innerText = selectedEvent.title;
            eventDateDisplay.innerText = selectedEvent.start.toISOString().split("T")[0];
            eventDetailsContainer.style.display = "block"; // Show event details
        }
    });

    calendar.render();

    // Handle Event Form Submission (Add Event)
    eventForm.addEventListener("submit", function (e) {
        e.preventDefault();
        let title = eventTitleInput.value.trim();
        let date = eventDateInput.value;

        if (title) {
            fetch("/add_event", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({title: title, date: date}),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        calendar.addEvent({
                            id: data.event.id, title: data.event.title, start: data.event.start
                        });
                        eventFormContainer.style.display = "none"; // Hide form after saving
                        eventTitleInput.value = ""; // Clear input field
                    } else {
                        alert("Error adding event: " + data.message);
                    }
                });
        }
    });

    // Cancel Event Form
    cancelEventBtn.addEventListener("click", function () {
        eventFormContainer.style.display = "none"; // Hide the form
    });

    // Close Event Details
    closeDetailsBtn.addEventListener("click", function () {
        eventDetailsContainer.style.display = "none";
    });

    // Show Edit Event Form
    document.addEventListener("click", function (event) {
        if (event.target.id === "editEventBtn") {
            editEventContainer.style.display = "block";  // Show edit form
            editEventTitle.value = selectedEvent.title;  // Set existing title
        }
    });

    // Save Edited Event
    saveEditEventBtn.addEventListener("click", function () {
        let newTitle = editEventTitle.value.trim();
        if (selectedEvent && newTitle) {
            fetch("/edit_event/" + selectedEvent.id, {  // Send event ID and new title to backend
                method: "PUT",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({title: newTitle})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        selectedEvent.setProp("title", newTitle);  // Update calendar event title
                        editEventContainer.style.display = "none";  // Hide edit form
                    } else {
                        alert("Error updating event: " + data.message);
                    }
                });
        }
    });

    // Cancel Edit Event
    cancelEditEventBtn.addEventListener("click", function () {
        editEventContainer.style.display = "none";  // Hide edit confirmation box
    });
    // Show Delete Confirmation Box
    document.addEventListener("click", function (event) {
        if (event.target.id === "deleteEventBtn") {
            deleteEventContainer.style.display = "block";  // Show delete confirmation box
        }
    });

    // Confirm Delete Event
    confirmDeleteEventBtn.addEventListener("click", function () {
        if (selectedEvent) {
            fetch("/delete_event/" + selectedEvent.id, {
                method: "DELETE",
                headers: {"Content-Type": "application/json"}
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        selectedEvent.remove();  // Remove event from calendar
                        deleteEventContainer.style.display = "none";  // Hide confirmation box
                    } else {
                        alert("Error deleting event: " + data.message);
                    }
                });
        }
    });

    // Cancel Delete Event
    cancelDeleteEventBtn.addEventListener("click", function () {
        deleteEventContainer.style.display = "none";  // Hide delete confirmation box
    });


});

//Index page
document.addEventListener("DOMContentLoaded", function () {
});

//Log in Register
document.addEventListener("DOMContentLoaded", function () {
    // Handle Login Form
    const loginForm = document.querySelector("form[action='/login']");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value.trim();
            const messageDiv = document.getElementById("login-message");

            if (!email || !password) {
                showMessage(messageDiv, "Please fill in all fields.", "danger");
                return;
            }

            try {
                const response = await fetch("/login", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({email, password})
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage(messageDiv, "Login successful! Redirecting...", "success");
                    setTimeout(() => window.location.href = "/chatbot", 1500);
                } else {
                    showMessage(messageDiv, data.message || "Login failed. Please try again.", "danger");
                }
            } catch (error) {
                console.error("Error logging in:", error);
                showMessage(messageDiv, "An error occurred. Please try again.", "danger");
            }
        });
    }

    // Handle Registration Form
    const registerForm = document.querySelector("form[action='/register']");
    if (registerForm) {
        registerForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const firstname = document.getElementById("firstname").value.trim();
            const lastname = document.getElementById("lastname").value.trim();
            const age = document.getElementById("age").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value.trim();
            const messageDiv = document.getElementById("register-message");

            if (!firstname || !lastname || !age || !email || !password) {
                showMessage(messageDiv, "Please fill in all fields.", "danger");
                return;
            }

            try {
                const response = await fetch("/register", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({firstname, lastname, age, email, password})
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage(messageDiv, "Registration successful! Redirecting to login...", "success");
                    setTimeout(() => window.location.href = "/login", 1500);
                } else {
                    showMessage(messageDiv, data.message || "Registration failed. Please try again.", "danger");
                }
            } catch (error) {
                console.error("Error registering:", error);
                showMessage(messageDiv, "An error occurred. Please try again.", "danger");
            }
        });
    }

    // Function to Show Messages
    function showMessage(element, message, type) {
        element.className = `alert alert-${type}`;
        element.textContent = message;
        element.classList.remove("d-none");
    }
});

//chat history scollable
document.addEventListener("DOMContentLoaded", function () {
    const chatBody = document.querySelector(".chat-body");
    if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight; // Auto-scroll to bottom
    }
});












