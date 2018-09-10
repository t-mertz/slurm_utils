from ...utils.argparse_wrap import ArgumentParser

parser = ArgumentParser(description="Run submission agent.") \
            .add_argument('-f', '--file', nargs=1, type=str, help="Name of or path to a configuration file") \
            .add_argument('START', nargs='?', default=1, type=int, help="First job to submit") \
            .add_argument('N', type=int, help="Number of jobs to submit")
