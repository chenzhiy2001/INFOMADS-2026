# a visualizer and verifier (that only verifies correctness not optimality)) 
# example input (that we don't deal with in this file)
# 4     <- number of jobs
# 0, 	10,	 1.1
# 5,	0.1,	 2
# 6,	3,	 1
# 0.1,	0.4,	 2

# r_j,	p_j,	a_j	

# output: (that we are gonna visualize and verify)
# job id (starts with 1), start processing time, execution time
# 4, 	0.1, 	0.4
# 1, 	0.5, 	5.4
# 2, 	5.9, 	0.1
# 3, 	6, 	3
# 1, 	9, 	5.6
# 30.1   <- total execution time, which is the sum of all the end TIMESTAMPs of all jobs, not the sum of all the execution times (which is 15.5 in this case)

# the results being matplotlib
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# if example_input.txt exist then load it as input, otherwise use the default input
# load file
file = "example_input.txt"
text = os.path.exists(file) and open(file).read() or """
4
0, 10, 1.1
5, 0.1, 2
6, 3, 1
0.1, 0.4, 2

4, 0.1, 0.4
1, 0.5, 5.4
2, 5.9, 0.1
3, 6, 3
1, 9, 5.6
30.1
"""

# split text into jobcount, joblist, output and execution time
lines = text.strip().splitlines()
jobcount = int(lines[0])
joblist = [tuple(map(float, line.split(','))) for line in lines[1:jobcount+1]] # (r_j, p_j, a_j)
# there is an empty line between joblist and output
output = [tuple(map(float, line.split(','))) for line in lines[jobcount+2:-1]] # (job id, start processing time, execution time)
execution_time = float(lines[-1]) # extract execution time

# define the "executor" (the single machine or person that does one job at a time)
# we generate the executor data structure by simulating the machine processing the jobs in the order given by the output
# in this way we can do the drawings and verifications of correctness along the way

executor_state = {"current_time": 0, "current_job": None, "job_states": {i+1: [{"start_time": None, "end_time": None}] for i in range(jobcount)}}

# drawing data is a list of (start_time, end_time, job_id) for each execution
drawing_data = []

for job_id, start_time, exec_time in output:
    job_id = int(job_id)
    # check if the job is ready to be processed (i.e., its release time has passed)
    r_j, p_j, a_j = joblist[job_id-1]
    if start_time < r_j:
        raise ValueError(f"Job {job_id} cannot start at {start_time} before its release time {r_j}.")
    
    # check if the job is being processed in the correct order (i.e., no overlap with previous jobs)
    if executor_state["current_time"] > start_time:
        raise ValueError(f"Job {job_id} cannot start at {start_time} while another job is still running.")
    
    # update the executor state and drawing data
    drawing_data.append((start_time, start_time + exec_time, job_id))
    executor_state["current_time"] = start_time + exec_time
    executor_state["current_job"] = job_id
    executor_state["job_states"][job_id].append({"start_time": start_time, "end_time": start_time + exec_time})


# The chart uses real timestamps, while the reported execution time is the sum
# of the final end timestamp for each job.
actual_completion_time = max(end_time for _, end_time, _ in drawing_data)
final_end_times = {
    job_id: max(end_time for _, end_time, current_job_id in drawing_data if current_job_id == job_id)
    for job_id in range(1, jobcount + 1)
}
total_execution_time = sum(final_end_times.values())

# draw using matplotlib
fig, ax = plt.subplots(figsize=(10, max(4, jobcount * 0.8)))

colors = plt.cm.tab20.colors
for start_time, end_time, job_id in drawing_data:
    ax.barh(
        job_id,
        end_time - start_time,
        left=start_time,
        height=0.5,
        color=colors[(job_id - 1) % len(colors)],
        edgecolor="black",
    )
    if end_time - start_time >= 0.75:
        ax.text(
            (start_time + end_time) / 2,
            job_id,
            f"Job {job_id}",
            ha="center",
            va="center",
            fontsize=9,
        )

ax.set_yticks(range(1, jobcount + 1))
ax.set_yticklabels([f"Job {job_id}" for job_id in range(1, jobcount + 1)])
ax.set_xlabel("Time")
ax.set_title(
    f"Schedule (total execution time: {total_execution_time:g}, "
    f"final timestamp: {actual_completion_time:g})"
)
ax.grid(axis="x", linestyle="--", alpha=0.5)
ax.axvline(
    actual_completion_time,
    color="black",
    linestyle=":",
    linewidth=1.5,
    label="Output completion",
)
ax.set_xlim(0, actual_completion_time)
ax.set_ylim(0.5, jobcount + 0.5)
ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig("schedule.png", dpi=150)
plt.close(fig)
print("Saved schedule visualization to schedule.png")

if not math.isclose(execution_time, total_execution_time, rel_tol=1e-9, abs_tol=1e-9):
    raise ValueError(
        f"Execution time mismatch: declared {execution_time:g}, "
        f"but the output schedule totals {total_execution_time:g}."
    )

print(f"Execution time verified: {total_execution_time:g}")




