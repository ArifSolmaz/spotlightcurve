# spotlightcurve/core.py
from __future__ import annotations
from astropy import units as u
import numpy as np
import lightkurve as lk

_CADENCE = {"short": "short", "fast": "fast", "long": "long"}

def search_result(target: str, author: str | None = None, cadence_hint: str | None = None):
    """Return a Lightkurve SearchResult for a TESS target with optional author/cadence hints."""
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
    """Download all matching rows and return (stitched_lightcurve, sectors_list)."""
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

    Robust across Lightkurve/Astropy versions:
    - Handles Quantity vs ndarray for period.
    - Handles Time object for transit time (BTJD preferred, JD→BTJD fallback).
    """
    # Period/duration grids in DAYS
    period = np.linspace(pmin, pmax, int(nper))
    dmax_eff = min(dmax, 0.9 * pmin)  # astropy BLS requires duration < min(period)
    duration = np.linspace(dmin, max(dmin, dmax_eff), 30)
    if duration.size == 0:
        duration = np.array([0.45 * pmin])

    bls = lc_flat.to_periodogram(
        method="bls",
        period=period,
        duration=duration,
        objective="snr",
    )

    # --- Period at max power (days) ---
    try:
        # Newer Lightkurve returns a Quantity
        P = bls.period_at_max_power.to_value(u.day)
    except Exception:
        # Fallback: argmax on sampled arrays
        idx = int(np.nanargmax(np.asarray(bls.power)))
        Pq = np.asarray(bls.period)[idx]
        P = Pq.to_value(u.day) if hasattr(Pq, "to_value") else float(Pq)

    # --- Transit time at max power (BTJD) ---
    t0 = bls.transit_time_at_max_power  # astropy.time.Time
    T0 = None
    # Preferred: direct BTJD readout (TESS convention)
    try:
        T0 = float(t0.to_value("btjd"))
    except Exception:
        pass
    # Some versions expose .btjd attribute
    if T0 is None:
        try:
            T0 = float(getattr(t0, "btjd"))
        except Exception:
            pass
    # Fallback: convert JD → BTJD
    if T0 is None:
        T0 = float(t0.to_value("jd")) - 2457000.0

    return bls, float(P), float(T0)