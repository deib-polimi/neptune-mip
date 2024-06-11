from .constraints_step1 import *


###################################################################

# Each table should have at least 1 host(and 1 master)
def constraint_table_presence(data, solver, mu):
    for t in range(len(data.tables)):
        solver.Add(
            solver.Sum([
                mu[j, t] for j in range(len(data.nodes))
            ]) == 1
        )


# A node can host either a master or a slave instance

def constraint_master_slave(data, solver, mu, sigma):
    for t in range(len(data.tables)):
        for j in range(len(data.nodes)):
            solver.Add(
                mu[j, t] + sigma[j, t] <= 1
            )

    # DEBUG force replication
    for t in range(len(data.tables)):
        solver.Add(
            solver.Sum([
                sigma[j, t] for j in range(len(data.nodes))
            ]) >= 1
        )


# If there is an assignment, we need a function instance on i, the dependency variable true and the
# assignment can be at most 1


def constraint_function_assignment(data, solver, y, cr, c, r):
    for i in range(len(data.nodes)):
        for t in range(len(data.tables)):
            for f in range(len(data.functions)):
                solver.Add(
                    solver.Sum([
                        y[f, t, i, j] for j in range(len(data.nodes))
                    ])
                    == cr[f, t, i]
                )
    # Linearization
    for i in range(len(data.nodes)):
        for t in range(len(data.tables)):
                for f in range(len(data.functions)):
                    solver.Add(
                        cr[f, t, i] <= c[f, i]
                    )
                    solver.Add(
                        cr[f, t, i] <= r[f, t]
                    )
                    solver.Add(
                        cr[f, t, i] >= c[f, i] + r[f, t] - 1
                    )
    # DEBUG
    # Force self loops
    for i in range(len(data.nodes)):
        for t in range(len(data.tables)):
            for f in range(len(data.functions)):
                solver.Add(
                        y[f, t, i, i] == 1
                )
    for i in range(len(data.nodes)):
        for f in range(len(data.functions)):
            solver.Add(
                c[f, i] == 1
            )


# The node storage capacity shouldn’t be filled

def constraint_node_capacity(data, solver, mu, sigma):
    for i in range(len(data.nodes)):
        solver.Add(
            solver.Sum([
                (sigma[i, t] + mu[i, t]) * data.tables_sizes[t]
                for t in range(len(data.tables))
            ]) <= data.node_storage_matrix[i]
        )


# rho definition using big-M method

def constraint_rho_according_to_y(data, solver, rho, y):
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            solver.Add(
                solver.Sum([
                    y[f, t, i, j]
                    for f in range(len(data.functions))
                    for i in range(len(data.nodes))
                ]) >= 1 - M * (1 - rho[j, t])
            )
            solver.Add(
                solver.Sum([
                    y[f, t, i, j]
                    for f in range(len(data.functions))
                    for i in range(len(data.nodes))
                ]) <= M * (rho[j, t])
            )


# r definition using big-M method

def constraint_r_according_to_beta_and_gamma(data, solver, r):
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            solver.Add(
                float(data.write_per_req_matrix[f, t] + data.read_per_req_matrix[f, t]) >= 1 - M * (1 - r[f, t])
            )
            solver.Add(
                float(data.write_per_req_matrix[f, t] + data.read_per_req_matrix[f, t]) <= M * (r[f, t])
            )


# If there is a function reading on table t in node j and the table was not present, then the table
# should be loaded from somewhere.

def constraint_migration(data, solver, rho, q):
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            solver.Add(
                rho[j, t] * float(1 - data.v_old_matrix[j, t]) ==
                solver.Sum([
                    q[i, j, t]
                    for i in range(len(data.nodes))
                ])
            )


# Table should be moved from a node where it was previously present

def constraint_migration_2(data, solver, q):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                solver.Add(
                    q[i, j, t] <= data.v_old_matrix[i, t]
                )


# The table should be present

def constraint_presence(data, solver, rho, mu, sigma):
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            solver.Add(
                rho[j, t] <= mu[j, t] + sigma[j, t]
            )


def constraint_linearity_z(data, solver, z, x, y):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for k in range(len(data.nodes)):
                for f in range(len(data.functions)):
                    for t in range(len(data.tables)):
                        solver.Add(
                            z[f, t, i, j, k] <= x[k, f, i]
                        )
                        solver.Add(
                            z[f, t, i, j, k] >= x[k, f, i] - (1 - y[f, t, i, j])
                        )
                        solver.Add(
                            z[f, t, i, j, k] <= y[f, t, i, j]
                        )
                        solver.Add(
                            z[f, t, i, j, k] >= 0
                        )


def constraint_linearity_w(data, solver, w, x, mu):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for k in range(len(data.nodes)):
                for f in range(len(data.functions)):
                    for t in range(len(data.tables)):
                        solver.Add(
                            w[f, t, i, j, k] <= x[k, f, i]
                        )
                        solver.Add(
                            w[f, t, i, j, k] >= x[k, f, i] - (1 - mu[j, t])
                        )
                        solver.Add(
                            w[f, t, i, j, k] <= mu[j, t]
                        )



def constraint_linearity_psi(data, solver, psi, x, mu, sigma):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                solver.Add(
                    psi[i, j, t] <= mu[j, t]
                )
                solver.Add(
                    psi[i, j, t] <= sigma[i, t]
                )
                solver.Add(
                    psi[i, j, t] >= mu[j, t] + sigma[i, t] - 1
                )


def constraint_linearity_gmax(data, solver, gmax, psi, d):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                solver.Add(
                    psi[i, j, t] * data.node_delay_matrix[i, j] <= data.node_delay_matrix[i, j]
                )
                solver.Add(
                    gmax[t] >= psi[i, j, t]
                )
                solver.Add(
                    gmax[t] <= psi[i, j, t] + data.max_delay * (1 - d[i, j])
                )
    solver.Add(
        solver.Sum([
            d[i, j]
            for i in range(len(data.nodes))
            for j in range(len(data.nodes))
        ]) == 1
    )
