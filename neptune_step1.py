import solver_utils as su
import numpy

class NeptuneStep1CPU(su.Solver):
    
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.x, self.c, self.n = {}, {}, {}

    def init_vars(self):
        su.init_x(self.data, self.solver, self.x)
        su.init_c(self.data, self.solver, self.c)
        su.init_n(self.data, self.solver, self.n)

    def init_constraints(self):
        su.constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        su.constrain_memory_usage(self.data, self.solver, self.c)
        su.constrain_handle_required_requests(self.data, self.solver, self.x)
        su.constrain_CPU_usage(self.data, self.solver, self.x)
        su.constrain_n_according_to_c(self.data, self.solver, self.n, self.c)

    def init_objective(self):
        su.minimize_node_utilization(self.data, self.objective, self.n)

    def results(self):
        return su.output_x_and_c(self.data, self.x, self.c)
       

class NeptuneStep1GPU(su.Solver):
    
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.x, self.c, self.n = {}, {}, {}

    def init_vars(self):
        su.init_x(self.data, self.solver, self.x)
        su.init_c(self.data, self.solver, self.c)
        su.init_n(self.data, self.solver, self.n)

    def init_constraints(self):
        su.constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        su.constrain_memory_usage(self.data, self.solver, self.c)
        su.constrain_memory_usage(self.data, self.solver, self.c)
        su.constrain_GPU_memory_usage(self.data, self.solver, self.c)
        su.constrain_GPU_usage(self.data, self.solver, self.x)
        su.constrain_handle_all_requests(self.data, self.solver, self.x, eq=False)

    def init_objective(self):
        su.maximize_handled_requests(self.data, self.objective, x)

    def results(self):
        return su.output_x_and_c(self.data, self.x, self.c)


