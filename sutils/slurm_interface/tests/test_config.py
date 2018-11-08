import unittest
from .. import config


class TestConfig(unittest.TestCase):
    def test_time_full(self):
        time = config.SBATCH_time("1-00:01:1")
        self.assertEqual(time.to_str(), "#SBATCH --time=1-00:01:01")


class TestSbatchConfig(unittest.TestCase):
    def test_exclusive_is_appended(self):
        conf = config.SbatchConfig(exclusive=True)
        self.assertEqual(conf.to_list(), ["--exclusive"])

    def test_nonexclusive_is_ignored(self):
        conf = config.SbatchConfig(exclusive=False)
        self.assertEqual(conf.to_list(), [])
