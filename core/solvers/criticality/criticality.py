from ..vsvbp import VSVBP
from .utils import *

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
