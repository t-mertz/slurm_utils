import sys
import os

from ...processing.process import process_exec
from . import core

def run(options):
    if options['filename'] is not None:
        if os.path.exists(options['filename']):
            process_exec(options['filename'])
        else:
            sys.stderr.write("file does not exist.\n")
    else:
        sys.stderr.write("filename required.\n")
        sys.exit(0) # end of program
