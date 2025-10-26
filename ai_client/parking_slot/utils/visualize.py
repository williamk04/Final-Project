import cv2

def draw_boxes(image_path, result, output_path):
    # Nếu result là list, lấy phần tử đầu tiên
    if isinstance(result, list):
        result = result[0]

    # Lấy danh sách các bounding boxes trong 'predictions'
    predictions = result.get('predictions', {}).get('predictions', [])

    # Đọc ảnh gốc
    image = cv2.imread(image_path)

    # Vẽ bounding box cho từng object
    for pred in predictions:
        x, y, w, h = int(pred['x']), int(pred['y']), int(pred['width']), int(pred['height'])
        class_name = pred['class']
        conf = pred['confidence']

        # Tính tọa độ góc trên trái và dưới phải
        x1, y1 = x - w // 2, y - h // 2
        x2, y2 = x + w // 2, y + h // 2

        # Chọn màu cho class
        color = (0, 255, 0) if class_name == "free" else (0, 0, 255)

        # Vẽ hình chữ nhật
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # Ghi nhãn class + confidence
        label = f"{class_name} ({conf:.2f})"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Lưu ảnh kết quả
    cv2.imwrite(output_path, image)
    print(f"✅ Kết quả đã lưu tại: {output_path}")
