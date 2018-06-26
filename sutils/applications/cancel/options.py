#from ...utils import argparse
import argparse

# delete
class ArgumentParser(object):
    def __init__(self, *args, **kwargs):
        self._parser = argparse.ArgumentParser(*args, **kwargs)
    
    def add_argument(self, *args, **kwargs):
        self._parser.add_argument(*args, **kwargs)
        return self
    
    def parse_args(self, *args, **kwargs):
        return self._parser.parse_args(*args, **kwargs)
# end delete

parser = ArgumentParser(description="Cancel SLURM jobs.") \
            .add_argument('-l', '--last', metavar='N', nargs=1, type=int, help='Cancel the last N jobs.') \
            .add_argument('-f', '--first', metavar='N', nargs=1, type=int, help='Cancel the first N jobs.')

#parser.parse_args(args)
