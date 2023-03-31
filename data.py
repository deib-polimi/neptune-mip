from time import sleep

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import neptune_step1
import neptune_step2
import solver_utils as su

from output import convert_x_matrix, convert_c_matrix

cpu_coeff = 1.3
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
def data_to_solver_input(schedule_input):
    # Schedule input topology
    community = schedule_input.get('community')
    namespace = schedule_input.get('namespace')
    functions = schedule_input.get('function_names', [])
    gpu_functions = schedule_input.get('gpu_function_names', [])
    gpu_functions_set = set(gpu_functions)
    gpu_functions_mask = np.array([f in gpu_functions_set for f in functions])
    nodes = schedule_input.get('node_names', [])
    gpu_nodes = schedule_input.get('gpu_node_names', [])
    gpu_nodes_set = set(gpu_nodes)
    gpu_nodes_mask = np.array([n in gpu_nodes_set for n in nodes])

    assert set(gpu_functions).issubset(set(functions))
    assert set(gpu_nodes).issubset(set(nodes))

    # Schedule input topology data
    function_memories = schedule_input.get('function_memories')
    node_memories = schedule_input.get('node_memories')
    gpu_node_memories = schedule_input.get('gpu_node_memories')
    actual_cpu_allocations = schedule_input.get('actual_cpu_allocations')
    actual_gpu_allocations = schedule_input.get('actual_gpu_allocations')
    node_cores = schedule_input.get('node_cores')
    gpu_function_memories = schedule_input.get('gpu_function_memories')

    # Cluster runtime data
    node_delay_matrix = [[1 if s != d else 0 for s in nodes] for d in nodes]
    gpu_node_delay_matrix = [[1 if s != d else 0 for s in nodes] for d in gpu_nodes]
    workload_on_source_matrix = np.array([[0 for _ in nodes] for _ in functions])
    gpu_workload_on_destination_matrix = np.array([[0 for _ in gpu_nodes] for _ in gpu_functions])
    workload_on_destination_matrix = np.array([[0 for _ in nodes] for _ in functions])
    cores_matrix = np.array([[0 for _ in nodes] for _ in functions])
    max_delay_matrix = [1000 for _ in functions]
    response_time_matrix = [[0 for _ in nodes] for _ in functions]
    gpu_response_time_matrix = [[1 for _ in gpu_nodes] for _ in gpu_functions]
    old_cpu_allocations = np.array([[0 for _ in nodes] for _ in functions])
    old_gpu_allocations = np.array([[0 for _ in gpu_nodes] for _ in gpu_functions])
    core_per_req_matrix = np.array([[1 for _ in nodes] for _ in functions])

    '''
    # Retrieve data from the database
    username = "user"
    password = "password"
    database_host = "metrics-database.kube-system.svc.cluster.local"
    database_port = 5432
    postgres_str = (f"postgresql://{username}:{password}@{database_host}:{database_port}")
    interval = "'30 seconds'"
    cnx = create_engine(postgres_str)
    ar_df = pd.read_sql(
        sql=f"SELECT function, source, count(*) AS arrival_rate FROM metric WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{namespace}' AND community = '{community}' GROUP BY function, source ",
        con=cnx)
    ard_df = pd.read_sql(
        sql=f"SELECT function, destination, gpu, count(*) AS arrival_rate FROM metric WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{namespace}' AND community = '{community}' GROUP BY function, destination, gpu",
        con=cnx)
    rt_df = pd.read_sql(
        sql=f"SELECT function, destination, gpu, avg(latency) AS response_time FROM metric WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{namespace}' AND community = '{community}' GROUP BY function, destination, gpu ",
        con=cnx)
    dl_df = pd.read_sql(
        sql=f"SELECT f,t,l FROM (SELECT from_node, to_node FROM ping GROUP BY from_node, to_node) as p1 INNER JOIN LATERAL (SELECT from_node as f, to_node as t, avg_latency as l FROM ping p2 WHERE p1.from_node = p2.from_node AND p1.to_node = p2.to_node ORDER BY timestamp DESC LIMIT 1) AS data ON true",
        con=cnx
    )
    cpu_df = pd.read_sql(
        sql=f"SELECT function, node, avg(cores) AS cores FROM resource WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{namespace}' AND community = '{community}' GROUP BY function, node",
        con=cnx
    )

    print(f"ARRIVAL RATE SOURCE \n\n {ar_df}")
    print(f"ARRIVAL RATE DESTINATION \n\n {ard_df}")
    print(f"RESPONSE TIME \n\n {rt_df}")
    print(f"DELAYS \n\n {dl_df}")
    print(f"CPU CONSUMPTION \n\n {cpu_df}")

    print(workload_on_destination_matrix)
    '''
   
    # Create auxiliary data structures
    node_map = {}
    func_map = {}
    gpu_node_map = {}
    gpu_func_map = {}
    for i, node in enumerate(nodes):
        node_map[node] = i
    for i, node in enumerate(gpu_nodes):
        gpu_node_map[node] = i
    for i, func in enumerate(functions):
        func = func.split("/")[1]
        func_map[func] = i
    for i, func in enumerate(gpu_functions):
        func = func.split("/")[1]
        gpu_func_map[func] = i

    '''
    # Populate the runtime data with the data retrieved from the database
    for node, func, response_time, gpu in zip(rt_df['destination'], rt_df['function'], rt_df['response_time'],
                                              rt_df['gpu']):
        if gpu:
            gpu_response_time_matrix[gpu_func_map[func]][gpu_node_map[node]] = response_time
            pass
        else:
            response_time_matrix[func_map[func]][node_map[node]] = response_time

    for node, func, arrival_rate in zip(ar_df['source'], ar_df['function'], ar_df['arrival_rate']):
        workload_on_source_matrix[func_map[func]][node_map[node]] = arrival_rate

    for node, func, cores in zip(cpu_df['node'], cpu_df['function'], cpu_df['cores']):
        cores_matrix[func_map[func]][node_map[node]] = cores

    for node, func, response_time, gpu in zip(ard_df['destination'], ard_df['function'], ard_df['arrival_rate'],
                                              ard_df['gpu']):
        if gpu:
            gpu_workload_on_destination_matrix[gpu_node_map[node]][gpu_func_map[func]] = response_time
            pass
        else:
            workload_on_destination_matrix[func_map[func]][node_map[node]] = response_time

    for from_node, to_node, latency in zip(dl_df['f'], dl_df['t'], dl_df['l']):
        if from_node in node_map and to_node in node_map:
            node_delay_matrix[node_map[from_node]][node_map[to_node]] = latency
        if from_node in node_map and to_node in gpu_node_map:
            gpu_node_delay_matrix[gpu_node_map[from_node]][gpu_node_map[to_node]] = latency
    '''
   
    for function_key, x in actual_cpu_allocations.items():
        for node, ok in x.items():
            if x:
                func = function_key.split("/")[1]
                old_cpu_allocations[func_map[func]][node_map[node]] = ok

    core_per_req_matrix = np.nan_to_num(cores_matrix / workload_on_destination_matrix, nan=0)

    old_cpu_allocations = np.array(old_cpu_allocations, dtype=bool).astype(int)
    if old_cpu_allocations.sum() == 0:
        old_cpu_allocations = old_cpu_allocations + 1

    print("CPU allocations:")
    print(old_cpu_allocations)

    old_gpu_allocations = np.array(old_gpu_allocations, dtype=bool).astype(int)
    if old_gpu_allocations.sum() == 0:
        old_gpu_allocations = old_gpu_allocations + 1

    print("GPU allocations:")
    print(old_gpu_allocations)

    # Pre solving
    cpu_data = su.Data(nodes, nodes, functions)
    cpu_data.node_memory_matrix = np.array(node_memories)
    cpu_data.function_memory_matrix = np.array(function_memories)
    cpu_data.node_delay_matrix = np.array(node_delay_matrix)
    cpu_data.workload_matrix = np.array(workload_on_source_matrix) * cpu_coeff
    cpu_data.max_delay_matrix = np.array(max_delay_matrix)
    cpu_data.response_time_matrix = np.array(response_time_matrix)
    cpu_data.node_cores_matrix = np.array(node_cores)
    cpu_data.cores_matrix = np.array(cores_matrix)
    cpu_data.old_allocations_matrix = np.array(old_cpu_allocations)
    cpu_data.core_per_req_matrix = np.array(core_per_req_matrix)

    cpu_presolver = neptune_step1.NeptuneStep1CPU(verbose=False)
    cpu_presolver.load_input(cpu_data)
    cpu_presolver.solve()
    cpu_presolver_x, cpu_presolver_c = cpu_presolver.results()

    print("CPU presolver routing rules")
    print(cpu_presolver_x)
    print("CPU presolver allocations")
    print(cpu_presolver_c)

    cpu_presolver_score = cpu_presolver.score()
    print("CPU presolver score")
    print(cpu_presolver_score)

    # The solving
    cpu_data = su.Data(nodes, nodes, functions)
    cpu_data.node_memory_matrix = np.array(node_memories)
    cpu_data.function_memory_matrix = np.array(function_memories)
    cpu_data.node_delay_matrix = np.array(node_delay_matrix)
    cpu_data.workload_matrix = np.array(workload_on_source_matrix) * cpu_coeff
    cpu_data.max_delay_matrix = np.array(max_delay_matrix)
    cpu_data.response_time_matrix = np.array(response_time_matrix)
    cpu_data.node_cores_matrix = np.array(node_cores)
    cpu_data.cores_matrix = np.array(cores_matrix)
    cpu_data.old_allocations_matrix = np.array(old_cpu_allocations)
    # cpu_data.old_allocations_matrix = np.array(cpu_presolver_c)
    cpu_data.core_per_req_matrix = np.array(core_per_req_matrix)
    cpu_data.max_score = cpu_presolver_score

    cpu_thesolver = neptune_step2.NeptuneStep2(verbose=False)
    print(cpu_data.old_allocations_matrix)
    cpu_thesolver.load_input(cpu_data)
    solved = cpu_thesolver.solve()
    if solved:
        cpu_thesolver_x, cpu_thesolver_c = cpu_thesolver.results()

        print("CPU thesolver routing rules")
        print(cpu_thesolver_x)
        print("CPU thesolver allocations")
        print(cpu_thesolver_c)

        cpu_thesolver_score = cpu_thesolver.score()
        print("CPU thesolver score")
        print(cpu_thesolver_score)

        return convert_x_matrix(cpu_thesolver_x, nodes, functions, nodes), convert_c_matrix(cpu_thesolver_c, functions, nodes)

    # The solving - part 2
    print("STARTING SOLVING PART 2")
    cpu_data = su.Data(nodes, nodes, functions)
    cpu_data.node_memory_matrix = np.array(node_memories)
    cpu_data.function_memory_matrix = np.array(function_memories)
    cpu_data.node_delay_matrix = np.array(node_delay_matrix)
    cpu_data.workload_matrix = np.array(workload_on_source_matrix) * cpu_coeff
    cpu_data.max_delay_matrix = np.array(max_delay_matrix)
    cpu_data.response_time_matrix = np.array(response_time_matrix)
    cpu_data.node_cores_matrix = np.array(node_cores)
    cpu_data.cores_matrix = np.array(cores_matrix)
    cpu_data.old_allocations_matrix = np.array(cpu_presolver_c)
    cpu_data.core_per_req_matrix = np.array(core_per_req_matrix)
    cpu_data.max_score = cpu_presolver_score

    cpu_thesolver = neptune_step2.NeptuneStep2(verbose=False)
    print(cpu_data.old_allocations_matrix)
    cpu_thesolver.load_input(cpu_data)
    solved = cpu_thesolver.solve()
    if solved:
        cpu_thesolver_x, cpu_thesolver_c = cpu_thesolver.results()

        print("CPU thesolver routing rules")
        print(cpu_thesolver_x)
        print("CPU thesolver allocations")
        print(cpu_thesolver_c)

        cpu_thesolver_score = cpu_thesolver.score()
        print("CPU thesolver score")
        print(cpu_thesolver_score)

        return convert_x_matrix(cpu_thesolver_x, nodes, functions, nodes), convert_c_matrix(cpu_thesolver_c, functions, nodes)
    else:
        return convert_x_matrix(cpu_presolver_x, nodes, functions, nodes), convert_c_matrix(cpu_presolver_c, functions, nodes)