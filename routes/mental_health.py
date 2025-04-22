# ===== Flask Blueprint: Mental Health Page =====
from flask import Blueprint, render_template

# ========== BLUEPRINT ==========
mental_health_bp = Blueprint("mental_health", __name__)


# ===== Route: /mental_health =====
@mental_health_bp.route("/mental_health")
def mental_health():
    return render_template("mental_health.html")
