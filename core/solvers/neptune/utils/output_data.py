import numpy as np


def output_q(data,q):
    q_matrix = np.empty(shape=(len(data.nodes), len(data.nodes), len(data.tables)))
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                q_matrix[i][j][t] = q[i, j, t].solution_value()
    return q_matrix

def output_y(data,y):
    y_matrix = np.empty(shape=(len(data.functions), len(data.tables), len(data.nodes), len(data.nodes),))
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for f in range(len(data.functions)):
                for t in range(len(data.tables)):
                    y_matrix[f, t, i, j] = y[f, t, i, j].solution_value()
    return y_matrix

def output_mu(data, mu):
    mu_matrix = np.empty(shape=(len(data.nodes),len(data.tables)))
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            mu_matrix[j, t]= mu[j, t].solution_value()
    return mu_matrix

def output_sigma(data, sigma):
    sigma_matrix = np.empty(shape=(len(data.nodes),len(data.tables)))
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            sigma_matrix[j, t]= sigma[j, t].solution_value()
    return sigma_matrix

def output_c(data, c):
    c_matrix = np.empty(shape=(len(data.functions), len(data.nodes)))
    for j in range(len(data.nodes)):
        for f in range(len(data.functions)):
            c_matrix[f][j] = c[f, j].solution_value()
    
    return c_matrix

def output_x(data, x):
    x_matrix = np.empty(shape=(len(data.nodes), len(data.functions), len(data.nodes)))
    for i in range(len(data.nodes)):
        for f in range(len(data.functions)):
            for j in range(len(data.nodes)):
                x_matrix[i, f, j] = x[i, f, j].solution_value()
    return x_matrix

def output_z(data, z):
    z_matrix = np.empty(shape=(len(data.functions), len(data.tables), len(data.nodes), len(data.nodes), len(data.nodes)))
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            for i in range(len(data.nodes)):
                for j in range(len(data.nodes)):
                    for k in range(len(data.nodes)):
                        z_matrix[f, t, i, j, k] = z[f, t, i, j, k].solution_value()
    return z_matrix

def output_w(data, w):
    w_matrix = np.empty(shape=(len(data.functions), len(data.tables), len(data.nodes), len(data.nodes), len(data.nodes)))
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            for i in range(len(data.nodes)):
                for j in range(len(data.nodes)):
                    for k in range(len(data.nodes)):
                        w_matrix[f, t, i, j, k] = w[f, t, i, j, k].solution_value()
    return w_matrix

def output_r(data, r):
    r_matrix = np.empty(shape=(len(data.functions), len(data.tables)))
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            r_matrix[f, t] = r[f, t].solution_value()
    return r_matrix

def output_rho(data, rho):
    rho_matrix = np.empty(shape=(len(data.nodes), len(data.tables)))
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            rho_matrix[j, t] = rho[j, t].solution_value()
    return rho_matrix

def output_gmax(data, gmax):
    gmax_vector = np.empty(shape=(len(data.tables),))
    for t in range(len(data.tables)):
        gmax_vector[t] = gmax[t].solution_value()
    return gmax_vector

def output_d(data, d):
    d_matrix = np.empty(shape=(len(data.nodes), len(data.nodes), len(data.tables)))
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                d_matrix[i, j, t] = d[i, j, t].solution_value()
    return d_matrix
