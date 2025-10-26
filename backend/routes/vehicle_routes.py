from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
import os
from bson import ObjectId
from utils.db import get_db
from services.vehicle_service import create_vehicle_record, update_vehicle_exit
from services.ai_service import detect_license_plate
from services.ocr_service import extract_text_from_plate

vehicle_bp = Blueprint("vehicle_bp", __name__)
db = get_db()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================================
# Helper: Convert ObjectId
# ================================
def convert_objectid(data):
    if data is None:
        return None
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    if isinstance(data, dict):
        return {
            key: str(value) if isinstance(value, ObjectId) else convert_objectid(value)
            for key, value in data.items()
        }
    return data


# -----------------------
# Vehicle Entry
# -----------------------
@vehicle_bp.route("/entry", methods=["POST"])
def vehicle_entry():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    detection = detect_license_plate(image_path)
    if not detection:
        return jsonify({"success": False, "message": "No plate detected"}), 400

    plate_text, image_url = extract_text_from_plate(
        image_path, detection, save_to_public=True, crop_name=f"plate_{file.filename}"
    )

    record = create_vehicle_record(db, plate_text, image_url)
    return jsonify({"success": True, "license_plate": plate_text, "data": record})


# -----------------------
# Vehicle Exit
# -----------------------
@vehicle_bp.route("/exit", methods=["POST"])
def vehicle_exit():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    detection = detect_license_plate(image_path)
    if not detection:
        return jsonify({"success": False, "message": "No plate detected"}), 400

    plate_text, _ = extract_text_from_plate(image_path, detection)
    record = update_vehicle_exit(db, plate_text, exit_image_url=image_path)

    if not record:
        return jsonify({"success": False, "message": "Vehicle not found or already exited"}), 404

    return jsonify({"success": True, "license_plate": plate_text, "data": record})

# ================================
# Get All Vehicles + Revenue
# ================================
@vehicle_bp.route("/vehicles", methods=["GET"])
def get_all_vehicles():
    vehicles = list(db["vehicles"].find())
    vehicles = convert_objectid(vehicles)

    vn_timezone = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_timezone)
    today_str = now_vn.strftime("%Y-%m-%d")

    today_revenue = 0
    revenue_by_day = {}  # 🔹 Tổng doanh thu từng ngày

    for v in vehicles:
        exit_time = v.get("exit_time")
        if not exit_time:
            continue

        # Convert exit_time về giờ Việt Nam
        exit_vn = exit_time.astimezone(vn_timezone)
        day_str = exit_vn.strftime("%Y-%m-%d")

        # Tính doanh thu hôm nay
        if day_str == today_str:
            today_revenue += v.get("fee", 0)

        # Tính doanh thu theo từng ngày
        revenue_by_day[day_str] = revenue_by_day.get(day_str, 0) + v.get("fee", 0)

    return jsonify({
        "success": True,
        "vehicles": vehicles,
        "todayRevenue": today_revenue,
        "revenueByDay": revenue_by_day  # 🔹 Trả về tổng doanh thu theo ngày
    })
