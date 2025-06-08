import pdfplumber
from langchain_openai import ChatOpenAI
from pdf2image import convert_from_path
import streamlit as st
import tempfile
import io
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages])


def convert_pdf_to_images(pdf_path):
    # 一時ディレクトリを使ってPDF→画像変換
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(pdf_path, output_folder=path, fmt='jpeg', dpi=200)
        return images

def convert_image_to_text(image):
    # Convert PIL Image to base64
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")
    logger.info(f"✅ 画像をbase64に変換完了 : 画像は{encoded_image[:100]}")
    # llmを使って画像からテキストを抽出
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": st.session_state.custom_prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            }
        ]
    }
    logger.info(f"✅ 画像からテキストを抽出中...")
    response = llm.invoke([message])
    logger.info(f"✅ 画像からテキストを抽出完了 : 回答 => {response.content[:100]}")
    return response.content
