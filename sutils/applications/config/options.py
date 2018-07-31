from ...utils.argparse_wrap import ArgumentParser

parser = ArgumentParser(description="Run configuration program.") \
            .add_argument('-c', '--create', metavar='FILE', type=str, help='Create new default configuration file.')  \
            .add_argument('-d', '--diff', metavar=('FILE1', 'FILE2'), nargs=2, help='Print difference between FILE1 and FILE2.')

