from ...utils.argparse import ArgumentParser

parser = ArgumentParser(description="Run configuration program.") \
            .add_argument('-c', '--create', metavar='filename', nargs=1, type=str, help='Create new default configuration file.') 

