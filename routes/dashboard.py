# ========== IMPORTS ==========
import random, json
from datetime import date, datetime
from bson import ObjectId
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from routes.auth import users_collection
from security.db import db_instance
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
from textblob import TextBlob

# ========== BLUEPRINT ==========
dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

# ========== DB SETUP ==========
events_collection = db_instance.get_collection("events")  # Creates "events" collection
users_collection = db_instance.get_collection("users")
mood_collection = db_instance.get_collection("mood_tracker")


# ========== SETUP ==========
@dashboard_bp.route("/dashboard")
def dashboard():
    """Render the dashboard page with chat history, health tips, reminders, and news."""
    if "user_id" not in session:  # If a user is not logged in, redirect to login
        return render_template("login.html")

    chat_history = get_chat_history(session["email"])
    reminders = get_events()

    return render_template(
        "dashboard.html",
        users=users_collection.find_one({"_id": ObjectId(session["user_id"])}),
        chat_history=chat_history,
        reminders=reminders
    )


# ========== CHAT HISTORY ==========
# Get chat history
def get_chat_history(user_email):
    """Fetch chat history from MongoDB based on the logged-in user."""
    chat_collection = db_instance.get_collection("chat_history")
    user_chat = chat_collection.find_one({"email": user_email})  # Match logged-in user

    if user_chat and "chat_history" in user_chat:
        return user_chat["chat_history"]  # Ensure returning actual chat list

    return []


# Delete Chat History
@dashboard_bp.route("/delete_chat_history", methods=["DELETE"])
def delete_chat_history():
    if "email" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    chat_collection = db_instance.get_collection("chat_history")
    result = chat_collection.delete_one({"email": session["email"]})

    if result.deleted_count > 0:
        return jsonify({"status": "success", "message": "Chat history deleted"})
    else:
        return jsonify({"status": "error", "message": "No history found to delete"}), 404


# ========== CALENDAR ROUTES ==========
@dashboard_bp.route("/calendar")
def calendar_view():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("calendar.html")


# Add event
@dashboard_bp.route("/add_event", methods=["POST"])
def add_event():
    if "email" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    data = request.json
    title = data.get("title")
    date = data.get("date")
    category = data.get("category", "General")

    if not title or not date:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    user_email = session["email"]
    existing_record = events_collection.find_one({"email": user_email})

    new_event = {
        "_id": ObjectId(),
        "title": title,
        "date": date,
        "category": category
    }

    if existing_record:
        events_collection.update_one(
            {"email": user_email},
            {"$push": {"events": new_event}}
        )
    else:
        events_collection.insert_one({
            "email": user_email,
            "events": [new_event]
        })

    return jsonify({"status": "success",
                    "event": {"id": str(new_event["_id"]), "title": new_event["title"], "start": new_event["date"]}})


# Get event
@dashboard_bp.route("/get_events", methods=["GET"])
def get_events():
    """Fetch events for the logged-in user."""
    if "email" not in session:
        return jsonify([])

    start = request.args.get("start")
    end = request.args.get("end")

    event_collection = db_instance.get_collection("events")
    mood_collection = db_instance.get_collection("mood_tracker")

    doc = event_collection.find_one({"email": session["email"]})
    events = []

    # 🎯 Filter and append actual calendar events
    if doc and "events" in doc:
        for event in doc["events"]:
            event_date = event.get("date")

            # ✅ Safely check the date is valid before comparing
            if isinstance(event_date, str) and start and end:
                if start <= event_date <= end:
                    events.append({
                        "id": str(event["_id"]),
                        "title": event["title"],
                        "start": event["date"],
                        "category": event.get("category", "General"),
                        "allDay": True,
                        "className": f"category-{event.get('category', 'general').lower()}"
                    })

    # 😊 Append mood emoji events
    mood_doc = mood_collection.find_one({"email": session["email"]})
    if mood_doc and "moods" in mood_doc:
        for mood_entry in mood_doc["moods"]:
            mood_date = mood_entry.get("date")
            if isinstance(mood_date, str):
                events.append({
                    "id": f"mood-{mood_date}",
                    "title": "😊",
                    "start": mood_date,
                    "allDay": True,
                    "className": "mood-symbol"
                })

    return jsonify(events)


