import unittest
from unittest.mock import patch
import subprocess

class TestSubmit(unittest.TestCase):
    def test_can_be_run(self):
        res = subprocess.run('ssubmit', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0)
