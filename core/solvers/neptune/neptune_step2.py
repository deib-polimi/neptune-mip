from .utils import *
from ..output import output_x_and_c
from ..solver import Solver

class NeptuneStep2Base(Solver):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x, self.c, self.moved_from, self.moved_to = ({},) * 4

    def init_vars(self):
        init_x(self.data, self.solver, self.x)
        init_c(self.data, self.solver, self.c)
        init_moved_from(self.data, self.solver, self.moved_from)
        init_moved_to(self.data, self.solver, self.moved_to)
        self.allocated = init_allocated(self.data, self.solver)
        self.deallocated = init_deallocated(self.data, self.solver)

    def init_constraints(self):
        constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        constrain_memory_usage(self.data, self.solver, self.c)
        constrain_handle_required_requests(self.data, self.solver, self.x)
        constrain_CPU_usage(self.data, self.solver, self.x)
        constrain_n_according_to_c(self.data, self.solver, self.n, self.c)
        constrain_moved_from(self.data, self.solver, self.moved_from, self.c)
        constrain_moved_to(self.data, self.solver, self.moved_to, self.c)
        constrain_migrations(self.data, self.solver, self.c, self.allocated, self.deallocated)
        constrain_deletions(self.data, self.solver, self.c, self.allocated, self.deallocated)

    def init_objective(self):
        minimize_disruption(self.data, self.objective, self.moved_from, self.moved_to, self.allocated, self.deallocated)

    def results(self):
        print("Number of delta pod deallocated")
        print(-self.deallocated.solution_value())
        print("Number of delta pod allocated")
        print(-self.allocated.solution_value())
        return output_x_and_c(self.data, self.x, self.c)



class NeptuneStep2MinUtilization(NeptuneStep2Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n = {}

    def init_vars(self):
        super().init_vars()
        init_n(self.data, self.solver, self.n)

    def init_constraints(self):
        super().init_constraints()
        constrain_node_utilization(self.data, self.solver, self.n)


class NeptuneStep2MinDelay(NeptuneStep2Base):
    def __init__(self, delay_coeff=1.3, **kwargs):
        super().__init__(**kwargs)
        self.delay_coeff = delay_coeff

    def init_constraints(self):
        super().init_constraints()
        constrain_network_delay(self.data, self.solver, self.delay_coeff)