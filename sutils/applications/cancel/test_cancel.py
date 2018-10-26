import unittest
from unittest.mock import patch, call, Mock
import getpass
import subprocess

from . import cancel
from ...test import test

def fix_mock_popen(func):
    def wrapper(self, popen, get_jobs):
        process_mock = Mock()
        attrs = {'communicate.return_value': (b'', b'')}
        process_mock.configure_mock(**attrs)
        popen.return_value = process_mock
        func(self, popen, get_jobs)
    return wrapper


@patch("sys.stdout.write", Mock())
@patch("sutils.applications.cancel.core.get_jobs", return_value=(0, 1, 2))
@patch("subprocess.Popen")
class TestScancel(unittest.TestCase):
    @fix_mock_popen
    def test_calls_get_jobs(self, popen, get_jobs):
        cancel.run({'all': True, 'last': None, 'first': None, 'force': False})
        from . import core
        core.get_jobs.assert_called_once_with()

    @fix_mock_popen
    def test_all(self, popen, get_jobs):
        cancel.run({'all': True, 'last': None, 'first': None, 'force': False})
        calls = [
            call(["scancel", 0], stderr=-1, stdout=-1),
            call().communicate(),
            call(["scancel", 1], stderr=-1, stdout=-1),
            call().communicate(),
            call(["scancel", 2], stderr=-1, stdout=-1),
            call().communicate()
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 3)

    @fix_mock_popen
    def test_all_force(self, popen, get_jobs):
        cancel.run({'all': True, 'last': None, 'first': None, 'force': True})
        calls = [
            call(['scancel', 0, 1, 2], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 1)

    @fix_mock_popen
    def test_first1(self, popen, get_jobs):
        cancel.run({'all': None, 'last': None, 'first': 1, 'force': False})
        calls = [
            call(['scancel', 0], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 1)

    @fix_mock_popen
    def test_first2(self, popen, get_jobs):
        cancel.run({'all': None, 'last': None, 'first': 2, 'force': False})
        calls = [
            call(['scancel', 0], stderr=-1, stdout=-1),
            call().communicate(),
            call(['scancel', 1], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 2)

    @fix_mock_popen
    def test_last1(self, popen, get_jobs):
        cancel.run({'all': None, 'last': 1, 'first': None, 'force': False})
        calls = [
            call(["scancel", 2], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 1)

    @fix_mock_popen
    def test_last2(self, popen, get_jobs):
        cancel.run({'all': None, 'last': 2, 'first': None, 'force': False})
        calls = [
            call(["scancel", 2], stderr=-1, stdout=-1),
            call().communicate(),
            call(["scancel", 1], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 2)

    @fix_mock_popen
    def test_last2_force(self, popen, get_jobs):
        cancel.run({'all': None, 'last': 2, 'first': None, 'force': True})
        #res = test.cmd_buffer.flush()
        #commands = res.strip().split("\n")
        calls = [
            call(["scancel", 2, 1], stderr=-1, stdout=-1),
            call().communicate()
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 1)
        # self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        # self.assertEqual(commands[1], "scancel {}".format("2 1"))
        # self.assertEqual(len(commands), 2)

    @fix_mock_popen    
    def test_first2_force(self, popen, get_jobs):
        cancel.run({'all': None, 'last': None, 'first': 2, 'force': True})
        calls = [
            call(['scancel', 0, 1], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 1)
    
    @fix_mock_popen
    def test_last1_force(self, popen, get_jobs):
        cancel.run({'all': None, 'last': 1, 'first': None, 'force': True})
        calls = [
            call(["scancel", 2], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 1)
        #res = test.cmd_buffer.flush()
        #commands = res.strip().split("\n")
        #self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        #self.assertEqual(commands[1], "scancel {}".format("2"))
        #self.assertEqual(len(commands), 2)
    
    @fix_mock_popen
    def test_first1_force(self, popen, get_jobs):
        cancel.run({'all': None, 'last': None, 'first': 1, 'force': True})
        calls = [
            call(['scancel', 0], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 1)
    
    @fix_mock_popen
    def test_first5_cancels_all_if_less_are_running(self, popen, get_jobs):
        cancel.run({'all': None, 'last': None, 'first': 5, 'force': False})
        calls = [
            call(['scancel', 0], stderr=-1, stdout=-1),
            call().communicate(),
            call(['scancel', 1], stderr=-1, stdout=-1),
            call().communicate(),
            call(['scancel', 2], stderr=-1, stdout=-1),
            call().communicate()
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 3)

    @fix_mock_popen
    def test_last5_cancels_all_if_less_are_running(self, popen, get_jobs):
        cancel.run({'all': None, 'last': 5, 'first': None, 'force': False})
        #res = test.cmd_buffer.flush()
        #commands = res.strip().split("\n")
        calls = [
            call(["scancel", 2], stderr=-1, stdout=-1),
            call().communicate(),
            call(["scancel", 1], stderr=-1, stdout=-1),
            call().communicate(),
            call(["scancel", 0], stderr=-1, stdout=-1),
            call().communicate(),
        ]
        popen.assert_has_calls(calls)
        self.assertEqual(popen.call_count, 3)
        # self.assertEqual(commands[0], "squeue --user {} --noheader".format(getpass.getuser()))
        # self.assertEqual(commands[1], "scancel {}".format(2))
        # self.assertEqual(commands[2], "scancel {}".format(1))
        # self.assertEqual(commands[3], "scancel {}".format(0))
        # self.assertEqual(len(commands), 4)
