import unittest
from .. import config


class TestConfig(unittest.TestCase):
    def test_time_full(self):
        time = config.SBATCH_time("1-00:01:1")
        self.assertEqual(time.to_str(), "#SBATCH --time=1-00:01:01")
