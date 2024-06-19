import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from .data import Data
from hurry.filesize import size

np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

keys = [
    # "solver",
    "community",
    "namespace",
    "function_names",
    "function_memories",
    "gpu_function_names",
    "gpu_function_memories",
    "node_names",
    "node_memories",
    "node_cores",
    "gpu_node_names",
    "gpu_node_memories",
    "function_max_delays",
    "actual_cpu_allocations",
    "actual_gpu_allocations",
    "node_storage"
]

solvers = ["NeptuneMinDelayAndUtilization", "NeptuneMinDelay", "NeptuneMinUtilization", "VSVBP", "Criticality",
           "CriticalityHeuristic", "MCF"]


def check_input(schedule_input):
    """
    Checks the validity of the scheduling input.
    Ensures all required keys are present and data is consistent.

    Parameters:
    - schedule_input (dict): The input dictionary to check.

    Raises:
    - AssertionError: If any required key is missing or data is inconsistent.
    """
    print(f"Checking scheduling input...")

    print(f"Checking that it contains all the required keys")
    for key in keys:
        assert key in schedule_input.keys(), f"Key `{key}` not in schedule input"

    # assert "type" in schedule_input["solver"]
    # assert schedule_input["solver"]["type"] in solvers

    functions = schedule_input.get('function_names', [])
    function_memories = schedule_input.get('function_memories', [])
    gpu_functions = schedule_input.get('gpu_function_names', [])
    gpu_function_memories = schedule_input.get('gpu_function_memories', [])
    print(f"Functions are: {functions}")
    print(f"GPU Functions are: {gpu_functions}")
    print(f"Function memories are: {[size(m) for m in function_memories]}")
    print(f"GPU Function memories are: {[size(m) for m in gpu_function_memories]}")

    print(f"Checking Function consistencies...")
    assert set(gpu_functions).issubset(set(functions))
    assert len(functions) == len(function_memories)
    assert len(gpu_functions) == len(gpu_function_memories)

    nodes = schedule_input.get('node_names', [])
    node_memories = schedule_input.get('node_memories', [])
    node_cores = schedule_input.get('node_cores', [])
    gpu_nodes = schedule_input.get('gpu_node_names', [])
    gpu_node_memories = schedule_input.get('gpu_node_memories', [])

    print(f"Nodes are: {nodes}")
    print(f"Nodes memories are: {[size(m) for m in node_memories]}")
    print(f"Nodes cores are: {node_cores}")
    print(f"GPU Nodes are: {gpu_nodes}")
    print(f"GPU Nodes memories are: {[size(m) for m in gpu_node_memories]}")

    print(f"Checking Nodes consistencies...")
    assert set(gpu_nodes).issubset(set(nodes))
    assert len(nodes) == len(node_memories)
    assert len(gpu_nodes) == len(gpu_node_memories)

    # Data related part

    tables = schedule_input.get('tables_names', [])
    tables_sizes = schedule_input.get('tables_sizes', [])

    print(f"Tables are: {tables}")
    print(f"Tables sizes are: {tables_sizes}")

    node_storage = schedule_input.get('node_storage', [])
    print(f"Nodes storage capacities are: {[size(m) for m in node_storage]}")

    print(f"Checking tables consistencies...")

    # Assuming that, if node's storage is 0, it has to be explicitly set
    # TODO: set capacity to 0 if not provided automatically
    # TODO: test also that a table that was previously declared is present somewhere

    assert len(node_storage) == len(nodes)
    assert len(tables) == len(tables_sizes)

    print("Everything seems consistent")


def data_to_solver_input(input, workload_coeff, with_db=True):
    aux_data = Data()

    setup_community_data(input, aux_data)

    setup_runtime_data(aux_data, input)

    create_mappings(aux_data)

    # Update data from database if specified
    if with_db:
        update_data_from_db(aux_data)

    # update_old_allocations(aux_data)

    data = Data(aux_data.nodes, aux_data.functions, aux_data.tables)
    data.node_memory_matrix = np.array(aux_data.node_memories)
    data.function_memory_matrix = np.array(aux_data.function_memories)
    data.node_delay_matrix = np.array(aux_data.node_delay_matrix)
    data.max_delay = np.max(data.node_delay_matrix)
    data.workload_matrix = np.array(aux_data.workload_on_source_matrix) * workload_coeff
    data.max_delay_matrix = np.array(aux_data.max_delay_matrix)
    data.response_time_matrix = np.array(aux_data.response_time_matrix)
    data.node_cores_matrix = np.array(aux_data.node_cores)
    data.cores_matrix = np.array(aux_data.cores_matrix)
    data.old_allocations_matrix = np.array(aux_data.old_cpu_allocations)
    data.core_per_req_matrix = np.array(aux_data.core_per_req_matrix)

    # Setup budget data
    setup_budget_data(data)

    # Data related part

    data.node_storage_matrix = np.array(aux_data.node_storage_matrix)
    data.v_old_matrix = np.array(aux_data.v_old_matrix)
    data.tables_sizes = np.array(aux_data.tables_sizes)
    data.read_per_req_matrix = np.array(aux_data.read_per_req_matrix)
    data.write_per_req_matrix = np.array(aux_data.write_per_req_matrix)
    data.v_old_matrix = np.array(aux_data.v_old_matrix)

    return data


