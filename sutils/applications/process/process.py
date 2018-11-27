import sys
import os

from ...processing.process import process_exec
from . import core

def run(options):
    kwargs = {}
    if options['directory'] is not None:
        kwargs['root_path'] = options['directory']
    if options['file'] is not None:
        kwargs['config_file'] = options['file']

    if options['filename'] is not None:
        if os.path.exists(options['filename']):
            core.run_process(options['filename'], **kwargs)
        else:
            sys.stderr.write("file does not exist.\n")
    else:
        sys.stderr.write("filename required.\n")
        sys.exit(0) # end of program
