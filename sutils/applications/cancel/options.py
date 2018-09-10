from ...utils.argparse_wrap import ArgumentParser, SUPPRESS
#import argparse

# delete
# class ArgumentParser(object):
#     def __init__(self, *args, **kwargs):
#         self._parser = argparse.ArgumentParser(*args, **kwargs)
    
#     def add_argument(self, *args, **kwargs):
#         self._parser.add_argument(*args, **kwargs)
#         return self
    
#     def parse_args(self, *args, **kwargs):
#         return self._parser.parse_args(*args, **kwargs)
# end delete

parser = ArgumentParser(description="Cancel SLURM jobs of current user.")#, argument_default=SUPPRESS)
parser.add_mutually_exclusive_group() \
            .add_argument('-l', '--last', metavar='N', type=int, help='Cancel the last N jobs.') \
            .add_argument('-f', '--first', metavar='N', type=int, help='Cancel the first N jobs.') \
            .add_argument('-a', '--all', nargs=0, help='Cancel all jobs.') \
            .add_argument('-F', '--force', nargs=0, action='store_true', help='Force immediate cancellation of all jobs. Faster but cannot be aborted.')

#parser.parse_args(args)