def setup_community_data(input, data):
    """
    Sets up community-related data in the Data object.

    Parameters:
    - input (dict): TODO
    - data (Data): The data object to set up.
    """

    data.community = input.get('community')
    data.namespace = input.get('namespace')
    data.functions = input.get('function_names', [])
    data.gpu_functions = input.get('gpu_function_names', [])
    data.gpu_functions_set = set(data.gpu_functions)
    data.gpu_functions_mask = np.array([f in data.gpu_functions_set for f in data.functions])
    data.nodes = input.get('node_names', [])
    data.gpu_nodes = input.get('gpu_node_names', [])
    data.gpu_nodes_set = set(data.gpu_nodes)
    data.gpu_nodes_mask = np.array([n in data.gpu_nodes_set for n in data.nodes])

    # TODO: maybe is better to do these checks in check_input for

    assert set(data.gpu_functions).issubset(set(data.functions))
    assert set(data.gpu_nodes).issubset(set(data.nodes))

    data.function_memories = input.get('function_memories')
    data.node_memories = input.get('node_memories')
    data.gpu_node_memories = input.get('gpu_node_memories')
    data.actual_cpu_allocations = input.get('actual_cpu_allocations')
    data.actual_gpu_allocations = input.get('actual_gpu_allocations')
    data.node_cores = input.get('node_cores')
    data.gpu_function_memories = input.get('gpu_function_memories')
    data.max_delay_matrix = [1000 for _ in range(len(data.function_memories))]

    # New parameter for node storage
    data.node_storage_matrix = np.array(input.get('node_storage', []))

    # New parameter for tables
    data.tables = input.get('tables_names', [])
    data.tables_names = input.get('tables_names', [])
    data.tables_sizes = input.get('tables_sizes', [])


