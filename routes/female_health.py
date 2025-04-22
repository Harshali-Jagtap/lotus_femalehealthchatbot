# ===== Flask Blueprint: Female Health Page =====
from flask import Blueprint, render_template

# ========== BLUEPRINT ==========
female_health_bp = Blueprint("female_health", __name__)


# ===== Route: /female_health =====
@female_health_bp.route("/female_health")
def female_health():
    return render_template("female_health.html")
