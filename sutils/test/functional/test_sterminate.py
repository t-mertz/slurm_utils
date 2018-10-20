import unittest
import subprocess

class TestSterminate(unittest.TestCase):
    def test_can_be_run(self):
        res = subprocess.run('sterminate')
        self.assertEqual(res.returncode, 0)
