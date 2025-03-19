import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, render_template, session, redirect, url_for
from routes.auth import auth_bp
from routes.chatbot import chatbot_bp
from routes.dashboard import dashboard_bp
from routes.index import index_bp
from routes.about import about_bp
import warnings
import logging
from transformers import logging as transformers_logging


app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

# Configure OpenAI
app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY missing in .env!")

# Suppress all warnings
warnings.filterwarnings("ignore", category=UserWarning)
transformers_logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(index_bp)
app.register_blueprint(about_bp)

def handle_gdpr_compliance():
    """Check GDPR requirements before processing requests"""
    # Implement your GDPR compliance checks here
    pass
@app.route("/")
def home():
    # this is for login the chatbot MAIN PART DONOT CHANGE ANYTHING
    # # Always show the homepage, regardless of session state
    # if "username" in session:
    #    session.clear()  # Clear the session when the homepage is accessed

    #return render_template("index.html")

    #chatbot within login FOR TESTING NOW
    # Redirect logged-in users to the chatbot page
    if "username" in session:
        return redirect(url_for("chatbot.chatbot_page"))
    # Show the homepage for non-logged-in users
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    print("✅ Starting Flask server...")  # ✅ Add this to check if Flask starts
    app.run(debug=True, use_reloader=False)
