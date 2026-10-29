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

    # define the cost function
    last = {} # job id: last slot of that job
    for j in range(1, n+1):
        last[j] = max(l for l,x in enumerate(seq) if x == j)
    omega = [] # counts per slot how many unfinished jobs there are (omega_l)
    for l in range(m):
        omega += [sum(1 for j in range(1, n+1) if last[j] >= l)]
    c = omega + omega # omega values for g_l and d_l (so twice), give this to the solver

    A_ub = []
    b_ub = []
    


    # pass it to LP-solver
    return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=(0, None), method="highs")

jobs = [(0, 10, 1.1), 
        (5, 0.1, 2),
        (6, 3, 1),
        (0.1, 0.4, 2)]

best = 2147483647
for i in sequences(4):
    sol = solve_sequence(i, jobs)
    if sol.fun < best:
        best = sol.fun
print(best)
