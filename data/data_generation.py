import numpy as np
import random

import pandas as pd

import data_random_graph as rg
import json
from data_check import *


def exponential_weights(decay_rate=1.0, max_value=10):
    """
    Generate exponentially decreasing weights for values from 0 to max_value.

    :param decay_rate: The rate of exponential decay (0 < decay_rate < 1)
    :param max_value: The maximum value for the random integers
    :return: List of weights corresponding to the values from 0 to max_value
    """
    weights = [np.exp(-decay_rate * i) for i in range(max_value + 1)]
    return weights


def quadratic_weights(shift=10, max_value=10):
    """
    Generate weights following a quadratic function shifted by a specified value.

    :param shift: The shift value for the quadratic function
    :param max_value: The maximum value for the random integers
    :return: List of weights corresponding to the values from 0 to max_value
    """
    weights = [((i - shift) ** 2) for i in range(max_value + 1)]
    weights[0] = weights[0] * 5
    return weights


def weighted_random_choice(elements, weights):
    """
    Generate a random integer from the elements with specified weights.

    :param elements: List of elements to choose from
    :param weights: List of weights corresponding to the elements
    :return: A randomly chosen element
    """
    return random.choices(elements, weights, k=1)[0]


def generate_workload_on_destination_matrix(num_functions, num_nodes):
    max_value = 10
    decay_rate = 0.5
    elements = list(range(max_value + 1))
    weights = exponential_weights(decay_rate, max_value)
    return [
        [weighted_random_choice(elements, weights) for _ in range(num_nodes)]
        for _ in range(num_functions)
    ]


def generate_delay_matrix(num_nodes):
    # Generate a symmetric delay matrix with random delays between 1 and 10
    delay_matrix = rg.random_delays(num_nodes)
    print(pd.DataFrame(delay_matrix))
    return delay_matrix


def generate_node_memories(num_nodes):
    # Generate random memory values for each node
    return [random.randint(250, 550) for _ in range(num_nodes)]


def generate_node_storage(num_nodes):
    # Generate random storage values for each node
    return [random.randint(512, 2048) for _ in range(num_nodes)]


def generate_node_cores(num_nodes):
    # Generate random core values between for each node
    return [random.randint(20, 50) for _ in range(num_nodes)]


def generate_function_memories(num_functions):
    return [random.randint(125, 200) for _ in range(num_functions)]


def generate_function_max_delays(num_functions):
    return [random.randint(20, 30) for _ in range(num_functions)]


# generate u_f_j
def generate_core_per_req_matrix(num_functions, num_nodes):
    return [[random.randint(1, 5) for _ in range(num_nodes)] for _ in range(num_functions)]


def generate_actual_cpu_allocations(function_names, node_names):
    return {fn: {node: random.choice([True]) for node in node_names} for fn in function_names}


def generate_table_sizes(num_tables):
    return [random.randint(100, 200) for _ in range(num_tables)]


