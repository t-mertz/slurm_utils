from ...utils.argparse import ArgumentParser

parser = ArgumentParser(description="Run configuration list program.") \
            .add_argument('-p', '--params', nargs='?', type=str, help='Display parameter information.', const='all', default=False)

