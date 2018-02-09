# slurm_utils
Python submission manager for SLURM

This package implements fast large-scale batch job submission via SLURM. Parameters are configured in standard .ini file syntax,
iteration through all possible parameter combinations, directory creation and job submission is done automatically.

Additional functionality includes:
- status monitoring of jobs submitted in current directory
- cancelling of first and last N jobs currently in queue or running
- fast and simple data processing for all parameters
