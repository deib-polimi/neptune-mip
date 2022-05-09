import datetime
import itertools
from typing import List, Tuple

import numpy as np
from ortools.linear_solver import pywraplp


class Data():
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


class Input:
    nodes: List[str] = []
    functions: List[str] = []

    node_memory_matrix: np.array = np.array([])
    function_memory_matrix: np.array = np.array([])
    node_delay_matrix: np.array = np.array([])
    workload_matrix: np.array = np.array([])
    max_delay_matrix: np.array = np.array([])
    response_time_matrix: np.array = np.array([])
    node_memory: np.array = np.array([])
    function_memory: np.array = np.array([])
    node_cores: np.array = np.array([])
    cores_matrix: np.array = np.array([])

    cpu_nodes: List[str] = []
    cpu_functions: List[str] = []

    cpu_node_memory_matrix: np.array = np.array([])
    cpu_function_memory_matrix: np.array = np.array([])
    cpu_node_delay_matrix: np.array = np.array([])
    cpu_workload_matrix: np.array = np.array([])
    cpu_max_delay_matrix: np.array = np.array([])
    cpu_response_time_matrix: np.array = np.array([])
    cpu_node_memory: np.array = np.array([])
    cpu_function_memory: np.array = np.array([])

    cpu_node_cores: np.array = np.array([])
    cpu_cores_matrix: np.array = np.array([])
    cpu_actual_allocation: np.array = np.array([])
    cpu_core_per_req: np.array = np.array([])

    x_cpu = np.array([])
    c_cpu = np.array([])

    gpu_nodes: List[str] = []
    gpu_functions: List[str] = []

    gpu_node_memory_matrix: np.array = np.array([])
    gpu_function_memory_matrix: np.array = np.array([])
    gpu_node_delay_matrix: np.array = np.array([])
    gpu_workload_matrix: np.array = np.array([])
    gpu_max_delay_matrix: np.array = np.array([])
    gpu_response_time_matrix: np.array = np.array([])
    gpu_node_memory: np.array = np.array([])
    gpu_function_memory: np.array = np.array([])

    x_gpu = np.array([])
    c_gpu = np.array([])

    cpu_function_gpu_map = {}

    def __init__(self,
                 cpu_nodes: List[str], cpu_functions: List[str],
                 gpu_nodes: List[str], gpu_functions: List[str]):
        # Initialize attributes
        self.cpu_nodes = cpu_nodes
        self.cpu_functions = cpu_functions
        self.gpu_nodes = gpu_nodes
        self.gpu_functions = gpu_functions
        self.functions = cpu_functions + gpu_functions
        self.nodes = cpu_nodes + gpu_nodes
        for i, cpu_f in enumerate(cpu_functions):
            cpu_function = cpu_f[:4]
            for j, gpu_f in enumerate(gpu_functions):
                gpu_function = gpu_f[:4]
                if cpu_function == gpu_function:
                    self.cpu_function_gpu_map[i] = j
                    break

    def load_node_memory_matrix(self, matrix: List[int]):
        self.node_memory_matrix = np.array(matrix, dtype=int)
        self.cpu_node_memory_matrix = self.node_memory_matrix[:len(self.cpu_nodes)]
        self.gpu_node_memory_matrix = self.node_memory_matrix[len(self.cpu_nodes):]

        # Check input correctness
        assert len(self.node_memory_matrix) == len(self.nodes), \
            f"Actual {len(self.node_memory_matrix.shape)}, Expected {len(self.nodes)}"

    def load_function_memory_matrix(self, matrix: List[int]):
        self.function_memory_matrix = np.array(matrix, dtype=int)
        self.cpu_function_memory_matrix = self.function_memory_matrix[:len(self.cpu_functions)]
        self.gpu_function_memory_matrix = self.function_memory_matrix[len(self.cpu_functions):]

        # Check input correctness
        assert len(self.function_memory_matrix) == len(self.functions), \
            f"Actual {len(self.function_memory_matrix)}, Expected {len(self.functions)}"

    def load_node_delay_matrix(self, matrix: List[List[int]]):
        self.node_delay_matrix = np.matrix(matrix, dtype=int)
        self.cpu_node_delay_matrix = self.node_delay_matrix[:, :len(self.cpu_nodes)]
        self.gpu_node_delay_matrix = self.node_delay_matrix[:, len(self.cpu_nodes):]

        # Check input correctness
        assert self.node_delay_matrix.shape == (len(self.nodes), len(self.nodes)), \
            f"Actual {self.node_delay_matrix.shape}, Expected {(len(self.nodes), len(self.nodes))}"

    def load_workload_matrix(self, matrix: List[List[int]]):
        self.workload_matrix = np.matrix(matrix, dtype=int)
        self.cpu_workload_matrix = self.workload_matrix[:, :len(self.cpu_functions)]
        self.gpu_workload_matrix = self.workload_matrix[:, len(self.cpu_functions):]

        # Check input correctness
        assert self.workload_matrix.shape == (len(self.nodes), len(self.functions)), \
            f"Actual {self.workload_matrix.shape}, Expected {(len(self.nodes), len(self.functions))}"

    def load_max_delay_matrix(self, matrix: List[int]):
        self.max_delay_matrix = np.array(matrix, dtype=int)
        self.cpu_max_delay_matrix = self.max_delay_matrix[:len(self.cpu_functions)]
        self.gpu_max_delay_matrix = self.max_delay_matrix[len(self.cpu_functions):]

        # Check input correctness
        assert len(self.max_delay_matrix) == len(self.functions), \
            f"Actual {len(self.max_delay_matrix)}, Expected {len(self.functions)}"

    def load_response_time_matrix(self, matrix: List[List[int]]):
        self.response_time_matrix = np.matrix(matrix, dtype=int)
        self.cpu_response_time_matrix = self.response_time_matrix[:len(self.cpu_nodes), :len(self.cpu_functions)]
        self.gpu_response_time_matrix = self.response_time_matrix[len(self.cpu_nodes):, len(self.cpu_functions):]

        # Check input correctness
        assert self.response_time_matrix.shape == (len(self.nodes), len(self.functions)), \
            f"Actual {self.response_time_matrix.shape}, Expected {(len(self.nodes), len(self.functions))}"


