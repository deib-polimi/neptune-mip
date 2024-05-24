from fontTools.varLib.instancer import solver

M = 10 ** 6
epsilon = 10 ** -6


# TODO rinominare a constraint

# If a function `f` is deployed on node i then c[f,i] is True
def constrain_c_according_to_x(data, solver, c, x):
    for f in range(len(data.functions)):
        for j in range(len(data.nodes)):
            solver.Add(
                solver.Sum([
                    x[i, f, j] for i in range(len(data.sources))
                ]) <= c[f, j] * M)
            solver.Add(
                solver.Sum([
                    x[i, f, j] for i in range(len(data.sources))
                ]) + epsilon >= c[f, j])


# The sum of the memory of functions deployed on a node is less than its capacity
def constrain_memory_usage(data, solver, c):
    for j in range(len(data.nodes)):
        solver.Add(
            solver.Sum([
                c[f, j] * data.function_memory_matrix[f] for f in range(len(data.functions))
            ]) <= data.node_memory_matrix[j])


# All requests in a node are rerouted somewhere else
def constrain_handle_all_requests(data, solver, x, eq=True):
    op = lambda x: x == 1 if eq else lambda x: x <= 1
    for f in range(len(data.functions)):
        for i in range(len(data.sources)):
            solver.Add(
                op(solver.Sum([
                    x[i, f, j] for j in range(len(data.nodes))
                ])))


# All requests except the ones managed by GPUs in a node are rerouted somewhere else
def constrain_handle_only_remaining_requests(data, solver, x):
    for f in range(len(data.functions)):
        for i in range(len(data.sources)):
            solver.Add(
                solver.Sum([
                    x[i, f, j] for j in range(len(data.nodes))
                ]) == 1 - data.prev_x[i][f].sum())


def constrain_handle_required_requests(data, solver, x):
    # Handle all requests
    if data.prev_x.shape == (0,):
        constrain_handle_all_requests(data, solver, x)
    # Handle all requests except for the ones handled by GPUs
    else:
        constrain_handle_only_remaining_requests(data, solver, x)


# Do not overload nodes' CPUs
def constrain_CPU_usage(data, solver, x):
    for j in range(len(data.nodes)):
        solver.Add(
            solver.Sum([
                x[i, f, j] * data.workload_matrix[f, i] * data.core_per_req_matrix[f, j] for f in
                range(len(data.functions)) for i in
                range(len(data.sources))
            ]) <= data.node_cores_matrix[j]
        )


# If a node i contains one or more functions then n[i] is True
def constrain_n_according_to_c(data, solver, n, c):
    for i in range(len(data.nodes)):
        solver.Add(
            solver.Sum([
                c[f, i] for f in range(len(data.functions))
            ]) <= n[i] * M)
        solver.Add(
            solver.Sum([
                c[f, i] for f in range(len(data.functions))
            ]) + epsilon >= n[i])


# The sum of the memory of functions deployed on a gpu device is less than its capacity
def constrain_GPU_memory_usage(data, solver, c):
    for j in range(len(data.nodes)):
        solver.Add(
            solver.Sum([
                c[f, j] * data.gpu_function_memory_matrix[f] for f in range(len(data.functions))
            ]) <= data.gpu_node_memory_matrix[j])


# Do not overload nodes' GPUs
def constrain_GPU_usage(data, solver, x):
    for f in range(len(data.functions)):
        for j in range(len(data.nodes)):
            solver.Add(
                solver.Sum([
                    x[i, f, j] * data.workload_matrix[f, i] * data.response_time_matrix[f, j] for i in
                    range(len(data.sources))
                ]) <= 1000)


def constrain_budget(data, solver, n):
    for j in range(len(data.nodes)):
        solver.Add(n[j] * data.node_costs[j] <= data.node_budget)


###################################################################

# Each table should have at least 1 host(and 1 master)
def constraint_table_presence(data, solver, mu):
    for t in range(len(data.tables)):
        solver.Add(
            solver.Sum([
                mu[j, t] == 1 for j in range(len(data.nodes))
            ])
        )


# A node can host either a master or a slave instance

def constraint_master_slave(data, solver, mu, sigma):
    for t in range(len(data.tables)):
        for j in range(len(data.nodes)):
            solver.Add(
                mu[j, t] + sigma[j, t] <= 1
            )


# If there is an assignment, we need a function instance on i, the dependency variable true and the
# assignment can be at most 1

def constraint_function_assignment(data, solver, y, c, r):
    pass


# The node storage capacity shouldn’t be filled

def constraint_node_capacity(data, solver, mu, sigma):
    for i in range(len(data.nodes)):
        solver.Add(
            solver.Sum([
                (sigma[i, t] + mu[i, t]) * data.s[t] <= data.node_storage_matrix[i]
                for t in range(len(data.tables))
            ])
        )


# rho definition using big-M method

def constraint_rho_according_to_y(data, solver, rho, y):
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            solver.Add(
                solver.Sum([
                    y[f, t, i, j] >= 1 - M * (1 - rho[j, t])
                    for f in range(len(data.nodes))
                    for i in range(len(data.nodes))
                ])
            )
            solver.Add(
                solver.Sum([
                    y[f, t, i, j] <= M * (rho[j, t])
                    for f in range(len(data.nodes))
                    for i in range(len(data.nodes))
                ])
            )


# r definition using big-M method

def constraint_r_according_to_beta_and_gamma(data, solver, r):
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            solver.Add(
                data.write_per_req_matrix[f, t] + data.read_per_req_matrix[f, t] >= 1 - M * (1 - r[f, t])
            )
            solver.Add(
                data.write_per_req_matrix[f, t] + data.read_per_req_matrix[f, t] <= M * (r[f, t])
            )


# If there is a function reading on table t in node j and the table was not present, then the table
# should be loaded from somewhere.

# TODO: add v_old_matrix in data file
def constraint_migration(data, solver, rho, q):
    for j in range(len(data)):
        for t in range(len(data.tables)):
            solver.Add(
                solver.Sum([
                    rho[j, t] * (1 - data.v_old_matrix[j, t]) >= q[i, j, t]
                    for i in range(len(data.nodes))
                ])
            )


# The table should be present

def constraint_presence(data, solver, rho, mu, sigma):
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            solver.Add(
                rho[j, t] <= mu[j, t] + sigma[j, t]
            )
