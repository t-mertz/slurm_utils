import sys
import argparse
from ..utils import ini


def get_config():
    """Return the essential configuration specifics, i.e. number of parameters,
    total number of jobs..
    """
    params, settings = ini.parameters_from_ini('config.ini')

    return params, settings

def get_number_params():
    return get_config()[0].get_dim()

def get_number_jobs():
    return get_config()[0].get_maxnum()


def main():
    p = argparse.ArgumentParser(prog="SLURM Utilities")
    p.add_argument("-p", help="display number of parameters", action='store_true')
    p.add_argument("-j", help="display number of jobs", action='store_true')
    args = vars(p.parse_args())

    if args['p']:
        print(get_number_params())
    elif args['j']:
        print(get_number_jobs())
    else:
        pass
    