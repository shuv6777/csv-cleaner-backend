from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
import base64

# -------------------------------
# INIT APP
# -------------------------------
app = FastAPI()

# -------------------------------
# ✅ PROPER CORS (FINAL FIX)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
# UPLOAD (COLUMNS + PREVIEW)
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
# PROCESS FILE
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

    encoded_file = base64.b64encode(output.read()).decode("utf-8")

    return {
        "file": encoded_file,
        "filename": "processed.xlsx",
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }