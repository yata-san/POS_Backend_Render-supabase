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

# PostgreSQLのエンジンを作成
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

print("Connecting to Supabase PostgreSQL...") 