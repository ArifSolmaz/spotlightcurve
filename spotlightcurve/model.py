from __future__ import annotations
import numpy as np

def transit_duration_hours(a_rs: float, rp_rs: float, period_days: float,
                           inc_deg: float, ecc: float, omega_deg: float) -> float:
    inc = np.deg2rad(inc_deg)
    b = a_rs * np.cos(inc)
    term = max(0.0, 1.0 - b**2)
    arg = np.clip(np.sqrt(term) / max(a_rs, 1e-6), 0.0, 1.0)
    dur_days = (period_days / np.pi) * np.arcsin(arg)
    return float(24.0 * dur_days)

def _fallback_box(t, rp_rs, t0_days, dur_days):
    t = np.asarray(t, float)
    depth = float(rp_rs) ** 2
    return 1.0 - ((np.abs(t - t0_days) < 0.5 * dur_days) * depth).astype(float)

def transit_batman(*, time_days, rp_rs, a_rs, inc_deg, period_days, t0_days,
                   ecc=0.0, omega_deg=90.0, u1=0.3, u2=0.2, ld_model="quadratic",
                   exp_time_days=None, supersample_factor=None):
    try:
        import batman
    except Exception:
        dur = transit_duration_hours(a_rs, rp_rs, period_days, inc_deg, ecc, omega_deg) / 24.0
        return _fallback_box(time_days, rp_rs, t0_days, dur)

    t = np.asarray(time_days, float)
    params = batman.TransitParams()
    params.t0 = float(t0_days)
    params.per = float(period_days)
    params.rp  = float(rp_rs)
    params.a   = float(a_rs)
    params.inc = float(inc_deg)
    params.ecc = float(ecc)
    params.w   = float(omega_deg)
    params.u   = [float(u1), float(u2)]
    params.limb_dark = ld_model

    if exp_time_days and supersample_factor:
        m = batman.TransitModel(params, t, exp_time=float(exp_time_days), supersample_factor=int(supersample_factor))
    else:
        m = batman.TransitModel(params, t)
    return m.light_curve(params)
