import streamlit as st
from ui import handle_file_upload, handle_question, render_settings

# タイトル
st.title("マルチモーダル サンプル")

# 設定UIの描画（APIキーやプロンプトなど）
render_settings()

# ファイルアップロードUI
uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])
handle_file_upload(uploaded_file)

# 質問フォーム
query = st.text_input("質問を入力してください")
if st.button("質問する") and query:
    handle_question(query)