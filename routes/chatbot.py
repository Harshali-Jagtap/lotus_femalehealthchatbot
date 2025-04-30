# ========== IMPORTS ==========
# Models, routing, user session handling, database
import re, random, json
from threading import Thread
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from security.db import db_instance
from models.biobert import BioBERT
from models.clinicalbert import ClinicalBERT
from models.drugbank import DrugBank
from models.medquad import MedQuAD
from routes.auth import users_collection
from models.t5_summarizer import T5Simplifier
from models.openAI import OpenAIAssistant
from models.bart_classifier import BARTClassifier
from datetime import datetime

# ========== LOAD ALL MODELS ==========
# NLP pipelines: DrugBank, MedQuAD, ClinicalBERT, BioBERT, BART, OpenAI, etc.
t5_simplifier = T5Simplifier()
medquad = MedQuAD()
biobert = BioBERT()
clinicalbert = ClinicalBERT()
drugbank = DrugBank(simplifier=t5_simplifier)
bart_classifier = BARTClassifier()
openai_assistant = OpenAIAssistant()

# ========== BLUEPRINT & DB ==========
chatbot_bp = Blueprint("chatbot", __name__, template_folder="templates")
chat_collection = db_instance.get_collection("chat_history")


# ========== CHATBOT PAGE ROUTE: /chatbot ==========
@chatbot_bp.route("/chatbot")
def chatbot():
    """Renders the chatbot interface with user details."""
    if "email" not in session:
        return redirect("/login")

    # Fetch user details from MongoDB
    user = users_collection.find_one({"email": session["email"]})
    return render_template("chatbot.html", user=user)


# ========== CHAT HISTORY ==========
def save_chat_history(user_email, user_message, bot_response):
    """Stores user chat history in MongoDB."""
    try:
        # Find the user in a chat history collection
        user_chat = chat_collection.find_one({"email": user_email})

        # Structure for new chat entry
        new_chat = {"user_message": user_message,
                    "bot_response": bot_response,
                    "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p")
                    }

        if user_chat:
            # If a user exists, append new chat to the chat array
            chat_collection.update_one(
                {"email": user_email},
                {"$push": {"chat_history": new_chat}}
            )
        else:
            # If a new user, create a new document
            chat_collection.insert_one({
                "email": user_email,
                "chat_history": [new_chat]
            })
    except Exception as e:
        print(f"Error saving chat history: {str(e)}")


# ========== TEXT PROCESSING HELPERS ==========
# Process user a query to required question
def process_user_query(user_input):
    # 1. DrugBank (exact match)
    drug_info = drugbank.get_drug_details(user_input)
    if drug_info and "No data" not in drug_info:
        return drug_info

    # 2. MedQuAD (semantic search)
    medquad_response = medquad.search_medquad(user_input)
    if medquad_response:
        return medquad_response

    # 3. BioBERT/ClinicalBERT (context-aware)
    if "symptom" in user_input.lower():
        context = "Common symptoms include fever, cough, fatigue, flu, headache, cold."
        return clinicalbert.analyze_symptoms(user_input, context)
    else:
        return biobert.answer_question(user_input, "General medical knowledge base.")

        # After getting raw_response from MedQuAD/DrugBank:
    simplified = t5_simplifier.simplify(raw_response)
    return simplified


# Empatheics repsonse from bot
def format_empathetic_response(raw):
    if not raw or len(raw.strip()) < 10:
        return raw  # Skip formatting if fallback or empty

    intro_phrases = [
        "Here's what I found for you:",
        "You're not alone — this is quite common.",
        "Let me help explain this for you:",
        "This might help you understand things better:",
        "Take a moment — here's a simplified explanation:"
    ]

    closing_phrases = [
        "Would you like to know more about symptoms, treatment, or causes?",
        "Feel free to ask if you want a simpler version.",
        "Let me know if you'd like related advice.",
        "I'm here to support you — just ask anything else.",
        "You're doing great. Ask anything you're unsure about."
    ]

    intro = random.choice(intro_phrases)
    closing = random.choice(closing_phrases)

    return f"{intro}\n\n{raw.strip()}\n\n{closing}"


