import unittest
from unittest.mock import Mock, patch

import numpy as np

from .. import api as slurm


@patch("sutils.slurm_interface.api._sinfo")
class TestSinfo(unittest.TestCase):
    def test_nooutput(self, _sinfo):
        _sinfo.return_value = ""

        res = slurm.SinfoResult("")
        self.assertEqual(slurm.sinfo()._data, res._data)

    def test_singleline(self, _sinfo):
        retval = "a b c d"
        _sinfo.return_value = retval

        res = slurm.SinfoResult(retval)
        self.assertEqual(slurm.sinfo()._data, res._data)


class TestSinfoResult(unittest.TestCase):
    def test_single_line_has_one_array_row(self):
        retval = "a b c d\n"

        res = slurm.SinfoResult(retval)
        self.assertTrue(np.all(res._data_array == np.array([["a", "b", "c", "d"]])))


class TestResult(unittest.TestCase):
    def test_empty_string_makes_empty_result(self):
        self.assertEqual(len(slurm.Result("")), 0)
