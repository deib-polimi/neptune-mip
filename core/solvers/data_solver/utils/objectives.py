import numpy as np
from ...neptune.utils.objectives import *

def minimize_network_data_delay(data, objective, x, z, w, gmax, q):
    # Constants
    C = len(data.nodes)
    F = len(data.functions)
    T = len(data.tables)
    delta = data.node_delay_matrix
    lambda_w = data.workload_matrix
    beta = data.read_per_req_matrix
    gamma = data.write_per_req_matrix
    size = data.table_size
    # C^f
    for i in range(C):
        for j in range(C):
            for f in range(F):
                objective.SetCoefficient(
                    x[i, f, j], float(delta[i, j] * lambda_w[f, i])
                )
    # C^r
    for i in range(C):
        for j in range(C):
            for k in range(C):
                for f in range(F):
                    for t in range(T):
                        objective.SetCoefficient(
                            z[f, t, i, j, k], float(delta[i, j]*beta[f, t]*size[t]*lambda_w[f, k])
                        )

    # C^w
    for i in range(C):
        for j in range(C):
            for k in range(C):
                for f in range(F):
                    for t in range(T):
                        objective.SetCoefficient(
                            w[f, t, i, j, k], float(delta[i, j] * gamma[f, t] * size[t] * lambda_w[f, k])
                        )
    # C^s
    for k in range(C):
        for t in range(T):
            for f in range(F):
                objective.SetCoefficient(
                    gmax[t], float(lambda_w[f, k] * gamma[f, t] * size[t])
                )
    # C^m
    for i in range(C):
        for j in range(C):
            for t in range(T):
                objective.SetCoefficient(
                    q[i, j, t], float(delta[i, j] * size[t])
                )

    objective.SetMinimization()
