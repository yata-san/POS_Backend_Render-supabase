from sqlalchemy import create_engine
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
base_path = Path(__file__).parents[1]  # backendディレクトリへのパス
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# Supabaseデータベース接続情報
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# IPv4を強制し、SSL設定を追加
if DATABASE_URL and "?" in DATABASE_URL:
    DATABASE_URL += "&options=-c%20default_transaction_isolation%3Dread_committed&sslmode=require"
else:
    DATABASE_URL += "?options=-c%20default_transaction_isolation%3Dread_committed&sslmode=require"

# PostgreSQLのエンジンを作成
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

print("Connecting to Supabase PostgreSQL...") 
print(f"Database URL (masked): {DATABASE_URL[:30]}...") 