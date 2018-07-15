from ...config.iniconfig import write_default

def run(options):
    if options['create'] is not None:
        write_default(options['create'])
