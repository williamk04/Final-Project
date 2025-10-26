import cv2
import easyocr

reader = easyocr.Reader(['en', 'vi'])

def read_plate_text(image_path, result):
    if isinstance(result, list):
        result = result[0]

    predictions = result.get('predictions', {}).get('predictions', [])
    if not predictions:
        print("❌ Không phát hiện được biển số để OCR.")
        return

    img = cv2.imread(image_path)
    h_img, w_img = img.shape[:2]

    for i, pred in enumerate(predictions):
        x, y = int(pred['x']), int(pred['y'])
        w, h = int(pred['width']), int(pred['height'])

        x1 = max(0, x - w // 2)
        y1 = max(0, y - h // 2)
        x2 = min(w_img, x + w // 2)
        y2 = min(h_img, y + h // 2)

        plate_crop = img[y1:y2, x1:x2]

        if plate_crop.size == 0:
            print(f"⚠️ Vùng cắt #{i+1} trống, bỏ qua.")
            continue

        # === Tiền xử lý nâng cao ===
        scale_factor = 2
        plate_crop = cv2.resize(plate_crop,
                                (plate_crop.shape[1]*scale_factor, plate_crop.shape[0]*scale_factor),
                                interpolation=cv2.INTER_LINEAR)

        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)

        # CLAHE để tăng contrast (tốt cho EasyOCR)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # Denoise nhẹ
        gray = cv2.GaussianBlur(gray, (3,3), 0)

        # OCR với allowlist chữ + số
        results = reader.readtext(gray, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        if results:
            # Ghép tất cả ký tự OCR được
            text = ''.join([r[1] for r in results])
            print(f"🔍 Biển số #{i+1}: {text}")
        else:
            print(f"⚠️ Không đọc được ký tự nào ở biển #{i+1}.")
