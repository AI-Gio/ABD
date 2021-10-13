from mesa import Agent
import random
import numpy as np
from scipy.stats import norm
import time

global_path = [(0, 0), (0, 1), (1, 0)]
global_known_p = []


class Medic(Agent):
    """
    Searches for patients in the field and brings them back to camp, if statistically possible
    """

    def __init__(self, unique_id, model, mode="None"):
        super().__init__(unique_id, model)
        self.brancard = []  # List to carry Patient Classes
        self.path = [(0, 0), (0, 1), (1, 0)]  # Default path list
        self.known_p = []  # List to save patients Class and location
        self.current_path = ()

        self.pickedup = False  # When picked up this becomes True, to prevent multiple patients to pickup
        self.traumatizedMessage = False  # When traumatized this becomes True, to prevent multiple traumatize messages
        self.previous_location = None  # When moving this becomes his former coordinates

        self.emotional_state = 100  # Emotional state number of the medic
        self.mode = mode
        global global_path
        global_path = [(0, 0), (0, 1), (1, 0)]
        global global_known_p
        global_known_p = []
        self.global_path = global_path
        self.known_p_removed = []

    def move_agent(self, location):
        self.previous_location = self.pos
        self.model.grid.move_agent(self, location)
        new_loc = self.model.grid.get_neighborhood(location, moore=False, include_center=True)
        self.path = self.path + (list(set(new_loc) - set(self.path)))  # removes duplicates

    def sort_known_patients(self):
        sorted_patients = []
        for patient in self.known_p:
            score = 0
            score -= abs(patient[0][0] - self.pos[0]) + abs(patient[0][1] - self.pos[1])
            score -= patient[0][0] + patient[0][1]
            sorted_patients.append(patient + tuple([score]))

        sorted_patients = sorted(sorted_patients, key=lambda x: x[2], reverse=True)
        self.known_p = [sublist[:-1] for sublist in sorted_patients]

    def merge_info(self):
        global global_path
        global global_known_p
        global_path = global_path + (list(set(self.path) - set(global_path)))  # removes duplicates
        self.path = self.path + (list(set(global_path) - set(self.path)))  # removes duplicates

        # haalt uit global_known_p eerst weg wat in self.known_p_removed zit
        l3 = [x for x in global_known_p if x not in self.known_p_removed]
        global_known_p = l3
        # merge dan alles
        global_known_p = global_known_p + list(set(self.known_p) - set(global_known_p))
        self.known_p = global_known_p
        self.sort_known_patients()

    def share_info(self):
        global global_path
        global global_known_p
        global_path = global_path + (list(set(self.path) - set(global_path)))  # removes duplicates
        global_known_p = self.known_p

    def get_info(self):
        global global_path
        global global_known_p
        self.path = self.path + (list(set(global_path) - set(self.path)))  # removes duplicates
        self.known_p = global_known_p
        self.sort_known_patients()

    def inspect(self, patient):
        """
        Medic inspects patient how severe the situation is and decides then what to do next
        :return:
        """
        print('Patient ' + str(patient.unique_id) + ': ' + str(patient.trueHealth) + "hp")
        z_scores = (patient.externHealth - self.pos[0] + self.pos[1]) / ((1 / 3) * 10)
        distance_reach_chance = norm.cdf(z_scores)
        pickup = random.choices(population=[True, False], weights=[distance_reach_chance, 1 - distance_reach_chance])[0]
        if not pickup and not patient.dead:  # als niet pickup en patient is niet dood dan
            return

        elif not patient.dead:
            print("Come. this is no place to die")
            if self.known_p:
                for i, p in enumerate(self.known_p):
                    if patient == p[1]:
                        self.known_p.pop(i)
                        self.known_p_removed.append(i)
                        if self.mode == "constant_info_share":
                            self.share_info()
            self.brancard.append(patient)
            self.pickedup = True
            self.model.grid.remove_agent(patient)

    def wander_choice_maker(self, locations, counter=0):
        """

        """
        choices = {}
        for pos in locations:
            surraw = [(list(pos)[-1][0], list(pos)[-1][1] + 1), (list(pos)[-1][0], list(pos)[-1][1] - 1),
                      (list(pos)[-1][0] + 1, list(pos)[-1][1]), (list(pos)[-1][0] - 1, list(pos)[-1][1])]
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
            possible_choices = self.wander_choice_maker(possible_choices, counter + 1)
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

        print(self.current_path)
        print(self.current_path[0])
        self.move_agent(self.current_path[0])
        # print(self.current_path[0], self.unique_id)
        del self.current_path[0]

    def walk(self, point):
        """
        Medic walks straight to a coordinate
        :return:
        """
        x, y = self.pos
        if x > point[0]:
            # moet naar links
            self.move_agent((x - 1, y))
        elif x < point[0]:
            # moet naar rechts
            self.move_agent((x + 1, y))
        elif y > point[1]:
            # naar beneden
            self.move_agent((x, y - 1))
        elif y < point[1]:
            # naar boven
            self.move_agent((x, y + 1))

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
            self.move_agent((x, y - 1))

    def step(self):
        """
        Searches for patients and bring them back decided by calculations
        """
        if self.emotional_state <= 0 and self.traumatizedMessage is False:
            print("Medic " + str(self.unique_id) + " is traumatized")
            self.traumatizedMessage = True
            return

        if self.emotional_state <= 0:
            return

        if self.model.height * self.model.width == len(self.path) and self.brancard == [] and self.known_p == []:
            print("Simulation has ended.")
            return

        cell_cross_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)  # coords
        cell_cross = self.model.grid.get_cell_list_contents(cell_cross_coords)
        own_cell = self.model.grid.get_cell_list_contents([self.pos])
        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

        if self.mode == "constant_info_share":
            self.get_info()

        if self.mode == "info_share_medbase" and len(medcamp) > 0:
            self.merge_info()

        if self.mode == "info_share_meet":
            medics = [obj for obj in cell_cross if isinstance(obj, Medic)]
            scouts = [obj for obj in cell_cross if isinstance(obj, Scout)]
            medics_and_scouts = medics + scouts
            for ms in medics_and_scouts:
                self.known_p_removed = self.known_p_removed + (
                    list(set(ms.known_p_removed) - set(self.known_p_removed)))
                l3 = [x for x in ms.known_p if x not in self.known_p_removed]
                self.known_p = self.known_p + (list(set(l3) - set(self.known_p)))  # removes duplicatess
                self.path = self.path + (list(set(ms.path) - set(self.path)))  # removes duplicates
                self.sort_known_patients()

        if len(patient) > 0 and len(self.brancard) == 0:
            pati = None
            for pat in patient:
                pati = pat
                if not pat.dead:
                    self.inspect(pat)
                if pat.dead:
                    self.known_p_removed.append((pat.pos, pat))
                if len(self.brancard) > 0:
                    break
            patient.remove(pati)

        if len(patient) > 0 and len(self.brancard) > 0:  # als er een patient om medic heen staat en de brancard is vol
            for p in patient:
                if p.pos not in [i[0] for i in self.known_p]:
                    if p.pos is None:
                        print(p.unique_id)
                    if not p.dead:
                        self.known_p.append((p.pos, p))
                        self.sort_known_patients()
                    if p.dead:
                        if (p.pos, p) in self.known_p:
                            self.known_p.remove((p.pos, p))
                        self.known_p_removed.append((p.pos, p))

        if len(medcamp) > 0 and len(self.brancard) > 0:  # als medic op medcamp staat word brancard geleegd
            medcamp[0].saved_patients.append(self.brancard[0])
            self.brancard[0].in_medcamp = True
            self.brancard = []
            self.pickedup = False

        if len(self.brancard) > 0:  # als de brancard vol is
            self.goBase()
            if self.brancard[0].trueHealth == 0:
                self.emotional_state -= 20
                self.model.grid.place_agent(self.brancard[0], self.pos)
                self.brancard[0].dead = True
                self.known_p.remove((self.pos, self.brancard[0]))
                self.known_p_removed.append((self.pos, self.brancard[0]))

                print("Patient died")
                self.brancard = []
                self.wander()
                self.pickedup = False

        elif len(self.known_p) > 0:  # als er locaties van patient zijn onthouden
            if (self.known_p[0][0] == self.pos and self.known_p[0][1] not in own_cell) or (
                    self.known_p[0][0] == self.pos and self.known_p[0][1].dead):
                self.known_p_removed.append(self.known_p[0])
                self.known_p.pop(0)
            else:
                print(self.known_p)
                self.walk(self.known_p[0][0])

        # als brancard leeg is en er zijn geen bekende plekken van patienten
        if len(self.brancard) == 0 and len(self.known_p) == 0:
            self.wander()
            self.pickedup = False

        if self.mode == "constant_info_share" or (self.mode == "info_share_medbase" and len(medcamp) > 0):
            self.share_info()


