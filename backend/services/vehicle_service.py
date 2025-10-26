
from datetime import datetime, timezone, timedelta

from pymongo import ReturnDocument
from models.vehicle_model import VehicleSchema
from bson import ObjectId

VN_TZ = timezone(timedelta(hours=7))
BASE_RATE = 5000
RATE_PER_MIN = BASE_RATE / 60

def create_vehicle_record(db, license_plate, image_url):
    now_utc = datetime.now(timezone.utc)

    record = {
        "license_plate": license_plate,
        "image_url": image_url,
        "entry_time": now_utc,
        "status": "in",
        "fee": 0
    }

    db["vehicles"].insert_one(record)

    vehicle_instance = VehicleSchema(**record)
    return {**vehicle_instance.model_dump(), "_id": str(ObjectId())}


def update_vehicle_exit(db, license_plate, exit_image_url=None):
    now_utc = datetime.now(timezone.utc)

    # get vehicle with status "in"
    vehicle = db["vehicles"].find_one(
        {"license_plate": license_plate, "status": "in"},
        sort=[("entry_time", -1)]
    )
    if not vehicle:
        return None

    # Fix datetime naive/aware
    entry_time = vehicle["entry_time"]
    if entry_time.tzinfo is None:
        entry_time = entry_time.replace(tzinfo=timezone.utc)

    # count time and fee
    duration_min = (now_utc - entry_time).total_seconds() / 60
    fee = round(duration_min * RATE_PER_MIN)
    if fee < BASE_RATE:
        fee = BASE_RATE

    # save to db
    update_data = {
        "status": "out",
        "exit_time": now_utc,
        "fee": fee,
        "duration_minutes": round(duration_min, 1)
    }

    if exit_image_url:
        update_data["exit_image_url"] = exit_image_url

    updated_vehicle = db["vehicles"].find_one_and_update(
        {"_id": vehicle["_id"]},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    vehicle_instance = VehicleSchema(
        license_plate=updated_vehicle["license_plate"],
        image_url=updated_vehicle.get("image_url"),
        entry_time=updated_vehicle["entry_time"],
        exit_time=updated_vehicle.get("exit_time"),
        status=updated_vehicle["status"],
        fee=updated_vehicle.get("fee")
    )

    return {**vehicle_instance.model_dump(), "_id": str(updated_vehicle["_id"])}