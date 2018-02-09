# slurm_utils
## Python submission manager for SLURM

This package implements fast large-scale batch job submission via [SLURM](https://slurm.schedmd.com/). Parameters are configured in standard .ini file syntax,
iteration through all possible parameter combinations, directory creation and job submission is done automatically.

## Additional functionality includes:
- status monitoring of jobs submitted in current directory
- cancelling of first and last N jobs currently in queue or running
- fast and simple data processing for all parameters


## Installation:

> python setup.py install

If you don't have write privileges in your site-packages directory, use the option --user to install in your user's site-packages.

> python setup.py install --user


## Run:

Commands are: scancel, ssubmit, sstatus
