from unittest import TestLoader,TextTestRunner

TESTMODE = False

def testmode():
    """Check if testmode is enabled."""
    return TESTMODE

def set_testmode(val):
    """Enable/disable testmode. This will catch all system calls and instead
    produce debug output that is suitable for tests.
    """
    global TESTMODE
    TESTMODE = bool(val)

class StringBuffer(object):
    def __init__(self, force_newline=False):
        self._value = ""
        self._force_newline = force_newline
    
    def write(self, input):
        self._value += str(input)
        if self._force_newline:
            self._value += "\n"
    
    def get(self):
        return self._value
    
    def flush(self):
        tmp = self._value
        self._value = ""

        return tmp
    

cmd_buffer = StringBuffer(force_newline=True)

loader = TestLoader()

suite = loader.discover(".", pattern='test*.py', top_level_dir=".")
