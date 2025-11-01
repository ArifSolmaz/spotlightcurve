from __future__ import annotations
import argparse
from .core import search_and_stitch, run_bls
from .preprocess import flatten_lightcurve
from .io import lc_to_csv

def download_main():
    p = argparse.ArgumentParser(description="Download & stitch a TESS light curve")
    p.add_argument("--target", default="WASP-52")
    p.add_argument("--author", default="SPOC")   # SPOC/QLP/Any
    p.add_argument("--cadence", default="short") # short/fast/long
    p.add_argument("--out", default="lightcurve.csv")
    a = p.parse_args()
    lc, _ = search_and_stitch(a.target, author=a.author, cadence_hint=a.cadence)
    lc_to_csv(lc, a.out)
    print(f"Wrote {a.out}")

def bls_main():
    p = argparse.ArgumentParser(description="Run BLS on a fetched/stiched light curve")
    p.add_argument("--target", default="WASP-52")
    p.add_argument("--author", default="SPOC")
    p.add_argument("--cadence", default="short")
    p.add_argument("--pmin", type=float, default=0.3)
    p.add_argument("--pmax", type=float, default=20.0)
    p.add_argument("--dmin", type=float, default=0.01)
    p.add_argument("--dmax", type=float, default=0.20)
    a = p.parse_args()
    lc, _ = search_and_stitch(a.target, author=a.author, cadence_hint=a.cadence)
    lc_flat = flatten_lightcurve(lc)
    _, P, T0 = run_bls(lc_flat, pmin=a.pmin, pmax=a.pmax, dmin=a.dmin, dmax=a.dmax)
    print(f"P={P:.6f} d, T0={T0:.6f} (BTJD)")
