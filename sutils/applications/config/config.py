from ...config.iniconfig import write_default

def run(options):
    if 'create' in options:
        write_default(options['create'])
