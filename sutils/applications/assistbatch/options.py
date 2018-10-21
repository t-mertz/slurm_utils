from ...utils.argparse_wrap import ArgumentParser, SUPPRESS

parser = ArgumentParser(description="Assisted sbatch for load optimization.")#, argument_default=SUPPRESS)
parser.add_argument('FILENAME', nargs=1, help='Name of the script file.')
