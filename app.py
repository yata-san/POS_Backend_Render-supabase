from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
from datetime import datetime
from db_control import crud, mymodels
from typing import List
from sqlalchemy import text
from db_control.connect_supabase import engine


app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


@app.get("/health")
def health_check():
    """アプリケーションの健全性をチェック"""
    health_status = {
        "status": "ok",
        "database": "unknown",
        "timestamp": datetime.now().isoformat()
    }
    
    # データベース接続チェック
    if engine is None:
        health_status["database"] = "disconnected"
        health_status["status"] = "error"
    else:
        try:
            with engine.begin() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                health_status["database"] = "connected"
                health_status["database_test"] = test_value
        except Exception as e:
            health_status["database"] = "error"
            health_status["database_error"] = str(e)
            health_status["status"] = "error"
    
    return health_status


@app.get("/test-db")
def test_database():
    """データベース接続をテストするエンドポイント"""
    if engine is None:
        return {
            "status": "error",
            "message": "Database engine is not initialized",
            "error_type": "ConfigurationError"
        }
    
    try:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            return {
                "status": "success", 
                "message": "Database connection successful",
                "test_query_result": test_value
            }
    except Exception as e:
        print(f"Database connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/items")
def read_one_item(code: str = Query(...)):
    if engine is None:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    print(f"商品検索: コード={code}")
    
    try:
        # prd_masterテーブルを参照
        result = crud.myselect(mymodels.PrdMaster, code, key_name="CODE")
        print(f"検索結果: {result}")
        
        if not result:
            print(f"商品が見つかりません: コード={code}")
            raise HTTPException(status_code=404, detail="Item not found")
        
        result_obj = json.loads(result)
        if not result_obj:
            print(f"結果が空です: コード={code}")
            raise HTTPException(status_code=404, detail="Item not found")
        
        print(f"商品情報を返します: {result_obj[0]}")
        return result_obj[0]
    except json.JSONDecodeError as e:
        print(f"JSON解析エラー: {e}")
        raise HTTPException(status_code=500, detail="Data parsing error")
    except Exception as e:
        print(f"予期しないエラー: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


class CartItem(BaseModel):
    CODE: str
    NAME: str
    PRICE: int
    PRD_ID: int
    qty: int

class PurchaseRequest(BaseModel):
    items: List[CartItem]
    subtotal: int
    total: int

@app.post("/purchase")
def purchase(req: PurchaseRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        with engine.begin() as conn:
            # 1. trd_headerにINSERT (PostgreSQL用にRETURNINGを使用)
            result = conn.execute(
                text(
                    "INSERT INTO trd_header (total_amt, total_amt_ex_tax) VALUES (:total_amt, :total_amt_ex_tax) RETURNING trd_id"
                ),
                {"total_amt": req.total, "total_amt_ex_tax": req.subtotal}
            )
            trd_id = result.fetchone()[0]

            # 2. trd_detailに商品ごとにINSERT
            for idx, item in enumerate(req.items, start=1):
                conn.execute(
                    text(
                        """
                        INSERT INTO trd_detail
                        (trd_id, dtl_id, prd_id, prd_code, prd_name, prd_price, quantity)
                        VALUES
                        (:trd_id, :dtl_id, :prd_id, :prd_code, :prd_name, :prd_price, :quantity)
                        """
                    ),
                    {
                        "trd_id": trd_id,
                        "dtl_id": idx,
                        "prd_id": item.PRD_ID,
                        "prd_code": item.CODE,
                        "prd_name": item.NAME,
                        "prd_price": item.PRICE,
                        "quantity": item.qty
                    }
                )
        return {"status": "success", "trd_id": trd_id}
    except Exception as e:
        print(f"Database error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Render用のポート設定
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
