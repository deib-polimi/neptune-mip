from hurry.filesize import size

keys = [
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
    "actual_gpu_allocations"
]


def check_input(schedule_input):
    print(f"Checking scheduling input...")

    print(f"Checking that it contains all the required keys")
    for key in keys:
        assert key in schedule_input.keys(), f"Key `{key}` not in schedule input"

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

    print("Everything seems consistent")