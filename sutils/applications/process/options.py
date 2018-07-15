from ...utils.argparse_wrap import ArgumentParser

parser = ArgumentParser(description="Run processing executable in every directory.") \
            .add_argument('filename', nargs=1, type=str, help="name of or path to the file")
