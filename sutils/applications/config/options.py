from ...utils.argparse_wrap import ArgumentParser

parser = ArgumentParser(description="Run configuration program.") \
            .add_argument('-c', '--create', metavar='filename', type=str, help='Create new default configuration file.') 

