from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QMessageBox,
    QWidget, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from urllib.request import urlopen
import sqlite3
from PIL import Image

# 내부 모듈
from api.openai_api import get_image_description, generate_style_image
from utils.file_handler import get_image_file
from utils.hair_swapper import merge_images
from utils.config import DB_PATH


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 헤어스타일 추천 프로그램")
        self.setGeometry(100, 100, 900, 500)
        self.image_path = None

        self.init_ui()
        self.init_db()

    def init_ui(self):
        # 이미지 라벨들
        self.image_label = QLabel("인물 사진")
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")

        self.generated_label = QLabel("추천 스타일 이미지 (합성됨)")
        self.generated_label.setFixedSize(300, 300)
        self.generated_label.setAlignment(Qt.AlignCenter)
        self.generated_label.setStyleSheet("border: 1px solid green;")

        # 버튼 및 결과창
        self.load_button = QPushButton("사진 열기")
        self.load_button.clicked.connect(self.load_image)

        self.generate_button = QPushButton("헤어스타일 추천 받기")
        self.generate_button.clicked.connect(self.generate_description)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)

        # 레이아웃 설정
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.generated_label)
        image_layout.addWidget(self.load_button)

        layout = QVBoxLayout()
        layout.addLayout(image_layout)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.result_output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image BLOB,
                prompt TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def load_image(self):
        try:
            path = get_image_file()
            if path:
                pixmap = QPixmap(path).scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio
                )
                if pixmap.isNull():
                    raise ValueError("이미지를 불러올 수 없습니다.")
                self.image_label.setPixmap(pixmap)
                self.image_path = path
        except Exception as e:
            QMessageBox.warning(self, "오류", f"이미지 불러오기 실패: {e}")

    def generate_description(self):
        if not self.image_path:
            self.result_output.setPlainText("인물 사진을 먼저 불러와 주세요.")
            return

        try:
            # 스타일 설명 요청
            prompt = "이 인물의 얼굴형, 분위기, 직업 등을 고려하여 어울리는 한국 트렌드 기반의 헤어스타일을 추천해줘. 구체적인 스타일 이름과 이유를 설명해줘."
            result = get_image_description(self.image_path, prompt)
            self.result_output.setPlainText(result)

            # DB에 저장
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                with open(self.image_path, "rb") as f:
                    image_blob = f.read()
                cursor.execute('''
                    INSERT INTO image_logs (image, prompt, response) VALUES (?, ?, ?)
                ''', (image_blob, prompt, result))
                conn.commit()

            # 스타일 프롬프트 추출
            style_prompt = ""
            for line in result.split('\n'):
                if "스타일" in line or "추천" in line:
                    style_prompt = line.strip()
                    break
            if not style_prompt:
                style_prompt = "한국 트렌드 헤어스타일"

            # 스타일 이미지 생성
            image_url = generate_style_image(style_prompt)
            if image_url.startswith("http"):
                image_data = urlopen(image_url).read()
                style_img_path = "generated_style.jpg"
                with open(style_img_path, "wb") as f:
                    f.write(image_data)

                # 이미지 합성
                blended_image = merge_images(self.image_path, style_img_path)
                if blended_image:
                    # PIL Image → QImage 수동 변환
                    rgb_image = blended_image.convert("RGB")
                    data = rgb_image.tobytes("raw", "RGB")
                    qimage = QImage(data, rgb_image.width, rgb_image.height, QImage.Format_RGB888)

                    result_pixmap = QPixmap.fromImage(qimage).scaled(
                        self.generated_label.width(),
                        self.generated_label.height(),
                        Qt.KeepAspectRatio
                    )
                    self.generated_label.setPixmap(result_pixmap)
                else:
                    QMessageBox.warning(self, "합성 실패", "이미지를 합성하지 못했습니다.")
            else:
                QMessageBox.warning(self, "이미지 생성 실패", image_url)

        except Exception as e:
            self.result_output.setPlainText(f"오류 발생: {e}")
