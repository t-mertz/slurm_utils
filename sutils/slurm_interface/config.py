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

    if '-' in self._value:
        tmp = self._value.split('-')
        days = try_int(tmp[0])
        tmp = tmp[1].split(':') 
    else:
        tmp = self._value.split(':')

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
        

    def __str__(self):
        return self.to_str()


class SBATCH_Option(object):
    """A single SBATCH option, which can check validity and convert to a string."""
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
