import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from database import create_document, get_documents, db
from schemas import SalesRecord, Prediction, Profile

app = FastAPI(title="UMKM Business Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "UMKM Prediction Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "❌ Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# Sales endpoints
@app.post("/api/sales", response_model=dict)
def add_sales(record: SalesRecord):
    try:
        inserted_id = create_document("salesrecord", record)
        return {"inserted_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sales", response_model=List[dict])
def list_sales(limit: Optional[int] = 100):
    try:
        docs = get_documents("salesrecord", {}, limit=limit)
        # Convert ObjectId to string for frontend compatibility
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
            if isinstance(d.get("date"), (date,)):
                d["date"] = d["date"].isoformat()
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Prediction logic (simple moving average / exponential moving average)
class PredictRequest(BaseModel):
    series: List[float]
    method: str = "sma"  # sma | ema
    window: int = 3
    alpha: Optional[float] = None  # used for EMA if provided

@app.post("/api/predict", response_model=dict)
def predict(req: PredictRequest):
    data = [x for x in req.series if x is not None]
    if len(data) < 2:
        raise HTTPException(status_code=400, detail="Series minimal 2 angka")

    method = req.method.lower()
    pred_value: float

    if method == "sma":
        w = max(1, min(req.window, len(data)))
        window_vals = data[-w:]
        pred_value = sum(window_vals) / len(window_vals)
    elif method == "ema":
        # alpha default if not provided
        alpha = req.alpha if req.alpha is not None else 2 / (req.window + 1)
        ema = data[0]
        for v in data[1:]:
            ema = alpha * v + (1 - alpha) * ema
        pred_value = ema
    else:
        raise HTTPException(status_code=400, detail="Method tidak dikenal. Pakai 'sma' atau 'ema'")

    # Save prediction to DB
    try:
        pred_doc = Prediction(
            method=method,
            window=req.window,
            input_points=data,
            predicted_value=float(pred_value)
        )
        inserted_id = create_document("prediction", pred_doc)
    except Exception:
        inserted_id = None

    return {
        "predicted": float(pred_value),
        "method": method,
        "window": req.window,
        "saved_id": inserted_id
    }

# Profile endpoints
@app.get("/api/profile", response_model=List[dict])
def get_profiles(limit: Optional[int] = 10):
    try:
        docs = get_documents("profile", {}, limit=limit)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/profile", response_model=dict)
def create_profile(profile: Profile):
    try:
        inserted_id = create_document("profile", profile)
        return {"inserted_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
