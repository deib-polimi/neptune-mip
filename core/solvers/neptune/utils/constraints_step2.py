import itertools
import numpy as np


def constrain_moved_from(data, solver, moved_from, c):
    for f in range(len(data.functions)):
        for j in range(len(data.nodes)):
            solver.Add(moved_from[f, j] >= 0)
            solver.Add(moved_from[f, j] >= c[f, j] - data.old_allocations_matrix[f, j])


def constrain_moved_to(data, solver, moved_to, c):
    for f in range(len(data.functions)):
        for j in range(len(data.nodes)):
            solver.Add(moved_to[f, j] >= 0)
            solver.Add(moved_to[f, j] >= data.old_allocations_matrix[f, j] - c[f, j])


# Find a solution with the same node utilization
def constrain_node_utilization(data, solver, n):
    try:
        alpha = data.alpha
        if alpha == 0.0: return
    except:
        pass
    solver.Add(
        solver.Sum([
            n[i]
            for i in range(len(data.nodes))
        ]) <= np.sum(data.prev_n))


# Find a solution with the similar network delay
def constrain_network_delay(data, solver, x, coeff):
    try:
        alpha = data.alpha
        if alpha == 1.0: return

    except:
        pass

    vals = itertools.product(range(len(data.sources)),
                             range(len(data.functions)),
                             range(len(data.nodes)))

    solver.Add(
        solver.Sum([
            x[i, f, j] * float(data.node_delay_matrix[i, j] * data.workload_matrix[f, i])
            for i, f, j in vals
        ]) <= coeff * np.sum(
            [float(data.node_delay_matrix[i, j] * data.workload_matrix[f, i] * data.prev_x[i, f, j]) for i, f, j in
             vals])
    )


def constrain_migrations(data, solver, c, allocated, deallocated):
    solver.Add(allocated <= 0)
    solver.Add(solver.Sum(
        [data.old_allocations_matrix[f, i]
         for f, i in itertools.product(range(len(data.functions)), range(len(data.nodes)))]) -
               solver.Sum([c[f, i]
                           for f, i in itertools.product(range(len(data.functions)),
                                                         range(len(data.nodes)))]) >= allocated)
    solver.Add(deallocated <= 0)
    solver.Add(solver.Sum(
        [c[f, i]
         for f, i in itertools.product(range(len(data.functions)), range(len(data.nodes)))]) -
               solver.Sum([data.old_allocations_matrix[f, i]
                           for f, i in itertools.product(range(len(data.functions)),
                                                         range(len(data.nodes)))]) >= deallocated)


def constrain_deletions(data, solver, c, allocated, deallocated):
    solver.Add(
        deallocated +
        allocated +
        solver.Sum([data.old_allocations_matrix[f, i]
                    for f, i in itertools.product(range(len(data.functions)), range(len(data.nodes)))]) -
        solver.Sum([c[f, i]
                    for f, i in itertools.product(range(len(data.functions)), range(len(data.nodes)))]) >= 0
    )


def constrain_creations(data, solver, c, allocated, deallocated):
    solver.Add(
        deallocated +
        allocated -
        solver.Sum([data.old_allocations_matrix[f, i]
                    for f, i in itertools.product(range(len(data.functions)), range(len(data.nodes)))]) +
        solver.Sum([c[f, i]
                    for f, i in itertools.product(range(len(data.functions)), range(len(data.nodes)))]) >= 0
    )


def constrain_score(data, solver, x, n, alpha):
    max_func_delay = data.max_delay_matrix
    max_node_delay = data.node_delay_matrix.max(axis=0)
    func_matrix = np.vstack([max_func_delay for _ in range(len(data.nodes))])
    node_matrix = np.vstack([max_node_delay for _ in range(len(data.functions))])
    max_delay_matrix = np.maximum(func_matrix, node_matrix.T)
    solver.Add(
        solver.Sum([n[i] * float(alpha / (len(data.nodes))) for i in range(len(data.nodes))]) +
        solver.Sum([x[i, f, j] * float(
            (1 - alpha) * data.workload_matrix[f, i] * data.node_delay_matrix[i, j] / max_delay_matrix[i, f]) for
                    i, f, j in
                    itertools.product(range(len(data.nodes)), range(len(data.functions)),
                                      range(len(data.nodes)))]) <= data.max_score * 1.3
    )