from ..solver import Solver
from .neptune_step1 import *
from .neptune_step2 import *
from .utils.output import convert_x_matrix, convert_c_matrix

class NeptuneBase(Solver):
    def __init__(self, step1=None, step2=None, **kwargs):
        super().__init__(**kwargs)
        self.step1 = step1
        self.step2 = step2
        self.solved = False

    def init_vars(self): pass
    def init_constraints(self): pass

    def solve(self):
        self.step1.load_data(self.data)
        self.step1.solve()
        self.step1_x, self.step1_c = self.step1.results()
        self.data.max_score = self.step1.score()
        self.step2.load_data(self.data)
        self.solved = self.step2.solve()
        self.step2_x, self.step2_c = self.step2.results()
        return self.solved
    
    def results(self): 
        if self.solved:
            return convert_x_matrix(self.step2_x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(self.step2_c, self.data.functions, self.data.nodes)
        else:
            return convert_x_matrix(self.step1_x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(self.step1_c, self.data.functions, self.data.nodes)
        

class NeptuneMinDelayAndUtilization(NeptuneBase):
    def __init__(self, **kwargs):
        super().__init__(
            NeptuneStep1CPUMinDelayAndUtilization(**kwargs), 
            NeptuneStep2MinDelayAndUtilization(**kwargs),
            **kwargs
            )


class NeptuneMinDelay(NeptuneBase):
    def __init__(self, **kwargs):
        super().__init__(
            NeptuneStep1CPUMinDelay(**kwargs), 
            NeptuneStep2MinDelay(**kwargs),
            **kwargs
            )

class NeptuneMinUtilization(NeptuneBase):
    def __init__(self, **kwargs):
        super().__init__(
            NeptuneStep1CPUMinUtilization(**kwargs), 
            NeptuneStep2MinUtilization(**kwargs),
            **kwargs
            )
