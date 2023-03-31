import itertools

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
    solver.Add(
        solver.Sum([
            n[i]
            for i in range(len(data.nodes))
        ]) == data.max_score 
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
