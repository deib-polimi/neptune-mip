from fontTools.varLib.instancer import solver
from ...neptune.utils.constraints_step1 import *


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
    for i in range(len(data.nodes)):
        for t in range(len(data.tables)):
            for f in range(len(data.functions)):
                solver.Add(
                    solver.Sum([
                        y[f, t, i, j] == c[f, i] * r[f, t]
                    ])
                )


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
                            w[f, t, i, j, k] >= x[k, f, i] - (1 - mu[f, t, i, j])
                        )
                        solver.Add(
                            w[f, t, i, j, k] <= mu[f, t, i, j]
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
            d[i, j] == 1
            for i in range(len(data.nodes))
            for j in range(len(data.nodes))
        ])
    )
