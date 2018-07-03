import importlib
import sys
import os

from ..applications import apps

def run_application():
    app_name = os.path.basename(sys.argv[0])
    try:
        pckg_name = apps.INSTALLED_APPS[app_name.upper()].lower()
    except KeyError:
        print("Unexpected error: Program {} unknown.".format(app_name))
        sys.exit(1)

    app_module = importlib.import_module(pckg_name, package='..applications.'+pckg_name)
    app_pckg = importlib.import_module(pckg_name, package='..applications')

    options = app_pckg.options.parser.parse_args(sys.argv[1:])

    app_module.run(options)
