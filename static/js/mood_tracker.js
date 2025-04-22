// ===== Event Filtering Listeners =====
async function fetchMoodData() {
    const res = await fetch("/get_all_moods");
    const data = await res.json();
    if (data && (data.status === "success" || data.mood)) {
        updateMoodTable(data.moods); // <-- FIXED
    }
}


// ===== Utility: Get Selected Mood or Habit Buttons =====
function getSelected(buttonGroupSelector, attribute) {
    const selected = [];
    document.querySelectorAll(`${buttonGroupSelector} .btn.active`).forEach(btn => {
        selected.push(btn.getAttribute(attribute));
    });
    return selected;
}

// ===== Toggle Button 'active' Class on Click =====
function toggleSelectableButtons(containerId, attr) {
    document.querySelectorAll(`#${containerId} button`).forEach(button => {
        button.addEventListener("click", () => {
            button.classList.toggle("active");
        });
    });
}

// ===== Save Mood Entry to Backend =====
async function saveMood() {
    const moods = getSelected("#moodButtons", "data-mood");
    const habits = getSelected("#habitButtons", "data-habit");
    const selectedDate = document.getElementById("calendarMoodDate").value;
    const today = new Date().toISOString().split("T")[0];

    // Prevent future entries
    // Require at least one mood
    if (new Date(selectedDate) > new Date(today)) {
        document.getElementById("moodSaveStatus").innerText = "Future entries are not allowed.";
        return;
    }

    // Require at least one mood
    if (moods.length === 0) {
        document.getElementById("moodSaveStatus").innerText = "Please select at least one mood.";
        return;
    }

    const notes = document.getElementById("symptomNotes").value;

    const res = await fetch("/save_mood_entry", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            date: selectedDate,
            moods: moods,
            habits: habits,
            notes: notes
        })
    });

    // Send data to serve
    const result = await res.json();

    if (res.status !== 200 || result.status === "error") {
        document.getElementById("moodSaveStatus").innerText = result.message || "Something went wrong.";
        showToast(result.message || "Mood could not be saved.", false); // Optional: toast error
        return;
    }

    document.getElementById("moodSaveStatus").innerText = result.message;
    showToast("Mood saved successfully!"); // Optional: toast success

    // Add mood emoji to calendar if today
    if (selectedDate === today && window.calendar) {
        const moodSymbol = "😊";
        const existingMood = calendar.getEventById(`mood-${selectedDate}`);
        if (existingMood) existingMood.remove();

        calendar.addEvent({
            id: `mood-${selectedDate}`,
            title: moodSymbol,
            start: selectedDate,
            allDay: true,
            classNames: ["mood-symbol"]
        });
    }

    fetchMoodData();
}

// ===== Enable Mood & Habit Button Toggles on Page Load =====
toggleSelectableButtons("moodButtons", "data-mood");
toggleSelectableButtons("habitButtons", "data-habit");

// ===== Load All Existing Mood Logs into Table =====
fetchMoodData();

// ===== Update HTML Mood Log Table =====
function updateMoodTable(data) {

    const tableBody = document.getElementById("moodTableBody");
    tableBody.innerHTML = "";

    data.forEach(log => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${log.date}</td>
            <td>${log.mood.join(", ")}</td>
            <td>${log.habits && log.habits.length ? log.habits.join(", ") : "-"}</td>
            <td>${log.notes || "-"}</td>
        `;

        tableBody.appendChild(row);
    });
}


// ===== Load Mood Insight Predictions + Bar Chart =====
async function loadMoodInsights() {
    const res = await fetch("/get_mood_insights");
    const data = await res.json();
    if (data.status !== "success") return;

    const counts = data.insights.counts;
    const labels = Object.keys(counts);
    const values = Object.values(counts);

    // Create bar chart from frequency data
    const ctx = document.getElementById("moodBarChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Mood Frequency",
                data: values,
                backgroundColor: "#42a5f5"
            }]
        }
    });
    // Show textual prediction
    document.getElementById("prediction").innerText = data.insights.prediction;
}

loadMoodInsights();


// ===== Toast Message Utility (Success/Error) =====
function showToast(message, isSuccess = true) {
    const toastEl = document.getElementById("eventToast");
    const toastBody = toastEl?.querySelector(".toast-body");

    toastBody.textContent = message;
    toastEl.classList.remove("text-bg-success", "text-bg-danger");
    toastEl.classList.add(isSuccess ? "text-bg-success" : "text-bg-danger");

    new bootstrap.Toast(toastEl).show();
}

// ===== Open Mood Tracker for Selected Date (from calendar.js) =====
function openMoodTrackerFromDate(date, isEdit = false) {
    document.getElementById("calendarMoodDate").value = date;
    document.getElementById("moodDateLabel").innerText = `Logging for: ${moment(date).format("ddd MMM D YYYY")}`;
    document.getElementById("moodTrackerModal").classList.add("active");

    if (isEdit) {
        fetch(`/get_mood_by_date?date=${date}`)
            .then(response => response.json())
            .then(data => {
                if (data && data.mood) {
                    prefillMoodForm(data); // You write this
                }
            });
    }
}

// ===== Prefill Mood Form with Existing Data =====
function prefillMoodForm(data) {
    // Clear existing selections
    document.querySelectorAll("#moodButtons .btn, #habitButtons .btn").forEach(btn => btn.classList.remove("active"));
    document.getElementById("symptomNotes").value = "";

    // Prefill moods
    if (data.mood && Array.isArray(data.mood)) {
        data.mood.forEach(m => {
            const btn = document.querySelector(`#moodButtons button[data-mood="${m}"]`);
            if (btn) btn.classList.add("active");
        });
    }

    // Prefill habits
    if (data.habits && Array.isArray(data.habits)) {
        data.habits.forEach(h => {
            const btn = document.querySelector(`#habitButtons button[data-habit="${h}"]`);
            if (btn) btn.classList.add("active");
        });
    }

    // Prefill notes
    if (data.notes) {
        document.getElementById("symptomNotes").value = data.notes;
    }
}


