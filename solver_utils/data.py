import numpy as np
from typing import List

class Data:
    sources: List[str] = []
    nodes: List[str] = []
    functions: List[str] = []

    node_memory_matrix: np.array = np.array([])
    function_memory_matrix: np.array = np.array([])
    node_delay_matrix: np.array = np.array([])
    workload_matrix: np.array = np.array([])
    max_delay_matrix: np.array = np.array([])
    response_time_matrix: np.array = np.array([])
    node_cores_matrix: np.array = np.array([])
    cores_matrix: np.array = np.array([])
    old_allocations_matrix: np.array = np.array([])
    core_per_req_matrix: np.array = np.array([])

    gpu_function_memory_matrix: np.array = np.array([])
    gpu_node_memory_matrix: np.array = np.array([])

    prev_x = np.array([])

    def __init__(self, sources: List[str], nodes: List[str], functions: List[str]):
        self.sources = sources
        self.nodes = nodes
        self.functions = functions