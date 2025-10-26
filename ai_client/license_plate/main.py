import os
from inference_sdk import InferenceHTTPClient
from utils.draw_boxes import draw_boxes_easyocr
from utils.ocr_reader import read_plate_text

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="1ISJGj6eOqmaELKDzBsO"
)

def detect_license_plate(image_path):
    result = CLIENT.run_workflow(
        workspace_name="license-plate-detection-mct72",
        workflow_id="custom-workflow-4",
        images={"image": image_path},
        use_cache=True
    )
    return result

if __name__ == "__main__":
    # ✅ Đường dẫn tuyệt đối an toàn, dù bạn chạy từ đâu cũng đúng
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, "images", "car2.jpg")
    output_path = os.path.join(base_dir, "results", "car2_result.jpg")

    # Kiểm tra ảnh có tồn tại không
    print("🔍 Checking image:", image_path)
    print("Exists?", os.path.exists(image_path))

    result = detect_license_plate(image_path)
    print("📦 Kết quả trả về từ API:")
    print(result)

    draw_boxes_easyocr(image_path, result, output_path)
    read_plate_text(image_path, result)
