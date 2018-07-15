import sys
from . import core

def run(options):
    if options['all'] is not None:
        run_all()
    elif options['last'] is not None:
        run_last(options.last)
    elif options['first'] is not None:
        run_first(options.first)
    else:
        sys.exit(0) # end of program

def run_all():
    core.cancel_all()

def run_last(N):
    core.cancel_last(N)

def run_first(N):
    core.cancel_first(N)
