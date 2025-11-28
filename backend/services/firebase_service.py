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


# ====================================================================
# 1) LƯU XE VÀO — CHECK-IN
# ====================================================================

def save_vehicle_entry(plate_text, image_url):
    try:
        current_dt = now_dt()
        current_iso = now_iso()

        # -------------------------------------------------------
        # 1. Kiểm tra xe có đang trong bãi không
        # -------------------------------------------------------
        existing = db.collection("vehicles") \
            .where("license_plate", "==", plate_text) \
            .where("status", "==", "in") \
            .limit(1).get()

        if existing:
            return None, f"Vehicle {plate_text} already inside"

        # -------------------------------------------------------
        # 2. Kiểm tra reservation
        # -------------------------------------------------------
        reservations = db.collection("reservations") \
            .where("plateNumber", "==", plate_text) \
            .where("status", "==", "reserved") \
            .limit(10).get()

        active_res = None

        for r in reservations:
            res_data = r.to_dict()
            start_dt = res_data["startTime"]
            end_dt = res_data["endTime"]

            if current_dt < start_dt:
                return None, f"Too early to check in. Reservation starts at {start_dt}"

            if start_dt <= current_dt <= end_dt:
                active_res = (r.id, res_data)
                break

        # -------------------------------------------------------
        # 3. XE ĐẶT CHỖ — CHECK IN
        # -------------------------------------------------------
        if active_res:
            res_id, res_data = active_res
            target_slot = res_data["slotId"]  # ví dụ: "A4"

            # ============================================
            # KIỂM TRA SLOT ĐẶT HIỆN TẠI CÓ BỊ CHIẾM KHÔNG
            # ============================================
            occupying = db.collection("reservations") \
                .where("slotId", "==", target_slot) \
                .where("status", "==", "checked_in") \
                .limit(1).get()

            slot_occupied = False

            if occupying:
                occ = occupying[0].to_dict()
                end_dt = occ["endTime"]

                # Nếu xe kia hết giờ nhưng chưa check out → vẫn chiếm
                if end_dt < current_dt:
                    slot_occupied = True

            # -------------------------------------------------------
            # Nếu slot bị chiếm → tự động tìm slot khác
            # -------------------------------------------------------
            if slot_occupied:
                free_slot = None

                all_slots = db.collection("parking_slots") \
                    .where("isActive", "==", True).stream()

                for s in all_slots:
                    slot_name = s.to_dict().get("name")

                    if slot_name == target_slot:
                        continue

                    # kiểm tra slot này có ai đang checked-in không
                    check = db.collection("reservations") \
                        .where("slotId", "==", slot_name) \
                        .where("status", "==", "checked_in") \
                        .limit(1).get()

                    if not check:
                        free_slot = slot_name
                        break

                # -----------------------------------------------
                # KHÔNG CÓ SLOT TRỐNG → HUỶ RESERVATION + HOÀN TIỀN VÀO VÍ USER
                # -----------------------------------------------
                if not free_slot:
                    refund_amount = res_data.get("paidFee", 0)
                    user_id = res_data.get("userId")

                    user_ref = None
                    user_doc = None
                    refunded_to_wallet = False
                    new_balance = None

                    if user_id:
                        user_ref = db.collection("users").document(user_id)
                        user_doc = user_ref.get()

                        if user_doc.exists:
                            user_data = user_doc.to_dict()
                            current_balance = user_data.get("wallet_balance", 0) or 0
                            new_balance = current_balance + refund_amount

                            # cập nhật wallet_balance
                            user_ref.update({
                                "wallet_balance": new_balance
                            })
                            refunded_to_wallet = True
                            print(f"[REFUND] User {user_id} refunded {refund_amount}. Balance {current_balance} → {new_balance}")
                        else:
                            print(f"[REFUND ERROR] User {user_id} not found → cannot refund wallet")
                    else:
                        print(f"[REFUND ERROR] Reservation {res_id} missing userId → cannot refund wallet")

                    # cập nhật reservation: failed + ghi refund info
                    db.collection("reservations").document(res_id).update({
                        "status": "failed",
                        "refundAmount": refund_amount,
                        "refundTime": now_iso(),
                        "refundReason": "No parking slot available",
                        "refunded": refunded_to_wallet
                    })

                    # trả về thông báo lỗi cùng thông tin refund
                    if refunded_to_wallet:
                        return None, (
                            f"Slot {target_slot} is occupied and no free slots available. "
                            f"Reservation refunded {refund_amount} VND to user {user_id} (new balance: {new_balance})."
                        )
                    else:
                        return None, (
                            f"Slot {target_slot} is occupied and no free slots available. "
                            f"Reservation marked failed and refund requested ({refund_amount} VND) but wallet update failed."
                        )

                # Nếu có free_slot thì cập nhật reservation sang slot mới
                db.collection("reservations").document(res_id).update({
                    "slotId": free_slot
                })

                print(f"[AUTO MOVE] Reservation {res_id} moved from {target_slot} → {free_slot}")
                target_slot = free_slot

            # ============================================
            #  TIẾN HÀNH CHECK-IN BÌNH THƯỜNG
            # ============================================

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
                "reservation_id": res_id,
                "slotId": target_slot
            })

            doc_ref = db.collection("vehicles").add(data)[1]

            return {"_id": doc_ref.id, **data}, None

        # -------------------------------------------------------
        # 4. XE VÃNG LAI
        # -------------------------------------------------------
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


# ====================================================================
# 2) XE RA — CHECK-OUT
# ====================================================================

def update_vehicle_exit(plate_text, exit_image_url):
    try:
        current_dt = now_dt()
        current_iso = now_iso()

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

        # -------------------------------------------------------
        # XE ĐẶT CHỖ
        # -------------------------------------------------------
        if data.get("is_reserved") and data.get("reservation_id"):
            res_id = data["reservation_id"]
            res_ref = db.collection("reservations").document(res_id)
            res_doc = res_ref.get()

            if res_doc.exists:
                res = res_doc.to_dict()
                end_dt = res["endTime"]

                overtime_minutes = max(0, int((current_dt - end_dt).total_seconds() / 60) - GRACE_PERIOD)
                overtime_fee = overtime_minutes * OVERTIME_FEE_PER_MIN

                actual_fee = res.get("paidFee", 0) + overtime_fee

                res_ref.update({
                    "status": "checked_out",
                    "checkOutTime": current_iso,
                    "overtimeFee": overtime_fee,
                    "actualTotalFee": actual_fee,
                })

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

        # -------------------------------------------------------
        # XE VÃNG LAI
        # -------------------------------------------------------
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


# ====================================================================
# 3) LẤY TẤT CẢ BẢN GHI XE
# ====================================================================

def get_all_vehicle_records():
    vehicles = []
    for doc in db.collection("vehicles").stream():
        vehicles.append(doc.to_dict())
    return vehicles