# Edit event
@dashboard_bp.route("/edit_event/<event_id>", methods=["PUT"])
def edit_event(event_id):
    """Edit title, category, or date of an event inside the events array."""
    if "email" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    data = request.json
    user_email = session["email"]

    updates = {}

    if "title" in data:
        updates["events.$.title"] = data["title"]
    if "category" in data:
        updates["events.$.category"] = data["category"]
    if "date" in data:
        updates["events.$.date"] = data["date"]

    if not updates:
        return jsonify({"status": "error", "message": "No update data provided"}), 400

    try:
        result = events_collection.update_one(
            {"email": user_email, "events._id": ObjectId(event_id)},
            {"$set": updates}
        )

        if result.modified_count > 0:
            return jsonify({"status": "success", "message": "Event updated"})
        else:
            return jsonify({"status": "error", "message": "Event not found or unchanged"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Delete event
@dashboard_bp.route("/delete_event/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Delete an event."""
    if "email" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    user_email = session["email"]

    try:
        event_object_id = ObjectId(event_id)  # Convert event_id to ObjectId
    except:
        return jsonify({"status": "error", "message": "Invalid event ID format"}), 400

    result = events_collection.update_one(
        {"email": user_email, "events._id": event_object_id},  # Match ObjectId
        {"$pull": {"events": {"_id": event_object_id}}}  # Pull event by ObjectId
    )

    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "Event deleted"})
    else:
        return jsonify({"status": "error", "message": "Event not found or already deleted"}), 404


# ========== MOOD TRACKER ROUTES ==========
# Store User Mood
@dashboard_bp.route("/save_mood_entry", methods=["POST"])
def save_mood_entry():
    if "email" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    data = request.json
    new_moods = data.get("moods", [])
    new_habits = data.get("habits", [])
    note_text = data.get("notes", "").strip()
    email = session["email"]
    date = data.get("date")

    # Extract symptoms from notes using TextBlob
    new_symptoms = []
    if note_text:
        blob = TextBlob(note_text)
        new_symptoms = blob.noun_phrases

    # Block future entries
    today = datetime.today().date()
    submitted_date = datetime.strptime(date, "%Y-%m-%d").date()

    if submitted_date > today:
        return jsonify({"status": "error", "message": "Future mood entries are not allowed."}), 400

    doc = mood_collection.find_one({"email": email})

    if not doc:
        # New user document
        mood_collection.insert_one({
            "email": email,
            "moods": [{
                "date": date,
                "mood": new_moods,
                "habits": new_habits,
                "notes": note_text,
                "symptoms": new_symptoms
            }]
        })
        return jsonify({"status": "success", "message": "Mood entry saved!"})

    # Check if the date already exists in moods
    for i, entry in enumerate(doc.get("moods", [])):
        if entry["date"] == date:
            # Merge with existing values
            merged_moods = list(set(entry.get("mood", []) + new_moods))
            merged_habits = list(set(entry.get("habits", []) + new_habits))

            mood_collection.update_one(
                {"email": email, f"moods.{i}.date": date},
                {"$set": {
                    f"moods.{i}.mood": merged_moods,
                    f"moods.{i}.habits": merged_habits,
                    f"moods.{i}.notes": note_text,
                    f"moods.{i}.symptoms": new_symptoms
                }}
            )
            return jsonify({"status": "success", "message": "Mood entry updated!"})

    # Else, push new entry for today
    mood_collection.update_one(
        {"email": email},
        {"$push": {"moods": {
            "date": date,
            "mood": new_moods,
            "habits": new_habits,
            "notes": note_text,
            "symptoms": new_symptoms
        }}}
    )

    return jsonify({"status": "success", "message": "Mood entry saved!"})


# Get User Mood
@dashboard_bp.route("/get_mood_entry", methods=["GET"])
def get_mood_entry():
    if "email" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    date = request.args.get("date")
    if not date:
        return jsonify({"status": "error", "message": "Missing date"}), 400

    doc = mood_collection.find_one({"email": session["email"]})
    if not doc or "moods" not in doc:
        return jsonify({"status": "not_found"})

    # Find mood by date
    for entry in doc["moods"]:
        if entry["date"] == date:
            return jsonify({
                "status": "success",
                "mood": entry["mood"],
                "habits": entry["habits"]
            })

    return jsonify({"status": "not_found"})


# Delete User mood
@dashboard_bp.route("/delete_mood_entry", methods=["DELETE"])
def delete_mood_entry():
    if "email" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    date = request.args.get("date")
    if not date:
        return jsonify({"status": "error", "message": "Missing date"}), 400

    result = mood_collection.update_one(
        {"email": session["email"]},
        {"$pull": {"moods": {"date": date}}}
    )

    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "Entry deleted"})
    else:
        return jsonify({"status": "error", "message": "Entry not found"}), 404


