from ..solver import Solver
from .neptune_step1 import *
from .neptune_function_first import *
from .neptune_step2 import *
from .utils.output import convert_x_matrix, convert_c_matrix
from .utils.constraints_data import *
from .utils.variables_data import *
from .utils.objectives_data import *
from ..solver import Solver


class NeptuneBase(Solver):
    def __init__(self, step1=None, step2_delete=None, step2_create=None, **kwargs):
        super().__init__(**kwargs)
        self.step1 = step1
        self.step2_delete = step2_delete
        self.step2_create = step2_create
        self.solved = False

    def init_vars(self):
        pass

    def init_constraints(self):
        pass

    def solve(self):
        self.step1.load_data(self.data)
        self.step1.solve()
        self.step1_x, self.step1_c = self.step1.results()
        self.data.max_score = self.step1.score()
        self.step2_delete.load_data(self.data)
        self.solved = self.step2_delete_solved = self.step2_delete.solve()
        self.step2_x, self.step2_c = self.step2_delete.results()
        if not self.solved:
            self.step2_create.load_data(self.data)
            self.solved = self.step2_create.solve()
            self.step2_x, self.step2_c = self.step2_create.results()
        return self.solved

    def results(self):
        if self.solved:
            return convert_x_matrix(self.step2_x, self.data.nodes, self.data.functions), convert_c_matrix(self.step2_c,
                                                                                                          self.data.functions,
                                                                                                          self.data.nodes)
        else:
            return convert_x_matrix(self.step1_x, self.data.nodes, self.data.functions), convert_c_matrix(self.step1_c,
                                                                                                          self.data.functions,
                                                                                                          self.data.nodes)

    def score(self):
        return {"step1": self.step1.score(),
                "step2": self.step2_delete.score() if self.step2_delete_solved else self.step2_create.score()}


class NeptuneMinDelayAndUtilization(NeptuneBase):
    def __init__(self, **kwargs):
        super().__init__(
            NeptuneStep1CPUMinDelayAndUtilization(**kwargs),
            NeptuneStep2MinDelayAndUtilization(mode="delete", **kwargs),
            NeptuneStep2MinDelayAndUtilization(mode="create", **kwargs),
            **kwargs
        )


class NeptuneMinDelay(NeptuneBase):
    def __init__(self, **kwargs):
        super().__init__(
            NeptuneStep1CPUMinDelay(**kwargs),
            NeptuneStep2MinDelay(mode="delete", **kwargs),
            NeptuneStep2MinDelay(mode="create", **kwargs),
            **kwargs
        )


class NeptuneMinUtilization(NeptuneBase):
    def __init__(self, **kwargs):
        super().__init__(
            NeptuneStep1CPUMinUtilization(**kwargs),
            NeptuneStep2MinUtilization(mode="delete", **kwargs),
            NeptuneStep2MinUtilization(mode="create", **kwargs),
            **kwargs
        )


