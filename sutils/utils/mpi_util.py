# This file is part of the SLURM utility
# implements an MPI interface
from __future__ import print_function
import os
import sys
from mpi4py import MPI
import numpy as np


COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()
SIZE = COMM.Get_size()


# check if current job is an MPI job
try:
    os.environ['OMPI_COMM_WORLD_SIZE']
    HAS_MPI = True
except KeyError:
    # job does not run MPI
    HAS_MPI = False

    # This may happen if one uses MPICH instead of OpenMPI
    if SIZE > 0:
        HAS_MPI = True


def get_work_split(work_size):
    """Returns array with sizes of work units per core and
    array with offsets of data.
    """
    base = work_size // SIZE
    leftover = work_size % SIZE

    sizes = np.ones(SIZE, dtype=int)*base
    sizes[:leftover] += 1
    offsets = np.zeros(SIZE, dtype=int)
    offsets[1:] = np.cumsum(sizes)[:-1]

    return sizes, offsets


def print_root(arg, file=sys.stdout, end='\n', flush=False):
    """Print only in root process."""
    if RANK == 0:
        print(arg, file=file, end=end, flush=flush)

class BaseOutFileStream(object):
    def print(self, arg):
        raise NotImplementedError
    
    def flush(self):
        raise NotImplementedError


class OutFileStream(BaseOutFileStream):
    """This class implements file IO for one file per instance."""
    def __init__(self, filename, split):
        self._buffer = []
        self._file = filename
        self._split = split
        if RANK == 0:
            # create file or delete contents of file
            with open(filename, 'w'):
                pass
    
    if HAS_MPI:
        def print(self, arg):
            self._buffer.append(arg)
    else:
        # we are automatically root if there is no MPI, so we can just
        # print
        def print(self, arg):
            if self._file is not None:
                with open(self._file, 'a') as outfile:
                    print(arg, file=outfile)
            else:
                # assume stdout
                print(arg)

    if HAS_MPI:
        def flush(self):
            buffer = COMM.gather(self._buffer, root=0)
            splits = COMM.gather(self._split, root=0)

            if RANK == 0:
                assert len(buffer) == len(splits)
                sorted_buffer = []*len(buffer)
                for ind, itm in zip(splits, buffer):
                    sorted_buffer[ind] = itm
                
                # here we do the actual printing
                with open(self._file, 'a') as outfile:
                    for itm in sorted_buffer:
                        print(itm, file=outfile)

    else:
        def flush(self):
            # nothing to do, we printed directly 
            pass

class BaseOutStreamHandler(object):
    def print(self, arg, filename):
        raise NotImplementedError
    
    def flush(self, arg, filename):
        raise NotImplementedError


class OutStreamHandler(BaseOutStreamHandler):
    """This class handles all file IO and implements the interface
    class BaseOutStreamHandler.
    """
    def __init__(self, split):
        self._files = dict()
        self._split = split # list of indices corresponding to data

    def print(self, arg, filename=None):
        """Print some argument to a file."""
        if not HAS_MPI:
            print_root(arg)
        else:
            if filename not in self._files:
                self._files.update({filename: OutFileStream(filename, self._split),})
            self._files[filename].print()
    
    def flush(self):
        """Flush all filestreams."""
        for f in self._files:
            f.flush()
    
    def __del__(self):
        self.flush()
            