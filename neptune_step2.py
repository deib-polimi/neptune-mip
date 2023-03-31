import solver_utils as su
import numpy

class NeptuneStep2(su.Solver):
    
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.x, self.c, self.n, self.moved_from, self.moved_to = ({},) * 5

    def init_vars(self):
        su.init_x(self.data, self.solver, self.x)
        su.init_c(self.data, self.solver, self.c)
        su.init_n(self.data, self.solver, self.n)
        su.init_moved_from(self.data, self.solver, self.moved_from)
        su.init_moved_to(self.data, self.solver, self.moved_to)
        self.allocated = su.init_allocated(self.data, self.solver)
        self.deallocated = su.init_deallocated(self.data, self.solver)

    def init_constraints(self):
        su.constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        su.constrain_memory_usage(self.data, self.solver, self.c)
        su.constrain_handle_required_requests(self.data, self.solver, self.x)
        su.constrain_CPU_usage(self.data, self.solver, self.x)
        su.constrain_n_according_to_c(self.data, self.solver, self.n, self.c)
        su.constrain_moved_from(self.data, self.solver, self.moved_from, self.c)
        su.constrain_moved_to(self.data, self.solver, self.moved_to, self.c)
        su.constrain_node_utilization(self.data, self.solver, self.n)
        su.constrain_migrations(self.data, self.solver, self.c, self.allocated, self.deallocated)
        su.constrain_deletions(self.data, self.solver, self.c, self.allocated, self.deallocated)

    def init_objective(self):
        su.minimize_disruption(self.data, self.objective, self.moved_from, self.moved_to, self.allocated, self.deallocated)

    def results(self):
        print("Number of delta pod deallocated")
        print(-self.deallocated.solution_value())
        print("Number of delta pod allocated")
        print(-self.allocated.solution_value())
        return su.output_x_and_c(self.data, self.x, self.c)

