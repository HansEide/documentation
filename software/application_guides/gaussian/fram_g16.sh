#!/bin/bash -l
#SBATCH --account=nnXXXXk
#SBATCH --nodes=1 --ntasks-per-node=32
#SBATCH --time=0-00:05:00
#SBATCH --output=slurm.%j.log

# make the program and environment visible to this script
module load Gaussian/g16_B.01

# name of input file without extention
input=water

# set the heap-size for the job to 20GB
export GAUSS_LFLAGS2="--LindaOptions -s 20000000"

# create the temporary folder
export GAUSS_SCRDIR=/cluster/work/users/$USER/$SLURM_JOB_ID
mkdir -p $GAUSS_SCRDIR

# split large temporary files into smaller parts
lfs setstripe --stripe-count 8 $GAUSS_SCRDIR

# copy input file to temporary folder
cp $SLURM_SUBMIT_DIR/$input.com $GAUSS_SCRDIR

# run the program
cd $GAUSS_SCRDIR
time g16.ib $input.com > $input.out

# copy result files back to submit directory
cp $input.out $input.chk $SLURM_SUBMIT_DIR

exit 0
