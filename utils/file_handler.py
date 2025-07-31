# utils/file_handler.py
from PyQt5.QtWidgets import QFileDialog
import base64

def get_image_file():
    file_path, _ = QFileDialog.getOpenFileName(
        None, "이미지 파일 선택", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
    )
    return file_path

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
