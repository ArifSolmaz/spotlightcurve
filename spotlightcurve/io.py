from __future__ import annotations
import pandas as pd
import lightkurve as lk

def lc_to_csv(lc, path: str):
    lc.to_pandas().to_csv(path, index=False); return path

def csv_to_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def load_tess(target: str, author: str = "SPOC", cadence: str = "2min"):
    """Download + stitch a TESS light curve with Lightkurve."""
    sr = lk.search_lightcurve(target, mission="TESS", author=author, cadence=cadence)
    lcs = sr.download_all()
    if not lcs:
        raise RuntimeError(f"No TESS light curves found for {target} (author={author}, cadence={cadence}).")
    return lcs.stitch().remove_nans()
