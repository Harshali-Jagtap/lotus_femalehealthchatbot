# routes/gdpr.py

from flask import Blueprint, render_template, session, redirect, url_for, request

# ===== GDPR Blueprint =====
gdpr_bp = Blueprint("gdpr", __name__, template_folder="templates")


# ===== Route: GDPR Consent Page =====
@gdpr_bp.route("/privacy")
def privacy_notice():
    """
    Renders the GDPR consent information page.
    """
    return render_template("privacy.html")


# ===== Route: Submit Consent =====
@gdpr_bp.route("/consent", methods=["POST"])
def consent():
    """
    Saves GDPR consent in user session and redirects to home.
    """
    session["gdpr_consent"] = True
    return redirect(url_for("index.home"))
