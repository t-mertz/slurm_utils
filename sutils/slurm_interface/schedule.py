import copy
from datetime import datetime

from . import api

def get_datetime_now():
    return datetime.now()

def get_scheduled_start(script, kwargs):
    kwargs_copy = copy.copy(kwargs)
    kwargs_copy['test_only'] = True
    res = api.sbatch(script, ignore_error=True, **kwargs_copy)
    datetime_string = res.stdout().split()[6]
    start = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
    #now = get_datetime_now()
    return start

def get_scheduled_waiting_time(script, kwargs):
    start = get_scheduled_start(script, kwargs)
    return start - get_datetime_now()
