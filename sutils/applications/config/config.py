from ...config.iniconfig import write_default
from . import core

def run(options):
    if options['create'] is not None:
        write_default(options['create'])
    if options['diff'] is not None:
        core.print_diff(options['diff'][0], options['diff'][1])
    
    # no optional arguments
    print("Interactive mode not yet implemented.")
