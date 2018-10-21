from . import core

def run(options):
    if options['FILENAME'] is not None:
        core.submit(options['FILENAME'])
    else:
        pass
