// ===== DOMContentLoaded: Wait until HTML is ready =====
document.addEventListener("DOMContentLoaded", function () {
    // ===== DOM Element References =====
    const calendarEl = document.getElementById("calendar");
    const eventFormContainer = document.getElementById("eventFormContainer");
    const eventForm = document.getElementById("eventForm");
    const cancelEventBtn = document.getElementById("cancelEventBtn");
    const eventDateInput = document.getElementById("eventDate");
    const eventTitleInput = document.getElementById("eventTitle");
    const eventTimeInput = document.getElementById("eventTime");
    const eventCategoryInput = document.getElementById("eventCategory");

    const eventDetailsContainer = document.getElementById("eventDetailsContainer");
    const eventTitleDisplay = document.getElementById("eventTitleDisplay");
    const eventDateDisplay = document.getElementById("eventDateDisplay");
    const eventCategoryDisplay = document.getElementById("eventCategoryDisplay");
    const closeDetailsBtn = document.getElementById("closeDetailsBtn");

    const editEventContainer = document.getElementById("editEventContainer");
    const editEventTitle = document.getElementById("editEventTitle");
    const editEventCategory = document.getElementById("editEventCategory");
    const saveEditEventBtn = document.getElementById("saveEditEventBtn");
    const cancelEditEventBtn = document.getElementById("cancelEditEventBtn");

    const deleteEventContainer = document.getElementById("deleteEventContainer");
    const deleteEventBtn = document.getElementById("deleteEventBtn");
    const confirmDeleteEventBtn = document.getElementById("confirmDeleteEventBtn");
    const cancelDeleteEventBtn = document.getElementById("cancelDeleteEventBtn");

    const toastEl = document.getElementById("eventToast");
    const toastBody = toastEl?.querySelector(".toast-body");

    const searchEventInput = document.getElementById("searchEventInput");
    const categoryFilter = document.getElementById("categoryFilter");

    let selectedEvent = null;

    // ===== Show Toast Message (Success or Error) =====
    function showToast(message, isSuccess = true) {
        toastBody.textContent = message;
        toastEl.classList.remove("text-bg-success", "text-bg-danger");
        toastEl.classList.add(isSuccess ? "text-bg-success" : "text-bg-danger");
        new bootstrap.Toast(toastEl).show();
    }

    // ===== Hide all open modal forms =====
    function hideAllForms() {
        document.querySelectorAll('.lotus-modal').forEach(modal => modal.classList.remove('active'));
        deleteEventContainer.style.display = "none";
    }

    // ===== Initialize FullCalendar =====
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth", selectable: true, editable: true, events: "/get_events",

        //Add view switcher
        headerToolbar: {
            left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },

        //Required to enable week/day views
        views: {
            timeGridWeek: {buttonText: 'Week'}, timeGridDay: {buttonText: 'Day'}, dayGridMonth: {buttonText: 'Month'}
        },

        eventClassNames: function (arg) {
            return [arg.event.extendedProps.category];
        },

        eventDidMount: function (info) {
            info.el.setAttribute("data-event-id", info.event.id); // Enable DOM targeting
        },

        // ===== Clicking a date opens options modal =====
        dateClick: function (info) {
            hideAllForms();  // hides both modals

            // store selected date in a hidden field
            document.getElementById("selectedDateStorage").value = info.dateStr;

            // update label in modal
            document.getElementById("selectedDateLabel").innerText = new Date(info.dateStr).toDateString();

            // show chooser modal
            document.getElementById("dateOptionsModal").classList.add("active");
        },

        // ===== Clicking an event opens event or mood modal =====
        eventClick: function (info) {
            const event = info.event;

            // Handle mood symbol click
            if (event.classNames.includes("mood-symbol")) {
                const date = moment(event.start).format("YYYY-MM-DD");

                fetch(`/get_mood_by_date?date=${date}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data && (data.status === "success" || data.mood)) {
                            document.getElementById("calendarMoodDate").value = date;
                            document.getElementById("moodDateLabel").innerText = "Editing Mood for: " + new Date(date).toDateString();

                            // Clear existing
                            document.querySelectorAll("#moodButtons .btn, #habitButtons .btn").forEach(btn => btn.classList.remove("active"));
                            document.getElementById("symptomNotes").value = "";

                            (data.mood || []).forEach(m => {
                                const btn = document.querySelector(`#moodButtons button[data-mood="${m}"]`);
                                if (btn) btn.classList.add("active");
                            });

                            (data.habits || []).forEach(h => {
                                const btn = document.querySelector(`#habitButtons button[data-habit="${h}"]`);
                                if (btn) btn.classList.add("active");
                            });

                            if (data.notes) {
                                document.getElementById("symptomNotes").value = data.notes;
                            }

                            document.getElementById("moodTrackerModal").classList.add("active");
                        } else {
                            showToast("No mood data found for this date.", false);
                        }
                    })
                    .catch(() => showToast("Failed to load mood data.", false));

                return;
            }

            // If it's a regular event, open event modal
            selectedEvent = event;
            eventTitleDisplay.innerText = selectedEvent.title;
            eventDateDisplay.innerText = new Date(selectedEvent.start).toLocaleString("en-US", {
                dateStyle: "medium", timeStyle: "short"
            });
            eventCategoryDisplay.innerText = selectedEvent.extendedProps.category || "General";
            document.getElementById("eventDetailsModal").classList.add("active");
        }

    });

    calendar.render();
    window.calendar = calendar;

    // ===== Search + Filter Events by Title or Category =====
    function applyFilters() {
        const searchQuery = searchEventInput.value.toLowerCase();
        const selectedCategory = categoryFilter.value;

        calendar.getEvents().forEach(event => {
            const matchesTitle = event.title.toLowerCase().includes(searchQuery);
            const matchesCategory = selectedCategory === "" || event.extendedProps.category === selectedCategory;

            const el = document.querySelector(`[data-event-id="${event.id}"]`);
            if (el) {
                el.style.display = (matchesTitle && matchesCategory) ? "" : "none";
            }
        });
    }

    // ===== Event Creation =====
    eventForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const title = eventTitleInput.value.trim();
        const date = eventDateInput.value;
        const time = eventTimeInput.value;
        const category = eventCategoryInput.value;
        const fullDate = time ? `${date}T${time}` : date;

        if (!title || !fullDate || !category) {
            showToast("All fields are required", false);
            return;
        }

        //Add event
        fetch("/add_event", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({title, date: fullDate, category})
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    calendar.addEvent({
                        id: data.event.id,
                        title: data.event.title,
                        start: data.event.start,
                        classNames: [data.event.category],
                        extendedProps: {
                            category: data.event.category
                        }
                    });
                    document.getElementById("eventFormModal").classList.remove("active");
                    clearAddEventForm();
                    showToast("Event added!");
                } else {
                    showToast("Error adding event", false);
                }
            });
        calendar.render(); // Refresh after adding
    });

    // ===== Modal Button Actions (Cancel, Close, Edit) =====
    cancelEventBtn.addEventListener("click", () => {
        document.getElementById("eventFormModal").classList.remove("active");
        clearAddEventForm();
    });
    cancelEditEventBtn.addEventListener("click", () => {
        document.getElementById("editEventModal").classList.remove("active");
    });

    closeDetailsBtn.addEventListener("click", () => {
        document.getElementById("eventDetailsModal").classList.remove("active");
    });

    // ===== Edit Event Logic =====
    document.getElementById("editEventBtn")?.addEventListener("click", () => {
        document.getElementById("editEventModal").classList.add("active");
        editEventTitle.value = selectedEvent.title;
        editEventCategory.value = selectedEvent.extendedProps.category || "General";
    });

    saveEditEventBtn.addEventListener("click", () => {
        const newTitle = editEventTitle.value.trim();
        const newCategory = editEventCategory.value;

        if (!newTitle || !newCategory) {
            showToast("All fields required", false);
            return;
        }

        //Edit event
        fetch(`/edit_event/${selectedEvent.id}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({title: newTitle, category: newCategory})
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    selectedEvent.setProp("title", newTitle);
                    selectedEvent.setExtendedProp("category", newCategory);
                    document.getElementById("editEventModal").classList.remove("active");
                    showToast("Event updated!");
                } else {
                    showToast("Error updating event", false);
                }
            });
    });

    // ===== Delete Event Confirmation =====
    deleteEventBtn?.addEventListener("click", () => {
        deleteEventContainer.style.display = "block";
        document.querySelector(".event-action-buttons")?.style.setProperty("display", "none");
    });

    confirmDeleteEventBtn.addEventListener("click", () => {

        //Delete event
        fetch("/delete_event/" + selectedEvent.id, {
            method: "DELETE"
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    selectedEvent.remove();
                    hideAllForms();
                    showToast("Event deleted.");
                } else {
                    showToast("Failed to delete event", false);
                }
            });
    });

    cancelDeleteEventBtn.addEventListener("click", () => {
        deleteEventContainer.style.display = "none";
        document.querySelector(".event-action-buttons")?.style.setProperty("display", "flex");
    });

    // ===== Utility: Reset Event Form =====
    function clearAddEventForm() {
        eventTitleInput.value = "";
        eventTimeInput.value = "";
        eventCategoryInput.value = "General";
        eventDateInput.value = "";
    }

    // ===== Trigger: Open Add Event Form for Selected Date =====
    window.openEventFormFromDate = function () {
        const selectedDate = document.getElementById("selectedDateStorage").value;
        document.getElementById("eventDate").value = selectedDate;
        document.getElementById("dateOptionsModal").classList.remove("active");
        document.getElementById("eventFormModal").classList.add("active");
        document.getElementById("eventTitle").focus();
    };

    // ===== Trigger: Open Mood Tracker for Selected Date =====
    window.openMoodTrackerFromDate = function () {
        const selectedDate = document.getElementById("selectedDateStorage").value;
        document.getElementById("calendarMoodDate").value = selectedDate;
        document.getElementById("moodDateLabel").innerText = "Logging for: " + new Date(selectedDate).toDateString();
        document.getElementById("dateOptionsModal").classList.remove("active");
        document.getElementById("moodTrackerModal").classList.add("active");
    };

    // ===== Utility: Clear Mood Entry Form =====
    function clearMoodForm() {
        document.querySelectorAll("#moodButtons .btn, #habitButtons .btn").forEach(btn => btn.classList.remove("active"));
        document.getElementById("symptomNotes").value = "";
    }

    // ===== Event Filtering Listeners =====
    searchEventInput.addEventListener("input", applyFilters);
    categoryFilter.addEventListener("change", applyFilters);
});