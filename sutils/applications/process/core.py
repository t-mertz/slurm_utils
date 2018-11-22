import os

def get_file_extension(filename):
    name = os.path.basename(filename)
    tmp = name.split('.')
    if len(tmp) > 1:
        return tmp[-1]
    else:
        return ''
