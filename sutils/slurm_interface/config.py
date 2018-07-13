from ..utils import ini
import re as regexpr
from ..configparse import cfgtypes

PREFIX = "#SBATCH --" # this prefix marks SBATCH settings


# time type
class TimeType(cfgtypes.Type):
    def __init__(self, string):
        super(TimeType, self).__init__(string)
        self._value = check_time(string)


def try_int(val):
    """Tries to convert val to int.

    Raises ValueError upon failure.
    In contrast to builtin.int this function returns 0 for an empty string.
    """
    try:
        return int(val)
    except ValueError:
        if len(val) == 0:
            return 0
        else:
            raise ValueError("Cannot convert to integer: {}".format(val))


def check_time(string):
    """Valid entries are 'minutes', 'minutes:seconds', 'hours:minutes:seconds",
    "days-hours:minutes:seconds".
    """
    days, hours, minutes, seconds = 0, 0, 0, 0

    if '-' in string:
        tmp = string.split('-')
        days = try_int(tmp[0])
        tmp = tmp[1].split(':') 
    else:
        tmp = string.split(':')

    if len(tmp) == 1:
        hours = try_int(tmp[0])
    elif len(tmp) == 2:
        hours, minutes = try_int(tmp[0]), try_int(tmp[1])
    elif len(tmp) == 3:
        hours, minutes, seconds = try_int(tmp[0]), try_int(tmp[1]), try_int(tmp[2])


    value = "{days:d}-:{hours:02d}:{minutes:02d}:{seconds:02d}".format(days=days,
                                                                    hours=hours,
                                                                    minutes=minutes,
                                                                    seconds=seconds)
    return value

def settings2str(settings):
    """Create a string out of settings, which can be inserted in the beginning of a bash script."""
    raise NotImplementedError

def SBATCH_Config(object):
    """Simple data type that holds a dict data member and has a to_str() method."""
    settings = ["begin",
                "constraint",
                "cpus-per-task",                        # min. CPUs per task on one node
                "error",                                # stderr filename
                "job-name",
                "mail-type",
                "mem",                                  # memory per node (MB)
                "mem-per-cpu",
                "mincpus",                              # min. CPUs per node
                "nodes",                                # min. nodes
                "ntasks",                               # number of tasks that will be launched
                "output",                               # stdout filename
                "partition",                            # partition(s) to submit to
                "time",                                 # time limit

               ]
    forbidden_settings = ["chdir",
                         ]
    def __init__(self, config_dict):
        self._cgf = config_dict

    def to_str(self):
        """Convert configuration to string, which can be written in bash scripts."""
        pass
        

    def __str__(self):
        return self.to_str()


class SLURM_Option(object):
    pass

class SBATCH_Option(SLURM_Option):
    """A single SBATCH option, which can check validity and convert to a string."""
    name = ""
    _valid = False
    def __init__(self, value_str):
        self._value = value_str.strip()
        if self._value == "":
            raise RuntimeError("Invalid Parameter for " + str(self.name))
        self.parse()

    def parse(self):
        raise NotImplementedError

    def is_valid(self):
        return self._valid

    def to_str(self):
        raise NotImplementedError

class SBATCH_begin(SBATCH_Option):
    """Specifies when to begin the job."""
    def parse(self):
        """Valid entries are very complex. We just forward this to SLURM."""
        self._valid = True

class SBATCH_time(SBATCH_Option):
    """Specifies the time limit for the job."""
    name = "time"
    def parse(self):
        """Valid entries are 'minutes', 'minutes:seconds', 'hours:minutes:seconds",
        "days-hours:minutes:seconds".
        """
        days, hours, minutes, seconds = 0, 0, 0, 0

        if '-' in self._value:
            tmp = self._value.split('-')
            days = int(tmp[0])
            tmp = tmp[1].split(':') 
        else:
            tmp = self._value.split(':')

        if len(tmp) == 1:
            hours = int(tmp[0])
        elif len(tmp) == 2:
            hours, minutes = int(tmp[0]), int(tmp[1])
        elif len(tmp) == 3:
            hours, minutes, seconds = int(tmp[0]), int(tmp[1]), int(tmp[2])


        self._value = "{days:d}-:{hours:02d}:{minutes:02d}:{seconds:02d}".format(days=days,
                                                                           hours=hours,
                                                                           minutes=minutes,
                                                                           seconds=seconds)
        self._valid = True

    def to_str(self):
        return PREFIX + self.name + "=" + self._value


