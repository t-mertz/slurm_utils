import unittest
import numpy as np

from . import numeric

class TestPointsRange(unittest.TestCase):
    def test_single_point_is_lo(self):
        self.assertEqual(numeric.points_range(1, 2, 1)[0], 1)

    def test_single_point_has_len_1(self):
        self.assertEqual(len(numeric.points_range(1, 2, 1)), 1)

    def test_two_points_are_hi_and_lo(self):
        self.assertTrue(np.all(numeric.points_range(1, 2, 2) == np.array([1., 2.])))
    
    def test_len_5(self):
        self.assertEqual(len(numeric.points_range(1, 2, 5)), 5)
    
    def test_len_0(self):
        self.assertEqual(len(numeric.points_range(1, 2, 0)), 0)
    
    def test_lo_equals_hi(self):
        self.assertEqual(len(numeric.points_range(1, 1, 2)), 2)

    def test_negative_num_raises_valueerror(self):
        self.assertRaises(ValueError, numeric.points_range, 1, 1, -1)
    
    def test_complex_num_raises_typeerror(self):
        self.assertRaises(TypeError, numeric.points_range, 1, 1, 1j)

class TestStepRange(unittest.TestCase):
    def test_zero_step_raises_valueerror(self):
        self.assertRaises(ValueError, numeric.step_range, 1, 2, 0)

    def test_lo_smaller_hi_negative_step_is_empty(self):
        self.assertEquals(len(numeric.step_range(1, 2, -1)), 0)
    
    def test_lo_larger_hi_positive_step_is_empty(self):
        self.assertEquals(len(numeric.step_range(2, 1, 1)), 0)

    def test_lo_equals_hi_has_len_1(self):
        self.assertEquals(len(numeric.step_range(1, 1, 1)), 1)

    def test_lo_equals_hi_is_lo(self):
        self.assertEquals(numeric.step_range(1, 1, 1)[0], 1)
    
    def test_contains_lo(self):
        self.assertEquals(numeric.step_range(1, 2, 1)[0], 1)
    
    def test_contains_hi(self):
        self.assertEquals(numeric.step_range(1, 2, 1)[-1], 2)

    def test_positive_step_is_correct(self):
        self.assertTrue(np.all(np.diff(numeric.step_range(1, 2, 0.5)) == 0.5))
    
    def test_negative_step_is_correct(self):
        self.assertTrue(np.all(np.diff(numeric.step_range(1, 2, -0.5)) == -0.5))
    
    def test_five_steps(self):
        self.assertEquals(len(numeric.step_range(1, 2, 1./4.)), 5)
    
    def test_all_int_is_int(self):
        self.assertEquals(numeric.step_range(1, 2, 1).dtype, int)
    
    def test_lo_float_is_float(self):
        self.assertTrue(numeric.step_range(1.1, 2, 1).dtype in [np.float64, np.float32, float])
    
    def test_hi_float_is_float(self):
        self.assertTrue(numeric.step_range(1, 2.1, 1).dtype in [np.float64, np.float32, float])
    
    def test_step_float_is_float(self):
        self.assertTrue(numeric.step_range(1, 2, 1.1).dtype in [np.float64, np.float32, float])
    
    def test_lo_hi_float_is_float(self):
        self.assertTrue(numeric.step_range(1.1, 2.1, 1).dtype in [np.float64, np.float32, float])
    
    def test_lo_step_float_is_float(self):
        self.assertTrue(numeric.step_range(1.1, 2, 1.1).dtype in [np.float64, np.float32, float])
    
    def test_hi_step_float_is_float(self):
        self.assertTrue(numeric.step_range(1, 2.1, 1.1).dtype in [np.float64, np.float32, float])

    def test_all_float_is_float(self):
        self.assertTrue(numeric.step_range(1.1, 2.1, 1.1).dtype in [np.float64, np.float32, float])
