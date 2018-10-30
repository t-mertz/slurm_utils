import importlib
import sys
import os

from . import apps

def run_application(app_name=None):
    if app_name is None:
        app_name = os.path.basename(sys.argv[0])
    
    try:
        pckg_name = apps.INSTALLED_APPS[app_name.upper()].lower()
    except KeyError:
        print("Unexpected error: Program {} unknown.".format(app_name))
        sys.exit(1)

    app_module = importlib.import_module('sutils.applications.{}.{}'.format(pckg_name, pckg_name))
    app_pckg = importlib.import_module('sutils.applications.'+pckg_name)

    options = vars(app_pckg.options.parser.parse_args(sys.argv[1:]))

    try:
        app_module.run(options)
    except KeyboardInterrupt:
        print("Keyboard interrupt.")
