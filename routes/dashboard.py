import random, json

from bson import ObjectId
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request

from routes.auth import users_collection
from security.db import db_instance  # Ensure this connects to your MongoDB instance
import requests

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

# Access the database using db_instance
events_collection = db_instance.get_collection("events")  # Creates "events" collection
users_collection = db_instance.get_collection("users")

@dashboard_bp.route("/dashboard")
def dashboard():
    """Render the dashboard page with chat history, health tips, reminders, and news."""
    if "user_id" not in session:  # ✅ If user is not logged in, redirect to login
     return render_template("login.html")

    chat_history = get_chat_history(session["email"])
    health_tip = random.choice(HEALTH_TIPS)  # Randomly pick a health tip
    reminders = get_events()
    health_news = get_health_news()

    return render_template(
        "dashboard.html",
        users=users_collection.find_one({"_id": ObjectId(session["user_id"])}),
        chat_history=chat_history,
        health_tip=health_tip,
        reminders=reminders,
        health_news=health_news
    )


# Dummy Health Tips (You can store them in the DB instead)
HEALTH_TIPS = [
    "Stay hydrated and drink at least 8 glasses of water daily.",
    "Regular exercise improves mental and physical health.",
    "A balanced diet with fruits and vegetables is key to wellness.",
    "Sleep at least 7-8 hours to maintain a healthy immune system.",
    "Practice mindfulness to reduce stress and anxiety."
]


@dashboard_bp.route("/toggle_health_tips", methods=["POST"])
def toggle_health_tips():
    """Enable or disable health tips."""
    session["show_health_tips"] = not session.get("show_health_tips", True)
    return jsonify({"status": "success", "show_health_tips": session["show_health_tips"]})


# Fetch chat history from MongoDB
def get_chat_history(user_email):
    """Fetch chat history from MongoDB based on the logged-in user."""
    chat_collection = db_instance.get_collection("chat_history")
    user_chat = chat_collection.find_one({"email": user_email})  # ✅ Match logged-in user

    if user_chat and "chat_history" in user_chat:
        return user_chat["chat_history"]  # ✅ Ensure returning actual chat list

    return []

# Fetch health-related news from an API
def get_health_news():
    try:
        news_api_url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": "health",
            "language": "en",
            "apiKey": "your_news_api_key"  # Replace with your actual NewsAPI key
        }
        response = requests.get(news_api_url, params=params)
        news_data = response.json()
        return news_data.get("articles", [])[:5]  # Get top 5 health news articles
    except Exception as e:
        print(f"Error fetching health news: {e}")
        return []


@dashboard_bp.route("/add_event", methods=["POST"])
def add_event():
    """Add an event for the logged-in user."""
    if "email" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    data = request.json
    if not data or "title" not in data or "date" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    user_email = session["email"]
    existing_record = events_collection.find_one({"email": user_email})

    new_event = {
        "_id": ObjectId(),  # Store ObjectId properly
        "title": data["title"],
        "date": data["date"]
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


@dashboard_bp.route("/get_events", methods=["GET"])
def get_events():
    """Fetch events for the logged-in user."""
    if "email" not in session:
        return jsonify([])

    user_email = session["email"]
    user_record = events_collection.find_one({"email": user_email})

    if not user_record or "events" not in user_record:
        return jsonify([])

    return jsonify([
        {
            "id": str(event["_id"]) if isinstance(event["_id"], ObjectId) else event["_id"],
            "title": event["title"],
            "start": event["date"]
        }
        for event in user_record["events"]
    ])


@dashboard_bp.route("/edit_event/<event_id>", methods=["PUT"])
def edit_event(event_id):
    """Edit an event title."""
    if "email" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    user_email = session["email"]
    data = request.json
    new_title = data.get("title")

    if not new_title:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        events_collection.update_one(
            {"email": user_email, "events._id": ObjectId(event_id)},
            {"$set": {"events.$.title": new_title}}
        )
        return jsonify({"status": "success", "message": "Event updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@dashboard_bp.route("/delete_event/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Delete an event."""
    if "email" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    user_email = session["email"]

    try:
        event_object_id = ObjectId(event_id)  # ✅ Convert event_id to ObjectId
    except:
        return jsonify({"status": "error", "message": "Invalid event ID format"}), 400

    result = events_collection.update_one(
        {"email": user_email, "events._id": event_object_id},  # ✅ Match ObjectId
        {"$pull": {"events": {"_id": event_object_id}}}  # ✅ Pull event by ObjectId
    )

    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "Event deleted"})
    else:
        return jsonify({"status": "error", "message": "Event not found or already deleted"}), 404
