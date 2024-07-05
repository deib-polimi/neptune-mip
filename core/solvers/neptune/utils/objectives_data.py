# Define the objective function

def minimize_network_data_delay(data, objective, x, z, w, gmax, q, c_f, c_r, c_w, c_s, c_m):
    # Constants
    C = len(data.nodes)
    F = len(data.functions)
    T = len(data.tables)
    delta = data.node_delay_matrix
    lambda_w = data.workload_matrix
    beta = data.read_per_req_matrix
    gamma = data.write_per_req_matrix
    size = data.tables_sizes

    # C^f

    if c_f:
        for i in range(C):
            for j in range(C):
                for f in range(F):
                    objective.SetCoefficient(
                        x[i, f, j], float(delta[i, j] * lambda_w[f, i])
                    )

    # C^r

    if c_r:
        for i in range(C):
            for j in range(C):
                for k in range(C):
                    for f in range(F):
                        for t in range(T):
                            objective.SetCoefficient(
                                z[f, t, i, j, k],
                                float(delta[i, j] * beta[f, t] * size[t] * lambda_w[f, k] * (1 / (60 * 2)))
                            )

    # C^w

    if c_w:
        for i in range(C):
            for j in range(C):
                for k in range(C):
                    for f in range(F):
                        for t in range(T):
                            objective.SetCoefficient(
                                w[f, t, i, j, k],
                                float(delta[i, j] * gamma[f, t] * size[t] * lambda_w[f, k] * (1 / (60 * 2)))
                            )
    # C^s

    if c_s:
        coefficients = {t: 0 for t in range(T)}

        for k in range(C):
            for t in range(T):
                for f in range(F):
                    coefficients[t] += float(lambda_w[f, k] * gamma[f, t] * size[t] * (1 / (60 * 2)))

        for t in range(T):
            objective.SetCoefficient(gmax[t], coefficients[t])
    # C^m

    if c_m:
        for i in range(C):
            for j in range(C):
                for t in range(T):
                    objective.SetCoefficient(
                        q[i, j, t], float(0.1 * delta[i, j] * size[t] * (1 / (60 * 2)))
                    )
    objective.SetMinimization()


def minimize_network_data_only_delay(data, objective, gmax, y, mu):
    # Constants
    C = len(data.nodes)
    F = len(data.functions)
    T = len(data.tables)
    delta = data.node_delay_matrix
    lambda_w = data.workload_matrix
    beta = data.read_per_req_matrix
    gamma = data.write_per_req_matrix
    size = data.tables_sizes
    x = data.prev_x

    # C^r

    coefficient = 0

    for i in range(C):
        for j in range(C):
            for f in range(F):
                for t in range(T):
                    for k in range(C):
                        coefficient += x[k, f, i] * lambda_w[f, k]

                    objective.SetCoefficient(
                        y[f, t, i, j],
                        float(coefficient * delta[i, j] * beta[f, t] * size[t] * (1 / (60 * 2)))
                    )
                    coefficient = 0

    # C^w

    coefficient = 0

    for j in range(C):
        for t in range(T):
            for k in range(C):
                for f in range(F):
                    for i in range(C):
                        coefficient += x[k, f, i] * lambda_w[f, k] * delta[i, j] * gamma[f, t]

            objective.SetCoefficient(
                mu[j, t],
                float(coefficient * size[t] * (1 / (60 * 2)))
            )
            coefficient = 0

    # C^s

    coefficient = 0

    for t in range(T):
        for f in range(F):
            for k in range(C):
                coefficient += float(lambda_w[f, k] * gamma[f, t] * (1 / (60 * 2)))
        print(coefficient)
        objective.SetCoefficient(gmax[t], coefficient * size[t])
        coefficient = 0


    # # C^m
    #
    # if c_m:
    #     for i in range(C):
    #         for j in range(C):
    #             for t in range(T):
    #                 objective.SetCoefficient(
    #                     q[i, j, t], float(0.1 * delta[i, j] * size[t] * (1 / (60 * 2)))
    #                 )
    objective.SetMinimization()
