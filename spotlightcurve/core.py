from __future__ import annotations
import numpy as np
import lightkurve as lk

_CADENCE = {"short": "short", "fast": "fast", "long": "long"}

def search_result(target: str, author: str | None = None, cadence_hint: str | None = None):
    kw = {"mission": "TESS"}
    if author and author.lower() != "any":
        kw["author"] = author
    if cadence_hint and _CADENCE.get(cadence_hint):
        kw["exptime"] = _CADENCE[cadence_hint]
    sr = lk.search_lightcurve(target, **kw)
    if len(sr) == 0 and "exptime" in kw:
        kw.pop("exptime", None)
        sr = lk.search_lightcurve(target, **kw)
    return sr

def search_and_stitch(target: str, author: str = "SPOC", cadence_hint: str = "short"):
    sr = search_result(target, author=author, cadence_hint=cadence_hint)
    if len(sr) == 0:
        raise RuntimeError("No light curves found.")
    lcs = lk.LightCurveCollection([row.download() for row in sr])
    stitched = lcs.stitch().remove_nans().normalize()
    sectors = [getattr(lc, "sector", None) or lc.meta.get("SECTOR") for lc in lcs]
    return stitched, sectors

def run_bls(lc_flat: "lk.LightCurve", pmin: float = 0.3, pmax: float = 20.0,
            dmin: float = 0.01, dmax: float = 0.20, nper: int = 6000):
    period = np.linspace(pmin, pmax, int(nper))
    dmax_eff = min(dmax, 0.9 * pmin)
    duration = np.linspace(dmin, max(dmin, dmax_eff), 30)
    if duration.size == 0:
        duration = np.array([0.45 * pmin])
    bls = lc_flat.to_periodogram(method="bls", period=period, duration=duration, objective="snr")
    P = float(bls.period_at_max_power)
    T0 = float(bls.transit_time_at_max_power)
    return bls, P, T0