class Patient(Agent):
    """
    Person that is stuck somewhere in the field after a disaster
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.severity = random.randint(0, 4)
        self.dead = False
        self.in_medcamp = False

    def step(self):
        if not self.in_medcamp:
            self.healthReduce()

    def createHealth(self, gridSize: list):
        """
        creates healthChart by using the gridsize to setup a max and min
        creates externhealth (the health that a doctor can see)
        creates truehealth (the health that a patient really has)
        """
        healthChart = list(reversed([gridSize[0] * i for i in range(1, 6)]))
        self.externHealth = healthChart[self.severity]
        self.trueHealth = np.random.normal(self.externHealth, 1 / 3, 1)[0]

    def healthReduce(self):
        """
        Patient reduces health every step by 0.1 until it dies
        """
        if self.trueHealth > 0:
            self.externHealth -= 0.1
            self.trueHealth -= 0.1
        else:
            self.dead = True


class Scout(Agent):
    def __init__(self, unique_id, model, mode="None"):
        super().__init__(unique_id, model)
        self.known_p = []
        self.path = []
        self.amount_found_p = 0  # connected to the found_p but get it's length
        self.current_path = ()
        self.previous_location = None
        self.stamina = 600  # amount of steps before it's out of stamina
        self.outMessage = False  # if out of stamina
        self.known_p_removed = []

        self.mode = mode

    def move_agent(self, location):
        """
        Saves his current place and moves to his surroundings (get_neighborhood) and saves it in path
        """
        self.previous_location = self.pos
        self.model.grid.move_agent(self, location)
        new_loc = self.model.grid.get_neighborhood(location, moore=False, include_center=True)
        self.path = self.path + (list(set(new_loc) - set(self.path)))  # removes duplicates

    def merge_info(self):
        global global_path
        global global_known_p
        global_path = global_path + (list(set(self.path) - set(global_path)))  # removes duplicates
        self.path = self.path + (list(set(global_path) - set(self.path)))  # removes duplicates

        # haalt uit global_known_p eerst weg wat in self.known_p_removed zit
        l3 = [x for x in global_known_p if
              x not in self.known_p_removed]  # https://stackoverflow.com/questions/4211209/remove-all-the-elements-that-occur-in-one-list-from-another
        global_known_p = l3
        # merge dan alles
        global_known_p = global_known_p + list(set(self.known_p) - set(global_known_p))
        self.known_p = global_known_p

    def share_info(self):
        """
        adds self path and known_p into a global variable so other agents can see it and use it
        """
        global global_path
        global global_known_p
        global_path = global_path + (list(set(self.path) - set(global_path)))  # removes duplicates
        global_known_p = self.known_p

    def get_info(self):
        global global_path
        global global_known_p
        self.path = self.path + (list(set(global_path) - set(self.path)))  # removes duplicates
        self.known_p = global_known_p

    def wander(self):
        """
        Scout wanders through field mostly away from base and tries to explore yet haven't found locations
        """

        if len(self.current_path) < 1:
            # get all best choices, shuffle and pick one randomly
            original_path = [[]]
            original_path[0].append(self.pos)
            possible_choices = self.wander_choice_maker(original_path)
            self.current_path = list(random.choice(possible_choices)[1::])

        self.move_agent(self.current_path[0])
        del self.current_path[0]

    def wander_choice_maker(self, locations, counter=0):
        choices = {}
        for pos in locations:
            surraw = [(list(pos)[-1][0], list(pos)[-1][1] + 1), (list(pos)[-1][0], list(pos)[-1][1] - 1),
                      (list(pos)[-1][0] + 1, list(pos)[-1][1]), (list(pos)[-1][0] - 1, list(pos)[-1][1])]
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
            possible_choices = self.wander_choice_maker(possible_choices, counter + 1)
        return possible_choices

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
            self.move_agent((x, y - 1))

    def step(self):
        for x in range(2):

            if self.stamina > 0:
                self.stamina = self.stamina - 1
            cell_cross_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)  # coords
            cell_cross = self.model.grid.get_cell_list_contents(cell_cross_coords)
            own_cell = self.model.grid.get_cell_list_contents([self.pos])
            patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
            medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

            if self.mode == "constant_info_share":
                self.get_info()

            if self.mode == "info_share_meet":
                medics = [obj for obj in cell_cross if isinstance(obj, Medic)]
                scouts = [obj for obj in cell_cross if isinstance(obj, Scout)]
                medics_and_scouts = medics + scouts
                for ms in medics_and_scouts:
                    self.known_p_removed = self.known_p_removed + (
                        list(set(ms.known_p_removed) - set(self.known_p_removed)))
                    l3 = [x for x in ms.known_p if x not in self.known_p_removed]
                    self.known_p = self.known_p + (list(set(l3) - set(self.known_p)))  # removes duplicatess
                    self.path = self.path + (list(set(ms.path) - set(self.path)))  # removes duplicates

            if self.mode == "info_share_medbase" and self.stamina <= 0 and len(medcamp) <= 0:
                self.goBase()

                if self.outMessage is False:
                    print("Scout " + str(self.unique_id) + " is out")
                    self.outMessage = True

            if len(patient) == 0 and self.stamina > 0:
                self.wander()

            elif len(patient) > 0:
                for p in patient:
                    if p.pos not in [i[0] for i in self.known_p]:
                        if p.pos is None:
                            print(p.unique_id)
                        if not p.dead:
                            self.known_p.append((p.pos, p))
                            self.amount_found_p = self.amount_found_p + 1
                        if p.dead:
                            if (p.pos, p) in self.known_p:
                                self.known_p.remove((p.pos, p))
                            self.known_p_removed.append((p.pos, p))
                self.wander()

            elif len(medcamp) == 1:
                pass

            if self.mode == "constant_info_share":
                self.share_info()

            if (self.mode == "info_share_medbase" and len(medcamp) > 0):
                self.merge_info()


class MedCamp(Agent):
    """
    MedCamp is where Medic will start from and go to, to retrieve Patient
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.saved_patients = []
        self.field = []

    def step(self):
        pass
