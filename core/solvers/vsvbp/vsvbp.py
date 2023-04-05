import datetime

import numpy as np
from ortools.linear_solver import pywraplp
from ..solver import Solver
from ortools.sat.python import cp_model
from .utils import *
from ..neptune.utils.output import convert_c_matrix, convert_x_matrix

class VSVBP(Solver):

    def __init__(self, num_users=8, **kwargs):
        super().__init__(**kwargs)
        self.num_users = num_users
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.x, self.c, self.y = {}, {}, {}
        self.first_step = True

    def load_data(self, data):
        self.prepare_data(data)
        super().load_data(data)

    def prepare_data(self, data):
        data.num_users = self.num_users
        data.node_coords = delay_to_geo(data.node_delay_matrix)
        data.user_coords = place_users_close_to_nodes(data.num_users, data.node_coords)
        prepare_requests(data)
        prepare_req_distribution(data)
        prepare_coverage(data)

    def init_vars(self):
        init_x(self.data, self.model, self.x)
        init_c(self.data, self.model, self.c)
        init_y(self.data, self.model, self.y)

    def init_constraints(self):
        if self.first_step:
            constrain_coverage(self.data, self.model, self.x)
            constrain_proximity(self.data, self.model, self.x)
            constrain_memory(self.data, self.model, self.c, self.y)
            constrain_cpu(self.data, self.model, self.x, self.y)
            constrain_request_handled(self.data, self.model, self.x)
            constrain_c_according_to_x(self.data, self.model, self.c, self.x)    
            constrain_y_according_to_x(self.data, self.model, self.y, self.x)
            constrain_amount_of_instances(self.data, self.model, self.c)
        else:
            add_hints(self.data, self.model, self.solver, self.x)
            constrain_previous_objective(self.data, self.model, self.x, self.solver.ObjectiveValue())
            
    
    def init_objective(self):
        if self.first_step:
            maximize_handled_requests(self.data, self.model, self.x)
        else:
            minimize_utilization(self.data, self.model, self.y)


    def solve(self):
        self.init_objective()
        self.solver.Solve(self.model)
        self.first_step = False

        self.init_constraints()
        self.init_objective()
        self.status = self.solver.Solve(self.model)

        self.log(f"Problem solved with status {self.status}")

    def results(self):
        xjr = output_xjr(self.data, self.solver, self.status, self.x, self.c, self.y)
        x, c = output_x_and_c(self.data, self.solver, self.c, xjr)
        return convert_x_matrix(x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(c, self.data.functions, self.data.nodes)
    


