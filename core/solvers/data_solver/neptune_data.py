from ..solver import Solver
from .utils import *

'''
class NeptuneData(Solver):
    def __init__(self, **kwargs):
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

    def init_vars(self):
        data = self.data
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

    def init_constraints(self):
        constrain_c_according_to_x(self.data, self.solver, self.c, self.x)
        constrain_memory_usage(self.data, self.solver, self.c)
        constrain_handle_all_requests(self.data, self.solver, self.x)
        constrain_CPU_usage(self.data, self.solver, self.x)
        constraint_table_presence(self.data, self.solver, self.mu)
        constraint_master_slave(self.data, self.solver, self.mu, self.sigma)
        constraint_function_assignment(self.data, self.solver, self.y, self.c, self.r)
        constraint_node_capacity(self.data, self.solver, self.mu, self.sigma)
        constraint_rho_according_to_y(self.data, self.solver, self.rho, self.y)
        constraint_r_according_to_beta_and_gamma(self.data, self.solver, self.r)
        constraint_migration(self.data, self.solver, self.rho, self.q)
        constraint_presence(self.data, self.solver, self.rho, self.mu, self.sigma)
        constraint_linearity_z(self.data, self.solver, self.z, self.x, self.y)
        constraint_linearity_w(self.data, self.solver, self.w, self.x, self.mu)
        constraint_linearity_psi(self.data, self.solver, self.psi, self.x, self.mu, self.sigma)
        constraint_linearity_gmax(self.data, self.solver, self.gmax, self.psi, self.d)

    def init_objective(self):
        minimize_network_data_delay(self.data, self.objective, self.x, self.z, self.w, self.gmax, self.q)

    def results(self):
        print("Decision variables:")
        # Print decision variables c
        for f in range(len(self.data.functions)):
            for i in range(len(self.data.nodes)):
                print(f"c[{f},{i}] =", self.c[f, i].solution_value())
        # Print decision variables x
        for k in range(len(self.data.nodes)):
            for f in range(len(self.data.functions)):
                for i in range(len(self.data.nodes)):
                    print(f"x[{k},{f},{i}] =", self.x[k, f, i].solution_value())
        # Print decision variables mu
        for j in range(len(self.data.nodes)):
            for t in range(len(self.data.tables)):
                print(f"mu[{j},{t}] =", self.mu[j, t].solution_value())
        # Print decision variables sigma
        for j in range(len(self.data.nodes)):
            for t in range(len(self.data.tables)):
                print(f"sigma[{j},{t}] =", self.sigma[j, t].solution_value())
        # Print decision variables y
        for f in range(len(self.data.functions)):
            for t in range(len(self.data.tables)):
                for i in range(len(self.data.nodes)):
                    for j in range(len(self.data.nodes)):
                        print(f"y[{f},{t},{i},{j}] =", self.y[f, t, i, j].solution_value())
        # Print decision variables r
        for f in range(len(self.data.functions)):
            for t in range(len(self.data.tables)):
                print(f"r[{f},{t}] =", self.r[f, t].solution_value())
        # Print decision variables rho
        for j in range(len(self.data.nodes)):
            for t in range(len(self.data.tables)):
                print(f"rho[{j},{t}] =", self.rho[j, t].solution_value())
        # Print decision variables q
        for i in range(len(self.data.nodes)):
            for j in range(len(self.data.nodes)):
                for t in range(len(self.data.tables)):
                    print(f"q[{i},{j},{t}] =", self.q[i, j, t].solution_value())
        # Print decision variables z
        for f in range(len(self.data.functions)):
            for t in range(len(self.data.tables)):
                for i in range(len(self.data.nodes)):
                    for j in range(len(self.data.nodes)):
                        for k in range(len(self.data.nodes)):
                            print(f"z[{f},{t},{i},{j},{k}] =", self.z[f, t, i, j, k].solution_value())
        # Print decision variables w
        for f in range(len(self.data.functions)):
            for t in range(len(self.data.tables)):
                for i in range(len(self.data.nodes)):
                    for j in range(len(self.data.nodes)):
                        for k in range(len(self.data.nodes)):
                            print(f"w[{f},{t},{i},{j},{k}] =", self.w[f, t, i, j, k].solution_value())
        # Print decision variables psi
        for i in range(len(self.data.nodes)):
            for j in range(len(self.data.nodes)):
                for t in range(len(self.data.tables)):
                    print(f"psi[{i},{j},{t}] =", self.psi[i, j, t].solution_value())
        # Print decision variables gmax
        for t in range(len(self.data.tables)):
            print(f"gmax[{t}] =", self.gmax[t].solution_value())
        # Print decision variables d
        for i in range(len(self.data.nodes)):
            for j in range(len(self.data.nodes)):
                print(f"d[{i},{j}] =", self.d[i, j].solution_value())


'''