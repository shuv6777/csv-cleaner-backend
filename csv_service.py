import pandas as pd
import io

# -----------------------------
# READ FILE
# -----------------------------
def read_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes))
    else:
        return pd.read_excel(io.BytesIO(file_bytes))


# -----------------------------
# GET COLUMNS
# -----------------------------
def get_columns(df: pd.DataFrame):
    return df.columns.tolist()


# -----------------------------
# FILTER + REORDER
# -----------------------------
def filter_and_reorder(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    # Keep only valid columns
    cols = [c for c in columns if c in df.columns]
    return df[cols]


# -----------------------------
# RENAME
# -----------------------------
def rename_columns(df: pd.DataFrame, rename_dict: dict) -> pd.DataFrame:
    valid_renames = {k: v for k, v in rename_dict.items() if k in df.columns}
    return df.rename(columns=valid_renames)


# -----------------------------
# CLEAN BASIC
# -----------------------------
def clean_basic(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace(r'^\s*$', None, regex=True)
    df = df.dropna(how="all")
    return df


# -----------------------------
# CONVERT TO OUTPUT FILE
# -----------------------------
def convert_file(df: pd.DataFrame, output_type: str):
    output = io.BytesIO()

    if output_type == "excel":
        df.to_excel(output, index=False)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "processed.xlsx"
    else:
        df.to_csv(output, index=False)
        mime = "text/csv"
        filename = "processed.csv"

    output.seek(0)
    return output.getvalue(), mime, filename