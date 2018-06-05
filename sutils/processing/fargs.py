"""Part of SLURM Utilities."""

def get_number_fargs(func):
    """Return the number of function arguments"""
    return func.func_code.co_argcount
