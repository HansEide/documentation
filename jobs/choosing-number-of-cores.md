(choosing-number-of-cores)=

# How to choose the number of cores

```{warning}
- Asking for too few can lead to underused nodes or longer run time
- Asking for too too many can mean wasted CPU resources
- Asking for too much can mean a lot longer queuing
```

```{contents} Table of Contents
    :depth: 3
```


## Why it matters

We request resources from the scheduler (queuing system).  But the scheduler
cannot tell how long the job will run and what resources it will really
consume.  Just the fact that I am asking the scheduler for 40 cores does not
mean that the code will actually run in parallel and use all of them.

Just because a website says that code X can run in parallel or "scales well"
does not mean that it will scale well for the particular feature/system/input
at hand.

Therefore it is important to verify and calibrate this setting for your use
case before computing very many similar jobs. Below we will show few
strategies.  Note that you don't have to go through this for every single run.
This just just to calibrate a job type. If many of your jobs have similar
resource demands, then the calibration will probably be meaningful for all of
them.


## Using the Slurm browser

This approach only works for a currently running job.

(The Slurm browser currently does not work. We will document this once the tool
is reactivated.)


## Using Arm Performance Reports

(This currently does not work because of network routing issues.  We are
working on restoring this.)


## Using top

While the job is running, find out on which node(s) it runs using `squeue -u $USER`,
then `ssh` into one of the listed compute nodes and run `top -u $USER`.


## Timing a series of runs

Here is an example C code (`example.c`) which we can compile and test a bit:
```c
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <time.h>
#include <math.h>

double compute_something(int n, int m)
{
    double s = 0.0;
    for(int i = 0; i < n; i++)
    {
        double f = rand();
        for(int j = 0; j < m; j++)
        {
            f = sqrt(f);
        }
        s += f;
    }
    return s;
}

int main(int argc, char* argv[])
{
    MPI_Init(&argc, &argv);

    int size;
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int my_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    const int k = 10000;

    double my_values[k];
    double buffer_recv[k];

    for(int j = 0; j < 100; j++)
    {
        for(int i = 0; i < k; i++)
        {
            my_values[i] = compute_something(1000/size, 10);
        }
        for(int l = 0; l < 1000; l++)
        {
            MPI_Alltoall(&my_values, 10, MPI_DOUBLE, buffer_recv, 10, MPI_DOUBLE, MPI_COMM_WORLD);
        }
    }

    MPI_Finalize();

    return EXIT_SUCCESS;
}
```

It does not matter so much what the code does. Here we wish to find out how
this code scales and what an optimum number of cores for it might be on our
system.

We can build our example binary with this script (`compile.sh`):
```
#!/bin/bash

module purge
module load foss/2020b

mpicc example.c -O3 -o mybinary -lm
```

Now take the following example script
(adapt `--account=nn____k`; this is tested on Saga):
```{code-block}
---
emphasize-lines: 9-10
---
#!/bin/bash

#SBATCH --account=nn____k
#SBATCH --qos=devel

#SBATCH --job-name='scaling'
#SBATCH --time=0-00:02:00
#SBATCH --mem-per-cpu=1GB
#SBATCH --ntasks=8
#SBATCH -o 008.out

module purge
module load foss/2020b

srun ./mybinary
```

Run a series of calculations on 1, 2, 4, 8, 16, 32, 64, and 128 cores.

You might get the following timings:

| Number of cores | Time spent in mybinary |
|-----------------|------------------------|
|   1             |       00:00:33         |
|   2             |       00:00:17         |
|   4             |       00:00:09         |
|   8             |       00:00:05         |
|  16             |       00:00:04         |
|  32             |       00:00:06         |
|  64             |       00:00:17         |
| 128             |       00:00:25         |

Please try this. What can we conclude? And how can we explain it?


## If it does not scale, what can be possible reasons?

