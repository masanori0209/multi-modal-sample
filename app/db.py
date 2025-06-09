import os
import logging
import psycopg2
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB設定
db_params = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", 5432)),
    "database": os.getenv("PG_DATABASE", "ragdb"),
    "user": os.getenv("PG_USER", "raguser"),
    "password": os.getenv("PG_PASSWORD", "ragpass"),
}
table_name = "documents"
logger.info("DB設定完了")

def get_database_size():
    """データベースのサイズを取得する"""
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        # データベースサイズを取得（バイト単位）
        cur.execute("""
            SELECT pg_database_size(%s);
        """, (db_params['database'],))
        size_bytes = cur.fetchone()[0]
        # サイズを適切な単位に変換
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            size_str = f"{size_bytes/(1024*1024):.2f} MB"
        else:
            size_str = f"{size_bytes/(1024*1024*1024):.2f} GB"
        return size_str
    except Exception as e:
        logger.error(f"❌ データベースサイズの取得中にエラーが発生: {e}")
        return "取得エラー"
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_table_info():
    """テーブル一覧, index一覧とそのサイズを取得する"""
    try:
        conn = psycopg2.connect(**db_params)
        with conn.cursor() as cur:
            # テーブル一覧とサイズを取得
            cur.execute("""
                WITH table_sizes AS (
                    SELECT
                        table_name,
                        pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size,
                        (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = t.table_name) as exists
                    FROM information_schema.tables t
                    WHERE table_schema = 'public'
                ),
                index_info AS (
                    SELECT
                        tablename as table_name,
                        indexname as index_name,
                        pg_size_pretty(pg_relation_size(quote_ident(indexname))) as index_size
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                )
                SELECT
                    t.table_name,
                    t.size as table_size,
                    COALESCE(
                        string_agg(
                            i.index_name || ' (' || i.index_size || ')',
                            ', '
                        ),
                        'No index'
                    ) as indexes
                FROM table_sizes t
                LEFT JOIN index_info i ON t.table_name = i.table_name
                WHERE t.exists > 0
                GROUP BY t.table_name, t.size
                ORDER BY t.table_name;
            """)
            tables = cur.fetchall()
            # 結果を整形
            table_info = []
            for table_name, table_size, indexes in tables:
                table_info.append({
                    "name": table_name,
                    "size": table_size,
                    "indexes": indexes
                })
            return table_info
    except Exception as e:
        logger.error(f"❌ テーブル情報の取得中にエラーが発生: {e}")
        return []
    finally:
        if conn:
            conn.close()

def clear_vector_store():
    """ベクトルストアのデータを全て削除する"""
    try:
        conn = psycopg2.connect(**db_params)
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM public.data_{table_name};")
        conn.commit()
        logger.info("✅ ベクトルストアのデータを削除しました")
    except Exception as e:
        logger.error(f"❌ ベクトルストアのデータ削除中にエラーが発生: {e}")
        raise
    finally:
        if conn:
            conn.close()