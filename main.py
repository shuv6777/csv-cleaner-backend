from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
import base64

app = FastAPI()

# -------------------------------
# 🔥 FORCE CORS (WORKS 100%)
# -------------------------------
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


# -------------------------------
# HELPERS
# -------------------------------
def read_file(contents, filename):
    if filename.endswith(".csv"):
        return pd.read_csv(io.StringIO(contents.decode("utf-8")))
    else:
        return pd.read_excel(io.BytesIO(contents))


# -------------------------------
# ROUTES
# -------------------------------
@app.get("/")
def home():
    return {"status": "Backend running"}

# -------------------------------
# UPLOAD
# -------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = read_file(contents, file.filename)

    preview = df.head(5).to_dict(orient="records")

    return {
        "columns": df.columns.tolist(),
        "preview": preview
    }

# -------------------------------
# PROCESS
# -------------------------------
@app.post("/process")
async def process_file(file: UploadFile = File(...), config: str = File(...)):
    contents = await file.read()
    df = read_file(contents, file.filename)

    config = json.loads(config)

    selected_columns = config.get("columns", df.columns.tolist())
    rename_map = config.get("rename", {})

    df = df[selected_columns]
    df = df.rename(columns=rename_map)

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    encoded = base64.b64encode(output.read()).decode("utf-8")

    return {
        "file": encoded,
        "filename": "processed.xlsx",
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }