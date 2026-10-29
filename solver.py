import numpy as np
from scipy.optimize import linprog
import time

# This program is entirely conform to paragraph 3 in the scientific paper.
# Here we generate all the possible job sequences, and for each sequence we
# solve the LP formulated in paragraph 3.2

# Give all possible sequences of numbers 1..n, where no number appears twice in a row,
# the sequence has length between n and 2n-1, and al numbers appear in a sequence at least once
def sequences(n):
    maxlen = 2 * n - 1
    result = []
    layer = [] # Layer contains feasible sequences, apart from that it might not contain all numbers 1..n
    for i in range(1, n+1): # First, fill layer with initial values (For n = 3, layer = [[1], [2], [3]] )
        layer.append([i]) 
    for length in range(1, maxlen + 1):
        result += [s for s in layer if len(set(s)) == n] # Add all the sets in layer which contain all the numbers 1..n to the result. (For the first few iterations there won't be anything added to result)
        if length < maxlen:
            layer = append_sequences(layer, n) # If layer contains sequences of length x, extend them to sequences with length x+1
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
        row[0:i+1] = -1 # Change the first i+1 elements to -1
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
        big_Q = jobs[j][1] * jobs[j][2] ** (len(I_j) - 1) # the right hand side Q
        b_eq.append(big_Q)

    # pass it to LP-solver
    solution = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=(0, None), method="highs")

    return solution, seq

def calculate_starttime(l, bestsol): # calculates the start time of segment l, to be showed in the output
    return f"{sum([n for i,n in enumerate(bestsol) if i <= l or m <= i < m + l]):.1f}"


# read instances from file
with open("offline test instances.txt") as file:
    inputblocks = file.read().strip().split("\n\n")
instances = []
for i in inputblocks:
    rows = i.split("\n")[1:]  # skip the count line
    instances.append([tuple(map(float, row.split(", "))) for row in rows])

# run all instances and put the results in a file
with open("offline test results.txt", "w") as out:
    for inst in instances:
        bestcost = 2147483647 # cost of current best solution
        bestsol = [] # decision variables of current best solution
        bestseq = [] # sequence corresponding to the current best solution
        start_time = time.time()
        for i in sequences(len(inst)):
            sol, seq = solve_sequence(i, inst)
            if sol.fun < bestcost: # When a better solution is found, update the "best" values
                bestcost = sol.fun
                bestsol = sol.x
                bestseq = seq
        end_time = time.time()
        # prints the output
        m = len(bestseq)
        for i in range(m):
            print(f"{bestseq[i]},\t {calculate_starttime(i, bestsol)},\t {bestsol[m:][i]:.1f}", file=out)
        print(f"{bestcost:.1f}", file=out)
        print(f"Runtime is {(end_time - start_time) * 1000} milliseconds", file=out)
        print(file=out)