def setup_runtime_data(data, input):
    """
    Sets up runtime-related data in the Data object.

    Parameters:
    - data (Data): The data object to set up.
    - input (dict): TODO
    """
    # Retrieve 'node_delay_matrix' from input, defaulting to None if not present
    node_delay_matrix = input.get('node_delay_matrix', None)

    # If 'node_delay_matrix' is provided in the input, use it
    # If 'node_delay_matrix' is not provided, create a default matrix
    # Delay between different nodes is set to 1, and delay from a node to itself is set to 0
    if node_delay_matrix:
        data.node_delay_matrix = node_delay_matrix
    else:
        data.node_delay_matrix = [[1 if s != d else 0 for s in data.nodes] for d in data.nodes]

    # Create a GPU node delay matrix with default values
    # Delay between different GPU nodes is set to 1, and delay from a node to itself is set to 0
    data.gpu_node_delay_matrix = [[1 if s != d else 0 for s in data.nodes] for d in data.gpu_nodes]

    # Attempt to retrieve 'workload_on_source_matrix' from the input dictionary
    workload_on_source_matrix = input.get('workload_on_source_matrix', None)

    # If 'workload_on_source_matrix' is provided in the input, convert it to a NumPy array and assign it
    # If 'workload_on_source_matrix' is not provided, create a default matrix with zeros
    # The matrix has a number of rows equal to the number of functions and a number of columns equal to the number of nodes

    if workload_on_source_matrix:
        data.workload_on_source_matrix = np.array(workload_on_source_matrix)
    else:
        data.workload_on_source_matrix = np.array([[0 for _ in data.nodes] for _ in data.functions])

    # Attempt to retrieve 'workload_on_destination_matrix' from the input dictionary
    workload_on_destination_matrix = input.get('workload_on_destination_matrix', None)

    # If 'workload_on_destination_matrix' is provided in the input, convert it to a NumPy array and assign it
    # If 'workload_on_destination_matrix' is not provided, create a default matrix with zeros
    # The matrix has a number of rows equal to the number of functions and a number of columns equal to the number of nodes

    if workload_on_destination_matrix:
        data.workload_on_destination_matrix = np.array(workload_on_destination_matrix)
    else:
        data.workload_on_destination_matrix = np.array([[0 for _ in data.nodes] for _ in data.functions])

    # Initialize GPU workload on destination matrix with zeros
    # Rows: GPU functions, Columns: GPU nodes
    data.gpu_workload_on_destination_matrix = np.array([[0 for _ in data.gpu_nodes] for _ in data.gpu_functions])

    # Retrieve or initialize cores matrix
    cores_matrix = input.get('cores_matrix', None)

    # If cores_matrix is not provided, create a default matrix with zeros
    # Rows: Functions, Columns: Nodes

    if cores_matrix:
        data.cores_matrix = cores_matrix
    else:
        data.cores_matrix = np.array([[0 for _ in data.nodes] for _ in data.functions])

    # Initialize response time matrix with zeros
    # Rows: Functions, Columns: Nodes
    data.response_time_matrix = [[0 for _ in data.nodes] for _ in data.functions]

    # Initialize GPU response time matrix with ones
    # Rows: GPU functions, Columns: GPU nodes
    data.gpu_response_time_matrix = [[1 for _ in data.gpu_nodes] for _ in data.gpu_functions]

    # Initialize old CPU allocations matrix with zeros
    # Rows: Functions, Columns: Nodes
    data.old_cpu_allocations = np.array([[0 for _ in data.nodes] for _ in data.functions])

    # Initialize old GPU allocations matrix with zeros
    # Rows: GPU functions, Columns: GPU nodes
    data.old_gpu_allocations = np.array([[0 for _ in data.gpu_nodes] for _ in data.gpu_functions])

    # Initialize core per request matrix with ones
    # Rows: Functions, Columns: Nodes
    # u_f_j

    core_per_req_matrix = input.get('core_per_req_matrix', None)
    if core_per_req_matrix:
        data.core_per_req_matrix = core_per_req_matrix
    else:
        data.core_per_req_matrix = np.array([[1 for _ in data.nodes] for _ in data.functions])

    # Data related part

    # Retrieve 'v_old_matrix' from input, defaulting to None if not present
    v_old_matrix = input.get('v_old_matrix', None)

    # If 'v_old_matrix' is provided in the input, use it
    # If 'v_old_matrix' is not provided, create a default matrix
    if v_old_matrix:
        data.v_old_matrix = v_old_matrix
    else:
        data.v_old_matrix = [[1 for _ in data.tables] for _ in data.nodes]

    # Retrieve 'read_per_req_matrix' from input, defaulting to None if not present
    read_per_req_matrix = input.get('read_per_req_matrix', None)

    # If 'read_per_req_matrix' is provided in the input, use it
    # If 'read_per_req_matrix' is not provided, create a default matrix
    if read_per_req_matrix:
        data.read_per_req_matrix = read_per_req_matrix
    else:
        data.read_per_req_matrix = [[0 for _ in data.functions] for _ in data.tables]

    # Retrieve 'write_per_req_matrix' from input, defaulting to None if not present
    write_per_req_matrix = input.get('write_per_req_matrix', None)

    # If 'write_per_req_matrix' is provided in the input, use it
    # If 'write_per_req_matrix' is not provided, create a default matrix
    if write_per_req_matrix:
        data.write_per_req_matrix = write_per_req_matrix
    else:
        data.write_per_req_matrix = [[0 for _ in data.functions] for _ in data.tables]


def setup_budget_data(data):
    data.node_costs = np.array([5 for _ in data.nodes])
    data.node_budget = 30


def create_mappings(data):
    data.node_map = {}
    data.func_map = {}
    data.gpu_node_map = {}
    data.gpu_func_map = {}

    for i, node in enumerate(data.nodes):
        data.node_map[node] = i
    for i, node in enumerate(data.gpu_nodes):
        data.gpu_node_map[node] = i
    for i, func in enumerate(data.functions):
        func = func.split("/")[1]
        data.func_map[func] = i
    for i, func in enumerate(data.gpu_functions):
        func = func.split("/")[1]
        data.gpu_func_map[func] = i

    # Data related part
    data.table_map = {}
    for t, table in enumerate(data.tables):
        data.table_map[table] = t


