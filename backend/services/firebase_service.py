from firebase_config import db
from vehicle_model import Vehicle
from datetime import datetime, timezone

RATE_PER_MINUTE = 1000
OVERTIME_FEE_PER_MIN = 5000
GRACE_PERIOD = 5  # phút

def now_dt():
    return datetime.now(timezone.utc)

def now_iso():
    return now_dt().isoformat()


# ============================================================
# 1) LƯU XE VÀO — CHECK-IN
# ============================================================
def save_vehicle_entry(plate_text, image_url):
    try:
        current_dt = now_dt()
        current_iso = now_iso()

        
        # 1. Kiểm tra xe có đang trong bãi không
        
        existing = db.collection("vehicles") \
            .where("license_plate", "==", plate_text) \
            .where("status", "==", "in") \
            .limit(1).get()

        if existing:
            return None, f"Vehicle {plate_text} already inside"

        
        # 2. Kiểm tra reservation
        
        reservations = db.collection("reservations") \
            .where("plateNumber", "==", plate_text) \
            .where("status", "==", "reserved") \
            .limit(10).get()

        active_res = None

        for r in reservations:
            res_data = r.to_dict()
            start_dt = res_data["startTime"]
            end_dt = res_data["endTime"]

            
            # Nếu đến quá sớm
            
            if current_dt < start_dt:
                return None, f"Too early to check in. Reservation starts at {start_dt}"

           
            # Đúng thời gian thì gắn reservation
            
            if start_dt <= current_dt <= end_dt:
                active_res = (r.id, res_data)
                break

        
        # 3. XE ĐẶT CHỖ — CHECK IN
        
        if active_res:
            res_id, res_data = active_res

            # update reservation
            db.collection("reservations").document(res_id).update({
                "status": "checked_in",
                "checkInTime": current_iso
            })

            # tạo record xe
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

        
        # 4. XE VÃNG LAI
        
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



# 2) CẬP NHẬT XE RA — EXIT

def update_vehicle_exit(plate_text, exit_image_url):
    try:
        current_dt = now_dt()
        current_iso = now_iso()

        
        # 1. Tìm xe còn "in"
        
        query = db.collection("vehicles") \
            .where("license_plate", "==", plate_text) \
            .where("status", "==", "in") \
            .limit(1).get()

        if not query:
            return {
                "success": False,
                "message": f"Vehicle {plate_text} not found or already exited"
            }

        doc = query[0]
        data = doc.to_dict()

        entry_dt = datetime.fromisoformat(data["entry_time"].replace("Z", "+00:00"))
        duration_minutes = int((current_dt - entry_dt).total_seconds() / 60)

        
        # 2. XE ĐẶT CHỖ (RESERVED)
        
        if data.get("is_reserved") and data.get("reservation_id"):
            res_id = data["reservation_id"]
            res_ref = db.collection("reservations").document(res_id)
            res_doc = res_ref.get()

            if res_doc.exists:
                res = res_doc.to_dict()
                end_dt = res["endTime"]

                
                # Tính overtime
                
                overtime_minutes = max(0, int((current_dt - end_dt).total_seconds() / 60) - GRACE_PERIOD)
                overtime_fee = overtime_minutes * OVERTIME_FEE_PER_MIN

                actual_fee = res.get("paidFee", 0) + overtime_fee

                # update reservation
                res_ref.update({
                    "status": "checked_out",
                    "checkOutTime": current_iso,
                    "overtimeFee": overtime_fee,
                    "actualTotalFee": actual_fee,
                })

            # update xe
            doc.reference.update({
                "status": "out",
                "exit_time": current_iso,
                "exit_image_url": exit_image_url,
                "duration_minutes": duration_minutes,
                "overtime_fee": overtime_fee
            })

            return {
                "success": True,
                "license_plate": plate_text,
                "reserved": True,
                "overtime_fee": overtime_fee,
                "paid_fee": res.get("paidFee", 0),
                "actual_total_fee": actual_fee
            }

        
        # 3. XE VÃNG LAI
        
        fee = duration_minutes * RATE_PER_MINUTE

        doc.reference.update({
            "fee": fee,
            "status": "out",
            "exit_time": current_iso,
            "exit_image_url": exit_image_url,
            "duration_minutes": duration_minutes,
        })

        return {
            "success": True,
            "license_plate": plate_text,
            "reserved": False,
            "fee": fee,
            "duration_minutes": duration_minutes
        }

    except Exception as e:
        print("update_vehicle_exit error:", e)
        return {"success": False, "message": str(e)}




# 3) LẤY TẤT CẢ BẢN GHI XE

def get_all_vehicle_records():
    vehicles = []
    for doc in db.collection("vehicles").stream():
        vehicles.append(doc.to_dict())
    return vehicles
