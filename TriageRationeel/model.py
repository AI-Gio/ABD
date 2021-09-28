import random

from mesa.space import MultiGrid
from mesa import Model
from mesa.time import SimultaneousActivation

from TriageRationeel.agents import *

class Triage(Model):
    """
    Simulation of Triage
    """
    # hier worden alle agents aangemaakt en geplaatst en grid aangemaakt
    def __init__(self, width=10, height=10, init_medic=1, init_patient=9):
        self.width = width
        self.height = height

        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=False)
        self.running = True

        medic_poss = []
        for m in range(init_medic):
            # print(m)
            medic = Medic(0, self)
            medic_poss.append((0,0))
            self.grid.place_agent(medic, (0,0))
            self.schedule.add(medic)

        total_a = init_patient#+ init_radio + init_cure
        x_l = random.sample(range(1, width), total_a)
        y_l = random.sample(range(1, height), total_a)

        coords = list(zip(x_l, y_l))
        coords= [(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,2),(3,3),(3,4),(3,5)]

        for p in range(init_patient):
            # print(p+1)
            patient = Patient(p+1, self)
            patient.createHealth([width, height])
            self.grid.place_agent(patient, coords[0])#coords[0]
            coords.pop(0)
            self.schedule.add(patient)

        medcamp = MedCamp(112, self)
        self.grid.place_agent(medcamp, (0,0))
        self.schedule.add(medcamp)


    def step(self):
        self.schedule.step()