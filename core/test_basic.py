from task import Task
from schedulers import simulate, metrics

tasks = [Task("T1", period=5, wcet=2), Task("T2", period=7, wcet=4)]  # U = 0.971

for policy in ["RMS", "EDF"]:
    print(policy, metrics(simulate(tasks, policy, horizon=35)))
    