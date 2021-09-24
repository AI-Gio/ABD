from mesa.space import MultiGrid
from mesa import Model
from mesa.time import SimultaneousActivation

from Triage2.agents import *

class Triage(Model):
    """
    Simulation of Triage
    """
    def __init__(self, width=10, height=10, init_medic=1, init_patient=1):
        self.width = width
        self.height = height

        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=False)
        self.running = True

        medic_poss = []
        for m in range(init_medic):
            medic = Medic(1, self)
            medic_poss.append((0,0))
            self.grid.place_agent(medic, (0,0))
            self.schedule.add(medic)

        for p in range(init_patient):
            patient = Patient(2, self)
            self.grid.place_agent(patient, (0, 1))
            self.schedule.add(patient)

    def step(self):
        self.schedule.step()
