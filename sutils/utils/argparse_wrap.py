# wrapper of argparse.ArgumentParser
# implements the Parser interface

import argparse

class ParserBase(object):
    pass

class Parser(ParserBase):
    """A parser should implement:
        - add_* method that returns itself
        - parse_* method
    """
    pass

class ArgumentParser(Parser):
    def __init__(self, *args, **kwargs):
        self._parser = argparse.ArgumentParser(*args, **kwargs)
    
    def add_argument(self, *args, **kwargs):
        self._parser.add_argument(*args, **kwargs)
        return self
    
    def parse_args(self, *args, **kwargs):
        return self._parser.parse_args(*args, **kwargs)
    
    def add_mutually_exclusive_group(self):
        return ArgumentGroup(self._parser.add_mutually_exclusive_group())
    
class ArgumentGroup(object):
    def __init__(self, group):
        self._group = group
    
    def add_argument(self, *args, **kwargs):
        self._group.add_argument(*args, **kwargs)
        return self
