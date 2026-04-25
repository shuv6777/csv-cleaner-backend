from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
import base64

app = FastAPI()

# -------------------------------
# 🔥 HANDLE PREFLIGHT (CRITICAL)
# -------------------------------
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )

# -------------------------------
# 🔥 FORCE CORS HEADERS
# -------------------------------
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = read_file(contents, file.filename)

    preview = df.head(5).to_dict(orient="records")

    return {
        "columns": df.columns.tolist(),
        "preview": preview
    }

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