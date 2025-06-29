# Supabase + Render デプロイガイド

## 1. Supabaseセットアップ

### データベースの準備
1. [Supabase](https://supabase.com/)でプロジェクトを作成
2. SQL Editor で以下のテーブルを作成：

```sql
-- 商品マスタテーブル
CREATE TABLE PRD_MASTER (
    PRD_ID SERIAL PRIMARY KEY,
    CODE CHAR(13) NOT NULL UNIQUE,
    NAME VARCHAR(50) NOT NULL,
    PRICE INTEGER NOT NULL
);

-- 取引ヘッダーテーブル
CREATE TABLE TRD_HEADER (
    TRD_ID SERIAL PRIMARY KEY,
    DATETIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    EMP_CD CHAR(10) NOT NULL DEFAULT '9999999999',
    STORE_CD CHAR(5) NOT NULL DEFAULT '30',
    POS_NO CHAR(3) NOT NULL DEFAULT '90',
    TOTAL_AMT INTEGER NOT NULL DEFAULT 0,
    TOTAL_AMT_EX_TAX INTEGER NOT NULL DEFAULT 0
);

-- 取引明細テーブル
CREATE TABLE TRD_DETAIL (
    TRD_ID INTEGER NOT NULL,
    DTL_ID INTEGER NOT NULL,
    PRD_ID INTEGER NOT NULL,
    PRD_CODE CHAR(13),
    PRD_NAME VARCHAR(50),
    PRD_PRICE INTEGER,
    QUANTITY INTEGER NOT NULL DEFAULT 1,
    TAX_CD INTEGER NOT NULL DEFAULT 10,
    PRIMARY KEY (TRD_ID, DTL_ID),
    FOREIGN KEY (TRD_ID) REFERENCES TRD_HEADER(TRD_ID),
    FOREIGN KEY (PRD_ID) REFERENCES PRD_MASTER(PRD_ID),
    FOREIGN KEY (PRD_CODE) REFERENCES PRD_MASTER(CODE)
);

-- 明細連番自動付与トリガー関数
CREATE OR REPLACE FUNCTION set_dtl_id()
RETURNS TRIGGER AS $$
DECLARE
    max_dtl_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(DTL_ID), 0)
    INTO max_dtl_id
    FROM TRD_DETAIL
    WHERE TRD_ID = NEW.TRD_ID;

    NEW.DTL_ID := max_dtl_id + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- トリガー
CREATE TRIGGER trg_set_dtl_id
BEFORE INSERT ON TRD_DETAIL
FOR EACH ROW
EXECUTE FUNCTION set_dtl_id();

```

-- 商品情報データ挿入
INSERT INTO prd_master (
    code,
    name,
    price
) VALUES (
    '4902506268556',
    'ぺんてる 洗たくでキレイカラーペン 水性 12色 SCS2-12(1セット)',
    800
);

INSERT INTO prd_master (
    code,
    name,
    price
) VALUES (
    '4901991054514',
    'トンボ鉛筆 プレイカラー2 12色 GCB-011(1セット)',
    1000
);

INSERT INTO prd_master (
    code,
    name,
    price
) VALUES (
    '4901991647860',
    'トンボ鉛筆 水性マーカーABT12色パステル AB-T12CPA',
    2200
);

INSERT INTO prd_master (
    code,
    name,
    price
) VALUES (
    '4901681506507',
    'ゼブラ マイルドライナー 10色セット WKT7-10C',
    1300
);

```

### 接続情報の取得
1. Supabaseダッシュボード → Settings → Database
2. Connection string (URI) をコピー
3. パスワード部分を実際のパスワードに置き換え

## 2. Renderセットアップ

### Web Serviceの作成
1. [Render](https://render.com/)にサインアップ/ログイン
2. "New" → "Web Service" を選択
3. GitHubリポジトリを接続

### 設定項目
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `Backend`

### 環境変数の設定
Environment Variables に以下を追加：
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## 3. ローカル開発

### 環境変数ファイル
`Backend/.env` ファイルを作成（.env.example を参考）：
```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### 起動方法
```bash
cd Backend
pip install -r requirements.txt
uvicorn app:app --reload
```

## 4. 変更点の概要

### Azure → Supabase の主な変更
- MySQL → PostgreSQL に変更
- SSL証明書設定を削除
- 依存関係: `pymysql`, `mysqlclient` → `psycopg2-binary`
- 接続設定の簡素化

### Render対応
- ポート設定の動的化（`$PORT` 環境変数使用）
- 起動コマンドの最適化

## 5. トラブルシューティング

### データベース接続エラー（重要）

**症状**: `Network is unreachable` エラー、IPv6接続問題
```
connection to server at "db.miwoocobzxzuzhdkzsbg.supabase.co" (2406:da14:271:9903:99ac:87a9:1e53:a9d7), port 5432 failed: Network is unreachable
```

**原因**: 
1. RenderでIPv6接続がサポートされていない
2. 環境変数が正しく設定されていない
3. Supabaseの接続設定に問題がある

**対策**:
1. **正しいDATABASE_URLの設定**
   - Supabaseダッシュボード → Settings → Database → Connection Pooling
   - **Transaction mode** を選択し、Connection stringをコピー
   ```
   postgres://postgres.xxx:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres
   ```

2. **IPv4強制の追加パラメータ**
   ```
   postgres://postgres.xxx:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres?sslmode=require&connect_timeout=30
   ```

3. **Renderの環境変数設定**
   - Render Dashboard → Your Service → Environment
   - `DATABASE_URL` を追加し、上記の接続文字列を設定

4. **接続テスト**
   - デプロイ後、`https://your-app.onrender.com/test-db` にアクセス
   - 接続状況を確認

### Environment Variables の正しい設定方法
1. Render Dashboard でサービスを選択
2. "Environment" タブをクリック
3. "Add Environment Variable" をクリック
4. Key: `DATABASE_URL`
5. Value: Supabaseから取得した接続文字列（パスワード付き）
6. "Save Changes" をクリック
7. サービスが自動的に再デプロイされる

### よくある問題
- **接続エラー**: DATABASE_URL の形式を確認
- **ポートエラー**: Renderでは自動的に `$PORT` 環境変数が設定される
- **SSL エラー**: Supabaseは自動的にSSLを処理するため、追加設定不要

### Python 3.13 互換性問題
**症状**: `ImportError: undefined symbol: _PyInterpreterState_Get`

**原因**: 
- `psycopg2-binary` がPython 3.13と互換性がない
- `runtime.txt` が正しく読み込まれていない

**対策**:
1. **`runtime.txt` の確認**: 余分なスペースや改行がないことを確認
   ```
   python-3.12.8
   ```

2. **psycopg2-binary のアップデート**: 最新版を使用
   ```
   psycopg2-binary==2.9.10
   ```

3. **代替案**: psycopg3 を使用
   ```
   psycopg[binary]==3.2.3
   ```

### ログの確認
Renderダッシュボードの "Logs" タブでエラーを確認できます。 