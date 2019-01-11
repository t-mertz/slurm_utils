from .test.test import testmode

if testmode():
    VERSION = "0.0.0"
else:
    import pkg_resources  # part of setuptools
    VERSION = pkg_resources.require("sutils")[0].version

VERSION_MAJOR = 0
VERSION_MINOR = 3
VERSION_PATCH = 1
#VERSION = "{}.{}.{}".format(VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

def version():
    return VERSION
