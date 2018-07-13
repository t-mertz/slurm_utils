import sys

from ...processing.process import process_exec

def run(options):
    if 'filename' in options:
        process_exec(options['filename'])
    else:
        sys.stderr.write("filename required.\n")
        sys.exit(0) # end of program
