import unittest

from . import cfgtypes


class TestIntType(unittest.TestCase):
    def test_empty(self):
        self.assertRaises(ValueError, cfgtypes.IntType, "")

    def test_positive(self):
        self.assertEqual(cfgtypes.IntType("1").value(), 1)

    def test_negative(self):
        self.assertEqual(cfgtypes.IntType("-1").value(), -1)
    
    def test_nonint(self):
        self.assertRaises(ValueError, cfgtypes.IntType, "1.1")

    def test_nonnumeric(self):
        self.assertRaises(ValueError, cfgtypes.IntType, "a")


class TestBoolType(unittest.TestCase):
    def test_empty(self):
        self.assertRaises(ValueError, cfgtypes.BoolType, "")
    
    def test_true_upper(self):
        self.assertEqual(cfgtypes.BoolType("True").value(), True)

    def test_true_lower(self):
        self.assertEqual(cfgtypes.BoolType("true").value(), True)
    
    def test_true_caps(self):
        self.assertEqual(cfgtypes.BoolType("TRUE").value(), True)

    def test_false_upper(self):
        self.assertEqual(cfgtypes.BoolType("False").value(), False)
    
    def test_false_lower(self):
        self.assertEqual(cfgtypes.BoolType("false").value(), False)
    
    def test_false_caps(self):
        self.assertEqual(cfgtypes.BoolType("FALSE").value(), False)

    def test_true_1(self):
        self.assertEqual(cfgtypes.BoolType("1").value(), True)
    
    def test_false_0(self):
        self.assertEqual(cfgtypes.BoolType("0").value(), False)
    
    def test_false_3(self):
        self.assertEqual(cfgtypes.BoolType("3").value(), False)
    
    def test_false_abc(self):
        self.assertEqual(cfgtypes.BoolType("abc").value(), False)
    
class TestFloatType(unittest.TestCase):
    def test_empty_raises_valueerror(self):
        self.assertRaises(ValueError, cfgtypes.FloatType, "")
    
    def test_nonnumeric_char_raises_valueerror(self):
        self.assertRaises(ValueError, cfgtypes.FloatType, "a")
    
    def test_nonnumeric_string_raises_valueerror(self):
        self.assertRaises(ValueError, cfgtypes.FloatType, "abc")

    def test_complex_raises_valueerror(self):
        self.assertRaises(ValueError, cfgtypes.FloatType, "1j")
    
    def test_negative_int(self):
        self.assertEqual(cfgtypes.FloatType("-1").value(), -1)
    
    def test_int(self):
        self.assertEqual(cfgtypes.FloatType("1").value(), 1)
    
    def test_decimal(self):
        self.assertEqual(cfgtypes.FloatType("4.15").value(), 4.15)
    
    def test_cut_decimal(self):
        self.assertEqual(cfgtypes.FloatType("2.").value(), 2.)
    
    def test_trailing_decimal(self):
        self.assertEqual(cfgtypes.FloatType(".3").value(), .3)

    def test_negative_decimal(self):
        self.assertEqual(cfgtypes.FloatType("-4.15").value(), -4.15)
    
    def test_negative_cut_decimal(self):
        self.assertEqual(cfgtypes.FloatType("-2.").value(), -2.)

    def test_negative_trailing_decimal(self):
        self.assertEqual(cfgtypes.FloatType("-.3").value(), -.3)
    
class TestRealType(unittest.TestCase):
    def test_int(self):
        self.assertEqual(cfgtypes.RealType("2").value(), 2)
    
    def test_float(self):
        self.assertEqual(cfgtypes.RealType("2.2").value(), 2.2)

    def test_neg_int(self):
        self.assertEqual(cfgtypes.RealType("-2").value(), -2)
    
    def test_neg_float(self):
        self.assertEqual(cfgtypes.RealType("-2.2").value(), -2.2)

    def test_int_cast_to_int(self):
        self.assertEqual(type(cfgtypes.RealType("2").value()), int)
    
    def test_float_cast_to_float(self):
        self.assertEqual(type(cfgtypes.RealType("2.2").value()), float)
    
    def test_neg_int_cast_to_int(self):
        self.assertEqual(type(cfgtypes.RealType("-2").value()), int)
    
    def test_neg_float_cast_to_float(self):
        self.assertEqual(type(cfgtypes.RealType("-2.2").value()), float)

    def test_complex_raises_valueerror(self):
        self.assertRaises(ValueError, cfgtypes.RealType, "2j")

    def test_nonnumeric_raises_valueerror(self):
        self.assertRaises(ValueError, cfgtypes.RealType, "abc")


class TestNumericType(unittest.TestCase):
    def test_int(self):
        self.assertEqual(cfgtypes.NumericType("2").value(), 2)
    
    def test_float(self):
        self.assertEqual(cfgtypes.NumericType("2.2").value(), 2.2)
    
    def test_complex(self):
        self.assertEqual(cfgtypes.NumericType("2j").value(), 2j)

    def test_neg_int(self):
        self.assertEqual(cfgtypes.NumericType("-2").value(), -2)
    
    def test_neg_float(self):
        self.assertEqual(cfgtypes.NumericType("-2.2").value(), -2.2)
    
    def test_neg_complex(self):
        self.assertEqual(cfgtypes.NumericType("-2j").value(), -2j)
    
    def test_int_cast_to_int(self):
        self.assertEqual(type(cfgtypes.NumericType("2").value()), int)
    
    def test_float_cast_to_float(self):
        self.assertEqual(type(cfgtypes.NumericType("2.2").value()), float)
    
    def test_complex_cast_to_complex(self):
        self.assertEqual(type(cfgtypes.NumericType("2j").value()), complex)

    def test_neg_int_cast_to_int(self):
        self.assertEqual(type(cfgtypes.NumericType("-2").value()), int)
    
    def test_neg_float_cast_to_float(self):
        self.assertEqual(type(cfgtypes.NumericType("-2.2").value()), float)
    
    def test_neg_complex_cast_to_complex(self):
        self.assertEqual(type(cfgtypes.NumericType("-2j").value()), complex)

    def test_nonnumeric_raises_valueerror(self):
        self.assertRaises(ValueError, cfgtypes.NumericType, "abc")

