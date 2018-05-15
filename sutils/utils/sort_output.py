# This file is part of the SLURM utility
# implements a file sorting routine

from __future__ import print_function
import numpy as np


def sort(infilename, outfilename):
    """Sort a file with lines 'index val1 val2 val3 val4 ...'
    along ascending index.

    This can be necessary for example when MPI is handling file IO.
    """
    unsorted_list = []
    with open(infilename, 'r') as infile:
        for line in infile:
            unsorted_list.append([int(line.split()[0]), line])
    
    sorted_array = np.sort(np.array(unsorted_list)[:, 0])

    with open(outfilename, "w") as outfile:
        for i, sorted_ind in enumerate(sorted_array):
            print(sorted_array[sorted_ind], file=outfile)
