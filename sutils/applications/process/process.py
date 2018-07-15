import sys

from ...processing.process import process_exec

def run(options):
    if options['filename'] is not None:
        process_exec(options['filename'])
    else:
        sys.stderr.write("filename required.\n")
        sys.exit(0) # end of program
