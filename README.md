# Multi-Modal Sample Chat Application

PDFファイルをアップロードして、テキスト検索と画像認識を組み合わせた対話型アプリケーションです。

## 機能

- PDFファイルのアップロードとテキスト抽出
- ベクトルデータベースを使用した効率的な検索
- テキストベースの質問応答
- 画像認識を活用したマルチモーダルな質問応答
- Streamlitベースの使いやすいUI

## 技術スタック

- Python
- Streamlit
- LangChain
- LlamaIndex
- OpenAI GPT-4
- PostgreSQL + pgvector
- Docker

## 必要条件

- Python 3.11以上
- Docker
- Docker Compose
- OpenAI API Key

## セットアップ

1. リポジトリをクローン:
```bash
git clone [repository-url]
cd multi-modal-app
```

2. 環境変数の設定:
`.env`ファイルを作成し、以下の環境変数を設定（DBはローカルのため内容は任意）:
```
OPENAI_API_KEY=your_api_key
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=ragdb
PG_USER=raguser
PG_PASSWORD=ragpass
```

3. Docker Composeで起動:
```bash
docker-compose up --build
```

## 使用方法

1. アプリケーションにアクセス:
   - ブラウザで `http://localhost:8501` にアクセス

2. PDFファイルのアップロード:
   - 「PDFファイルをアップロードしてください」セクションでPDFファイルを選択

3. 質問:
   - テキストボックスに質問を入力
   - 「質問する」ボタンをクリック

4. 設定
   以下の設定を変えられます。
   - OpenAI API Key: OpenAIのAPIキーを設定
   - 画像読み込み時プロンプト: PDFから画像を抽出する際の指示を設定
   - システムプロンプト: 回答の出力形式を指定

## プロジェクト構造

```
multi-modal-sample/
├── app/                    # アプリケーションのメインコード
│   ├── __init__.py        # Pythonパッケージ定義
│   ├── config.py          # 設定ファイル（APIキー、DB設定など）
│   ├── Dockerfile         # アプリケーション用Dockerfile
│   ├── main.py            # アプリケーションのエントリーポイント
│   ├── pyproject.toml     # Pythonプロジェクト設定
│   ├── ui.py              # Streamlit UIの実装
│   └── utils.py           # ユーティリティ関数（PDF処理、画像処理など）
├── docker-compose.yml     # Docker Compose設定
├── .env                   # 環境変数設定（要作成）
├── .gitignore            # Git除外設定
└── README.md             # プロジェクトドキュメント
```

### 主要コンポーネント

- `app/config.py`: アプリケーションの設定を管理（OpenAI API、データベース接続など）
- `app/ui.py`: Streamlitベースのユーザーインターフェース実装
- `app/utils.py`: PDFファイルの処理、画像抽出、テキスト変換などのユーティリティ関数
- `app/main.py`: アプリケーションのメインエントリーポイント
- `docker-compose.yml`: PostgreSQLとpgvectorを含む開発環境の設定









