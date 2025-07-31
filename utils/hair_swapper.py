# utils/hair_swapper.py
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)

def blend_images(base_img, style_img):
    base = cv2.resize(base_img, (512, 512))
    style = cv2.resize(style_img, (512, 512))
    blended = cv2.addWeighted(base, 0.65, style, 0.35, 0)
    return blended

def apply_hairstyle(base_path, style_path, save_path="output.jpg"):
    base_img = cv2.imread(base_path)
    style_img = cv2.imread(style_path)

    faces = app.get(base_img)
    if not faces:
        raise ValueError("얼굴을 인식하지 못했습니다.")

    result_img = blend_images(base_img, style_img)
    cv2.imwrite(save_path, result_img)
    return save_path

from PIL import Image

def merge_images(face_path, hair_path, size=(300, 300)):
    try:
        face_img = Image.open(face_path).convert("RGBA").resize(size)
        hair_img = Image.open(hair_path).convert("RGBA").resize(size)
        combined = Image.alpha_composite(face_img, hair_img)
        return combined
    except Exception as e:
        print(f"이미지 병합 오류: {e}")
        return None
