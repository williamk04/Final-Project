import torch
import cv2
import os
import uuid
from . import utils_rotate

# Load YOLO models
yolo_detector = torch.hub.load(
    'yolov5', 'custom', path='models/LP_detector_nano_61.pt',
    source='local', force_reload=False
)
yolo_ocr = torch.hub.load(
    'yolov5', 'custom', path='models/LP_ocr_nano_62.pt',
    source='local', force_reload=False
)
yolo_ocr.conf = 0.6

UPLOAD_FOLDER = "uploads"
CROP_FOLDER = os.path.join(UPLOAD_FOLDER, "crops")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROP_FOLDER, exist_ok=True)


def detect_and_read_plate(file):
    """Nhận ảnh, detect biển số, OCR ký tự, chỉ lưu crop của biển số confidence cao nhất."""
    # Lưu ảnh gốc
    image_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}.jpg")
    file.save(image_path)
    image = cv2.imread(image_path)

    # Phát hiện biển số
    detections = yolo_detector(image, size=640).pandas().xyxy[0].to_dict(orient="records")
    plates = []

    if not detections:
        # Không phát hiện được gì
        return plates, f"/{image_path.replace('\\', '/')}"

    # Chọn detection có confidence cao nhất
    best_det = max(detections, key=lambda d: float(d["confidence"]))

    x1, y1, x2, y2 = map(int, [best_det['xmin'], best_det['ymin'], best_det['xmax'], best_det['ymax']])
    crop = image[y1:y2, x1:x2]

    # OCR biển số
    text = ocr_plate(crop)

    # Lưu crop
    crop_filename = f"{uuid.uuid4().hex}.jpg"
    crop_path = os.path.join(CROP_FOLDER, crop_filename)
    cv2.imwrite(crop_path, crop)

    plates.append({
        "text": text,
        "bbox": [x1, y1, x2, y2],
        "confidence": float(best_det["confidence"]),
        "crop_url": f"/{crop_path.replace('\\', '/')}"
    })

    return plates, f"/{image_path.replace('\\', '/')}"



def ocr_plate(crop_img):
    """Nhận diện ký tự trên biển số."""
    text = "unknown"

    for cc in range(2):
        for ct in range(2):
            rotated = utils_rotate.deskew(crop_img, cc, ct)
            results = yolo_ocr(rotated, size=640)
            preds = results.pandas().xyxy[0]
            if len(preds) > 0:
                chars = preds.sort_values("xmin")["name"].tolist()
                text = "".join(chars)
                return text
    return text
