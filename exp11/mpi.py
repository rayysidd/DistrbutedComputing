from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 1000  # size of NxN matrices (use larger N for visible speedup)

# Root initializes matrices
if rank == 0:
    A = np.random.randint(0, 10, (N, N))
    B = np.random.randint(0, 10, (N, N))
else:
    A = None
    B = np.empty((N, N), dtype=int)

# Broadcast matrix B
comm.Bcast(B, root=0)

# Determine number of rows per process
rows_per_proc = N // size
local_A = np.empty((rows_per_proc, N), dtype=int)

# Scatter rows of A
comm.Scatter(A, local_A, root=0)

# Start timer (each process)
comm.Barrier()  # synchronize before timing
start = MPI.Wtime()

# Local computation
local_C = np.dot(local_A, B)

# Gather results
if rank == 0:
    C = np.empty((N, N), dtype=int)
else:
    C = None

comm.Gather(local_C, C, root=0)

comm.Barrier()
end = MPI.Wtime()

# Print results and timing
if rank == 0:
    print(f"\nParallel matrix multiplication using {size} processes completed.")
    print(f"Execution time: {end - start:.4f} seconds")

# mpiexec -n 4 python mpi.py
