import numpy as np
import requests
import pprint
import networkx as nx
import time

from data_generation import DataGenerator
import graph_visualization as gv
from data_check import *
import json

# Generate the random data

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

SEED = config["SEED"]
max_attempts = config["max_attempts"]
url = config["request"]["url"]

data_generator = DataGenerator(auto_generate=False, seed=SEED)

input_data = data_generator.generate_input_data(max_attempts=max_attempts)

print("Infrastructure Data:")
print("")
gv.display_node_table(input_data)
print("")
gv.display_function_table(input_data)
print("")
gv.display_tables_table(input_data)
print("")

print("Monitored Data:")
print("\n(Workload, Cores)")
gv.display_function_node_matrix(input_data)
print("\n(Read,Write)")
gv.display_function_table_matrix(input_data)
print("\nTable location")
gv.display_table_node_matrix(input_data)

start_time = time.time()
response = requests.request(method='get', url=url, json=input_data)
end_time = time.time()
response_time = end_time - start_time 
print(f"Response time: {response_time:.4f} seconds\n")

print("\nSolution found!")
print("")

response_data = response.json()
# pprint.pprint(response_data)
# gv.draw_network(response_data)

graph = gv.create_graph_from_data(input_data)

#gv.draw_topology_graph(input_data, graph)

gv.draw_migrations_graph(response_data)
gv.draw_function_dep_graph(response_data)




# TODO: riconsiderare i costi


# TODO: richiesta costa un tot, inoltrare richiesta può pesare

# TODO: ricontrollare tables

# # Node infrastructure
# node_names = data_generator.generate_node_names()
# num_nodes = len(node_names)

# node_delay_matrix = data_generator.generate_delay_matrix(num_nodes)
# node_memories = data_generator.generate_node_memories(num_nodes)
# node_storage = data_generator.generate_node_storage(num_nodes)
# node_cores = data_generator.generate_node_cores(num_nodes)

# # Functions data

# function_names = data_generator.generate_function_names()
# num_functions = len(function_names)

# function_memories = data_generator.generate_function_memories(num_functions)
# function_max_delays = data_generator.generate_function_max_delays(num_functions)
# actual_cpu_allocations = data_generator.generate_actual_cpu_allocations(function_names, node_names)

# # Tables data

# tables_names = data_generator.generate_table_names()
# num_tables = len(tables_names)

# tables_sizes = data_generator.generate_table_sizes(num_tables)
# v_old_matrix = data_generator.generate_v_old_matrix(num_nodes, num_tables)

# # Monitored data
# write_per_req_matrix = data_generator.generate_write_per_req_matrix(num_functions, num_tables)
# read_per_req_matrix = data_generator.generate_read_per_req_matrix(num_functions, num_tables)
# workload_on_source_matrix = data_generator.generate_workload_on_source_matrix(num_functions, num_nodes)

# # Generate and check if the total workload can be served by the community
# attempts = 0
# total_cores = sum(node_cores)
# print("Total cores: ", total_cores)

# core_per_req_matrix = data_generator.generate_core_per_req_matrix(num_functions, num_nodes)
# while check_workload(core_per_req_matrix, total_cores,  workload_on_source_matrix):
#     core_per_req_matrix = data_generator.generate_core_per_req_matrix(num_functions, num_nodes)
#     attempts += 1
#     if attempts >= max_attempts:
#             raise Exception("Error: Maximum attempts exceeded. The workload cannot be served by the community.")




# cores_matrix = data_generator.generate_cores_matrix(num_functions, num_nodes)
# workload_on_destination_matrix = data_generator.generate_workload_on_destination_matrix(num_functions, num_nodes)

# input_data = {
#     "with_db": False,
#     "solver": {
#         "type": "NeptuneData",
#         "args": {"alpha": 1, "verbose": True, "soften_step1_sol": 1.3}
#     },
#     "workload_coeff": 1,
#     "community": "community-test",
#     "namespace": "namespace-test",
#     "node_names": node_names,
#     "node_delay_matrix": node_delay_matrix,
#     "workload_on_source_matrix": workload_on_source_matrix,  # lambda_f_i
#     "node_memories": node_memories,
#     "node_storage": node_storage,
#     "node_cores": node_cores,
#     "gpu_node_names": [],
#     "gpu_node_memories": [],
#     "function_names": function_names,
#     "function_memories": function_memories,
#     "function_max_delays": function_max_delays,
#     "cores_per_req_matrix": core_per_req_matrix,
#     "gpu_function_names": [],
#     "gpu_function_memories": [],
#     "actual_cpu_allocations": actual_cpu_allocations,
#     "actual_gpu_allocations": {},
#     "tables_names": tables_names,
#     "tables_sizes": tables_sizes,
#     "v_old_matrix": v_old_matrix,
#     "write_per_req_matrix": write_per_req_matrix,
#     "read_per_req_matrix": read_per_req_matrix,
#     "cores_matrix": cores_matrix,  # TODO: cos'è?
#     "workload_on_destination_matrix": workload_on_destination_matrix
# }

# Print the data

# print(json.dumps(input_data, indent=4))
# print(input_data)