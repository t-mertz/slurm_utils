#! /bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --job-name=JOBNAME
#SBATCH --mem-per-cpu=2000
#SBATCH --time=1-23:05:00
#SBATCH --partition=parallel
#SBATCH --mail-type=FAIL
#SBATCH --tmp=2000

. ~/.bashrc

#export PYTHONPATH="$PYTHONPATH:$HOME/TISM_Michael/python/"
export CTAUX_CODE_PATH="$HOME/CODES/RDMFT_TISM/CTAUXSM/danny_interface"

#echo $CTAUX_CODE_PATH
#module list

if [ -n "$SLURM_JOB_ID" ] ; then
    TMPDIR="/local/$SLURM_JOB_ID"
fi

if [ -z "$NSLOTS" ] ; then
export NSLOTS=24
fi
echo $NSLOTS

python - <<EOF
from __future__ import print_function
import sys,os
from std_imports import *
import matplotlib
matplotlib.use('Agg')
import get_dmft_results as gdr


max_iters = 30
cont = False
U = U_VAL
mu = U/2.
beta = 20.
N = 24
M = 60
boundaries = "PP"
p = 1
q = 6
lambda_x = LAMBDA_VAL
gamma = GAMMA_VAL
t = 1.
num_sweeps = 10**7
row_sym = 'rect6x1'
force_filling = FILLING_VAL #4.0 / 3.0
solver = "CT-AUX"
covar_factor = 0.01

import os
cwd = os.getcwd()

import time
start = time.time()

import RDMFT_TISM

import glob
filelist = glob.glob('SE_iter*.npy')
last_iter = -1
for filename in filelist:
	num = int(filename.split('_iter')[1].split('.')[0])
	if num > last_iter:
		last_iter = num

if last_iter >= max_iters-1:
	pass
else:
	if last_iter == -1:
		last_iter = False
		valid = False

	RDMFT_TISM.TI_CTAUX(U,mu,beta,(N,M),boundaries,(p,q),max_iters,num_sweeps,row_sym,lambda_x=lambda_x,gamma=gamma,force_filling=force_filling,solver=solver,continue_from_iter=cont)

RDMFT_TISM.TI_ContinueCTAUX_SE(covar_factor=covar_factor,model=4)
RDMFT_TISM.GenerateAllDataCTAUX()
RDMFT_TISM.JudgeValidity()

# Cache processed data for later use
# creates a file dmft_data.npz with zero-frequency self-energy, Fermi gap, magnetization
gdr.cache_data(".")

if True:
    # Clean up files we don't want to keep for space saving reasons.

    def unlinkdan(x):
        try:
            os.unlink(x)
        except:
            pass

    for i in range(max_iters-6):
        if i % 30 != 0:
            unlinkdan('SE_iter{0}.npy'.format(i))
            unlinkdan('everything_iter{0}.npz'.format(i))
    unlinkdan('data.pickle.gz')
    unlinkdan('SE.pickle.gz')

    # Also remove the huge *.npz files
    if True:
        import glob
        filelist = glob.glob('G[kx]*.npz')
        for filename in filelist:
            unlinkdan(filename)

os.chdir(cwd)
with open('runtime.txt','wb') as file:
    file.write(str(time.time() - start))

EOF

exit 0
