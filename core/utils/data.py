import numpy as np
from typing import List


class Data:

    def __init__(self, nodes: List[str] = None, functions: List[str] = None, tables: List[str] = None):
        """
        Initialize the Data object with optional lists of sources, nodes, and functions.
        If not provided, these attributes are initialized as empty lists.

        Parameters:
        - nodes (List[str]): List of node identifiers.
        - functions (List[str]): List of function identifiers.
        - tables (List[str]): List of tables identifiers.

        """

        # Initialize sources, nodes, and functions with provided values or empty lists
        # Sets

        self.nodes = nodes if nodes else []
        self.functions = functions if functions else []
        self.tables = tables if tables else []

        # Initialize matrices as empty numpy arrays

        # Inputs
        self.max_delay_matrix: np.array = np.array([])  # phi_f
        self.function_memory_matrix: np.array = np.array([])  # m_f_CPU
        self.gpu_function_memory_matrix: np.array = np.array([])  # m_f_GPU
        self.v_old_matrix: np.array = np.array([])  # v_old_j_t
        self.tables_sizes: np.array = np.array([])  # s_t

        # Infrastructure data

        self.node_memory_matrix: np.array = np.array([])  # M_j_CPU
        self.gpu_node_memory_matrix: np.array = np.array([])  # M_j_GPU
        self.node_cores_matrix: np.array = np.array([])  # U_j_CPU/GPU
        self.node_storage_matrix: np.array = np.array([])  # S_j

        # Monitored data
        self.node_delay_matrix: np.array = np.array([])  # delta_i,j
        self.workload_matrix: np.array = np.array([])  # lambda_f,i
        self.core_per_req_matrix: np.array = np.array([])  # u_j,f_CPU/GPU
        self.read_per_req_matrix: np.array = np.array([])  # beta_f_t
        self.write_per_req_matrix: np.array = np.array([])  # gamma_f_t
        self.r_ft_matrix: np.array = np.array([])   # r_ft
        self.max_delay = 0  # delta_max

        # Decision variables old
        self.prev_x = np.array([])  # x_f,i,j_CPU/GPU(old)
        self.prev_c = np.array([])  # c_f,i_CPU/GPU(old)
        self.old_allocations_matrix: np.array = np.array([])  # TODO Remove

        # Not part of optimization

        self.cores_matrix: np.array = np.array([])  # TODO
        self.response_time_matrix: np.array = np.array([])  # TODO

        self.node_costs: np.array = np.array([])  # TODO
        self.node_budget: int = 0  # TODO

        def update_node_delay_matrix(self, new_matrix: np.array):
            """
            Update the node delay matrix and recalculate the maximum delay.
            """
            self.node_delay_matrix = new_matrix
            if self.node_delay_matrix.size > 0:
                self.max_delay = np.max(self.node_delay_matrix)
            else:
                self.max_delay = 0  # Default value when the matrix is empty
