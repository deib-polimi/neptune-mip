def convert_q(q, data):
    q_ijt_values = {}
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                q_ijt_values[f"q[{i}][{j}][{t}]"] = q[i][j][t]
    return q_ijt_values

def convert_c(c, data):
    c_fi_values = {}
    for i in range(len(data.nodes)):
        for f in range(len(data.functions)):
            c_fi_values[f"c[{f}][{i}]"] = c[f][i]
    return c_fi_values

def convert_mu(mu, data):
    mu_jt_values = {}
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            mu_jt_values[f"mu[{j}][{t}]"] = mu[j][t]
    return mu_jt_values

def convert_sigma(sigma, data):
    sigma_jt_values = {}
    for j in range(len(data.nodes)):
        for t in range(len(data.tables)):
            sigma_jt_values[f"sigma[{j}][{t}]"] = sigma[j, t]
    
    return sigma_jt_values

def convert_y(y, data):
    y_ftij_values = {}
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for f in range(len(data.functions)):
                for t in range(len(data.tables)):
                    y_ftij_values[f"y[{f}][{t}][{i}][{j}]"] = y[f, t, i, j]
    return y_ftij_values



    

