import os

def get_file_extension(filename):
    name = os.path.basename(filename)
    tmp = name.split('.')
    if len(tmp) > 1:
        return tmp[-1]
    else:
        return ''

def is_executable(filename):
    return os.access(filename, os.X_OK)
