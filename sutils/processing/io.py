def print_formatted(*args):
    num = len(args)
    print(("    ".join(["{}"]*num)).format(*args))


def run_protect(func):
    def tmp(*args):
        try:
            func(*args, **kwargs)
        except IOError as e:
            print(e)

    return tmp
