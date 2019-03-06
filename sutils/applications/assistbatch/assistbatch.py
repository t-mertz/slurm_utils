import os
import sys

from . import core

def run(options):
    if options['FILENAME'] is not None:
        if os.access(options['FILENAME'], os.R_OK):
            core.submit(options['FILENAME'])
        else:
            sys.stderr.write("No permission to read '{}'\n".format(options['FILENAME']))
    else:
        pass
