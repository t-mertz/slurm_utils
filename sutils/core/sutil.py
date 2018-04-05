# part of SLURM Utilities (sutil)
# implements the argument parsing

import argparse
import core


def get_splash_msg():
    help_msg = "\n"
    help_msg += "You are running ssubmit version {}".format(core.VERSION) + "\n"
    help_msg += "\n" + "Copyright (c) {} {}".format(core.COPYRIGHT_RANGE, core.AUTHOR)  + "\n"
    

    return help_msg

def parse_cmdline():
    parser = argparse.ArgumentParser(description=get_splash_msg(), add_help=True)

    parser.add_argument('mode', choices=['submit', 'status', 'config', 'cancel'], help="Mode in which to run sutils. Allowed values: 'submit', 'status', 'config', 'cancel'.")
    #parser.add_argument()

    args = parser.parse_args()

    return args

def parse_cmdline_submit():
    parser = argparse.ArgumentParser(description=get_splash_msg(), add_help=True)

    parser.add_argument('start', type=int)
    parser.add_argument('num', type=int)

    args = parser.parse_args()

    return args

def parse_cmdline_status():
    pass

def parse_cmdline_config():
    pass

def parse_cmdline_cancel():
    pass

#parse_cmdline()
parse_cmdline_submit()