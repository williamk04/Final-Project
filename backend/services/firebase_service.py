from firebase_config import db
from vehicle_model import Vehicle
from datetime import datetime, timezone
from firebase_admin import firestore
def save_vehicle_entry(plate_text, image_url):
    # KIỂM TRA XE ĐANG Ở TRONG BÃI
    query = db.collection("vehicles")\
              .where("license_plate", "==", plate_text)\
              .where("status", "==", "in")\
              .limit(1).get()
    if query:
        # Trả về None hoặc raise exception tùy bạn xử lý
        return None, f"Vehicle {plate_text} is already in the parking lot"

    # Nếu chưa có, tạo record mới
    vehicle = Vehicle(
        license_plate=plate_text,
        image_url=image_url,
        entry_time=datetime.now(timezone.utc),
        status="in"
    )
    doc_ref = db.collection("vehicles").add(vehicle.to_dict())
    return {"_id": doc_ref[1].id, **vehicle.to_dict()}, None




# Giả sử rate_per_minute là phí mỗi phút (ví dụ 1000 VND)
RATE_PER_MINUTE = 1000

def update_vehicle_exit(plate_text, exit_image_url, rate_per_minute=RATE_PER_MINUTE):
    
    # Lấy record vehicle đang 'in'
    query = db.collection("vehicles")\
              .where("license_plate", "==", plate_text)\
              .where("status", "==", "in")\
              .limit(1).get()
    
    if not query:
        return None
    
    doc = query[0]
    data = doc.to_dict()

    # Lấy entry_time từ Firestore
    entry_time_str = data.get("entry_time")
    if not entry_time_str:
        return None  # không có entry_time, không thể tính duration

    # Chuyển entry_time từ ISO string sang datetime
    entry_time = datetime.fromisoformat(entry_time_str)

    # Tính duration (phút)
    now = datetime.now(timezone.utc)
    duration_minutes = int((now - entry_time).total_seconds() / 60)

    # Tính phí
    fee = duration_minutes * rate_per_minute

    # Cập nhật Firestore
    doc.reference.update({
        "status": "out",
        "exit_image_url": exit_image_url,
        "exit_time": now.isoformat(),
        "duration_minutes": duration_minutes,
        "fee": fee
    })

    # Trả về record mới
    updated_data = doc.to_dict()
    updated_data.update({
        "exit_time": now.isoformat(),
        "duration_minutes": duration_minutes,
        "fee": fee,
        "exit_image_url": exit_image_url,
        "status": "out"
    })
    return {"_id": doc.id, **updated_data}

def get_all_vehicle_records():
    db = firestore.client()
    docs = db.collection("vehicles").stream()
    vehicles = []
    for doc in docs:
        v = doc.to_dict()
        vehicles.append(v)
    return vehicles