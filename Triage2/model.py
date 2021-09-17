from mesa.space import MultiGrid
from mesa import Model
from mesa.time import SimultaneousActivation

class Triage(Model):
    """
    Simulation of Triage
    """
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height

        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=False)




    def step(self):
        self.schedule.step()
