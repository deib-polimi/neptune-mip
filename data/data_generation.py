import numpy as np
import random
import data_random_graph as rg
import json
from data_check import *

class DataGenerator:
    def __init__(self, auto_generate=False, seed=None):
        self.auto_generate = auto_generate
        random.seed(seed)
        # Load configuration from config.json
        with open('data/config/config.json', 'r') as config_file:
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

    def generate_delay_matrix(self, num_nodes):
        # Generate a symmetric delay matrix with random delays between 1 and 10
        delay_matrix = rg.random_delays(num_nodes)
        return delay_matrix

    def generate_node_memories(self, num_nodes):
        # Generate random memory values for each node
        return [random.randint(50, 500) for _ in range(num_nodes)]

    def generate_node_storage(self, num_nodes):
        # Generate random storage values for each node
        return [random.randint(128,968) for _ in range(num_nodes)]

    def generate_node_cores(self, num_nodes):
        # Generate random core values between for each node
        return [random.randint(10000, 100000) for _ in range(num_nodes)]
    
    def generate_function_names(self):
        num_functions = random.randint(self.min_functions, self.max_functions)
        return [f"ns/fn_{i}" for i in range(1, num_functions + 1)]

    def generate_function_memories(self, num_functions):
        return [random.randint(1, 10) for _ in range(num_functions)]

    def generate_function_max_delays(self, num_functions):
        return [random.randint(1000, 2000) for _ in range(num_functions)]

    # generate u_f_j
    def generate_core_per_req_matrix(self, num_functions, num_nodes):
        return [[random.randint(1, 5) for _ in range(num_nodes)] for _ in range(num_functions)]

    def generate_actual_cpu_allocations(self, function_names, node_names):
        return {fn: {node: random.choice([True]) for node in node_names} for fn in function_names}
        
    def generate_table_names(self):
        num_tables = random.randint(self.min_tables, self.max_tables)
        return [f"table_{chr(97 + i)}" for i in range(num_tables)]

    def generate_table_sizes(self, num_tables):
        return [random.randint(100, 200) for _ in range(num_tables)]

    def generate_v_old_matrix(self, num_nodes, num_tables):
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

    def generate_read_per_req_matrix(self, num_functions, num_tables):
        return [[random.randint(0, 10) for _ in range(num_tables)] for _ in range(num_functions)]

    def generate_write_per_req_matrix(self, num_functions, num_tables):
        return [[random.randint(0, 10) for _ in range(num_tables)] for _ in range(num_functions)]

    def generate_workload_on_source_matrix(self, num_functions, num_nodes):
        return [[random.randint(5, 30) for _ in range(num_nodes)] for _ in range(num_functions)]

    def generate_cores_matrix(self, num_functions, num_nodes):
        return [[random.randint(1, 10) for _ in range(num_nodes)] for _ in range(num_functions)]

    def generate_workload_on_destination_matrix(self, num_functions, num_nodes):
        return [[random.randint(0, 10) for _ in range(num_nodes)] for _ in range(num_functions)]
    

    def generate_input_data(self, max_attempts=1):
        if self.auto_generate:
            # Node infrastructure
            node_names = self.generate_node_names()
            num_nodes = len(node_names)

            node_delay_matrix = self.generate_delay_matrix(num_nodes)
            node_memories = self.generate_node_memories(num_nodes)
            node_storage = self.generate_node_storage(num_nodes)
            node_cores = self.generate_node_cores(num_nodes)

            # Functions data
            function_names = self.generate_function_names()
            num_functions = len(function_names)

            function_memories = self.generate_function_memories(num_functions)
            function_max_delays = self.generate_function_max_delays(num_functions)
            actual_cpu_allocations = self.generate_actual_cpu_allocations(function_names, node_names)

            # Tables data
            table_names = self.generate_table_names()
            num_tables = len(table_names)

            table_sizes = self.generate_table_sizes(num_tables)
            v_old_matrix = self.generate_v_old_matrix(num_nodes, num_tables)

            # Monitored data
            write_per_req_matrix = self.generate_write_per_req_matrix(num_functions, num_tables)
            read_per_req_matrix = self.generate_read_per_req_matrix(num_functions, num_tables)
            workload_on_source_matrix = self.generate_workload_on_source_matrix(num_functions, num_nodes)

            # Generate and check if the total workload can be served by the community
            attempts = 0
            total_cores = sum(node_cores)
            print("Total cores: ", total_cores)

            core_per_req_matrix = self.generate_core_per_req_matrix(num_functions, num_nodes)
            while check_workload(core_per_req_matrix, total_cores, workload_on_source_matrix):
                core_per_req_matrix = self.generate_core_per_req_matrix(num_functions, num_nodes)
                attempts += 1
                if attempts >= max_attempts:
                    raise Exception("Error: Maximum attempts exceeded. The workload cannot be served by the community.")

            cores_matrix = self.generate_cores_matrix(num_functions, num_nodes)
            workload_on_destination_matrix = self.generate_workload_on_destination_matrix(num_functions, num_nodes)

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
                "write_per_req_matrix": write_per_req_matrix,
                "read_per_req_matrix": read_per_req_matrix,
                "cores_matrix": cores_matrix,  # TODO: cos'è?
                "workload_on_destination_matrix": workload_on_destination_matrix
            }

            return input_data,num_nodes,num_functions,num_tables
        else:
            with open('config/default_data.json', 'r') as default_file:
                self.default_data = json.load(default_file)
            return self.default_data
        