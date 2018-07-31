import unittest
import getpass

from . import cancel
from ...test import test

class TestScancel(unittest.TestCase):
    def test_all(self):
        cancel.run({'all': True, 'last': None, 'first': None, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(0))
        self.assertEqual(commands[2], "scancel {}".format(1))
        self.assertEqual(commands[3], "scancel {}".format(2))

        
