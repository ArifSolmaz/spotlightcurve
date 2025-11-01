__version__ = "0.0.1"
from .core import search_and_stitch, search_result, run_bls
from .preprocess import quality_mask, flatten_lightcurve
from .model import transit_batman, transit_duration_hours
__all__ = [
    "search_and_stitch","search_result","run_bls",
    "quality_mask","flatten_lightcurve",
    "transit_batman","transit_duration_hours",
]
