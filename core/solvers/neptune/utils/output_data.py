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