class Solver:
    solver = pywraplp.Solver.CreateSolver('SCIP')
    objective = solver.Objective()
    x = {}
    c = {}
    # moved_from = {}
    # moved_to = {}
    data: Data = None

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        if verbose:
            self.solver.EnableOutput()
        pass

    def load_input(self, data: Data):
        self.data = data

        # Initialize variable
        self.log("Initializing variables...")
        for f in range(len(data.functions)):
            for i in range(len(data.sources)):
                for j in range(len(data.nodes)):
                    self.x[i, f, j] = self.solver.NumVar(0, self.solver.infinity(), f"x[{i}][{f}][{j}]")
        for f in range(len(data.functions)):
            for i in range(len(data.nodes)):
                self.c[f, i] = self.solver.BoolVar(f"c[{f}][{i}]")
        # for f in range(len(data.functions)):
        #     for i in range(len(data.nodes)):
        #         self.moved_from[f, i] = self.solver.BoolVar(f"moved_from[{f}][{i}]")
        #         self.moved_to[f, i] = self.solver.BoolVar(f"moved_to[{f}][{i}]")

        # Initialize constraints
        self.log("Initializing constraints...")
        # If a function `f` is deployed on node `n` then c[f,n] is True
        for f in range(len(data.functions)):
            for j in range(len(data.nodes)):
                self.solver.Add(
                    self.solver.Sum([
                        self.x[i, f, j] for i in range(len(data.sources))
                    ]) <= self.c[f, j] * 1000)

        # The sum of the memory of functions deployed on a node `n` is less than its capacity
        for j in range(len(data.nodes)):
            self.solver.Add(
                self.solver.Sum([
                    self.c[f, j] * self.data.function_memory_matrix[f] for f in range(len(data.functions))
                ]) <= data.node_memory_matrix[j])

        # All requests in a node are rerouted somewhere else
        if data.prev_x.shape == (0,):
            for f in range(len(data.functions)):
                for i in range(len(data.sources)):
                    self.solver.Add(
                        self.solver.Sum([
                            self.x[i, f, j] for j in range(len(data.nodes))
                        ]) == 1)
        # If GPUs are set, consider the traffic forwarded to gpu
        else:
            for f in range(len(data.functions)):
                for i in range(len(data.sources)):
                    self.solver.Add(
                        self.solver.Sum([
                            self.x[i, f, j] for j in range(len(data.nodes))
                        ]) == 1 - data.prev_x[i][f].sum())

        # Consider the amount of cores available on a node
        # Do not overload a node
        for j in range(len(data.nodes)):
            self.solver.Add(
                self.solver.Sum([
                    self.x[i, f, j] * self.data.workload_matrix[f, i] * self.data.core_per_req_matrix[f,j] for f in range(len(data.functions)) for i in
                    range(len(data.sources))
                ]) <= self.data.node_cores_matrix[j]
            )

        # # If any function has been moved from a node
        # for f in range(len(self.data.functions)):
        #     for j in range(len(self.data.nodes)):
        #         self.solver.Add(self.moved_from[f, j] >= 0)
        #         self.solver.Add(self.moved_from[f, j] >= self.c[f, j] - self.data.old_allocations_matrix[f, j])
        #
        # # If any function has been moved to a node
        # for f in range(len(self.data.functions)):
        #     for j in range(len(self.data.nodes)):
        #         self.solver.Add(self.moved_to[f, j] >= 0)
        #         self.solver.Add(self.moved_to[f, j] >= self.data.old_allocations_matrix[f, j] - self.c[f, j])

    def log(self, msg: str):
        if self.verbose:
            print(f"{datetime.datetime.now()}: {msg}")

    def solve(self):
        # Starting to solve
        self.log("Starting solving problem...")

        # for f in range(len(self.data.functions)):
        #     for j in range(len(self.data.nodes)):
        #         self.objective.SetCoefficient(self.moved_from[f, j], 100000)
        #         self.objective.SetCoefficient(self.moved_to[f, j], 100000)

        # Objective function
        for f in range(len(self.data.functions)):
            for i in range(len(self.data.sources)):
                for j in range(len(self.data.nodes)):
                    self.objective.SetCoefficient(
                        self.x[i, f, j], float(self.data.node_delay_matrix[i, j] * self.data.workload_matrix[f, i])
                    )
        self.objective.SetMinimization()

        # Solve problem
        status = self.solver.Solve()
        self.log(f"Problem solved with status {status}")

    def results(self) -> Tuple[np.array, np.array]:
        # Fill x matrix
        x_matrix = np.empty(shape=(len(self.data.sources), len(self.data.functions), len(self.data.nodes)))
        for j in range(len(self.data.nodes)):
            for i in range(len(self.data.sources)):
                for f in range(len(self.data.functions)):
                    x_matrix[i][f][j] = self.x[i, f, j].solution_value()
        # Fill c matrix
        c_matrix = np.empty(shape=(len(self.data.functions), len(self.data.nodes)))
        for j in range(len(self.data.nodes)):
            for f in range(len(self.data.functions)):
                c_matrix[f][j] = self.c[f, j].solution_value()
        return x_matrix, c_matrix

    def score(self) -> float:
        return self.objective.Value()


