from sutils.test import test
from unittest import TextTestRunner


if __name__ == "__main__":
    test.set_testmode(True)
    suite = test.get_suite()
    TextTestRunner(buffer=True).run(suite)
