# This file is part of the SLURM utility
# Implements a user interface for the data processor
import subprocess
import sys
import os

from ..core import core
from . import fargs

def process_py(func, root_path=".", config_file="config.ini"):
    try:
        proc = get_processor("python", func, root_path=root_path, config_file=config_file)
    except ValueError as e:
        sys.stdout.write("An error occurred: " + str(e) + "\n")
        sys.exit(1)

    proc.run()

def process_exec(filename):
    try:
        proc = get_processor("external", filename)
    except ValueError as e:
        sys.stdout.write("An error occurred: " + str(e) + "\n")
        sys.exit(1)

    proc.run()

class DataProcessor(core.DataProcessor):
    """Run specified Python function on data."""
    def __init__(self, func, root_path=None, config_file=None):
        super(DataProcessor, self).__init__(root_path=root_path, config_file=config_file)
        #check if func takes three arguments!
        if fargs.get_number_fargs(func) == 3:
            self.process = func
        else:
            raise ValueError("Function must take exactly three arguments (dirname, job_idx, plist).")
        
    def run(self):
        self.iterate()

def get_processor(script_type, func, root_path=".", config_file="config.ini"):
    """Factory function for processors"""
    if script_type.lower() == 'python':
        # this can raise an exception.
        # ok, since we expect this to be run from within an external Python script anyhow
        return DataProcessor(func, root_path, config_file)
    elif script_type.lower() == 'external':
        try:
            return ExternalProcessor(func)
        except OSError as e:
            sys.stderr.write(str(e))
            sys.exit(1)
        except Exception as e:
            # can only happen if Popen raises some exception. Timeout?
            sys.stderr.write("There has been an error:\n" + str(e))
            sys.exit(1)

    elif script_type.lower() == 'bash':
        try:
            return ShellProcessor(func)
        except Exception as e:
            sys.stderr.write(str(e))
            sys.exit(1)

    else:
        raise NotImplementedError(script_type)

class ShellProcessor(core.ParameterIterator):
    """Run shell script on data."""
    def __init__(self, script_name):
        super(ShellProcessor, self).__init__()
        self._script_name = script_name

    def process(self, dirname, job_idx, plist):
        # maybe copy the script file to a temporary file in the job_directory
        p = subprocess.Popen(['bash', self._script_name], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.wait()
        sys.stdout.write(p.stdout)
        sys.stderr.write(p.stderr)

class ExternalProcessor(core.ParameterIterator):
    """Run external program on data."""
    def __init__(self, filename):
        super(ExternalProcessor, self).__init__()
        filename = os.path.join("..", filename) # ParameterIterator cd's into job-dirs
        if not os.access(filename, os.F_OK):
            raise OSError("File {} does not exist.".format(filename))
        if not os.access(filename, os.X_OK):
            raise OSError("File {} is not an executable.".format(filename))
        self._executable = filename

    def process(self, firname, job_idx, plist):
        p = subprocess.Popen([], executable=self._executable, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.wait()
        sys.stdout.write(p.stdout)
        sys.stderr.write(p.stderr)
