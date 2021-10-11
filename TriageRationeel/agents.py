from mesa import Agent
import random
import time
import numpy as np

class Medic(Agent):
    """
    Searches for patients in the field and brings them back to camp, if statistically possible
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.brancard = []
        self.path = [(0, 0), (0, 1), (1, 0)]
        self.known_p = []
        self.current_path = ()
        self.previous_location = None
        self.emotional_state = 100
        self.pickedup = False

    def move_agent(self, location):
        self.previous_location = self.pos
        self.model.grid.move_agent(self, location)
        new_loc = self.model.grid.get_neighborhood(location, moore=False, include_center=True)
        self.path = self.path + (list(set(new_loc) - set(self.path)))  # removes duplicates


    def inspect(self, patient):
        """
        Medic inspects patient how severe the situation is and decides then what to do next
        :return:
        """
        print('Patient ' + str(patient.unique_id) + ': ' + str(patient.health) + "hp")
        if self.pos[0] + self.pos[1] >= patient.health and patient.dead == False:
            self.emotional_state = self.emotional_state - 20
            print("Medic: Omae wa mou, shindeiru\nPatient: NANI???\n*Patient died*")
            if self.known_p:
                for i, p in enumerate(self.known_p):
                    if patient == p[1]:
                        self.known_p.pop(i)
            patient.health = 0
            patient.dead = True

        elif patient.dead == False:
            print("Come. this is no place to die")
            if self.known_p:
                for i, p in enumerate(self.known_p):
                    if patient == p[1]:
                        self.known_p.pop(i)
            self.brancard.append(patient)
            self.pickedup = True
            self.model.grid.remove_agent(patient)

    def wander_choice_maker(self, locations, counter=0):
        choices = {}
        for pos in locations:
            surraw = [(list(pos)[-1][0], list(pos)[-1][1]+1), (list(pos)[-1][0], list(pos)[-1][1]-1),
                      (list(pos)[-1][0]+1, list(pos)[-1][1]), (list(pos)[-1][0]-1, list(pos)[-1][1])]
            sur = [i for i in surraw if (0 <= i[0] < self.model.width) and (0 <= i[1] < self.model.height)]
            if self.previous_location in sur and len(sur) > 1:
                sur.remove(self.previous_location)
            for loc in sur:
                if loc in pos:
                    continue
                sursuround = self.model.grid.get_neighborhood(loc, moore=False, include_center=True)
                score = 0
                for surloc in sursuround:
                    if surloc not in self.path:
                        score += 1

                path = list(pos)
                path.append(loc)
                choices[tuple(path)] = score


        possible_choices = [k for k, v in choices.items() if v == max(choices.values())]

        if (len(possible_choices) > 1 and counter < 3) and max(choices.values()) < 4:
            possible_choices = self.wander_choice_maker(possible_choices, counter+1)
        # elif (len(possible_choices) > 1 and counter >= 3) and max(choices.values()) < 4:
            # right = [x for x in self.model.grid.empties if x[0] > self.pos[0]]
            # rightcount = len(set(right) - set(self.path))
            # left = [x for x in self.model.grid.empties if x[0] < self.pos[0]]
            # leftcount = len(set(left) - set(self.path))
            # up = [x for x in self.model.grid.empties if x[1] > self.pos[1]]
            # upcount = len(set(up) - set(self.path))
            # down = [x for x in self.model.grid.empties if x[1] < self.pos[1]]
            # downcount = len(set(down) - set(self.path))
            # count_list = [rightcount, leftcount, upcount, downcount]
            # max_index = count_list.index(max(count_list))
            # return {
            #     0: [(self.pos, (self.pos[0] + 1, self.pos[1]))],
            #     1: [(self.pos, (self.pos[0] - 1, self.pos[1]))],
            #     2: [(self.pos, (self.pos[0], self.pos[1] + 1))],
            #     3: [(self.pos, (self.pos[0], self.pos[1] - 1))],
            #     }.get(max_index)
        return possible_choices

    def wander(self):
        """
        Medic wanders through field mostly away from base and tries to explore yet haven't found locations
        """

        if len(self.current_path) < 1:
            # get all best choices, shuffle and pick one randomly
            original_path = [[]]
            original_path[0].append(self.pos)
            possible_choices = self.wander_choice_maker(original_path)
            self.current_path = list(random.choice(possible_choices)[1::])

        self.move_agent(self.current_path[0])
        del self.current_path[0]

    def walk(self, point):
        """
        Medic walks straight to a coordinate
        :return:
        """
        x, y = self.pos
        if x > point[0]:
            # moet naar links
            self.move_agent((x-1,y))
        elif x < point[0]:
            # moet naar rechts
            self.move_agent((x + 1, y))
        elif y > point[1]:
            # naar beneden
            self.move_agent((x, y-1))
        elif y < point[1]:
            # naar boven
            self.move_agent((x, y+1))

    def goBase(self):
        """
        Uses shortest path alg to return to base to return patient
        :return:
        """
        self.current_path = ()
        x, y = self.pos
        if self.pos[0] > 0:
            self.move_agent((x - 1, y))
        elif self.pos[1] > 0:
            self.move_agent((x,y-1))

    def step(self):
        """
        Searches for patients and bring them back decided by calculations
        """
        if self.emotional_state <= 0:
            print(f"Medic is traumatized")
            quit()

        if self.model.height * self.model.width == len(self.path) and self.brancard == [] and self.known_p == []:
            print("Simulation has ended.")
            quit()

        print("grid:{}, walked path:{}".format(self.model.height * self.model.width, len(self.path)))
        print(len(self.model.grid.empties))

        cell_cross_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True) # coords
        cell_cross = self.model.grid.get_cell_list_contents(cell_cross_coords)
        own_cell = self.model.grid.get_cell_list_contents([self.pos])
        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

        if len(patient) > 0 and len(self.brancard) == 0:
            pati = None
            for pat in patient:
                pati = pat
                if not pat.dead:
                    self.inspect(pat)
                if len(self.brancard) > 0:
                    break
            patient.remove(pati)

        if len(patient) > 0 and len(self.brancard) > 0: # als er een patient om medic heen staat en de brancard is vol
            for p in patient:
                if p.pos not in [p[0] for p in self.known_p]:
                    if p.pos is None:
                        print(p.unique_id)
                    if not p.dead:
                        self.known_p.append((p.pos, p))

        if len(medcamp) > 0 and len(self.brancard) > 0: # als medic op medcamp staat word brancard geleegd
            medcamp[0].saved_patients.append(self.brancard[0])
            self.brancard = []
            self.pickedup = False

        nb_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)

        if len(self.brancard) > 0: # als de brancard vol is
            self.goBase()
            if self.brancard[0].health == 0:
                print("Patient died")
                self.brancard = []
                self.wander()
                self.pickedup = False

        elif len(self.known_p) > 0: # als er locaties van patient zijn onthouden
            self.walk(self.known_p[0][0])

        if len(self.brancard) == 0 and len(self.known_p) == 0: # als brancard leeg is en er zijn geen bekende plekken van patienten
            self.wander()
            self.pickedup = False

class Patient(Agent):
    """
    Person that is stuck somewhere in the field after a disaster
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.severity = random.randint(1, 5)
        self.health = 100
        self.dead = False

    def step(self):
        self.healthReduce()

    def createHealth(self, gridSize:list):
        healthChart = [100, 80, 60, 40, 20]
        healthScale = random.choice(healthChart)
        #now we finetune it with a std to make it unpredictable
        sizeSteps = 20
        global sizeSteps
        amountSteps = 4
        std = sizeSteps/amountSteps
        self.health = round(np.random.normal(healthScale, std, 1)[0])
        self.externHealth = healthScale #this number is the approximate health that the doctor knows


        # if gridSize[0] > gridSize[1]:
        #     self.health = gridSize[0] / 50 * healthChart[self.severity-1]
        # else:
        #     self.health = gridSize[1] / 50 * healthChart[self.severity-1]
        # self.health = randomHealth
        print(self.health)

    def healthReduce(self):
        if self.health > 0:
            # self.health = self.health + (self.health - 100) / ((self.health - (self.health - 100)) * 10)
            self.health -= 1
        else:
            self.dead = True

class MedCamp(Agent):
    """
    MedCamp is where Medic will start from and go to, to retrieve Patient
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.saved_patients = []

    def step(self):
        pass
