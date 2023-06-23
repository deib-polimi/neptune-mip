from ..vsvbp import VSVBP
from .utils import prepare_order_requests
from ..criticality import CriticalityHeuristic

class MCF(CriticalityHeuristic):
    def prepare_data(self, data):
        VSVBP.prepare_data(self, data)
        prepare_order_requests(data)
