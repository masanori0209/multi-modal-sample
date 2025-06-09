# app/ui.py
import streamlit as st
import tempfile
import time
import os
from llama_index.core import Document
from utils import process_file
from config import index, agent, custom_prompt, system_prompt
from db import get_database_size, get_table_info, clear_vector_store
import logging
logger = logging.getLogger(__name__)

# 設定処理
def render_settings():
    with st.sidebar:
        # データベース情報
        st.subheader("📊 データベース情報")
        db_size = get_database_size()
        st.metric("データベースサイズ", db_size)
        # テーブル一覧
        st.subheader("📋 テーブル一覧")
        tables = get_table_info()
        if tables:
            for table in tables:
                st.text(f"• {table['name']} ({table['size']})")
        else:
            st.info("テーブルが存在しません")
        # セッションのリセットボタン
        if st.button("セッションのリセット"):
            st.session_state.clear()
            st.rerun()
        # ベクトルストアのクリアボタン
        if st.button("ベクトルストアのデータをクリア"):
            try:
                clear_vector_store()
                st.success("✅ ベクトルストアのデータを削除しました")
                # データベース情報を更新
                st.rerun()
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
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
        # APIキーが変更されたら、APIキーを更新
        if st.session_state.get("OPENAI_API_KEY") != os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = st.session_state.get("OPENAI_API_KEY")

# ファイルアップロード処理
def handle_file_upload(uploaded_file):
    # 新しいファイルがアップロードされた場合、前回の処理状態をリセット
    if uploaded_file and "current_file_name" in st.session_state:
        if st.session_state.current_file_name != uploaded_file.name:
            st.session_state.file_processed = False
            # 前回の一時ファイルを削除
            if "tmpfile_path" in st.session_state:
                try:
                    os.remove(st.session_state.tmpfile_path)
                except Exception as e:
                    logger.error(f"一時ファイルの削除中にエラーが発生: {e}")
    # 現在のファイル名を保存
    if uploaded_file:
        st.session_state.current_file_name = uploaded_file.name

    if uploaded_file and not st.session_state.get("file_processed", False):
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile.write(uploaded_file.read())
            tmpfile_path = tmpfile.name
            st.session_state.tmpfile_path = tmpfile_path

        status_message = st.empty()
        status_message.success("✅ ファイルアップロード完了。インデックス登録中...")
        time.sleep(1)

        try:
            text = process_file(tmpfile_path)
            if text.strip():
                doc = Document(text=text, metadata={"filename": uploaded_file.name})
                index.insert(doc)
                status_message.success("✅ インデックス登録完了")
            else:
                status_message.warning("⚠️ テキストが抽出できませんでした。")
        except Exception as e:
            status_message.error(f"❌ エラーが発生しました: {str(e)}")
            logger.error(f"ファイル処理中にエラーが発生: {e}")
        finally:
            # 一時ファイルを削除
            try:
                os.remove(tmpfile_path)
            except Exception as e:
                logger.error(f"一時ファイルの削除中にエラーが発生: {e}")
        time.sleep(3)
        status_message.empty()
        st.session_state.file_processed = True

# 質問処理
def handle_question(query):
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
