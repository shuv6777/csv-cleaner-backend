from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json

from csv_service import (
    read_file,
    get_columns,
    filter_and_reorder,
    rename_columns,
    clean_basic,
    convert_file
)

app = FastAPI()

# -----------------------------
# CORS (IMPORTANT FOR REACT)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def home():
    return {"message": "CSV Cleaner API is running"}


# -----------------------------
# UPLOAD → GET COLUMNS
# -----------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    df = read_file(contents, file.filename)

    return {
        "columns": get_columns(df)
    }


# -----------------------------
# PROCESS FILE
# -----------------------------
@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    config: str = Form(...)
):
    contents = await file.read()

    # 🔥 SAFE PARSE (NO eval)
    config = json.loads(config)

    df = read_file(contents, file.filename)

    df = filter_and_reorder(df, config.get("columns", []))
    df = rename_columns(df, config.get("rename", {}))
    df = clean_basic(df)

    # Output format (optional)
    output_type = config.get("output_type", "csv")

    file_data, mime_type, file_name = convert_file(df, output_type)

    return {
        "file": file_data.decode("latin1"),  # safe binary transfer
        "mime": mime_type,
        "filename": file_name
    }


# -----------------------------
# LOCAL RUN (for testing)
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)