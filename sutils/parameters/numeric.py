"""numeric.py

Some useful functions.
"""
import numpy as np
from .type_traits import is_float, is_int, is_zero

def points_range(lo, hi, num):
    """Returns a range from :lo: to :hi: including :num: points. Is always float."""
    return np.linspace(lo, hi, num)

def step_range(lo, hi, step):
    """Returns a range from :lo: to :hi: in steps of :step:. :hi: is always included.

        If :lo:, :hi: and :step: are integers, the range will contain only integers.
        Otherwise the range will contain floats.
    """
    if is_zero(step):
        raise ValueError("Step cannot be zero.")
    if is_int(lo) and is_int(hi) and is_int(step):
        return np.arange(lo, hi+step, step, dtype=int)
    else:
        return np.arange(lo, hi+step/2, step)
