from . import core

def run(options):
    if "params" in options:
        core.get_parameter_info(options['params'])
    