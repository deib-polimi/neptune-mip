import numpy as np
from typing import List


class Data:

    def __init__(self, nodes: List[str] = None, functions: List[str] = None):
        self.nodes = nodes if nodes else []
        self.functions = functions if functions else []
        self.node_memory_matrix: np.array = np.array([])
        self.function_memory_matrix: np.array = np.array([])
        self.node_delay_matrix: np.array = np.array([])
        self.workload_matrix: np.array = np.array([])
        self.max_delay_matrix: np.array = np.array([])
        self.response_time_matrix: np.array = np.array([])
        self.node_cores_matrix: np.array = np.array([])
        self.cores_matrix: np.array = np.array([])
        self.old_allocations_matrix: np.array = np.array([])
        self.core_per_req_matrix: np.array = np.array([])

        self.gpu_function_memory_matrix: np.array = np.array([])
        self.gpu_node_memory_matrix: np.array = np.array([])
        self.prev_x = np.array([])

        self.node_costs: np.array = np.array([])
        self.node_budget: int = 0