class GPUSolver:
    solver = pywraplp.Solver.CreateSolver('SCIP')
    objective = solver.Objective()
    x = {}
    c = {}
    data: Data = None

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        if verbose:
            self.solver.EnableOutput()
        pass

    def load_input(self, data: Data):
        self.data = data

        # Initialize variable
        self.log("Initializing variables...")
        for f in range(len(data.functions)):
            for i in range(len(data.sources)):
                for j in range(len(data.nodes)):
                    self.x[i, f, j] = self.solver.NumVar(0, 1, f"x[{i}][{f}][{j}]")
        for f in range(len(data.functions)):
            for i in range(len(data.nodes)):
                self.c[f, i] = self.solver.BoolVar(f"c[{f}][{i}]")

        # Initialize constraints
        self.log("Initializing constraints...")
        # If a function `f` is deployed on node `n` then c[f,n] is True
        for f in range(len(data.functions)):
            for j in range(len(data.nodes)):
                self.solver.Add(
                    self.solver.Sum([
                        self.x[i, f, j] for i in range(len(data.sources))
                    ]) <= self.c[f, j] * 1000000)

        # The sum of the memory of functions deployed on a node is less than its capacity
        for j in range(len(data.nodes)):
            self.solver.Add(
                self.solver.Sum([
                    self.c[f, j] * self.data.function_memory_matrix[f] for f in range(len(data.functions))
                ]) <= data.node_memory_matrix[j])

        # The sum of the memory of functions deployed on a gpu device is less than its capacity
        for j in range(len(data.nodes)):
            self.solver.Add(
                self.solver.Sum([
                    self.c[f, j] * self.data.gpu_function_memory_matrix[f] for f in range(len(data.functions))
                ]) <= data.gpu_node_memory_matrix[j])

        # Don't overload GPUs
        # Set the response time to 1
        for f in range(len(data.functions)):
            for j in range(len(data.nodes)):
                self.solver.Add(
                    self.solver.Sum([
                        self.x[i, f, j] * data.workload_matrix[f, i] * data.response_time_matrix[f, j] for i in
                        range(len(data.sources))
                    ]) <= 1000)

        # Serve at most all requests
        for f in range(len(data.functions)):
            for i in range(len(data.sources)):
                self.solver.Add(
                    self.solver.Sum([
                        self.x[i, f, j] for j in range(len(data.nodes))
                    ]) <= 1)

    def log(self, msg: str):
        if self.verbose:
            print(f"{datetime.datetime.now()}: {msg}")

    def solve(self):
        # Starting to solve
        self.log("Starting solving problem...")

        # Objective function
        # Satisfy the maximum amount of requests
        for f in range(len(self.data.functions)):
            for i in range(len(self.data.sources)):
                for j in range(len(self.data.nodes)):
                    self.objective.SetCoefficient(
                        self.x[i, f, j], float(self.data.workload_matrix[f, i])
                    )
        self.objective.SetMaximization()

        # Solve problem
        status = self.solver.Solve()
        self.log(f"Problem solved with status {status}")

    def results(self) -> Tuple[np.array, np.array]:
        # Fill x matrix
        x_matrix = np.zeros(shape=(len(self.data.sources), len(self.data.functions), len(self.data.nodes)))
        for j in range(len(self.data.nodes)):
            for i in range(len(self.data.sources)):
                for f in range(len(self.data.functions)):
                    x_matrix[i][f][j] = self.x[i, f, j].solution_value()
        # Fill c matrix
        c_matrix = np.zeros(shape=(len(self.data.functions), len(self.data.nodes)))
        for j in range(len(self.data.nodes)):
            for f in range(len(self.data.functions)):
                c_matrix[f][j] = self.c[f, j].solution_value()
        return x_matrix, c_matrix

    def score(self) -> int:
        return self.solver.objective