def update_data_from_db(data):
    username = "user"
    password = "password"
    database_host = "metrics-database.kube-system.svc.cluster.local"
    database_port = 5432
    postgres_str = f"postgresql://{username}:{password}@{database_host}:{database_port}"
    interval = "'30 seconds'"

    # Create a connection to the database
    cnx = create_engine(postgres_str)

    # Define SQL queries
    ar_query = f"""
       SELECT function, source, count(*) AS arrival_rate
       FROM metric
       WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{data.namespace}' AND community = '{data.community}'
       GROUP BY function, source
       """

    ard_query = f"""
       SELECT function, destination, gpu, count(*) AS arrival_rate
       FROM metric
       WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{data.namespace}' AND community = '{data.community}'
       GROUP BY function, destination, gpu
       """

    rt_query = f"""
       SELECT function, destination, gpu, avg(latency) AS response_time
       FROM metric
       WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{data.namespace}' AND community = '{data.community}'
       GROUP BY function, destination, gpu
       """

    dl_query = """
       SELECT f, t, l
       FROM (
           SELECT from_node, to_node
           FROM ping
           GROUP BY from_node, to_node
       ) AS p1
       INNER JOIN LATERAL (
           SELECT from_node AS f, to_node AS t, avg_latency AS l
           FROM ping p2
           WHERE p1.from_node = p2.from_node AND p1.to_node = p2.to_node
           ORDER BY timestamp DESC
           LIMIT 1
       ) AS data ON TRUE
       """

    cpu_query = f"""
       SELECT function, node, avg(cores) AS cores
       FROM resource
       WHERE timestamp > now() - INTERVAL {interval} AND namespace = '{data.namespace}' AND community = '{data.community}'
       GROUP BY function, node
       """

    # Execute SQL queries and store results in DataFrames
    ar_df = pd.read_sql(ar_query, cnx)
    ard_df = pd.read_sql(ard_query, cnx)
    rt_df = pd.read_sql(rt_query, cnx)
    dl_df = pd.read_sql(dl_query, cnx)
    cpu_df = pd.read_sql(cpu_query, cnx)

    print(f"ARRIVAL RATE SOURCE \n\n {ar_df}")
    print(f"ARRIVAL RATE DESTINATION \n\n {ard_df}")
    print(f"RESPONSE TIME \n\n {rt_df}")
    print(f"DELAYS \n\n {dl_df}")
    print(f"CPU CONSUMPTION \n\n {cpu_df}")

    for node, func, response_time, gpu in zip(rt_df['destination'], rt_df['function'], rt_df['response_time'],
                                              rt_df['gpu']):
        if gpu:
            data.gpu_response_time_matrix[data.gpu_func_map[func]][data.gpu_node_map[node]] = response_time
            pass
        else:
            data.response_time_matrix[data.func_map[func]][data.node_map[node]] = response_time

    for node, func, arrival_rate in zip(ar_df['source'], ar_df['function'], ar_df['arrival_rate']):
        data.workload_on_source_matrix[data.func_map[func]][data.node_map[node]] = arrival_rate

    for node, func, cores in zip(cpu_df['node'], cpu_df['function'], cpu_df['cores']):
        data.cores_matrix[data.func_map[func]][data.node_map[node]] = cores

    for node, func, response_time, gpu in zip(ard_df['destination'], ard_df['function'], ard_df['arrival_rate'],
                                              ard_df['gpu']):
        if gpu:
            data.gpu_workload_on_destination_matrix[data.gpu_node_map[node]][data.gpu_func_map[func]] = response_time
            pass
        else:
            data.workload_on_destination_matrix[data.func_map[func]][data.node_map[node]] = response_time

    for from_node, to_node, latency in zip(dl_df['f'], dl_df['t'], dl_df['l']):
        if from_node in data.node_map and to_node in data.node_map:
            data.node_delay_matrix[data.node_map[from_node]][data.node_map[to_node]] = latency
        if from_node in data.node_map and to_node in data.gpu_node_map:
            data.gpu_node_delay_matrix[data.gpu_node_map[from_node]][data.gpu_node_map[to_node]] = latency


def update_old_allocations(data):
    for function_key, x in data.actual_cpu_allocations.items():
        for node, ok in x.items():
            if x:
                func = function_key.split("/")[1]
                data.old_cpu_allocations[data.func_map[func]][data.node_map[node]] = ok

    data.core_per_req_matrix = np.nan_to_num(data.cores_matrix / data.workload_on_destination_matrix, nan=0)

    data.old_cpu_allocations = np.array(data.old_cpu_allocations, dtype=bool).astype(int)
    if data.old_cpu_allocations.sum() == 0:
        data.old_cpu_allocations = data.old_cpu_allocations + 1

    print("CPU allocations:")
    print(data.old_cpu_allocations)

    data.old_gpu_allocations = np.array(data.old_gpu_allocations, dtype=bool).astype(int)
    if data.old_gpu_allocations.sum() == 0:
        data.old_gpu_allocations = data.old_gpu_allocations + 1

    print("GPU allocations:")
    print(data.old_gpu_allocations)