# Get all moods
@dashboard_bp.route("/get_all_moods", methods=["GET"])
def get_all_moods():
    if "email" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    doc = mood_collection.find_one({"email": session["email"]})
    if not doc or "moods" not in doc:
        return jsonify({"status": "success", "moods": []})

    mood_data = doc["moods"]
    return jsonify({"status": "success", "moods": mood_data})


# ========== MOOD INSIGHT & PREDICTION ==========
@dashboard_bp.route("/get_mood_insights")
def get_mood_insights():
    """
    Combines:
    - Frequency-based mood counts
    - Rule-based interpretation
    - ML-based prediction using Logistic Regression
    """
    if "email" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    doc = mood_collection.find_one({"email": session["email"]})
    if not doc or "moods" not in doc:
        return jsonify({"status": "success", "insights": {}})

    from collections import Counter
    mood_counts = Counter()
    daily_data = []

    for entry in doc["moods"]:
        for mood in entry.get("mood", []):
            mood_counts[mood] += 1
        daily_data.append({
            "date": entry["date"],
            "moods": entry["mood"]
        })

    # Predictive Rule-based Summary
    recent_5 = sorted(daily_data, key=lambda x: x["date"], reverse=True)[:5]
    recent_moods = sum((x["moods"] for x in recent_5), [])
    prediction = "You're doing well!"
    if recent_moods.count("sad") >= 3:
        prediction = "You've been feeling sad a lot lately. Consider relaxing or talking to someone."

    # ML-based Prediction: Sad/Anxious Likelihood Tomorrow
    if len(daily_data) >= 7:
        X = []
        y = []

        for i, d in enumerate(daily_data):
            row = [
                "sad" in d["moods"],
                "anxious" in d["moods"],
                "happy" in d["moods"]
            ]
            X.append(row)
            # Label: was next day sad or anxious?
            if i < len(daily_data) - 1:
                next_moods = daily_data[i + 1]["moods"]
                y.append(1 if "sad" in next_moods or "anxious" in next_moods else 0)

        if len(X) > len(y):
            X = X[:-1]

        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression()
        model.fit(X, y)

        last_day = daily_data[-1]
        test_features = [[
            "sad" in last_day["moods"],
            "anxious" in last_day["moods"],
            "happy" in last_day["moods"]
        ]]

        prob = model.predict_proba(test_features)[0][1]
        prediction += f" Based on the model, there's a {round(prob * 100)}% chance of sadness/anxiety tomorrow."

    return jsonify({
        "status": "success",
        "insights": {
            "counts": dict(mood_counts),
            "prediction": prediction
        }
    })


# ========== MOOD BY DATE (for editing/viewing) ==========
@dashboard_bp.route('/get_mood_by_date')
def get_mood_by_date():
    email = session.get("email")
    date = request.args.get("date")
    mood_collection = db_instance.get_collection("mood_tracker")
    entry = mood_collection.find_one({"email": email, "moods.date": date}, {"moods.$": 1})
    if entry and "moods" in entry:
        return jsonify(entry["moods"][0])
    return jsonify({})