def generate_dynamic_follow_up(user_message, bot_response=None):
    """
    Generates a helpful follow-up question based on the user's query and bot's previous answer.
    """
    prompt = f""" You are a medical assistant chatbot. Based on the user's message and your previous answer, generate a single, relevant follow-up question to continue the conversation. 
    Do not repeat the same answer. Be specific, helpful, and concise.
    User's message: "{user_message}"
    Your previous answer: "{bot_response if bot_response else ''}"
    Follow-up question:"""

    try:
        response = openai_assistant.get_safe_response(prompt)
        return response.strip().split('\n')[0]
    except:
        return "Would you like to know more about symptoms, treatment, or causes?"


# Starter word interpretation for a drug/medicine query
def extract_drug_name(text):
    patterns = [
        r"what is (.+)",
        r"tell me about (.+)",
        r"purpose of (.+)",
        r"use of (.+)",
        r"side effects of (.+)",
        r"dosage for (.+)",
        r"how is the dosage for (.+)",
        r"how to take (.+)",
        r"when to take (.+)",
        r"(.*)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return text.split()[-1]  # Fallback


# Fo text to be simlpe
def needs_simplification(text):
    if not text or len(text.split()) < 40:
        return False
    medical_terms = ["contraindication", "metabolized", "pharmacokinetics", "therapeutic", "diagnostic"]
    return any(term in text.lower() for term in medical_terms)


# Load mental health data
def load_mental_health_data():
    with open("data/mental_health.json", "r", encoding="utf-8") as file:
        return json.load(file)


mental_health_data = load_mental_health_data()


# Check for mental health query
def check_mental_health_query(user_message):
    user_message = user_message.lower()
    for entry in mental_health_data:
        if any(keyword in user_message for keyword in entry["keywords"]):
            print(f"Detected mental health category: {entry['category']}")
            return entry["response"]
    return None


# Prompt loading
def load_prompt_responses():
    with open("data/prompt_responses.json", "r", encoding="utf-8") as f:
        return json.load(f)


prompt_responses = load_prompt_responses()


# Static messages
def check_static_prompts(user_message):
    user_message = user_message.lower().strip()
    for item in prompt_responses:
        if user_message == item["prompt"]:
            return item["response"]
    return None


# Mental health support
@chatbot_bp.route("/mental-support", methods=["POST"])
def mental_support():
    topic = request.json.get("topic", "")
    prompt = f"""
            You are a compassionate wellness assistant. 
            Based on the topic "{topic}", provide 3 real support resources such as:
            
            - Calming music or playlists (if they want music)
            - Useful apps or articles (if general emotional support)
            - Mindfulness activities (e.g., breathing, journaling)
            
            Respond with just the list. Each line should be a separate recommendation.
            """
    try:
        response = openai_assistant.get_safe_response(prompt)
        lines = [line.strip() for line in response.strip().split("\\n") if line.strip()]
        return jsonify({"resources": lines})
    except Exception as e:
        print("OpenAI error in /mental-support:", e)
        return jsonify({"resources": ["⚠️ Sorry, something went wrong while fetching resources."]})


# Follow uup conversation
def is_follow_up_like(msg):
    """Only treat very short, vague replies as follow-ups."""
    msg = msg.lower().strip()
    word_count = len(msg.split())

    vague_starters = [
        "yes", "no", "maybe", "since", "today", "just now", "i have", "me too", "same",
        "what about", "how about", "and", "not really", "a bit", "a lot",
        "at rest", "while sleeping", "in the morning", "after eating", "sometimes", "during"
    ]

    # Only treat as follow-up if a message is short or clearly vague
    if word_count <= 4:
        return any(msg.startswith(w) or msg == w for w in vague_starters)
    return False


# For medical topics
def is_new_medical_topic(msg):
    """
    Returns True if the message looks like a new, self-contained query.
    """
    msg = msg.strip().lower()
    keywords = ["what is", "how to", "i have", "i feel", "why", "tell me about", "symptoms", "side effects", "cause",
                "can", "could", "should", "pain", "fever", "itchy", "scalp", "headache", "bleeding", "vomit"]
    return any(msg.startswith(k) for k in keywords) or len(msg.split()) > 4


# ========== ACTIVE CHAT ROUTE (CURRENT) ==========
@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    """
       Processes user messages and routes them through the appropriate pipeline:
       DrugBank → MedQuAD → Mental Health → ClinicalBERT → BioBERT → OpenAI
       Includes follow-up support and context tracking.
    """
    user_email = session.get("email")
    user_message = request.json.get("message", "").strip()
    is_prompt = request.json.get("is_prompt", False)

    try:
        print(f"User message: {user_message}")

        # Handle static prompt buttons
        if is_prompt:
            static_response = check_static_prompts(user_message)
            if static_response:
                return jsonify({"response": static_response, "follow_up": None})

        # Detect conversation context
        is_follow_up = is_follow_up_like(user_message) and session.get("last_followup")

        if is_new_medical_topic(user_message):
            print("New medical topic. Resetting follow-up context.")
            session["last_followup"] = None
            combined_message = user_message
        elif is_follow_up:
            last_bot_followup = session["last_followup"]
            combined_message = f"{last_bot_followup.strip().rstrip('?.,!')} {user_message}"
            print("🔗 Follow-up reply matched with last bot prompt:", combined_message)
        else:
            combined_message = user_message

        response = None

        # Returns to pipeline for new medical/wellbeing queries
        if not is_follow_up:
            # DrugBank
            drug_name = extract_drug_name(combined_message)
            response = drugbank.get_drug_details(drug_name)
            if response:
                print("DrugBank match")

            # MedQuAD
            if not response:
                response = medquad.search_medquad(combined_message)
                if response:
                    print("MedQuAD match")

            # Mental Health
            if not response:
                response = check_mental_health_query(combined_message)

            # ClinicalBERT
            symptom_keywords = ["pain", "symptom", "ache", "fever", "cough", "vomiting", "headache", "dizzy", "tired"]
            vague_prompts = ["symptoms", "advice", "tips", "help", "general", "what to do"]
            if (not response and
                    any(kw in combined_message.lower() for kw in symptom_keywords) and
                    len(combined_message.split()) > 4 and
                    not any(v in combined_message.lower() for v in vague_prompts)):
                print("🩺 Using ClinicalBERT")
                response = clinicalbert.analyze_symptoms(combined_message)
                if not response or len(response.strip()) < 15:
                    response = None

            # BioBERT
            female_keywords = ["period", "menstruation", "menstrual", "ovulation", "pregnancy", "fertility",
                               "uterus", "pcos", "birth control", "get periods"]
            if (not response and len(combined_message.split()) > 4 and not any(
                    w in combined_message.lower() for w in female_keywords)):
                print("Using BioBERT")
                response = biobert.answer_question(combined_message)
                if not response or len(response.strip()) < 15:
                    response = None
            else:
                print("Skipping BioBERT")

        else:
            print("Follow-up message — skipping MedQuAD, DrugBank, BERTs")

        # OpenAI fallback for all accepted topics or follow-ups
        if not response:
            print("Fallback to OpenAI (medical/wellbeing/follow-up only)...")

            if (
                    bart_classifier.is_medical_query(combined_message)
                    or check_mental_health_query(combined_message)
                    or any(word in combined_message.lower() for word in
                           ["relax", "meditate", "calm", "breathe", "anxious", "wellbeing", "mindfulness"])
                    or is_follow_up
            ):
                print("OpenAI allowed")
                response = openai_assistant.get_safe_response(combined_message)
                if not response or len(response.strip()) < 10:
                    response = "I'm sorry, I couldn't find a clear answer. Try rephrasing your question."
                response = format_empathetic_response(response)
            else:
                print("Rejected non-medical/wellbeing query")
                return jsonify({
                    "response": "⚠️ I can only answer medical or wellbeing-related queries.",
                    "follow_up": None
                })

        # Generate follow-up
        follow_up = generate_dynamic_follow_up(combined_message, response)
        session["last_followup"] = follow_up

        Thread(target=save_chat_history, args=(user_email, user_message, response)).start()

        return jsonify({
            "response": response,
            "follow_up": follow_up
        })

    except Exception as e:
        print(f"Error in chat route: {str(e)}")
        return jsonify({
            "response": "Sorry, something went wrong. Please try again later.",
            "follow_up": None
        })
