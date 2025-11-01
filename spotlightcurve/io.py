from __future__ import annotations
import pandas as pd

def lc_to_csv(lc, path: str):
    lc.to_pandas().to_csv(path, index=False); return path

def csv_to_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path)
