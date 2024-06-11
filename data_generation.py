import numpy as np
import random
import random_graph as rg

class DataGeneration:
    def __init__(self, autogen=False):
        self.autogen = autogen
        self.max_nodes = 3
        self.min_nodes = 3
        self.max_functions = 3
        self.min_functions = 3
        self.max_tables = 2
        self.min_tables = 2

    def generate_node_names(self):
        if self.autogen:
            num_nodes = random.randint(self.min_nodes, self.max_nodes)
            return [f"node_{chr(97 + i)}" for i in range(num_nodes)]
        return ["node_a", "node_b", "node_c"]

    def generate_delay_matrix(self, num_nodes):
        if self.autogen:
            # Generate a symmetric delay matrix with random delays between 1 and 1000
            delay_matrix = rg.random_delays(num_nodes)
        else:
            # Default delay matrix for 3 nodes
            delay_matrix = [[0, 250, 250], [250, 0, 4], [250, 4, 0]]
        return delay_matrix

    def generate_node_memories(self, num_nodes):
        if self.autogen:
            # Generate random memory values between 50 and 500 for each node
            return [random.randint(50, 500) for _ in range(num_nodes)]
        # Default memory values for 3 nodes
        return [100, 100, 200]

    def generate_node_storage(self, num_nodes):
        if self.autogen:
            # Generate random storage values between 512 and 4096 for each node
            return [random.randint(4096, 8192) for _ in range(num_nodes)]
        # Default storage values for 3 nodes
        return [1024, 1024, 2048]

    def generate_node_cores(self, num_nodes):
        if self.autogen:
            # Generate random core values between 10 and 200 for each node
            return [random.randint(500, 1000) for _ in range(num_nodes)]
        # Default core values for 3 nodes
        return [100, 50, 50]

    def generate_function_names(self):
        if self.autogen:
            num_functions = random.randint(self.min_functions, self.max_functions)
            return [f"ns/fn_{i}" for i in range(1, num_functions + 1)]
        return ["ns/fn_1", "ns/fn_2"]

    def generate_function_memories(self, num_functions):
        if self.autogen:
            return [random.randint(1, 10) for _ in range(num_functions)]
        return [5, 5]

    def generate_function_max_delays(self, num_functions):
        if self.autogen:
            return [random.randint(1000, 2000) for _ in range(num_functions)]
        return [100, 100]

    # genera u_f_j
    def generate_core_per_req_matrix(self, num_functions, num_nodes):
        if self.autogen:
            return [[random.randint(1, 5) for _ in range(num_nodes)] for _ in range(num_functions)]

    def generate_actual_cpu_allocations(self, function_names, node_names):
        if self.autogen:
            return {fn: {node: random.choice([True]) for node in node_names} for fn in function_names}
        return {
            "ns/fn_1": {"node_a": True, "node_b": True, "node_c": True},
            "ns/fn_2": {"node_a": True, "node_b": True, "node_c": True}
        }

    def generate_table_names(self):
        if self.autogen:
            num_tables = random.randint(self.min_tables, self.max_tables)
            return [f"table_{chr(97 + i)}" for i in range(num_tables)]
        return ["table_a", "table_b"]

    def generate_table_sizes(self, num_tables):
        if self.autogen:
            return [random.randint(100, 200) for _ in range(num_tables)]
        return [500, 200]

    def generate_v_old_matrix(self, num_nodes, num_tables):
        # print(f"Generating {num_nodes} x {num_tables} matrix")
        if self.autogen:
            matrix = [[-1 for _ in range(num_tables)] for _ in range(num_nodes)]
            # print(matrix)
            for i in range(num_tables):  # Iterating over columns
                # Select the number of copies
                num_copies = random.randint(1, num_nodes // 2 + 1)
                # print(f"Selected copies for table {i}: {num_copies}")
                while num_copies > 0:
                    for j in range(num_nodes):  # Iterating over columns

                        if matrix[j][i] == -1 and random.choice([True, False]):
                            matrix[j][i] = 1
                            num_copies -= 1
                            if num_copies == 0:
                                break
            # Set all remaining None values to 1
            for i in range(num_nodes):
                for j in range(num_tables):
                    if matrix[i][j] == -1:
                        matrix[i][j] = 0
            print("Old table locations: ")
            for row in matrix:
                print(row)
            return matrix
        return [[0, 1], [0, 0], [1, 0]]

    def generate_read_per_req_matrix(self, num_functions, num_tables):
        if self.autogen:
            return [[random.randint(0, 10) for _ in range(num_tables)] for _ in range(num_functions)]
        return [[22, 0], [0, 11]]

    def generate_write_per_req_matrix(self, num_functions, num_tables):
        if self.autogen:
            return [[random.randint(0, 10) for _ in range(num_tables)] for _ in range(num_functions)]
        return [[33, 0], [0, 20]]

    def generate_workload_on_source_matrix(self, num_functions, num_nodes):
        if self.autogen:
            return [[random.randint(5, 30) for _ in range(num_nodes)] for _ in range(num_functions)]
        return [[100, 0, 0], [1, 0, 0]]

    def generate_cores_matrix(self, num_functions, num_nodes):
        if self.autogen:
            return [[random.randint(1, 10) for _ in range(num_nodes)] for _ in range(num_functions)]
        return [[1, 1, 100] for _ in range(num_functions)]  # Default cores matrix

    def generate_workload_on_destination_matrix(self, num_functions, num_nodes):
        if self.autogen:
            return [[random.randint(0, 10) for _ in range(num_nodes)] for _ in range(num_functions)]
        return [[1, 1, 100] for _ in range(num_functions)]  # Default workload on destination matrix
