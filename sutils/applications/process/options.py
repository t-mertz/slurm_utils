from ...utils.argparse_wrap import ArgumentParser

parser = ArgumentParser(description="Run processing executable in every directory.") \
            .add_argument('filename', metavar='FILE', type=str, help="name of or path to the file") \
            .add_argument('-d', '--directory', metavar='PATH', type=str, help="root directory of the calculation") \
            .add_argument('-f', '--file', metavar='FILENAME', type=str, help="name of the config file") \
            .add_argument('start', metavar='START', nargs='?', type=int, help="first job to consider")