class TestStringType(unittest.TestCase):
    pass

class TestPathType(unittest.TestCase):
    pass

class TestListType(unittest.TestCase):
    # this is a base type, it is tested with the derived types
    pass

class TestStringListType(unittest.TestCase):
    def test_single_item_is_len_1_list(self):
        self.assertEqual(len(cfgtypes.StringListType("1")), 1)

    def test_single_item_is_in_list(self):
        self.assertEqual(cfgtypes.StringListType("1").value(), ["1"])
    
    def test_comma_separator_without_spaces_len(self):
        self.assertEqual(len(cfgtypes.StringListType("1,2,3,4")), 4)

    def test_comma_separator_without_spaces(self):
        self.assertEqual(cfgtypes.StringListType("1,2,3,4").value(), ["1", "2", "3", "4"])

    def test_comma_separator_with_spaces_len(self):
        self.assertEqual(len(cfgtypes.StringListType("1, 2, 3, 4")), 4)

    def test_comma_separator_with_spaces(self):
        self.assertEqual(cfgtypes.StringListType("1, 2, 3, 4").value(), ["1", "2", "3", "4"])

    def test_comma_separator_with_more_spaces_len(self):
        self.assertEqual(len(cfgtypes.StringListType("1 , 2 , 3  , 4")), 4)
    
    def test_comma_separator_with_more_spaces(self):
        self.assertEqual(cfgtypes.StringListType("1 , 2 , 3  , 4").value(), ["1", "2", "3", "4"])

    def test_single_word_is_len_1_list(self):
        self.assertEqual(len(cfgtypes.StringListType("word")), 1)

    def test_single_word_is_in_list(self):
        self.assertEqual(cfgtypes.StringListType("word").value(), ["word"])
    
    def test_words_comma_separator_without_spaces_len(self):
        self.assertEqual(len(cfgtypes.StringListType("word1,word2,word3,word4")), 4)

    def test_words_comma_separator_without_spaces(self):
        self.assertEqual(cfgtypes.StringListType("word1,word2,word3,word4").value(), ["word1", "word2", "word3", "word4"])

    def test_words_comma_separator_with_spaces_len(self):
        self.assertEqual(len(cfgtypes.StringListType("word1, word2, word3, word4")), 4)

    def test_words_comma_separator_with_spaces(self):
        self.assertEqual(cfgtypes.StringListType("word1, word2, word3, word4").value(), ["word1", "word2", "word3", "word4"])

    def test_words_comma_separator_with_more_spaces_len(self):
        self.assertEqual(len(cfgtypes.StringListType("word1 , word2 , word3  , word4")), 4)
    
    def test_words_comma_separator_with_more_spaces(self):
        self.assertEqual(cfgtypes.StringListType("word1 , word2 , word3  , word4").value(), ["word1", "word2", "word3", "word4"])

class TestIntListType(unittest.TestCase):
    def test_single_item_is_len_1_list(self):
        self.assertEqual(len(cfgtypes.IntListType("1")), 1)

    def test_single_item_is_in_list(self):
        self.assertEqual(cfgtypes.IntListType("1").value(), [1])
    
    def test_comma_separator_without_spaces_len(self):
        self.assertEqual(len(cfgtypes.IntListType("1,2,3,4")), 4)

    def test_comma_separator_without_spaces(self):
        self.assertEqual(cfgtypes.IntListType("1,2,3,4").value(), [1, 2, 3, 4])

    def test_comma_separator_with_spaces_len(self):
        self.assertEqual(len(cfgtypes.IntListType("1, 2, 3, 4")), 4)

    def test_comma_separator_with_spaces(self):
        self.assertEqual(cfgtypes.IntListType("1, 2, 3, 4").value(), [1, 2, 3, 4])

    def test_comma_separator_with_more_spaces_len(self):
        self.assertEqual(len(cfgtypes.IntListType("1 , 2 , 3  , 4")), 4)
    
    def test_comma_separator_with_more_spaces(self):
        self.assertEqual(cfgtypes.IntListType("1 , 2 , 3  , 4").value(), [1, 2, 3, 4])

class TestBoolListType(unittest.TestCase):
    def test_single_item_is_len_1_list(self):
        self.assertEqual(len(cfgtypes.BoolListType("1")), 1)

    def test_single_item_is_in_list(self):
        self.assertEqual(cfgtypes.BoolListType("1").value(), [True])
    
    def test_comma_separator_without_spaces_len(self):
        self.assertEqual(len(cfgtypes.BoolListType("True,False,0,1")), 4)

    def test_comma_separator_without_spaces(self):
        self.assertEqual(cfgtypes.BoolListType("True,False,0,1").value(), [True, False, False, True])

    def test_comma_separator_with_spaces_len(self):
        self.assertEqual(len(cfgtypes.BoolListType("True, False, 0, 1")), 4)

    def test_comma_separator_with_spaces(self):
        self.assertEqual(cfgtypes.BoolListType("True, False, 0, 1").value(), [True, False, False, True])

    def test_comma_separator_with_more_spaces_len(self):
        self.assertEqual(len(cfgtypes.BoolListType("True , False , 0  , 1")), 4)
    
    def test_comma_separator_with_more_spaces(self):
        self.assertEqual(cfgtypes.BoolListType("True , False , 0  , 1").value(), [True, False, False, True])
