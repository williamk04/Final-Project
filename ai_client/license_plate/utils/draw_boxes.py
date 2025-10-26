import cv2
import math

def draw_boxes_easyocr(image_path, results, output_path):
    """
    Vẽ khung quanh vùng biển số được nhận diện bởi Roboflow.
    Results là output từ Roboflow Workflow (format JSON/dict)
    """
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"❌ Không thể đọc ảnh từ: {image_path}")
        return
    
    # Parse kết quả từ Roboflow
    # results = [{'predictions': {'image': {...}, 'predictions': [...]}}]
    
    if not results or len(results) == 0:
        print("❌ Không có dữ liệu kết quả từ API")
        return
    
    predictions_list = results[0].get('predictions', {}).get('predictions', [])
    
    if not predictions_list:
        print("❌ Không phát hiện được biển số trong ảnh.")
        return
    
    # Duyệt qua từng detection
    for pred in predictions_list:
        # Lấy tọa độ center và kích thước
        x_center = pred.get('x', 0)
        y_center = pred.get('y', 0)
        width = pred.get('width', 0)
        height = pred.get('height', 0)
        confidence = pred.get('confidence', 0)
        class_name = pred.get('class', 'Unknown')
        
        # Tính tọa độ góc trái trên và phải dưới
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        
        # Vẽ khung chữ nhật
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Vẽ text thông tin
        text = f"{class_name} ({confidence:.2f})"
        cv2.putText(img, text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        print(f"✅ Phát hiện: {class_name} | Confidence: {confidence:.2f} | Vị trí: ({x_center}, {y_center})")
    
    cv2.imwrite(output_path, img)
    print(f"✅ Đã lưu ảnh kết quả tại: {output_path}")