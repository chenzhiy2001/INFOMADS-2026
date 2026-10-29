import numpy as np
from scipy.optimize import linprog

# Give all possible sequences of numbers 1..n, where no number appears twice in a row,
# the sequence has length between n and 2n-1, and al numbers appear in a sequence at least once
def sequences(n):
    maxlen = 2 * n - 1
    result = []
    layer = []
    for i in range(1, n+1):
        layer.append([i])
    for length in range(1, maxlen + 1):
        result += [s for s in layer if len(set(s)) == n]
        if length < maxlen:
            layer = append_sequences(layer, n)
    return result

# Takes a list of length x lists, and transforms it into a list of lists with length x+1, according to the rules above
def append_sequences(layer, n):
    result = []
    for s in layer:
        for k in range(n):
            if s[-1] != k+1: # make sure a number doesn't appear twice in a row
                result.append(s + [k+1])
    return result
    

def solve_sequence(seq, jobs):
    m = len(seq) # amount of slots
    n = len(jobs) # amount of jobs

    # define the cost function (3)
    last = {} # job id: last slot of that job
    for j in range(1, n+1):
        last[j] = max(l for l,x in enumerate(seq) if x == j)
    omega = [] # counts per slot how many unfinished jobs there are (omega_l)
    for l in range(m):
        omega += [sum(1 for j in range(1, n+1) if last[j] >= l)]
    c = omega + omega # omega values for g_l and d_l (so twice), give this to the solver

    A_ub = []
    b_ub = []
    # Constraint (5)
    for i in range(m):
        row = np.zeros(2*m) # Create array with zeros of length 2m
        row[0:i+1] = -1 # Change the first i elements to -1
        row[m:m+i] = -1 # Change element m to m+i to -1
        A_ub.append(row.tolist())
        b_ub.append(-jobs[seq[i]-1][0])

    A_eq = []
    b_eq = []
    # Constraint (6)
    for j in range(n):
        row = np.zeros(2*m) # Create an array with zeros of length 2m
        I_j = [i for i, v in enumerate(seq) if j+1 == v] # Get all indexes of slots where job j is being processed
        for i in I_j:
            row[m+i] = 1
        A_eq.append(row)
        big_Q = jobs[j][1] * jobs[j][2] ** (len(I_j) - 1)
        b_eq.append(big_Q)

    # pass it to LP-solver
    solution = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=(0, None), method="highs")

    return solution, seq


jobs = [(0, 2, 1.3), 
        (1, 10, 1.1),
        (5, 3, 2),
        (3.5, 0.5, 3)]

bestcost = 2147483647
bestsol = []
bestseq = []
for i in sequences(4):
    sol, seq = solve_sequence(i, jobs)
    if sol.fun < bestcost:
        bestcost = sol.fun
        bestsol = sol.x
        bestseq = seq

def calculate_starttime(l): # calculates the start time of segment l
    return str(sum([n for i,n in enumerate(bestsol) if i <= l or m <= i < m + l]))

m = len(bestseq)
for i in range(m):
    print(str(bestseq[i]) + ",\t" + calculate_starttime(i) + ",\t" + str(bestsol[m:][i]))
print(bestcost)
