from random import sample
from itertools import product
from mesa.space import MultiGrid
from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

from TriageRationeel.agents import *

class Triage(Model):
    """
    Simulation of Triage
    """
    # Here get all the agents made and placed in the grid
    def __init__(self, width=20, height=20, init_medic=2, init_patient=9, init_scouts=0, mode="None"):
        self.width = width
        self.height = height

        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=False)
        self.running = True

        medic_poss = []
        for m in range(init_medic):
            medic = Medic(m, self, mode=mode)
            medic_poss.append((0,0))
            self.grid.place_agent(medic, (0,0))
            self.schedule.add(medic)

        scout_poss = []
        for s in range(init_scouts):
            scout = Scout(s+10, self, mode=mode)
            scout_poss.append((0,0))
            self.grid.place_agent(scout, (1,1))
            self.schedule.add(scout)

        total_a = init_patient
        coords = sample(list(product(range(1,width), repeat=2)), k=init_patient) #bron: https://stackoverflow.com/questions/60641177/how-do-i-make-a-list-of-random-unique-tuples

        for p in range(init_patient):
            patient = Patient(p+20, self)
            patient.createHealth([width, height])
            self.grid.place_agent(patient, coords[0])
            coords.pop(0)
            self.schedule.add(patient)

        medcamp = MedCamp(69420112, self)
        self.grid.place_agent(medcamp, (0,0))
        self.schedule.add(medcamp)

        agents = self.schedule.agents

        # Graphs the amount of patients that have been saved or died
        self.datacollector = DataCollector({"Dead_patients": lambda m: m.get_dead_patients(agents),
                                            "Saved_Patients": lambda m: m.get_saved_patients(agents)})

    def get_dead_patients(self, agents):
        """Graphs the amount of patients that have died"""
        return len([obj for obj in agents if isinstance(obj, Patient) and obj.dead])

    def get_saved_patients(self, agents):
        """Graphs the amount of patients that have been saved"""
        medcamp = [obj for obj in agents if isinstance(obj, MedCamp)]
        return medcamp[0].saved_patients_amount

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
