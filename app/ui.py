# app/ui.py
import streamlit as st
import tempfile
import time
import os
from llama_index.core import Document
from utils import extract_text_from_pdf, convert_pdf_to_images, convert_image_to_text
from config import index, agent, custom_prompt, system_prompt
import logging
logger = logging.getLogger(__name__)

# 設定処理
def render_settings():
    with st.sidebar:
        st.header("⚙️ 設定")
        st.text_input(
            "OpenAI API Key",
            type="password",
            key="OPENAI_API_KEY",
            value=os.getenv("OPENAI_API_KEY")
        )
        st.text_area(
            "画像読み込み時プロンプト",
            key="custom_prompt",
            placeholder="例: 画像から正確な日本語テキストを抽出してください",
            value=custom_prompt
        )
        st.text_area(
            "システムプロンプト",
            key="system_prompt",
            placeholder="例: テーブル形式で出力してください",
            value=system_prompt
        )

# ファイルアップロード処理
def handle_file_upload(uploaded_file):
    if uploaded_file and "file_processed" not in st.session_state:
        st.session_state.file_processed = False

    if uploaded_file and not st.session_state.file_processed:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            tmpfile.write(uploaded_file.read())
            tmpfile_path = tmpfile.name
            st.session_state.tmpfile_path = tmpfile_path

        status_message = st.empty()
        status_message.success("✅ PDFアップロード完了。インデックス登録中...")
        time.sleep(1)

        text = extract_text_from_pdf(tmpfile_path)
        if text.strip():
            doc = Document(text=text, metadata={"filename": uploaded_file.name})
            index.insert(doc)
            status_message.success("✅ インデックス登録完了")
        else:
            images = convert_pdf_to_images(tmpfile_path)
            logger.info(f"✅ 画像抽出完了 : 画像は{len(images)}枚です。")
            for image in images:
                doc = Document(text=convert_image_to_text(image), metadata={"filename": uploaded_file.name})
                index.insert(doc)
                logger.info(f"✅ インデックス登録処理中 : 要約 => {doc.text[:500]}")
            if images:
                status_message.success(f"✅ インデックス登録完了 : 内容は{len(images)}枚の画像です。")
            else:
                status_message.warning("⚠️ テキストが抽出できませんでした。")

        time.sleep(3)
        status_message.empty()
        st.session_state.file_processed = True

# 質問処理
def handle_question(query, uploaded_file):
    # agentのシステムプロンプトを取得
    __system_prompt = st.session_state.get("system_prompt", system_prompt)
    # システムプロンプトを割り当て
    agent.system_prompt = __system_prompt
    with st.spinner("回答中..."):
        # Agentを使って会話
        response = agent.chat(query)
    st.markdown("### GPTの回答")
    st.write(response.response)
    logger.info(f"✅ GPTの回答完了 : 回答 => {response.response}")
