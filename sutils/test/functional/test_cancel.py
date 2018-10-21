import unittest
from unittest.mock import patch
import subprocess

class TestCancel(unittest.TestCase):
    @patch('sutils.applications.cancel.cancel.run')
    def test_can_be_run(self, run):
        res = subprocess.run('sterminate', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0)
