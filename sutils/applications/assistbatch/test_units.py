import unittest

from . import units

class TestConvertToBase(unittest.TestCase):
    def test_base_to_base(self):
        self.assertEqual(units.convert_to_base("1001"), 1001)
    
    def test_K_to_base_smaller_goes_to_0(self):
        self.assertEqual(units.convert_to_base("42K"), 0)
    
    def test_K_to_base(self):
        self.assertEqual(units.convert_to_base("2048K"), 2)

    def test_K_to_base_odd_is_rounded(self):
        self.assertEqual(units.convert_to_base("2180K"), 2)
    
    def test_M_to_base(self):
        self.assertEqual(units.convert_to_base("42M"), 42)

    def test_G_to_base(self):
        self.assertEqual(units.convert_to_base("42G"), 42*1024)

    def test_T_to_base(self):
        self.assertEqual(units.convert_to_base("42T"), 42*1024*1024)
