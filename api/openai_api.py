# api/openai_api.py
import openai
from utils.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_image_description(image_path, prompt_text):
    with open(image_path, "rb") as img_file:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "당신은 이미지 분석과 패션 스타일 추천을 잘하는 전문가입니다."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{img_file.read().encode('base64').decode()}"
                        }}
                    ],
                },
            ],
            max_tokens=1000
        )
    return response.choices[0].message.content.strip()

def generate_style_image(prompt_text):
    try:
        response = openai.Image.create(
            prompt=prompt_text,
            n=1,
            size="512x512",
            model="dall-e-3"
        )
        return response['data'][0]['url']
    except Exception as e:
        return f"이미지 생성 오류: {e}"
