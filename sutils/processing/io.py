from __future__ import print_function
import sys

err = sys.stderr
out = sys.stdout

def print_formatted(*args, **kwargs):
    if "dest" in kwargs:
        if kwargs['dest'] in [err, "err", "error", "stderr"]:
            dest = err
        elif kwargs['dest'] in [out, "out", "stdout"]:
            dest = out
        else:
            raise ValueError("Invalid destination: %" % dest)
    else:
        dest = out # default is stdout
    num = len(args)
    print(("    ".join(["{}"]*num)).format(*args), file=dest)

def print_error(string):
    print(string, file=sys.stderr)


def run_protect(func):
    def tmp(*args):
        try:
            func(*args, **kwargs)
        except IOError as e:
            print(e)

    return tmp

def save_array(index, **kwargs):
    """Save data as array in numpy syntax.

    This works the same way as the numpy.savez function.
    """
    pass
    # first caller needs to create array

    # load array and store data into it

    # save array