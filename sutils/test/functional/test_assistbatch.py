import unittest
from unittest.mock import patch
import subprocess
import sys

class TestAssistbatch(unittest.TestCase):
    def test_can_be_run(self):
        res = subprocess.run(['asbatch', 'filename'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0)

    def test_no_filename_argument_is_error(self):
        res = subprocess.run('asbatch', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 2)