def generate_v_old_matrix(num_nodes, num_tables):
    matrix = [[-1 for _ in range(num_tables)] for _ in range(num_nodes)]
    for i in range(num_tables):
        # Select the number of copies
        num_copies = random.randint(1, num_nodes // 2 + 1)

        # print(f"Selected copies for table {i}: {num_copies}")
        while num_copies > 0:
            for j in range(num_nodes):

                if matrix[j][i] == -1 and random.choice([True, False]):
                    matrix[j][i] = 1
                    num_copies -= 1
                    if num_copies == 0:
                        break
    # Set all remaining None values to 0
    for i in range(num_nodes):
        for j in range(num_tables):
            if matrix[i][j] == -1:
                matrix[i][j] = 0
    print("Old table locations: ")
    for row in matrix:
        print(row)
    return matrix


def generate_read_per_req_matrix(num_functions, num_tables):
    max_value = 30
    elements = list(range(max_value + 1))
    weights = quadratic_weights(int(max_value / 2), max_value)
    return [
        [weighted_random_choice(elements, weights) for _ in range(num_tables)]
        for _ in range(num_functions)
    ]


def generate_write_per_req_matrix(num_functions, num_tables):
    max_value = 30
    elements = list(range(max_value + 1))
    weights = quadratic_weights(int(max_value / 2), max_value)
    return [
        [weighted_random_choice(elements, weights) for _ in range(num_tables)]
        for _ in range(num_functions)
    ]


def generate_workload_on_source_matrix(num_functions, num_nodes):
    max_value = 30
    decay_rate = 0.5
    elements = list(range(max_value + 1))
    weights = exponential_weights(decay_rate, max_value)
    return [
        [weighted_random_choice(elements, weights) for _ in range(num_nodes)]
        for _ in range(num_functions)
    ]


def generate_cores_matrix(num_functions, num_nodes):
    return [[random.randint(1, 10) for _ in range(num_nodes)] for _ in range(num_functions)]


def generate_r_ft_matrix(num_functions, num_tables, reads_matrix):
    r_ft_matrix = [[0 for _ in range(num_tables)] for _ in range(num_functions)]

    # Populate the r_ft_matrix based on the reads_matrix
    for i in range(num_functions):
        for j in range(num_tables):
            if reads_matrix[i][j] > 0:
                r_ft_matrix[i][j] = 1

    return r_ft_matrix


class DataGenerator:
    def __init__(self, auto_generate=False, seed=None):
        self.default_data = None
        self.auto_generate = auto_generate
        random.seed(seed)
        # Load configuration from config.json
        with open('config/config.json', 'r') as config_file:
            config = json.load(config_file)
        self.max_nodes = config["data_generation"]["max_nodes"]
        self.min_nodes = config["data_generation"]["min_nodes"]
        self.max_functions = config["data_generation"]["max_functions"]
        self.min_functions = config["data_generation"]["min_functions"]
        self.max_tables = config["data_generation"]["max_tables"]
        self.min_tables = config["data_generation"]["min_tables"]
        self.solver = config["solver"]
        self.with_db = self.solver["with_db"]

    def generate_node_names(self):
        num_nodes = random.randint(self.min_nodes, self.max_nodes)
        return [f"node_{chr(97 + i)}" for i in range(num_nodes)]

    def generate_function_names(self):
        num_functions = random.randint(self.min_functions, self.max_functions)
        return [f"ns/fn_{i}" for i in range(1, num_functions + 1)]

    def generate_table_names(self):
        num_tables = random.randint(self.min_tables, self.max_tables)
        return [f"table_{chr(97 + i)}" for i in range(num_tables)]

    def generate_input_data(self, max_attempts=1):
        if self.auto_generate:
            # Node infrastructure
            node_names = self.generate_node_names()
            num_nodes = len(node_names)

            node_delay_matrix = generate_delay_matrix(num_nodes)
            node_memories = generate_node_memories(num_nodes)
            node_storage = generate_node_storage(num_nodes)
            node_cores = generate_node_cores(num_nodes)

            # Functions data
            function_names = self.generate_function_names()
            num_functions = len(function_names)

            function_memories = generate_function_memories(num_functions)
            function_max_delays = generate_function_max_delays(num_functions)
            actual_cpu_allocations = generate_actual_cpu_allocations(function_names, node_names)

            # Tables data
            table_names = self.generate_table_names()
            num_tables = len(table_names)

            table_sizes = generate_table_sizes(num_tables)
            v_old_matrix = generate_v_old_matrix(num_nodes, num_tables)

            # Monitored data
            write_per_req_matrix = generate_write_per_req_matrix(num_functions, num_tables)
            read_per_req_matrix = generate_read_per_req_matrix(num_functions, num_tables)
            workload_on_source_matrix = generate_workload_on_source_matrix(num_functions, num_nodes)

            r_ft_matrix = generate_r_ft_matrix(num_functions, num_tables, read_per_req_matrix)

            # DEBUG
            print("R_FT matrix:\n", r_ft_matrix)

            # Generate and check if the total workload can be served by the community
            attempts = 0
            total_cores = sum(node_cores)
            print("Total cores: ", total_cores)

            core_per_req_matrix = generate_core_per_req_matrix(num_functions, num_nodes)
            while check_workload(core_per_req_matrix, total_cores, workload_on_source_matrix):
                core_per_req_matrix = generate_core_per_req_matrix(num_functions, num_nodes)
                attempts += 1
                if attempts >= max_attempts:
                    raise Exception("Error: Maximum attempts exceeded. The workload cannot be served by the community.")

            cores_matrix = generate_cores_matrix(num_functions, num_nodes)
            workload_on_destination_matrix = generate_workload_on_destination_matrix(num_functions, num_nodes)

            input_data = {
                "with_db": self.with_db,
                "solver": self.solver,
                "workload_coeff": 1,
                "community": "community-test",
                "namespace": "namespace-test",
                "node_names": node_names,
                "node_delay_matrix": node_delay_matrix,
                "workload_on_source_matrix": workload_on_source_matrix,  # lambda_f_i
                "node_memories": node_memories,
                "node_storage": node_storage,
                "node_cores": node_cores,
                "gpu_node_names": [],
                "gpu_node_memories": [],
                "function_names": function_names,
                "function_memories": function_memories,
                "function_max_delays": function_max_delays,
                "cores_per_req_matrix": core_per_req_matrix,
                "gpu_function_names": [],
                "gpu_function_memories": [],
                "actual_cpu_allocations": actual_cpu_allocations,
                "actual_gpu_allocations": {},
                "table_names": table_names,
                "table_sizes": table_sizes,
                "v_old_matrix": v_old_matrix,
                "r_ft_matrix": r_ft_matrix,
                "write_per_req_matrix": write_per_req_matrix,
                "read_per_req_matrix": read_per_req_matrix,
                "cores_matrix": cores_matrix,
                "workload_on_destination_matrix": workload_on_destination_matrix
            }

            return input_data, num_nodes, num_functions, num_tables
        else:
            with open('config/default_data.json', 'r') as default_file:
                self.default_data = json.load(default_file)
            return self.default_data
