import sys
from . import core

def run(options):
    if options['all'] is not None:
        run_all(force=options['force'])
    elif options['last'] is not None:
        run_last(options['last'], force=options['force'])
    elif options['first'] is not None:
        run_first(options['first'], force=options['force'])
    else:
        sys.exit(0) # end of program

def run_all(force=False):
    core.cancel_all(force=force)

def run_last(N, force=False):
    core.cancel_last(N, force=force)

def run_first(N, force=False):
    core.cancel_first(N, force=force)
