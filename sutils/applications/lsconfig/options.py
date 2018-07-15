from ...utils.argparse_wrap import ArgumentParser

parser = ArgumentParser(description="Run configuration list program.") \
            .add_argument('-p', '--params', nargs='?', type=str, help='Display parameter information.', const=False, default=None)