class NeptuneData(Solver):
    def __init__(self, c_f=True, c_r=False, c_w=False, c_s=False, c_m=False, **kwargs):
        super().__init__(**kwargs)
        self.x = {}
        self.c = {}
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
        # Initialize all variables
        init_x(data, solver, self.x)
        init_c(data, solver, self.c)
        init_mu(data, solver, self.mu)
        init_sigma(data, solver, self.sigma)
        init_z(data, solver, self.z)
        init_q(data, solver, self.q)
        init_w(data, solver, self.w)
        init_psi(data, solver, self.psi)
        init_gmax(data, solver, self.gmax)
        init_y(data, solver, self.y)
        init_rho(data, solver, self.rho)
        init_r(data, solver, self.r)
        init_d(data, solver, self.d)
        init_cr(data, solver, self.cr)
        init_psi(data, solver, self.eta)

    def init_constraints(self):
        constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        constrain_memory_usage(self.data, self.solver, self.c)
        constrain_handle_all_requests(self.data, self.solver, self.x, eq=True)
        constrain_CPU_usage(self.data, self.solver, self.x)
        constraint_table_presence(self.data, self.solver, self.mu)
        constraint_master_slave(self.data, self.solver, self.mu, self.sigma)
        constraint_function_assignment(self.data, self.solver, self.y, self.cr, self.c, self.r)
        constraint_node_capacity(self.data, self.solver, self.mu, self.sigma)
        constraint_rho_according_to_y(self.data, self.solver, self.rho, self.y)
        constraint_r_according_to_beta_and_gamma(self.data, self.solver, self.r)
        constraint_migration(self.data, self.solver, self.rho, self.q)
        constraint_migration_2(self.data, self.solver, self.q, self.sigma, self.mu)
        constraint_presence(self.data, self.solver, self.rho, self.mu, self.sigma)
        constraint_linearity_z(self.data, self.solver, self.z, self.x, self.y)
        constraint_linearity_w(self.data, self.solver, self.w, self.x, self.mu)
        constraint_linearity_psi(self.data, self.solver, self.psi, self.mu, self.sigma)
        constraint_linearity_gmax(self.data, self.solver, self.gmax, self.psi, self.d)

    def init_objective(self):
        c_f = self.c_f
        c_r = self.c_r
        c_w = self.c_w
        c_s = self.c_s
        c_m = self.c_m

        minimize_network_data_delay(self.data, self.objective, self.x, self.z, self.w, self.gmax, self.q, c_f, c_r, c_w,
                                    c_s, c_m)

    def results(self):
        q = output_q(self.data, self.q)
        c = output_c(self.data, self.c)
        mu = output_mu(self.data, self.mu)
        sigma = output_sigma(self.data, self.sigma)
        y = output_y(self.data, self.y)
        z = output_z(self.data, self.z)
        w = output_w(self.data, self.w)
        x = output_x(self.data, self.x)
        gmax = output_gmax(self.data, self.gmax)
        c_f = compute_c_f_cost(self.data, x)
        c_r = compute_c_r_cost(self.data, z)
        c_w = compute_c_w_cost(self.data, w)
        c_s = compute_c_s_cost(self.data, gmax)
        return q, c, mu, sigma, y, c_f, c_r, c_w, c_s


    '''

        DEBUG

        print("Decision variables:")
        # Print decision variables c
        print("\n##### C matrix #####\n")
        for f in range(len(self.data.functions)):
            row = []
            for i in range(len(self.data.nodes)):
                row.append(self.c[f, i].solution_value())
            print("\t".join(map(str, row)))

        # Print decision variables x
        for k in range(len(self.data.nodes)):
            print(f"\n##### x matrix for k={k} #####\n")
            for f in range(len(self.data.functions)):
                row = []
                for i in range(len(self.data.nodes)):
                    row.append(self.x[k, f, i].solution_value())
                print("\t".join(map(str, row)))

        # Print decision variables mu
        print("\n##### mu matrix #####\n")
        for j in range(len(self.data.nodes)):
            row = []
            for t in range(len(self.data.tables)):
                row.append(self.mu[j, t].solution_value())
            print("\t".join(map(str, row)))

        # Print decision variables sigma
        print("\n##### sigma matrix #####\n")
        for j in range(len(self.data.nodes)):
            row = []
            for t in range(len(self.data.tables)):
                row.append(self.sigma[j, t].solution_value())
            print("\t".join(map(str, row)))

        # Print decision variables y
        for f in range(len(self.data.functions)):
            for t in range(len(self.data.tables)):
                print(f"\n##### y matrix for f={f}, t={t} #####\n")
                for i in range(len(self.data.nodes)):
                    row = []
                    for j in range(len(self.data.nodes)):
                        row.append(self.y[f, t, i, j].solution_value())
                    print("\t".join(map(str, row)))

        # Print z variables
        for f in range(len(self.data.functions)):
            for t in range(len(self.data.tables)):
                for i in range(len(self.data.nodes)):
                    print(f"\n##### z matrix for f={f}, t={t}, i={i} #####\n")
                    for j in range(len(self.data.nodes)):
                        row = []
                        for k in range(len(self.data.nodes)):
                            row.append(self.z[f, t, i, j, k].solution_value())
                        print("\t".join(map(str, row)))

        # Print decision variables r
        print("\n##### r matrix #####\n")
        for f in range(len(self.data.functions)):
            row = []
            for t in range(len(self.data.tables)):
                row.append(self.r[f, t].solution_value())
            print("\t".join(map(str, row)))

        # Print decision variables rho
        print("\n##### rho matrix #####\n")
        for j in range(len(self.data.nodes)):
            row = []
            for t in range(len(self.data.tables)):
                row.append(self.rho[j, t].solution_value())
            print("\t".join(map(str, row)))
        
        # Print decision variables q
        for t in range(len(self.data.tables)):
            print(f"\n##### q matrix for t={t} #####\n")
            for i in range(len(self.data.nodes)):
                row = []
                for j in range(len(self.data.nodes)):
                    row.append(self.q[i, j, t].solution_value())
                print("\t".join(map(str, row)))
        
        # Print decision variables gmax
        print("\n##### gmax vector #####\n")
        for t in range(len(self.data.tables)):
            print(self.gmax[t].solution_value())

        # Print decision variables d
        for t in range(len(self.data.tables)):
            print(f"\n##### d matrix for t={t}#####\n")
            for i in range(len(self.data.nodes)):
                row = []
                for j in range(len(self.data.nodes)):
                    row.append(self.d[i, j, t].solution_value())
                print("\t".join(map(str, row)))
        '''
