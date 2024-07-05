from ortools.linear_solver import pywraplp

from ..solver import Solver
from .neptune_step1 import *
from .neptune_step2 import *
from .utils.output import convert_x_matrix, convert_c_matrix
from .utils.constraints_data import *
from .utils.variables_data import *
from .utils.objectives_data import *
from ..solver import Solver


class NeptuneFunctionsFirst(Solver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.solved = None
        self.data_step = NeptuneStepData(**kwargs)
        self.functions_step = NeptuneStepFunctions(**kwargs)

    def init_vars(self):
        pass

    def init_constraints(self):
        pass

    def solve(self):
        self.functions_step.load_data(self.data)
        self.solved = self.functions_step.solve()
        self.data.prev_x, self.data.prev_c = self.functions_step.results()
        if self.solved == pywraplp.Solver.OPTIMAL or self.solved == pywraplp.Solver.FEASIBLE:
            print('Function step done.')
            self.data_step.load_data(self.data)
            self.solved = self.data_step.solve()
        else:
            print('No solution found in Functions step')

        return self.solved

    def results(self):
        return self.data_step.results()

    def score(self):
        return self.data_step.score()


class NeptuneStepData(Solver):
    def __init__(self, c_f=True, c_r=False, c_w=False, c_s=False, c_m=False, **kwargs):
        super().__init__(**kwargs)
        self.mu = {}
        self.sigma = {}
        self.z = {}
        self.q = {}
        self.w = {}
        self.psi = {}
        self.gmax = {}
        self.y = {}
        self.rho = {}
        self.r = {}
        self.d = {}
        self.cr = {}
        self.eta = {}
        self.c_f = c_f
        self.c_r = c_r
        self.c_w = c_w
        self.c_s = c_s
        self.c_m = c_m

    def init_vars(self):
        data = self.data
        solver = self.solver

        init_mu(data, solver, self.mu)
        init_sigma(data, solver, self.sigma)
        # init_z(data, solver, self.z)
        init_q(data, solver, self.q)
        # init_w(data, solver, self.w)
        init_psi(data, solver, self.psi)
        init_gmax(data, solver, self.gmax)
        init_y(data, solver, self.y)
        init_rho(data, solver, self.rho)
        init_r(data, solver, self.r)
        init_d(data, solver, self.d)
        init_cr(data, solver, self.cr)
        init_psi(data, solver, self.eta)

    def init_constraints(self):
        c = self.data.prev_c
        constraint_table_presence(self.data, self.solver, self.mu)
        constraint_master_slave(self.data, self.solver, self.mu, self.sigma)
        constraint_function_assignment(self.data, self.solver, self.y, self.cr, c, self.r)
        constraint_node_capacity(self.data, self.solver, self.mu, self.sigma)
        constraint_rho_according_to_y(self.data, self.solver, self.rho, self.y)
        constraint_r_according_to_beta_and_gamma(self.data, self.solver, self.r)
        constraint_migration(self.data, self.solver, self.rho, self.q)
        constraint_migration_2(self.data, self.solver, self.q, self.sigma, self.mu)
        constraint_presence(self.data, self.solver, self.rho, self.mu, self.sigma)
        # constraint_linearity_z(self.data, self.solver, self.z, self.x, self.y)
        # constraint_linearity_w(self.data, self.solver, self.w, self.x, self.mu)
        constraint_linearity_psi(self.data, self.solver, self.psi, self.mu, self.sigma)
        constraint_linearity_gmax(self.data, self.solver, self.gmax, self.psi, self.d)

    def init_objective(self):
        minimize_network_data_only_delay(self.data, self.objective, self.gmax, self.y, self.mu)

    def results(self):
        x = self.data.prev_x
        q = output_q(self.data, self.q)
        mu = output_mu(self.data, self.mu)
        sigma = output_sigma(self.data, self.sigma)
        y = output_y(self.data, self.y)
        gmax = output_gmax(self.data, self.gmax)
        rho = output_rho(self.data, self.rho)
        z = compute_z(self.data, x, y)
        c_f = compute_c_f_cost(self.data, x)
        w = compute_w(self.data, x, mu)
        c_r = compute_c_r_cost(self.data, z)
        c_w = compute_c_w_cost(self.data, w)
        c_s = compute_c_s_cost(self.data, gmax)

        return q, self.data.prev_c, mu, sigma, y, c_f, c_r, c_w, c_s


class NeptuneStepFunctions(Solver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x = {}
        self.c = {}

    def init_vars(self):
        init_x(self.data, self.solver, self.x)
        init_c(self.data, self.solver, self.c)

    def init_constraints(self):
        constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        constrain_memory_usage(self.data, self.solver, self.c)
        constrain_handle_required_requests(self.data, self.solver, self.x)
        constrain_CPU_usage(self.data, self.solver, self.x)

    def init_objective(self):
        minimize_network_delay(self.data, self.objective, self.x)

    def results(self):
        x = output_x(self.data, self.x)
        c = output_c(self.data, self.c)
        self.data.prev_x = x
        self.data.prev_c = c
        return x, c
