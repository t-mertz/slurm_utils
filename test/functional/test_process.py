import unittest
from unittest.mock import patch
import subprocess

class TestProcess(unittest.TestCase):
    def test_can_be_run(self):
        res = subprocess.run(['sprocess', 'filename'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0)

    def test_no_argument_is_an_error(self):
        res = subprocess.run('sprocess', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 2)
