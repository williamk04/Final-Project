import cv2
import numpy as np

def deskew(image, cc, ct):
    """Căn chỉnh góc ảnh để dễ OCR hơn"""
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    angle = cc * 2 - 1  # quay nhẹ trái/phải
    scale = 1.0 + ct * 0.05
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated
