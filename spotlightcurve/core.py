# spotlightcurve/core.py
from __future__ import annotations
from astropy import units as u
import numpy as np
import lightkurve as lk

__all__ = ["search_result", "search_and_stitch", "run_bls"]

# Cadence hint mapping used by Lightkurve (TESS)
_CADENCE = {"short": "short", "fast": "fast", "long": "long"}


def search_result(
    target: str,
    author: str | None = None,
    cadence_hint: str | None = None,
):
    """
    Return a Lightkurve SearchResult for a TESS target with optional author/cadence hints.
    Falls back to searching without exptime if the first query returns nothing.
    """
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


def search_and_stitch(
    target: str,
    author: str = "SPOC",
    cadence_hint: str = "short",
):
    """
    Download all matching light curves and return (stitched_lightcurve, sectors_list).
    """
    sr = search_result(target, author=author, cadence_hint=cadence_hint)
    if len(sr) == 0:
        raise RuntimeError("No light curves found.")
    lcs = lk.LightCurveCollection([row.download() for row in sr])
    stitched = lcs.stitch().remove_nans().normalize()
    sectors = [getattr(lc, "sector", None) or lc.meta.get("SECTOR") for lc in lcs]
    return stitched, sectors


def run_bls(
    lc_flat: "lk.LightCurve",
    pmin: float = 0.3,
    pmax: float = 20.0,
    dmin: float = 0.01,
    dmax: float = 0.20,
    nper: int = 6000,
):
    """
    Run BLS on a flattened LightCurve and return (bls, P_days, T0_btjd).

    This implementation is resilient across Lightkurve/Astropy releases:
      • Computes P from argmax of bls.power (avoids API differences).
      • Converts transit time to BTJD, with JD→BTJD fallback.
    """
    # Period & duration grids in DAYS
    period = np.linspace(pmin, pmax, int(nper))
    dmax_eff = min(dmax, 0.9 * pmin)  # ensure duration < min(period)
    duration = np.linspace(dmin, max(dmin, dmax_eff), 30)
    if duration.size == 0:
        duration = np.array([0.45 * pmin])

    bls = lc_flat.to_periodogram(
        method="bls",
        period=period,     # days
        duration=duration, # days
        objective="snr",
    )

    # ---- Period at max power (days) via argmax (avoids Quantity/Time quirks)
    idx = int(np.nanargmax(np.asarray(bls.power)))
    per_i = np.asarray(bls.period)[idx]  # Quantity or float
    P = float(per_i.to_value(u.day)) if hasattr(per_i, "to_value") else float(per_i)

    # ---- Transit time at max power → BTJD
    t0 = bls.transit_time_at_max_power  # astropy.time.Time
    # Try direct BTJD
    try:
        T0 = float(t0.to_value("btjd"))
    except Exception:
        # Some versions expose attribute .btjd
        try:
            T0 = float(getattr(t0, "btjd"))
        except Exception:
            # Fallback: JD → BTJD (BJD/JD - 2457000)
            T0 = float(t0.to_value("jd")) - 2457000.0

    return bls, P, T0