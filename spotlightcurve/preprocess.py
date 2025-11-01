from __future__ import annotations
import numpy as np
import lightkurve as lk

__all__ = ["quality_mask", "flatten_lightcurve"]

def quality_mask(flux: np.ndarray, sigma: float = 5.0):
    f  = np.asarray(flux, float)
    mu = np.nanmedian(f)
    sd = np.nanstd(f)
    if not np.isfinite(sd) or sd == 0:
        return np.isfinite(f)
    z = np.abs((f - mu) / sd)
    return np.isfinite(f) & np.isfinite(z) & (z < float(sigma))

def flatten_lightcurve(lc: "lk.LightCurve", window_length: int = 401) -> "lk.LightCurve":
    return lc.flatten(window_length=int(window_length), return_trend=False)
