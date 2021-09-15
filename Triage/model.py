from mesa import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from Triage.agents import *
import random

class Triage(Model):
    """
    Model will keep track of cured patients and if Medic dies
    """
    def __init__(self, width, height, init_medic=1, init_patients=2,init_cure=1, init_radio=1):
        self.width = width
        self.height = height
        self.init_medic = init_medic
        self.init_patients = init_patients
        self.init_cure = init_cure
        self.init_radio = init_radio

        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=True)

        # create Medic
        medic_poss = []
        for m in range(init_medic):
            medic = Medic((0,0), self, False)
            medic_poss.append((0,0))
            self.grid.place_agent(medic, (0,0))
            self.schedule.add(medic)

        # create unique coords for every agent except medic/static/scream
        total_a = init_cure + init_patients + init_radio
        x_l = random.sample(range(1, width), total_a)
        y_l = random.sample(range(1, height), total_a)

        coords = list(zip(x_l, y_l))

        # create Cure
        for i in range(init_cure):
            cure = Cure(coords[0], self)
            self.grid.place_agent(cure, coords[0])
            coords.pop(0)
            self.schedule.add(cure)

        # create Radio with surrounding static
        for i in range(init_radio):
            radio = Radio(coords[0], self)
            self.grid.place_agent(radio, coords[0])
            self.schedule.add(radio)
            # add surrounding static from radio
            nb = self.grid.get_neighborhood(coords[0],False,False)
            for n in nb:
                st = Static(n, self)
                self.grid.place_agent(st, n)
                self.schedule.add(st)                                       # Not sure if this is needed !!!!!
            coords.pop(0)

        # create Patient with surrounding Scream
        for i in range(init_patients):
            patient = Patient(coords[0], self)
            self.grid.place_agent(patient, coords[0])
            self.schedule.add(patient)
            # add surrounding scream from patient
            nb = self.grid.get_neighborhood(coords[0],False,False)
            for n in nb:
                sc = Scream(n,self)
                self.grid.place_agent(sc, n)
                self.schedule.add(sc)                                        # Not sure if this is needed !!!!!
            coords.pop(0)

    def step(self):
        self.schedule.step()

e = Triage(10, 10, 1, 2, 1)
e.step()
