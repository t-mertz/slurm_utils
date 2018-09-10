import unittest
import getpass

from . import cancel
from ...test import test

class TestScancel(unittest.TestCase):
    def test_all(self):
        cancel.run({'all': True, 'last': None, 'first': None, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(0))
        self.assertEqual(commands[2], "scancel {}".format(1))
        self.assertEqual(commands[3], "scancel {}".format(2))
        self.assertEqual(len(commands), 4)

    def test_all_force(self):
        cancel.run({'all': True, 'last': None, 'first': None, 'force': True})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format("0 1 2"))
        self.assertEqual(len(commands), 2)

    def test_first1(self):
        cancel.run({'all': None, 'last': None, 'first': 1, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(0))
        self.assertEqual(len(commands), 2)

    def test_first2(self):
        cancel.run({'all': None, 'last': None, 'first': 2, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(0))
        self.assertEqual(commands[2], "scancel {}".format(1))
        self.assertEqual(len(commands), 3)

    def test_last1(self):
        cancel.run({'all': None, 'last': 1, 'first': None, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(2))
        self.assertEqual(len(commands), 2)

    def test_last2(self):
        cancel.run({'all': None, 'last': 2, 'first': None, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(2))
        self.assertEqual(commands[2], "scancel {}".format(1))
        self.assertEqual(len(commands), 3)

    def test_last2_force(self):
        cancel.run({'all': None, 'last': 2, 'first': None, 'force': True})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format("2 1"))
        self.assertEqual(len(commands), 2)
    
    def test_first2_force(self):
        cancel.run({'all': None, 'last': None, 'first': 2, 'force': True})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format("0 1"))
        self.assertEqual(len(commands), 2)
    
    def test_last1_force(self):
        cancel.run({'all': None, 'last': 1, 'first': None, 'force': True})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format("2"))
        self.assertEqual(len(commands), 2)
    
    def test_first1_force(self):
        cancel.run({'all': None, 'last': None, 'first': 1, 'force': True})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format("0"))
        self.assertEqual(len(commands), 2)
        
    def test_first5_cancels_all_if_less_are_running(self):
        cancel.run({'all': None, 'last': None, 'first': 5, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(0))
        self.assertEqual(commands[2], "scancel {}".format(1))
        self.assertEqual(commands[3], "scancel {}".format(2))
        self.assertEqual(len(commands), 4)

    def test_last5_cancels_all_if_less_are_running(self):
        cancel.run({'all': None, 'last': 5, 'first': None, 'force': False})
        res = test.cmd_buffer.flush()
        commands = res.strip().split("\n")
        self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        self.assertEqual(commands[1], "scancel {}".format(2))
        self.assertEqual(commands[2], "scancel {}".format(1))
        self.assertEqual(commands[3], "scancel {}".format(0))
        self.assertEqual(len(commands), 4)
