"""Convert units for human readable values"""

conv_factor = {
    'K': 1/1024,
    'M': 1,
    'G': 1024,
    'T': 1024*1024
}

def convert_to_base(string):
    """Convert the string to an integer number of base units.
    Example: 3G = 3*1024
    """
    stripped = string.strip()
    try:
        return int(stripped)
    except ValueError:
        if stripped[-1] in ('K', 'M', 'G', 'T'):
            return int(int(stripped[:-1]) * conv_factor[stripped[-1]])
        else:
            ValueError(f"Invalid unit {stripped[-1]}")
