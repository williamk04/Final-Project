import os
from inference_sdk import InferenceHTTPClient
import cv2
import json
from utils.visualize import draw_boxes

# ==== 1. Lấy đường dẫn tuyệt đối gốc ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==== 2. Đường dẫn tuyệt đối cho ảnh và kết quả ====
IMAGE_PATH = os.path.join(BASE_DIR, "images", "test1.jpg")
OUTPUT_PATH = os.path.join(BASE_DIR, "results", "output_test1.jpg")

# ==== 3. Kết nối Roboflow ====
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="1ISJGj6eOqmaELKDzBsO"  
)

# ==== 4. Gọi workflow (hoặc model detect_parking) ====
result = client.run_workflow(
    workspace_name="license-plate-detection-mct72",  
    workflow_id="custom-workflow-6",                
    images={"image": IMAGE_PATH},
    use_cache=True
)

# ==== 5. In kết quả ====
print(json.dumps(result, indent=2))

# ==== 6. Vẽ bounding boxes lên ảnh ====
draw_boxes(IMAGE_PATH, result, OUTPUT_PATH)

print(f"Saved result to: {OUTPUT_PATH}")
