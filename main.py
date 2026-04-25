from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
import base64

app = FastAPI()

# ✅ CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------

def read_file(contents, filename):
    if filename.endswith(".csv"):
        return pd.read_csv(io.StringIO(contents.decode("utf-8")))
    else:
        return pd.read_excel(io.BytesIO(contents))


def get_columns(df):
    return df.columns.tolist()


# -------------------------------
# ROUTES
# -------------------------------

@app.get("/")
def home():
    return {"message": "CSV Cleaner Backend Running"}


# 🔹 UPLOAD → get columns + preview
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    df = read_file(contents, file.filename)

    # ✅ PREVIEW (TOP 5 ROWS)
    preview = df.head(5).to_dict(orient="records")

    return {
        "columns": get_columns(df),
        "preview": preview
    }


# 🔹 PROCESS → apply config & return file
@app.post("/process")
async def process_file(file: UploadFile = File(...), config: str = File(...)):
    contents = await file.read()
    df = read_file(contents, file.filename)

    config = json.loads(config)

    selected_columns = config.get("columns", df.columns.tolist())
    rename_map = config.get("rename", {})

    # ✅ Select columns
    df = df[selected_columns]

    # ✅ Rename columns
    df = df.rename(columns=rename_map)

    # ✅ Convert to Excel in memory
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    # ✅ Convert to base64 (frontend expects this)
    encoded_file = base64.b64encode(output.read()).decode("utf-8")

    return {
        "file": encoded_file,
        "filename": "processed.xlsx",
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }