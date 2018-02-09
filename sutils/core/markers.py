"""Markers set by jobs to communicate status of execution.

Tracking the status of a job without communicating with the job directly is done as follows:

* Before submitting, a line is added to the beginning of the bash script, which prints status "running"
* Another line is added at the end, which prints "completed"

The current status can be deduced as follows:
* Check squeue. If job is found, use that status.
* If job is not found:
    * If status in file is "running", set status to "failed"
    * If status in file is "completed", set status to "completed"
    * If status in file is "", set status to "cancelled"

In total there are five possible values for the status:
* queued
* running
* completed
* cancelled
* failed
"""
import sutils.utils.util as util
import hashlib

if util.is_python3():
    import enum


# Status classes
################################################################################################################

if util.is_python3():
    class Status(enum.Enum):
        queued      = 0
        running     = 1
        completed   = 2
        cancelled   = 3
        failed      = 4
else:
    class Status(object):
        queued      = 0
        running     = 1
        completed   = 2
        cancelled   = 3
        failed      = 4

        _strings = ['queued', 'running', 'completed', 'cancelled', 'failed']
        _hashkeys = []
        for s in _strings:
            m = hashlib.md5()
            m.update(s)
            _hashkeys.append(m.hexdigest)

        @staticmethod
        def to_str(status):
            if status < 5:
                return Status._strings[status]
            else:
                raise ValueError("Invalid input.")

        @staticmethod
        def to_crypt(status):
            m = hashlib.md5()
            m.update(status)
            return m.hexdigest()
        
        @staticmethod
        def decrypt(status):
            try:
                ind = Status._hashkeys.index(status)
            except ValueError:
                raise ValueError("Invalid status")
            return ind






# Marker classes
################################################################################################################

class AbstractMarker(object):
    """Marker contains a value attribute and methods to retrieve it."""

    def __init__(self):
        self._value = None

    def get_value(self):
        raise NotImplementedError
    
    def set_value(self):
        raise NotImplementedError

class Marker(AbstractMarker):
    """Base class for all markers."""
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value
    
    def set_value(self, value):
        # check if valid value
        self._value = value

class FileMarker(Marker):
    """Marker that writes and gets its value to and from a local file.

    This makes use of the hashed representation of the status message, since
    those are unlikely to be found in output files.
    """
    def store(self):
        pass

class DatabaseMarker(Marker):
    """Marker that stores and gets its value to and from a global database."""
    pass
