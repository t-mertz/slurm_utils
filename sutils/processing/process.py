# This file is part of the SLURM utility
# Implements a user interface for the data processor
import subprocess
import sys

from ..core import core
import fargs

def process_py(func):
    try:
        proc = get_processor("python", func)
    except ValueError as e:
        sys.stdout.write("An error occurred: " + str(e) + "\n")
        sys.exit(1)

    proc.run()


class DataProcessor(core.DataProcessor):
    """Run specified Python function on data."""
    def __init__(self, func):
        super(DataProcessor, self).__init__()
        #check if func takes three arguments!
        if fargs.get_number_fargs(func) == 3:
            self.process = func
        else:
            raise ValueError("Function must take exactly three arguments (dirname, job_idx, plist).")
        
    def run(self):
        self.iterate()

def get_processor(script_type, func):
    """Factory function for processors"""
    if script_type.lower() == 'python':
        return DataProcessor(func)
    else:
        raise NotImplementedError(script_type)

class ShellProcessor(core.ParameterIterator):
    """Run shell script on data."""
    def __init__(self, script_name):
        super(ShellProcessor, self).__init__()
        self._script_name = script_name

    def process(self, dirname, job_idx, plist):
        # maybe copy the script file to a temporary file in the job_directory
        subprocess.Popen(['bash', self._script_name]) 

class ExternalProcessor(core.ParameterIterator):
    """Run external program on data."""
    pass
