#!/bin/bash -l
################### Gaussian Job Batch Script Example ###################
# Section for defining queue-system variables:
#-------------------------------------
# Slurm-section
#SBATCH --account=nnXXXXk
#SBATCH --nodes=1 --ntasks-per-node=32
#SBATCH --time=1-20:30:00
#SBATCH --output=slurm.%j.log
######################################
# Section for defining job variables and settings:
#-------------------------------------

input=water # Name of input without extention
extention=com # We use the same naming scheme as the software default

module load Gaussian/g16_B.01

# This one is important; setting the heap-size for the job to 20GB:
export GAUSS_LFLAGS2="--LindaOptions -s 20000000"
#Creating the gaussian temp dir:
export GAUSS_SCRDIR=/cluster/work/users/$USER/$SLURM_JOB_ID
mkdir -p $GAUSS_SCRDIR

# Creating aliases:
submitdir=$SLURM_SUBMIT_DIR
tempdir=$GAUSS_SCRDIR

# split large temporary files into smaller parts:
lfs setstripe --stripe-count 8 $tempdir

# Moving files to scratch:
cd $submitdir
cp $input.com $tempdir
cd $tempdir

# Running program, pay attention to command name:

time g16.ib $input.com > g16_$input.out

# Cleaning up and moving files back to home/submitdir:

cp g16_$input.out $submitdir
cp $input.chk $submitdir

exit 0
