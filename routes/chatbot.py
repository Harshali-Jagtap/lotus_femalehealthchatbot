import json
import random
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from security.db import db_instance
from models.biobert import BioBERT
from models.clinicalbert import ClinicalBERT
from models.drugbank_parser import DrugBankParser
from models.medquad import MedQuAD
from routes.auth import  users_collection
from models.t5_summarizer import T5Simplifier
from models.openAI import OpenAIAssistant

# Load AI models
t5_simplifier = T5Simplifier()
medquad = MedQuAD()
biobert = BioBERT()
clinicalbert = ClinicalBERT()
drugbank = DrugBankParser()

chatbot_bp = Blueprint("chatbot", __name__, template_folder="templates")

# Save chat history in MongoDB
chat_collection = db_instance.get_collection("chat_history")


@chatbot_bp.route("/chatbot")
def chatbot():
    """Renders the chatbot interface with user details."""
    if "email" not in session:
        return redirect("/login")

    # Fetch user details from MongoDB
    user = users_collection.find_one({"email": session["email"]})
    return render_template("chatbot.html", user=user)


# In chatbot.py, update process_user_query():
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


def save_chat_history(user_email, user_message, bot_response):
    """Stores user chat history in MongoDB."""
    try:
        # Find the user in chat history collection
        user_chat = chat_collection.find_one({"email": user_email})

        # Structure for new chat entry
        new_chat = {"user_message": user_message, "bot_response": bot_response}

        if user_chat:
            # If user exists, append new chat to the chat array
            chat_collection.update_one(
                {"email": user_email},
                {"$push": {"chat_history": new_chat}}
            )
        else:
            # If new user, create a new document
            chat_collection.insert_one({
                "email": user_email,
                "chat_history": [new_chat]
            })
    except Exception as e:
        print(f"❌ Error saving chat history: {str(e)}")


# @chatbot_bp.route("/chat", methods=["POST"])
# def chat():
#     user_message = request.json.get("message", "").lower().strip()
#     raw_response = None
#
#     # Step 1: Check if the query is MEDICAL
#     is_medical = any(keyword in user_message for keyword in
#                      ["symptom", "pain", "drug", "fever", "hypertension", "dose"])
#
#     if is_medical:
#         # Existing priorities 1-4
#         medquad_response = medquad.search_medquad(user_message)
#         if medquad_response:
#             raw_response = medquad_response
#
#         if not raw_response:
#             drug_response = drugbank.get_drug_details(user_message)
#             if drug_response and "No data" not in drug_response:
#                 raw_response = drug_response
#
#         if not raw_response and any(keyword in user_message for keyword in ["symptom", "pain", "ache"]):
#             raw_response = clinicalbert.analyze_symptoms(user_message)
#
#         if not raw_response:
#             raw_response = biobert.answer_question(user_message)
#
#     # New: Fallback to OpenAI if no valid response
#     else:
#         try:
#             openai_assistant = OpenAIAssistant()
#             raw_response = openai_assistant.get_safe_response(user_message)
#         except Exception as e:
#             raw_response = "I couldn't find an answer. Please try another question."
#
#         # Simplify only medical responses
#     if is_medical and raw_response:
#         simplified = t5_simplifier.simplify(raw_response)
#     else:
#         simplified = raw_response  # Return OpenAI's already-simple response
#
#     return jsonify({"response": simplified})


@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower().strip()
    raw_response = None
    print(f"\n🔍 User Query: '{user_message}'")

    # Step 1: Check if the query is MEDICAL
    is_medical = any(keyword in user_message for keyword in
                     ["symptom", "pain", "drug", "fever", "hypertension", "dose"])
    print(f"🏥 Medical Query? {'✅' if is_medical else '❌'}")

    if is_medical:
        print("\n🩺 Starting Medical Pipeline:")
        # Priority 1: MedQuAD
        medquad_response = medquad.search_medquad(user_message)
        if medquad_response:
            print(f"1️⃣ MedQuAD Answer: {medquad_response[:100]}...")
            raw_response = medquad_response
        else:
            print("1️⃣ MedQuAD: ❌ No match")

        # Priority 2: DrugBank
        if not raw_response:
            drug_response = drugbank.get_drug_details(user_message)
            if drug_response and "No data" not in drug_response:
                print(f"2️⃣ DrugBank Answer: {drug_response[:100]}...")
                raw_response = drug_response
            else:
                print("2️⃣ DrugBank: ❌ No match")

        # Priority 3: ClinicalBERT
        if not raw_response and any(keyword in user_message for keyword in ["symptom", "pain", "ache"]):
            print("3️⃣ Trying ClinicalBERT...")
            raw_response = clinicalbert.analyze_symptoms(user_message)
            print(f"ClinicalBERT Answer: {raw_response[:100]}..." if raw_response else "3️⃣ ClinicalBERT: ❌ No match")

        # Priority 4: BioBERT
        if not raw_response:
            print("4️⃣ Trying BioBERT...")
            raw_response = biobert.answer_question(user_message)
            print(f"BioBERT Answer: {raw_response[:100]}..." if raw_response else "4️⃣ BioBERT: ❌ No match")

    # Non-medical path
    else:
        print("\n🌐 Non-Medical Query Path:")
        try:
            print("🤖 Asking OpenAI...")
            openai_assistant = OpenAIAssistant()
            raw_response = openai_assistant.get_safe_response(user_message)
            print(f"OpenAI Response: {raw_response[:100]}...")
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            raw_response = "I couldn't find an answer. Please try another question."

    # Response processing
    print("\n🔧 Processing Response:")
    if raw_response:
        if is_medical:
            print("⚕️ Simplifying medical response...")
            simplified = t5_simplifier.simplify(raw_response)
        else:
            simplified = raw_response
        print(f"📤 Final Response: {simplified[:120]}...")
    else:
        simplified = "I couldn't find an answer. Please try another question."
        print("📤 No valid responses found")

    return jsonify({"response": simplified})