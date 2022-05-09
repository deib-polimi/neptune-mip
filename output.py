import json
from collections import defaultdict

import numpy as np


def convert_x_matrix(matrix, sources, functions, nodes):
    routings = defaultdict(lambda : defaultdict(lambda : defaultdict(float)))
    assert matrix.shape == (len(sources), len(functions), len(nodes)), f"X matrix shape malformed. matrix shape is {matrix.shape} but it should be {(len(sources), len(functions), len(nodes))}"
    for i, source in enumerate(sources):
        for f, function in enumerate(functions):
            for j, destination in enumerate(nodes):
                if matrix[i][f][j] > 0.001:
                    routings[source][function][destination] = np.round(matrix[i][f][j], 3)
    return json.loads(json.dumps(routings))

def convert_c_matrix(matrix, functions, nodes):
    allocations = defaultdict(lambda : defaultdict(bool))
    assert matrix.shape == (len(functions), len(nodes)), f"X matrix shape malformed. matrix shape is {matrix.shape} but it should be {(len(sources), len(functions), len(nodes))}"
    for f, function in enumerate(functions):
        for j, destination in enumerate(nodes):
            if matrix[f][j] > 0.001:
                allocations[function][destination] = True
    return json.loads(json.dumps(allocations))