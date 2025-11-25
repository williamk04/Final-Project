from firebase_config import db
from vehicle_model import Vehicle
from datetime import datetime, timezone

RATE_PER_MINUTE = 1000
OVERTIME_FEE_PER_MIN = 5000

def now_dt():
    return datetime.now(timezone.utc)

def now_iso():
    return now_dt().isoformat()

def save_vehicle_entry(plate_text, image_url):
    try:
        current_dt = now_dt()
        current_iso = current_dt.isoformat()

        # 1️⃣ Kiểm tra xe đang trong bãi
        existing = db.collection("vehicles") \
            .where("license_plate", "==", plate_text) \
            .where("status", "==", "in") \
            .limit(1).get()
        if existing:
            return None, f"Vehicle {plate_text} already inside"

        # 2️⃣ Kiểm tra reservation hợp lệ
        reservations = db.collection("reservations") \
            .where("plateNumber", "==", plate_text) \
            .where("status", "==", "reserved") \
            .limit(10).get()

        active_res = None
        for r in reservations:
            res_data = r.to_dict()
            start_dt = res_data["startTime"]  # DatetimeWithNanoseconds
            end_dt = res_data["endTime"]

            if start_dt <= current_dt <= end_dt:
                active_res = (r.id, res_data)
                break

        if active_res:
            res_id, res_data = active_res
            db.collection("reservations").document(res_id).update({
                "status": "checked_in",
                "checkInTime": current_iso
            })

            vehicle = Vehicle(
                license_plate=plate_text,
                image_url=image_url,
                entry_time=current_dt,
                status="in"
            )
            data = vehicle.to_dict()
            data.update({
                "entry_time": current_iso,
                "is_reserved": True,
                "reservation_id": res_id
            })
            doc_ref = db.collection("vehicles").add(data)[1]
            return {"_id": doc_ref.id, **data}, None

        # 3️⃣ Xe vãng lai
        vehicle = Vehicle(
            license_plate=plate_text,
            image_url=image_url,
            entry_time=current_dt,
            status="in"
        )
        data = vehicle.to_dict()
        data.update({
            "entry_time": current_iso,
            "is_reserved": False
        })
        doc_ref = db.collection("vehicles").add(data)[1]
        return {"_id": doc_ref.id, **data}, None

    except Exception as e:
        print("save_vehicle_entry error:", e)
        return None, str(e)

def update_vehicle_exit(plate_text, exit_image_url):
    try:
        current_dt = now_dt()
        current_iso = current_dt.isoformat()

        query = db.collection("vehicles") \
            .where("license_plate", "==", plate_text) \
            .where("status", "==", "in") \
            .limit(1).get()
        if not query:
            return None

        doc = query[0]
        data = doc.to_dict()

        entry_dt = datetime.fromisoformat(data["entry_time"].replace("Z", "+00:00"))
        duration_minutes = int((current_dt - entry_dt).total_seconds() / 60)

        # --- Xe đặt chỗ ---
        if data.get("is_reserved") and data.get("reservation_id"):
            res_id = data["reservation_id"]
            res_ref = db.collection("reservations").document(res_id)
            res_doc = res_ref.get()

            if res_doc.exists:
                res = res_doc.to_dict()
                end_dt = res["endTime"]  # trực tiếp so sánh với datetime

                overtime = max(0, int((current_dt - end_dt).total_seconds() / 60) - 5)
                overtime_fee = overtime * OVERTIME_FEE_PER_MIN

                res_ref.update({
                    "status": "checked_out",
                    "checkOutTime": current_iso,
                    "overtimeFee": overtime_fee,
                    "actualTotalFee": res.get("paidFee", 0) + overtime_fee
                })
        else:
            # --- Xe vãng lai ---
            fee = duration_minutes * RATE_PER_MINUTE
            doc.reference.update({"fee": fee})

        doc.reference.update({
            "status": "out",
            "exit_time": current_iso,
            "exit_image_url": exit_image_url,
            "duration_minutes": duration_minutes
        })

        data.update({
            "status": "out",
            "exit_time": current_iso,
            "exit_image_url": exit_image_url,
            "duration_minutes": duration_minutes
        })
        return {"_id": doc.id, **data}

    except Exception as e:
        print("update_vehicle_exit error:", e)
        return None

def get_all_vehicle_records():
    vehicles = []
    for doc in db.collection("vehicles").stream():
        vehicles.append(doc.to_dict())
    return vehicles
