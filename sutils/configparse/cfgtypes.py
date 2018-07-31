"""types.py

Here we define types for configparse
"""
import os

# types

class BaseType(object):
    pass


class Type(BaseType):
    """Type conversion.
    
    Use member value to return converted value.
    """
    def __init__(self, str):
        if len(str) == 0:
            raise ValueError("Empty string.")
    
    def value(self):
        return self._value

class IntType(Type):
    """Integer"""
    def __init__(self, str):
        super(IntType, self).__init__(str)
        self._value = int(str)

class FloatType(Type):
    """Integer"""
    def __init__(self, str):
        super(FloatType, self).__init__(str)
        self._value = float(str)

class RealType(Type):
    """This type tries to cast to (in this order): int, float"""
    def __init__(self, str):
        super(RealType, self).__init__(str)
        try:
            self._value = int(str)
        except ValueError:
            try:
                self._value = float(str)
            except ValueError:
                raise ValueError("Cannot cast {} to numeric.".format(str))

class NumericType(Type):
    """This numeric type tries to cast to (in this order): int, float, complex"""
    def __init__(self, string):
        super(NumericType, self).__init__(string)
        try:
            self._value = int(string)
        except ValueError:
            try:
                self._value = float(string)
            except ValueError:
                try:
                    self._value = complex(string)
                except ValueError:
                    raise ValueError("Cannot cast {} to numeric.".format(string))

class StringType(Type):
    """String"""
    def __init__(self, string):
        super(StringType, self).__init__(string)
        self._value = str(string)

class BoolType(Type):
    """Boolean"""
    def __init__(self, string):
        super(BoolType, self).__init__(string)
        self._value = string.lower() in ['true', '1']

class PathType(Type):
    """Path as a string"""
    def __init__(self, string):
        super(PathType, self).__init__(string)
        self._value = os.path.normpath(os.path.normcase(string))


class ListType(Type):
    """Conversion to list containing elements of a certain type.
    
        :param element_t: desired type of the list elements
        :param string: string or list to parse
        :type string: string, list
    """
    def __init__(self, element_t, string):
        super(ListType, self).__init__(string)
        if isinstance(string, str):
            str_list = string.split(',')
        elif isinstance(string, list):
            str_list = string
        else:
            raise TypeError("Input must be string or list.")
        
        for i, item in enumerate(str_list):
            str_list[i] = element_t(item).value()

        self._value = str_list


class StringListType(ListType):
    def __init__(self, str):
        super(StringListType, self).__init__(StringType, str)

class IntListType(ListType):
    def __init__(self, str):
        super(StringListType, self).__init__(IntType, str)

class BoolListType(ListType):
    def __init__(self, str):
        super(StringListType, self).__init__(BoolType, str)
