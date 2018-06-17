"""type_traits.py

We need to assess if a string can be converted to int or float.
This module provides simple tests is_<type>.
"""

def is_float(val):
    try:
        float(val)
    except:
        return False
    return True

def is_int(val):
    try:
        int(val)
    except:
        return False
    return True