class SBATCH_partition(SBATCH_Option):
    """Name of the partition."""
    name = "partition"
    def parse(self):
        self._valid = True


class ToggleOption(SLURM_Option):
    _value = False
    _option = ""
    def __init__(self, value):
        self._value = bool(value)
    
    def parse(self):
        if self._value:
            return [self._option]
        return []

class ArgOption(SLURM_Option):
    _value = None
    _option = ""
    def __init__(self, value=None):
        self._value = value

    def _convert(self):
        """Can be overridden to perform conversion to str."""
        pass
    
    def parse(self):
        if self._value is not None:
            self._convert()
            return [self._option, self._value]
        else:
            return []

class Scancel_job_id(ArgOption):
    pass

class ArgumentList(object):
    _args = []
#    _arg_info = {}
#    def add_argument(self, name, cmd_arg, type):
#        """Add an argument to the known arguments."""
#        self._arg_info[name] = [cmd_arg, type]
#        return self

    def to_list(self):
        return self._args

class Scancel_Options(ArgumentList):
    settings = {
        'job_id' : '',
    }

    def __init__(self, job_id):
        self._args = []
        self._args += Scancel_job_id(job_id).parse()


class Squeue_user(ArgOption):
    _option = "--user"

class Squeue_noheader(ToggleOption):
    _option = "--noheader"

class Squeue_Options(ArgumentList):
    settings = {
        'username'  : '--user',
        'noheader'  : '--noheader',
    }

    def __init__(self, userid=None, noheader=False):
        self._args = []
        self._args += Squeue_user(userid).parse()
        self._args += Squeue_noheader(noheader).parse()

#squeue_options = ArgumentList().add_argument('username', '--user', str) \
#                               .add_argument('noheader', '--noheader', bool)

class Sbatch_Options(ArgumentList):
    settings = {
        'work_dir'   : '--workdir',
    }

    def __init__(self, work_dir):
        self._args = []
        self._args += "{} {}".format(self.settings['work_dir'], work_dir)


# this is the most recent interface

class SbatchConfig(ArgumentList):
    """Container for sbatch configuration."""
    class Workdir(ArgOption):
        _option = "--workdir"
    
    def __init__(self, work_dir):
        cls = self.__class__
        self._args = []
        self._args += cls.Workdir(work_dir).parse()

class ScancelConfig(ArgumentList):
    """Container for scancel configuration."""
    pass

class SqueueConfig(ArgumentList):
    """Container for squeue configuration."""

    class Noheader(ToggleOption):
        _option = "--noheader"
    
    class User(ArgOption):
        _option = "--user"

    class Jobs(ArgOption):
        _option = "--jobs"
        def convert(self):
            """Make sure that _value is a string of comma separated IDs."""
            tmp = [str(i) for i in list(self._value)]
            self._value = ",".join(tmp)
    
    class Format(ArgOption):
        _option = "--Format"

    class Sort(ArgOption):
        _option = "--sort"
    
    class States(ArgOption):
        _option = "--states"

    def __init__(self, jobs=None, userid=None, noheader=False, format=None, sort=None, states=None):
        cls = self.__class__
        self._args = []
        self._args += cls.User(userid).parse()
        self._args += cls.Noheader(noheader).parse()
        self._args += cls.Jobs(jobs).parse()
        self._args += cls.Format(format).parse()
        self._args += cls.Sort(sort).parse()
        self._args += cls.States(states).parse()

