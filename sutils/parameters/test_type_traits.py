import unittest

from . import type_traits # is_int, is_float

class TestIsInt(unittest.TestCase):
    def test_None(self):
        self.assertFalse(type_traits.is_int(None))
    
    def test_False(self):
        self.assertTrue(type_traits.is_int(False))
    
    def test_True(self):
        self.assertTrue(type_traits.is_int(True))
    
    def test_list(self):
        self.assertFalse(type_traits.is_int([]))
    
    def test_dict(self):
        self.assertFalse(type_traits.is_int({}))
    
    def test_complex(self):
        self.assertFalse(type_traits.is_int(1j))
    
    def test_float(self):
        self.assertFalse(type_traits.is_int(1.2))
    
    def test_nfloat(self):
        self.assertFalse(type_traits.is_int(-1.5))
    
    def test_char(self):
        self.assertFalse(type_traits.is_int('a'))

    def test_emptychar(self):
        self.assertFalse(type_traits.is_int(''))
    
    def test_numericchar(self):
        self.assertFalse(type_traits.is_int('4'))
    
    def test_numericstring(self):
        self.assertFalse(type_traits.is_int('10'))
    
    def test_string(self):
        self.assertFalse(type_traits.is_int('False'))
    
    def test_0(self):
        self.assertTrue(type_traits.is_int(0))

    def test_5(self):
        self.assertTrue(type_traits.is_int(5))
    
    def test_n5(self):
        self.assertTrue(type_traits.is_int(-5))
    

    """ there is no 'long' type in python3"""
    #def test_7L(self):
    #    self.assertTrue(type_traits.is_int(7L))
    
    #def test_n7L(self):
    #    self.assertTrue(type_traits.is_int(-7L))


class TestIsFloat(unittest.TestCase):
    def test_None(self):
        self.assertFalse(type_traits.is_float(None))
    
    def test_False(self):
        self.assertTrue(type_traits.is_float(False))
    
    def test_True(self):
        self.assertTrue(type_traits.is_float(True))
    
    def test_list(self):
        self.assertFalse(type_traits.is_float([]))
    
    def test_dict(self):
        self.assertFalse(type_traits.is_float({}))
    
    def test_complex(self):
        self.assertFalse(type_traits.is_float(1j))
    
    def test_float(self):
        self.assertTrue(type_traits.is_float(1.2))
    
    def test_nfloat(self):
        self.assertTrue(type_traits.is_float(-1.5))
    
    def test_char(self):
        self.assertFalse(type_traits.is_float('a'))

    def test_emptychar(self):
        self.assertFalse(type_traits.is_float(''))
    
    def test_numericchar(self):
        self.assertFalse(type_traits.is_float('4'))
    
    def test_numericstring(self):
        self.assertFalse(type_traits.is_float('10'))
    
    def test_string(self):
        self.assertFalse(type_traits.is_float('False'))
    
    def test_0(self):
        self.assertTrue(type_traits.is_float(0))

    def test_5(self):
        self.assertTrue(type_traits.is_float(5))
    
    def test_n5(self):
        self.assertTrue(type_traits.is_float(-5))
    
    """ there is no 'long' type in python3"""
    # def test_7L(self):
    #     self.assertTrue(type_traits.is_float(7L))
    
    # def test_n7L(self):
    #     self.assertTrue(type_traits.is_float(-7L))
    
class TestIsZero(unittest.TestCase):
    def test_None(self):
        self.assertFalse(type_traits.is_zero(None))
    
    def test_False(self):
        self.assertTrue(type_traits.is_zero(False))
    
    def test_True(self):
        self.assertFalse(type_traits.is_zero(True))
    
    def test_list(self):
        self.assertFalse(type_traits.is_zero([]))
    
    def test_dict(self):
        self.assertFalse(type_traits.is_zero({}))
    
    def test_complex(self):
        self.assertFalse(type_traits.is_zero(1j))
    
    def test_float(self):
        self.assertFalse(type_traits.is_zero(1.2))
    
    def test_nfloat(self):
        self.assertFalse(type_traits.is_zero(-1.5))
    
    def test_char(self):
        self.assertFalse(type_traits.is_zero('a'))

    def test_emptychar(self):
        self.assertFalse(type_traits.is_zero(''))
    
    def test_numericchar(self):
        self.assertFalse(type_traits.is_zero('4'))
    
    def test_numericstring(self):
        self.assertFalse(type_traits.is_zero('10'))
    
    def test_string(self):
        self.assertFalse(type_traits.is_zero('False'))
    
    def test_0(self):
        self.assertTrue(type_traits.is_zero(0))

    def test_n0(self):
        self.assertTrue(type_traits.is_zero(-0))
    
    def test_float_0(self):
        self.assertTrue(type_traits.is_zero(0.))

    def test_complex_0(self):
        self.assertTrue(type_traits.is_zero(0.j))

    def test_5(self):
        self.assertFalse(type_traits.is_zero(5))
    
    def test_n5(self):
        self.assertFalse(type_traits.is_zero(-5))
    
    """ there is no 'long' type in python3"""
    # def test_7L(self):
    #     self.assertFalse(type_traits.is_zero(7L))
    
    # def test_n7L(self):
    #     self.assertFalse(type_traits.is_zero(-7L))
