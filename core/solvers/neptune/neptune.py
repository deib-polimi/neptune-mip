from ..solver import Solver
from .neptune_step1 import *
from .neptune_step2 import *
from .utils.output import convert_x_matrix, convert_c_matrix

class NeptuneBase(Solver):
    def __init__(self, step1=None, step2_delete=None, step2_create=None, **kwargs):
        super().__init__(**kwargs)
        self.step1 = step1
        self.step2_delete = step2_delete
        self.step2_create = step2_create
        self.solved = False

    def init_vars(self): pass
    def init_constraints(self): pass

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
            return convert_x_matrix(self.step2_x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(self.step2_c, self.data.functions, self.data.nodes)
        else:
            return convert_x_matrix(self.step1_x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(self.step1_c, self.data.functions, self.data.nodes)
    
    def score(self):
        return { "step1": self.step1.score(), "step2": self.step2_delete.score() if self.step2_delete_solved else self.step2_create.score() }

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
