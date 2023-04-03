from ..solver import Solver
from .neptune_step1 import *
from .neptune_step2 import NeptuneStep2MinUtilization
from ..output import convert_x_matrix, convert_c_matrix

class NeptuneCPUOnly(Solver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step1 = NeptuneStep1CPUMinDelayAndUtilization(**kwargs)
        self.step2 = NeptuneStep2MinUtilization(**kwargs)
        self.solved = False

    def init_vars(self): pass
    def init_constraints(self): pass

    def solve(self):
        self.step1.load_data(self.data)
        self.step1.solve()
        self.step1_x, self.step1_c = self.step1.results()
        print("Step 1 x", self.step1_x)
        print("Step 1 c", self.step1_c)
        self.data.max_score = self.step1.score()
        print("score", self.data.max_score)
        #self.step2.load_data(self.data)
        #self.solved = self.step2.solve()
        #self.step2_x, self.step2_c = self.step2.results()
        #print("Step 2 x", self.step2_x)
        #print("Step 2 c", self.step2_c)
        return self.solved
    
    def results(self): 
        if self.solved:
            return convert_x_matrix(self.step2_x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(self.step2_c, self.data.functions, self.data.nodes)
        else:
            return convert_x_matrix(self.step1_x, self.data.nodes, self.data.functions, self.data.nodes), convert_c_matrix(self.step1_c, self.data.functions, self.data.nodes)
        
