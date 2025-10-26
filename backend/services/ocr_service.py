import easyocr
from PIL import Image
import numpy as np
import os

reader = easyocr.Reader(["en", "vi"], gpu=False)

def extract_text_from_plate(image_path, detection, save_to_public=False, crop_name=None):
    """
    Extract license plate text and optionally save cropped plate to frontend/public/uploads
    """
    try:
        # Get bounding box from detection
        if isinstance(detection, list) and len(detection) > 0:
            pred = detection[0]
        elif isinstance(detection, dict):
            pred = detection
        else:
            return "Unknown", None
        
        required_keys = ['x', 'y', 'width', 'height']
        if not all(key in pred for key in required_keys):
            return "Unknown", None
        
        image = Image.open(image_path)
        x = pred.get("x", 0)
        y = pred.get("y", 0)
        w = pred.get("width", 0)
        h = pred.get("height", 0)
        left = max(0, int(x - w/2))
        top = max(0, int(y - h/2))
        right = min(image.width, int(x + w/2))
        bottom = min(image.height, int(y + h/2))
        
        plate_crop = image.crop((left, top, right, bottom))
        
        # Save image to public
        if save_to_public:
            if crop_name is None:
                crop_name = os.path.basename(image_path).replace(".jpg", "_crop.jpg").replace(".png","_crop.png")
            frontend_uploads = "../frontend/public/uploads"
            os.makedirs(frontend_uploads, exist_ok=True)
            public_path = os.path.join(frontend_uploads, crop_name)
            plate_crop.save(public_path)
            image_url = f"/uploads/{crop_name}"  # URL React có thể dùng
        else:
            # save image debug
            debug_path = image_path.replace(".jpg", "_crop.jpg").replace(".png","_crop.png")
            plate_crop.save(debug_path)
            image_url = debug_path
        
        # OCR
        plate_array = np.array(plate_crop)
        result = reader.readtext(plate_array, detail=0)
        plate_text = "Unknown"
        if result and len(result) > 0:
            plate_text = "".join(result).replace(" ", "").upper()
        
        return plate_text, image_url

    except Exception as e:
        print(f"OCR error: {e}")
        import traceback
        traceback.print_exc()
        return "Unknown", None
