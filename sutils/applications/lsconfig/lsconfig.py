from . import core

def run(options):
    if options["params"] is not None:
        if not options["params"]:
            options["params"] = None # this happens if no parameter name is specified
        core.get_parameter_info(options['params'])
    