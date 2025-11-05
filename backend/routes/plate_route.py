from flask import Blueprint, request, jsonify
from services.plate_service import detect_and_read_plate
from services.firebase_service import save_vehicle_entry
from services.firebase_service import update_vehicle_exit
import os, uuid
from services.plate_service import UPLOAD_FOLDER
plate_bp = Blueprint("plate_bp", __name__)

@plate_bp.route("/entry", methods=["POST"])
def entry_vehicle():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    plates, image_path = detect_and_read_plate(file)

    if not plates:
        return jsonify({"success": False, "message": "No plate detected"}), 200

    # Chọn biển số có confidence cao nhất
    best_plate = max(plates, key=lambda x: x["confidence"])

    # Lưu vào Firebase
    record = save_vehicle_entry(best_plate["text"], image_path)
    

    return jsonify({
        "success": True,
        "detected_plate": best_plate,
        "firebase_record": record
    }), 200

@plate_bp.route("/exit", methods=["POST"])
def exit_vehicle():
    if 'exit_image' not in request.files:
        return jsonify({"success": False, "message": "Exit image missing"}), 400

    exit_file = request.files['exit_image']

    # Detect OCR biển số
    plates, _ = detect_and_read_plate(exit_file)
    if not plates:
        return jsonify({"success": False, "message": "No plate detected in exit image"}), 400

    best_plate = max(plates, key=lambda x: x["confidence"])
    plate_text = best_plate["text"]

    # Lưu ảnh exit
    exit_filename = f"{uuid.uuid4().hex}.jpg"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    exit_path = os.path.join(UPLOAD_FOLDER, exit_filename)
    exit_file.save(exit_path)
    exit_url = f"/{exit_path.replace('\\', '/')}"

    # Update Firebase
    record = update_vehicle_exit(plate_text, exit_url)
    if not record:
        return jsonify({"success": False, "message": f"Vehicle {plate_text} not found or already exited"}), 404

    return jsonify({
        "success": True,
        "message": f"Vehicle {plate_text} exited",
        "vehicle": record,
        "detected_plate": best_plate
    }), 200