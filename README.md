# spotlightcurve

Minimal tools to fetch, preprocess, and analyze exoplanet transits (TESS/Kepler) and explore star-spot signals, built on [Lightkurve](https://docs.lightkurve.org) and [Astropy](https://www.astropy.org).

## Install (from GitHub)

> Until a PyPI release, install directly from the repo:

```python
%pip install --no-build-isolation "git+https://github.com/ArifSolmaz/spotlightcurve@main"
```

Check the version:

```python
import spotlightcurve as sc
print(getattr(sc, "__version__", "unknown"))
```

## Local development

```bash
git clone https://github.com/ArifSolmaz/spotlightcurve
cd spotlightcurve
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -e .
pytest -q
```

## Quick start (works now)

Fetch a TESS light curve, flatten it, and run a BLS period search.

```python
import matplotlib.pyplot as plt
from spotlightcurve.core import search_and_stitch, run_bls
from spotlightcurve.preprocess import flatten_lightcurve

# 1) Download + stitch TESS light curve(s)
lc, sectors = search_and_stitch("WASP-52", author="SPOC", cadence_hint="short")
print("Sectors:", sectors)

# 2) Flatten (remove long-term trends)
lc_flat = flatten_lightcurve(lc, window_length=401)

# 3) BLS period search
bls, P, T0 = run_bls(lc_flat, pmin=0.3, pmax=20.0)
print(f"BLS: P = {P:.6f} d,  T0 (BTJD) = {T0:.6f}")

# 4) Plot
fig = bls.plot()
plt.show()
```

### (Optional) Simple transit model
If you also install `batman-package`, you can synthesize a basic transit curve:

```python
import numpy as np
import matplotlib.pyplot as plt
from spotlightcurve.model import transit_batman

t = np.linspace(T0 - 0.2, T0 + 0.2, 1200)        # days
model = transit_batman(
    time_days=t,
    rp_rs=0.13, a_rs=12.0, inc_deg=88.0,
    period_days=P, t0_days=T0,
    u1=0.32, u2=0.27, ld_model="quadratic",
    exp_time_days=2.0/(60*24), supersample_factor=7
)

plt.plot((t - T0)*24.0, model)
plt.xlabel("Hours from mid-transit")
plt.ylabel("Relative flux")
plt.tight_layout(); plt.show()
```

## Streamlit app

This repository also includes a Streamlit UI (e.g., `streamlit_app3.py`) that uses the same API.  
To deploy on Streamlit Cloud, set:
- `requirements.txt` with: `streamlit`, `numpy<2`, `pandas`, `matplotlib`, `astropy>=5,<6`, `lightkurve==2.4.3`, `astroquery`, `batman-package`
- `runtime.txt` with `python-3.11`
- Main file: `streamlit_app3.py`

## License

MIT
