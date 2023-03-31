import numpy as np


def output_x_and_c(data, x, c):
    x_matrix = np.empty(shape=(len(data.sources), len(data.functions), len(data.nodes)))
    for j in range(len(data.nodes)):
        for i in range(len(data.sources)):
            for f in range(len(data.functions)):
                x_matrix[i][f][j] = x[i, f, j].solution_value()
    c_matrix = np.empty(shape=(len(data.functions), len(data.nodes)))
    for j in range(len(data.nodes)):
        for f in range(len(data.functions)):
            c_matrix[f][j] = c[f, j].solution_value()
    return x_matrix, c_matrix


