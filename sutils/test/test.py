from unittest import TestLoader,TextTestRunner

TESTMODE = False

def set_testmode(val):
    """Enable/disable testmode. This will catch all system calls and instead
    produce debug output that is suitable for tests.
    """
    global TESTMODE
    TESTMODE = bool(val)

loader = TestLoader()

suite = loader.discover(".", pattern='test*.py', top_level_dir=".")
