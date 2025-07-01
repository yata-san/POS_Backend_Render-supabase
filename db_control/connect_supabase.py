from sqlalchemy import create_engine
import os
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse

# 環境変数の読み込み
base_path = Path(__file__).parents[1]  # backendディレクトリへのパス
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# Supabaseデータベース接続情報
DATABASE_URL = os.getenv('DATABASE_URL')

# engine変数を最初にNoneで初期化
engine = None

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set")
    print("Available environment variables:")
    for key in os.environ:
        if 'DATABASE' in key.upper() or 'SUPABASE' in key.upper():
            print(f"  {key}: {'*' * min(len(os.environ[key]), 10)}...")
else:
    # DATABASE_URLの詳細を安全に表示（デバッグ用）
    try:
        parsed = urllib.parse.urlparse(DATABASE_URL)
        print(f"URL Scheme: {parsed.scheme}")
        print(f"Username: {parsed.username}")
        print(f"Hostname: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path}")
        print(f"Query params: {parsed.query}")
        # パスワードは安全性のため表示しない
        if parsed.password:
            print(f"Password length: {len(parsed.password)} characters")
            print(f"Password starts with: {parsed.password[:3]}...")
        else:
            print("Password: NOT SET")
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")

    # postgres:// を postgresql:// に変換（SQLAlchemy 2.0対応）
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        print("URL protocol converted from postgres:// to postgresql://")

    # SSL設定とその他のパラメータを追加
    if "?" in DATABASE_URL:
        if "sslmode" not in DATABASE_URL:
            DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

    # PostgreSQLのエンジンを作成（明示的にpsycopg2を指定）
    try:
        engine = create_engine(
            DATABASE_URL,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300,  # 5分に短縮
            pool_size=5,
            max_overflow=0,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30,
            }
        )
        print("Database engine created successfully")
    except Exception as e:
        print(f"Error creating database engine: {e}")
        # エラーが発生してもアプリケーションを起動する
        engine = None

    print("Connecting to Supabase PostgreSQL...") 
    print(f"Database URL (masked): {DATABASE_URL.split('@')[0]}@***")  # セキュリティのため接続先をマスク 