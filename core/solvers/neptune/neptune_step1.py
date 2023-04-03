from .utils import *
from ..output import output_x_and_c
from ..solver import Solver


class NeptuneStep1Base(Solver):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x, self.c = {}, {}

    def init_vars(self):
        init_x(self.data, self.solver, self.x)
        init_c(self.data, self.solver, self.c)

    def init_constraints(self):
        constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        constrain_memory_usage(self.data, self.solver, self.c)

    def init_objective(self):
        raise NotImplementedError("Solvers must implement init_objective()")

    def results(self):
        return output_x_and_c(self.data, self.x, self.c)
    

class NeptuneStep1CPUBase(NeptuneStep1Base):

    def init_constraints(self):
        super().init_constraints()
        constrain_handle_required_requests(self.data, self.solver, self.x)
        constrain_CPU_usage(self.data, self.solver, self.x)

       
class NeptuneStep1CPUMinUtilization(NeptuneStep1CPUBase):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n = {}

    def init_vars(self):
        super().init_vars()
        init_n(self.data, self.solver, self.n)

    def init_constraints(self):
        super().init_constraints()
        constrain_n_according_to_c(self.data, self.solver, self.n, self.c)

    def init_objective(self):
        minimize_node_utilization(self.data, self.objective, self.n)

    


class NeptuneStep1CPUMinDelay(NeptuneStep1CPUBase):
    
    def init_objective(self):
        minimize_network_delay(self.data, self.objective, self.x)

class NeptuneStep1CPUMinDelayAndUtilization(NeptuneStep1CPUMinUtilization):
    def __init__(self, alpha=0.5, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha
        print("al", alpha)

    def init_objective(self):
        minimize_node_delay_and_utilization(self.data, self.objective, self.n, self.x, self.alpha)

class NeptuneStep1GPUBase(NeptuneStep1Base):

    def init_constraints(self):
        super().init_constraints()
        constrain_GPU_memory_usage(self.data, self.solver, self.c)
        constrain_GPU_usage(self.data, self.solver, self.x)

    def init_objective(self):
        maximize_handled_requests(self.data, self.objective, self.x)


class NeptuneStep1GPUMinUtilization(NeptuneStep1GPUBase): pass

class NeptuneStep1GPUMinDelay(NeptuneStep1GPUBase): pass