Here are typical problems:
- At some point more time is spent communicating than computing
- Memory-bound jobs saturate the memory bandwidth
- At some point the non-parallelized code section dominates the compute time ([Amdahl's law](https://en.wikipedia.org/wiki/Amdahl%27s_law))


### Example for a memory-bound job

Here is an example Fortran code (`example.f90`) which we can compile and test a bit:
```fortran
integer function random_integer(lower_bound, upper_bound)

    implicit none

    integer, intent(in) :: lower_bound
    integer, intent(in) :: upper_bound

    real(8) :: f

    call random_number(f)

    random_integer = lower_bound + floor((upper_bound + 1 - lower_bound)*f)

end function


program example

    implicit none

    ! adjust these
    integer, parameter :: size_mb = 1900
    integer(8), parameter :: num_rounds = 500000000

    integer :: size_mw
    integer, external :: random_integer
    real(8), allocatable :: a(:)
    integer :: iround, iposition

    size_mw = int(1000000*size_mb/7.8125d0)
    allocate(a(size_mw))
    a = 0.0d0

    do iround = 1, num_rounds
        iposition = random_integer(1, size_mw)
        a(iposition) = a(iposition) + 1.0d0
    end do

    deallocate(a)
    print *, 'ok all went fine'

end program
```

We can build our example binary with this script (`compile.sh`):
```
#!/bin/bash

module load foss/2020b

gfortran example.f90 -o mybinary
```

Now take the following example script
(adapt `--account=nn____k`; this is tested on Saga):
```
#!/bin/bash

#SBATCH --account=nn____k
#SBATCH --qos=devel

#SBATCH --job-name='mem-bandwidth'
#SBATCH --time=0-00:02:00
#SBATCH --mem-per-cpu=2000M
#SBATCH --ntasks=1

module load foss/2020b

module load Arm-PerfReports/20.0.3
echo "set sysroot /" > gdbfile
export ALLINEA_DEBUGGER_USER_FILE=gdbfile

perf-report ./mybinary
```

This will generate the following performance report:
```{code-block} txt
---
emphasize-lines: 4, 15
---
...

Summary: mybinary is Compute-bound in this configuration
Compute:                                    100.0% |=========|
MPI:                                          0.0% |
I/O:                                          0.0% |
This application run was Compute-bound. A breakdown of this time and advice for
investigating further is in the CPU section below.  As very little time is
spent in MPI calls, this code may also benefit from running at larger scales.

CPU:
A breakdown of the 100.0% CPU time:
Scalar numeric ops:                           4.6% ||
Vector numeric ops:                           0.0% |
Memory accesses:                             88.1% |========|
The per-core performance is memory-bound. Use a profiler to identify
time-consuming loops and check their cache performance.  No time is spent in
vectorized instructions. Check the compiler's vectorization advice to see why
key loops could not be vectorized.

...
```

How do you interpret this result? Will it help to buy faster processors? What
limitations can you imagine when running this on many cores on the same node?


## What is MPI and OpenMP and how can I tell?

These two parallelization schemes are very common( but there are other schemes):
- [Message passing interface](https://en.wikipedia.org/wiki/Message_Passing_Interface):
  typically each task allocates its own memory, tasks communicate via messages,
  and it is no problem to go beyond one node.
- [OpenMP](https://www.openmp.org/):
  threads share memory and communicate through memory, and we cannot go beyond one node.


### How to tell if the code is using one of the two?

- If you wrote the software: then you probably know
- If it is written by somebody else:
  - It can be difficult to tell
  - Consult manual for the software or contact support (theirs or ours)
  - `grep -i mpi` and `grep -i "omp "` the source code
  - Example: <https://github.com/MRChemSoft/mrchem> (uses both MPI and OpenMP)


### Python/R/Matlab

- Often not parallelized
- But can use parallelization (e.g. `mpi4py` or `multiprocessing`)


### Code may call a library which is shared-memory parallelized

- Examples: BLAS libraries, NumPy, SciPy

Here is an example which you can try (`example.py`) where we compute a couple
of matrix-matrix multiplications using Numpy:
```python
import numpy as np

n = 5000

# run it multiple times, just so that it runs longer and we have enough time to
# inspect it while it's running
for _ in range(10):
    matrix_a = np.random.rand(n, n)
    matrix_b = np.random.rand(n, n)

    matrix_c = np.matmul(matrix_a, matrix_b)

print("calculation completed")
```

It can be interesting to try this example with the following run script (adapt `--account=nn____k`; this is tested on Saga):
```{code-block}
---
emphasize-lines: 14-16
---
#!/bin/bash

#SBATCH --account=nn____k
#SBATCH --qos=devel

#SBATCH --job-name='example'
#SBATCH --time=0-00:02:00
#SBATCH --mem-per-cpu=1500M
#SBATCH --nodes=1
#SBATCH --tasks-per-node=4

module load Python/3.6.6-foss-2018b

# export MKL_NUM_THREADS=4
# export NUMEXPR_NUM_THREADS=4
# export OMP_NUM_THREADS=4

python example.py
```

Run this example and check the timing. Then uncomment the highlighted lines and
run it again and compare timings.  It can also be interesting to log into the
compute node while the job is running and using `top -u $USER`. Can you explain
what is happening here?