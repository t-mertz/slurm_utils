import sys
from . import core

def run(options):
    if 'all' in options:
        run_all()
    elif 'last' in options:
        run_last(options.last)
    elif 'first' in options:
        run_first(options.first)
    else:
        sys.exit(0) # end of program

def run_all():
    core.cancel_all()

def run_last(N):
    core.cancel_last(N)

def run_first(N):
    core.cancel_first(N)
