import unittest
from unittest.mock import patch
import subprocess

class TestConfig(unittest.TestCase):
    def test_can_be_run(self):
        res = subprocess.run('sconfig', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0)
