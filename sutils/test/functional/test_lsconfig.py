import unittest
import subprocess

class TestLSconfig(unittest.TestCase):
    def test_can_be_run(self):
        res = subprocess.run('slsconfig')
        self.assertEqual(res.returncode, 0)
