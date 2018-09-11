"""type_traits.py

We need to assess if a string can be converted to int or float.
This module provides simple tests is_<type>.
"""

def is_float(val):
    try:
        return float(val) - val == 0
    except:
        return False
    return False

def is_int(val):
    try:
        return int(val) - val == 0
    except:
        return False
    return False

def is_zero(val):
    return val == 0
