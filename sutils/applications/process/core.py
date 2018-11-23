import os

from ...processing import process as proc_impl

def get_file_extension(filename):
    name = os.path.basename(filename)
    tmp = name.split('.')
    if len(tmp) > 1:
        return tmp[-1]
    else:
        return ''

def is_executable(filename):
    return os.access(filename, os.X_OK)

def run_process(filename):
    fext = get_file_extension(filename)
    isx = is_executable(filename)

    if isx:
        p = proc_impl.get_processor('external', filename)
    elif fext == 'sh':
        p = proc_impl.get_processor('bash', filename)
    elif fext == 'py':
        p = proc_impl.get_processor('python.script', filename)

    p.run()
