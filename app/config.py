import os
import logging
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool
from llama_index.vector_stores.postgres import PGVectorStore
from db import db_params, table_name, get_database_size, get_table_info, clear_vector_store

# 環境変数読み込み
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("DB設定完了")

# ベクトルストアとインデックス構築
vector_store = PGVectorStore.from_params(
    **db_params,
    table_name=table_name,
    embed_dim=1536,
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context,
)
logger.info("ベクトルストア準備完了")

# Retriever Query Engine 構築
retriever = index.as_retriever()
query_engine = RetrieverQueryEngine.from_args(retriever=retriever)

# Agent tool として登録
tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    description="PostgreSQLベースのドキュメント検索エンジン"
)

custom_prompt = os.getenv("CUSTOM_PROMPT", "画像から項目とデータに分けて出力してください")
system_prompt = os.getenv("SYSTEM_PROMPT", "ドキュメント検索エンジンからデータを取得して回答してください")

# LLMとAgentを動的に生成する関数
def get_llm_and_agent(model_name=None, sys_prompt=None):
    if model_name is None:
        model_name = "gpt-4o-mini"
    if sys_prompt is None:
        sys_prompt = system_prompt
    llm = OpenAI(model=model_name, temperature=0)
    Settings.llm = llm
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    agent = OpenAIAgent.from_tools(
        tools=[tool],
        system_prompt=sys_prompt,
        verbose=True,
    )
    return llm, agent

# デフォルトのllm/agent
llm, agent = get_llm_and_agent()

logger.info("Agent 構築完了")

