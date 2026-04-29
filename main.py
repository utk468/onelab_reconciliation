from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
import json
import uvicorn
from app.generator import generate_synthetic_data
from app.reconciler import reconcile_data
from app.database import db_client

app = FastAPI(title="Payment Reconciliation Dashboard")

# Setup directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-data")
async def generate_data():
    tx_path, set_path = generate_synthetic_data()
    return {"message": "Synthetic data generated successfully.", "tx_path": tx_path, "set_path": set_path}

@app.post("/upload")
async def upload_files(transactions: UploadFile = File(...), settlements: UploadFile = File(...)):
    tx_path = os.path.join(DATA_DIR, "uploaded_transactions.csv")
    set_path = os.path.join(DATA_DIR, "uploaded_settlements.csv")
    
    with open(tx_path, "wb") as buffer:
        buffer.write(await transactions.read())
        
    with open(set_path, "wb") as buffer:
        buffer.write(await settlements.read())
        
    return {"message": "Files uploaded successfully.", "tx_path": tx_path, "set_path": set_path}

@app.get("/reconcile")
async def run_reconciliation(tx_file: str = "transactions.csv", set_file: str = "settlements.csv"):
    tx_path = os.path.join(DATA_DIR, tx_file)
    set_path = os.path.join(DATA_DIR, set_file)
    
    if not os.path.exists(tx_path) or not os.path.exists(set_path):
        return JSONResponse(status_code=400, content={"error": "Data files not found. Generate or upload first."})
        
    result = reconcile_data(tx_path, set_path)
    
    # Save report for download
    report_id = str(uuid.uuid4())
    report_path = os.path.join(DATA_DIR, f"report_{report_id}.json")
    with open(report_path, "w") as f:
        json.dump(result, f)
        
    result["report_id"] = report_id
    
    # Save to MongoDB
    db_client.save_report(result, tx_path=tx_path, set_path=set_path)

    return result

@app.get("/report/{report_id}")
async def download_report(report_id: str):
    report_path = os.path.join(DATA_DIR, f"report_{report_id}.json")
    if not os.path.exists(report_path):
        return JSONResponse(status_code=404, content={"error": "Report not found"})
    return FileResponse(report_path, filename=f"reconciliation_report_{report_id}.json", media_type="application/json")

if __name__ == "__main__":
    print("Starting Payment Reconciliation Dashboard...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)