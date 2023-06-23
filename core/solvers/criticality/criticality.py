from ..vsvbp import VSVBP
from .utils import *
from ..neptune.utils.output import convert_c_matrix, convert_x_matrix
from ..vsvbp.utils.output import output_x_and_c

class Criticality(VSVBP):
    def __init__(self, danger_radius_km=0.5, **kwargs):
        super().__init__(**kwargs)
        self.danger_radius_km = danger_radius_km

 
    def prepare_data(self, data):
        super().prepare_data(data)
        prepare_aux_vars(data, self.danger_radius_km)
        prepare_criticality(data)
        prepare_live_position(data)        
        prepare_coverage_live(data)


    def init_objective(self):
        if self.first_step:
            maximize_handled_most_critical_requests(self.data, self.model, self.x)
        else:
            super().init_objective()


class CriticalityHeuristic(Criticality):
    def init_vars(self): 
        self.x_jr, self.c_fj, self.y_j, self.S_active = init_all_vars(self.data)

    def init_constraints(self): pass
    def init_objective(self): pass

    def solve(self):
        criticality_heuristic(self.data, self.log, self.S_active, self.y_j, self.c_fj, self.x_jr)

    def results(self):
        x, c = output_x_and_c(self.data, None, self.c_fj, self.x_jr)
        return convert_x_matrix(x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(c, self.data.functions, self.data.nodes)