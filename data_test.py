import numpy as np
import requests
import pprint
import networkx as nx

from data_generation import DataGeneration
import json
import graph_visualization as gv

# Generate the random data


SEED = 25

dataG = DataGeneration(autogen=True, seed=SEED)

node_names = dataG.generate_node_names()
num_nodes = len(node_names)

node_delay_matrix = dataG.generate_delay_matrix(num_nodes)
node_memories = dataG.generate_node_memories(num_nodes)
node_storage = dataG.generate_node_storage(num_nodes)
node_cores = dataG.generate_node_cores(num_nodes)

function_names = dataG.generate_function_names()
num_functions = len(function_names)

function_memories = dataG.generate_function_memories(num_functions)
function_max_delays = dataG.generate_function_max_delays(num_functions)
actual_cpu_allocations = dataG.generate_actual_cpu_allocations(function_names, node_names)

tables_names = dataG.generate_table_names()
num_tables = len(tables_names)

tables_sizes = dataG.generate_table_sizes(num_tables)
v_old_matrix = dataG.generate_v_old_matrix(num_nodes, num_tables)
write_per_req_matrix = dataG.generate_write_per_req_matrix(num_functions, num_tables)
read_per_req_matrix = dataG.generate_read_per_req_matrix(num_functions, num_tables)
workload_on_source_matrix = dataG.generate_workload_on_source_matrix(num_functions, num_nodes)


total_cores = 0
for element in node_cores:
        total_cores += element

core_per_req_matrix = dataG.generate_core_per_req_matrix(num_functions, num_nodes)
cores_needed = np.inf

print("Total cores: ", total_cores)
while cores_needed >= total_cores:
    cores_needed = 0
    core_per_req_matrix = dataG.generate_read_per_req_matrix(num_functions, num_nodes)
    for i in range(len(core_per_req_matrix)):
        for j in range(len(core_per_req_matrix[i])):
            cores_needed += core_per_req_matrix[i][j] * workload_on_source_matrix[i][j]
    print("cores needed: ", cores_needed)



cores_matrix = dataG.generate_cores_matrix(num_functions, num_nodes)
workload_on_destination_matrix = dataG.generate_workload_on_destination_matrix(num_functions, num_nodes)

input_data = {
    "with_db": False,
    "solver": {
        "type": "NeptuneData",
        "args": {"alpha": 1, "verbose": True, "soften_step1_sol": 1.3}
    },
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
    "tables_names": tables_names,
    "tables_sizes": tables_sizes,
    "v_old_matrix": v_old_matrix,
    "write_per_req_matrix": write_per_req_matrix,
    "read_per_req_matrix": read_per_req_matrix,
    "cores_matrix": cores_matrix,  # TODO: cos'è?
    "workload_on_destination_matrix": workload_on_destination_matrix
}

# Print the data

# print(json.dumps(input_data, indent=4))
# print(input_data)
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

response = requests.request(method='get', url="http://localhost:5000/", json=input_data)

print("\nSolution found!")
print("")

response_data = response.json()
# pprint.pprint(response_data)
# gv.draw_network(response_data)

graph = gv.create_graph_from_data(input_data)

#gv.draw_topology_graph(input_data, graph)

#gv.draw_migrations_graph(response_data)
#gv.draw_function_dep_graph(response_data)




# TODO: riconsiderare i costi


# TODO: richiesta costa un tot, inoltrare richiesta può pesare
