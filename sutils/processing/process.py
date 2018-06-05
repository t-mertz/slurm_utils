# This file is part of the SLURM utility
# Implements a user interface for the data processor
import subprocess

from ..core import core
import fargs

def process(func):
    try:
        proc = get_processor(func)
    except ValueError as e:
        sys.stdout.write("An error occurred: " + str(e))
        sys.exit(1)

    proc.run()


class DataProcessor(core.ParameterIterator):
    """Run specified Python function on data."""
    def __init__(self, func):
        super().__init__(self)
        #check if func takes three arguments!
        if fargs.get_number_fargs(func) == 3:
            self.process = func
        else:
            raise ValueError("Function must take exactly three arguments (dirname, job_idx, plist).")
        
    def run(self):
        self.iterate()

def get_processor(func):
    return DataProcessor(func)

class ShellProcessor(core.ParameterIterator):
    """Run shell script on data."""
    def __init__(self, script_name):
        super().__init__(self)
        self._script_name = script_name

    def process(self, dirname, job_idx, plist):
        # maybe copy the script file to a temporary file in the job_directory
        subprocess.Popen(['bash', self._script_name]) 

class ExternalProcessor(core.ParameterIterator):
    """Run external program on data."""
    pass
