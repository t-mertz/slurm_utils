import pkg_resources  # part of setuptools
VERSION = pkg_resources.require("sutils")[0].version

#VERSION_MAJOR = 0
#VERSION_MINOR = 2
#VERSION_PATCH = 0
#VERSION = "{}.{}.{}".format(VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

def version():
    return VERSION
