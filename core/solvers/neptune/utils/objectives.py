import numpy as np

def minimize_network_delay(data, objective, x):
    for f in range(len(data.functions)):
        for i in range(len(data.sources)):
            for j in range(len(data.nodes)):
                objective.SetCoefficient(
                    x[i, f, j], float(data.node_delay_matrix[i, j] * data.workload_matrix[f, i])
                )
    objective.SetMinimization()


def maximize_handled_requests(data, objective, x):
    for f in range(len(data.functions)):
        for i in range(len(data.sources)):
            for j in range(len(data.nodes)):
                objective.SetCoefficient(
                    x[i, f, j], float(data.workload_matrix[f, i])
                )
    objective.SetMaximization()

def minimize_node_utilization(data, objective, n):
    for i in range(len(data.nodes)):
        objective.SetCoefficient(n[i], 1)
    objective.SetMinimization()

def minimize_node_delay_and_utilization(data, objective, n, x, alpha):
    offset_util = -alpha * 1 / (len(data.nodes)-1) 
    for i in range(len(data.nodes)):
        objective.SetCoefficient(n[i], float(alpha/(len(data.nodes)-1)))

    total_workload = np.sum(data.workload_matrix)
    max_delay = min(np.amax(data.node_delay_matrix), np.amax(data.max_delay_matrix))
    if total_workload:
        for f in range(len(data.functions)):
            for i in range(len(data.sources)):
                for j in range(len(data.nodes)):
                    workload = data.workload_matrix[f, i]
                    delay = data.node_delay_matrix[i, j]
                    print(max_delay)
                    if total_workload:
                        max_workload_delay = max_delay*np.sum(workload)
                        objective.SetCoefficient(x[i, f, j], float((1-alpha)*workload*delay/max_workload_delay))
    
    objective.SetOffset(offset_util)
    objective.SetMinimization()


def minimize_disruption(data, objective, moved_from, moved_to, allocated, deallocated):
    w = np.ma.size(data.old_allocations_matrix)
    for f in range(len(data.functions)):
        for j in range(len(data.nodes)):
            objective.SetCoefficient(moved_from[f, j], w)
            objective.SetCoefficient(moved_to[f, j], w)
    objective.SetCoefficient(allocated, w - 1)
    objective.SetCoefficient(deallocated, w + 1)
    objective.SetMinimization()

