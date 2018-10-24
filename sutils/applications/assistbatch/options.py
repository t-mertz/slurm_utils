from ...utils.argparse_wrap import ArgumentParser, SUPPRESS

parser = ArgumentParser(description="Assisted sbatch for load optimization.")#, argument_default=SUPPRESS)
parser.add_argument('FILENAME', help='Name of the script file.')
