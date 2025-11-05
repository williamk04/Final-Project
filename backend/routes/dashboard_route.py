from flask import Blueprint, jsonify
from services.firebase_service import get_all_vehicle_records
from services.dashboard_service import get_dashboard_summary

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/summary", methods=["GET"])
def dashboard_summary():
    try:
        vehicles = get_all_vehicle_records()
        data = get_dashboard_summary(vehicles)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
