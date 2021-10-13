from mesa import Agent
import random
import numpy as np
from scipy.stats import norm
import gc

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
        """
        Saves his current place and moves to his surroundings (get_neighborhood) and saves it in path
        """
        self.previous_location = self.pos
        self.model.grid.move_agent(self, location)
        new_loc = self.model.grid.get_neighborhood(location, moore=False, include_center=True)
        self.path = self.path + (list(set(new_loc) - set(self.path)))  # removes duplicates

    def sort_known_patients(self):
        """
        sorts the known patients list by how long it will take to get them to the
        medic base.
        """
        sorted_patients = []
        for patient in self.known_p:
            score = 0
            score -= abs(patient[0][0] - self.pos[0]) + abs(patient[0][1] - self.pos[1])  # how far away the patient is from medic
            score -= patient[0][0] + patient[0][1]  # how far away the patient is from medic base
            sorted_patients.append(patient + tuple([score]))  # add patient with score to a list

        sorted_patients = sorted(sorted_patients, key=lambda x: x[2], reverse=True)  # sort the list by the score
        self.known_p = [sublist[:-1] for sublist in sorted_patients]  # updates known patients with sorted list minus the scores

    def merge_info(self):
        """
        When meeting another medic/scout or stores its info at the medic base, this function will
        correctly merge all information. All known locations are simply merged, and the locations
        of patients are scanned to determine wether a patient location is still relevant. Irrelevant
        patient locations are removed.
        """
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
        l3 = []

    def share_info(self):
        """
        adds self path and known_p into a global variable so other agents can see it and use it
        """
        global global_path
        global global_known_p
        global_path = global_path + (list(set(self.path) - set(global_path)))  # removes duplicates
        global_known_p = self.known_p

    def get_info(self):
        """
        retrieves the information in global variables that have been adapted by other agents, and puts it in
        its own respective variables.
        """
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
        Calculates which direction the agent should go. The agent will look at each
        direction and see which direction will theoretically give the most new information.
        If multiple directions are winners, the agent will look a step further within those
        directions and then calculate which path gives the most information.

        Parameters
        ----------
            counter (int): How many steps ahead the agent is allowed to look
            locations (list(list(tuple)))): directions/paths to calculate from

        Returns
        -------
             possible_choices: A list of paths
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
        Scout wanders through field and tries to explore yet haven't found locations, if best location paths
        are multiple steps long, the agent will go through the entire path first.
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

        # message played once when medic is out of the game
        if self.emotional_state <= 0 and self.traumatizedMessage is False:
            print("Medic " + str(self.unique_id) + " is traumatized")
            self.traumatizedMessage = True
            return

        # Medic will stop doing anything if emotional state is below 0
        if self.emotional_state <= 0:
            return

        # Medic will stop doing anything if it knows everything and has nothing to do or explore
        if self.model.height * self.model.width == len(self.path) and self.brancard == [] and self.known_p == []:
            print("Simulation has ended.")
            return

        # get contents and information of surrounding
        cell_cross_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)  # coords
        cell_cross = self.model.grid.get_cell_list_contents(cell_cross_coords)  # contents
        own_cell = self.model.grid.get_cell_list_contents([self.pos])  # own cell contents
        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]  # patient classes in surrounding
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]  # medcamp classes on location

        # mode when constantly sharing information with all other agents
        if self.mode == "constant_info_share":
            self.get_info()

        # mode of sharing information whenever an agent is at the medic base
        if self.mode == "info_share_medbase" and len(medcamp) > 0:
            self.merge_info()

        # mode of sharing information with all other agents when met
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

        # if there is a petient around the medic but the brancard is not full
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

        # if there is a petient around the medic but the brancard is full
        if len(patient) > 0 and len(self.brancard) > 0:
            for p in patient:
                if p.pos not in [i[0] for i in self.known_p]:
                    if not p.dead:
                        self.known_p.append((p.pos, p))
                        self.sort_known_patients()
                    if p.dead:
                        if (p.pos, p) in self.known_p:
                            self.known_p.remove((p.pos, p))
                        self.known_p_removed.append((p.pos, p))

        # if the medic is on the medic base the brancard gets emptied
        if len(medcamp) > 0 and len(self.brancard) > 0:
            medcamp[0].saved_patients_amount += 1
            self.brancard[0].in_medcamp = True
            self.brancard = []
            self.pickedup = False

        # if the brancard is contains a patient
        if len(self.brancard) > 0:
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

        # if there are known locations containing patients
        elif len(self.known_p) > 0:
            if (self.known_p[0][0] == self.pos and self.known_p[0][1] not in own_cell) or (
                    self.known_p[0][0] == self.pos and self.known_p[0][1].dead):
                self.known_p_removed.append(self.known_p[0])
                self.known_p.pop(0)
            else:
                self.walk(self.known_p[0][0])

        # if the brancard is empty and there ar no known places with patients
        if len(self.brancard) == 0 and len(self.known_p) == 0:
            self.wander()
            self.pickedup = False

        if self.mode == "constant_info_share" or (self.mode == "info_share_medbase" and len(medcamp) > 0):
            self.share_info()

        gc.collect()


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
    """
    Scout agent, cannot save patients but can move much faster than a medic, main job
    is to gather information.
    """
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
        """
        When meeting another medic/scout or stores its info at the medic base, this function will
        correctly merge all information. All known locations are simply merged, and the locations
        of patients are scanned to determine wether a patient location is still relevant. Irrelevant
        patient locations are removed.
        """
        global global_path
        global global_known_p
        global_path = global_path + (list(set(self.path) - set(global_path)))  # removes duplicates
        self.path = self.path + (list(set(global_path) - set(self.path)))  # removes duplicates

        # haalt uit global_known_p eerst weg wat in self.known_p_removed zit
        l3 = [x for x in global_known_p if
              x not in self.known_p_removed]
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
        """
        retrieves the information in global variables that have been adapted by other agents, and puts it in
        its own respective variables.
        """
        global global_path
        global global_known_p
        self.path = self.path + (list(set(global_path) - set(self.path)))  # removes duplicates
        self.known_p = global_known_p

    def wander(self):
        """
        Scout wanders through field and tries to explore yet haven't found locations, if best location paths
        are multiple steps long, the agent will go through the entire path first.
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
        """
        Calculates which direction the agent should go. The agent will look at each
        direction and see which direction will theoretically give the most new information.
        If multiple directions are winners, the agent will look a step further within those
        directions and then calculate which path gives the most information.

        Parameters
        ----------
            counter (int): How many steps ahead the agent is allowed to look
            locations (list(list(tuple)))): directions/paths to calculate from

        Returns
        -------
             possible_choices: A list of paths
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

    def goBase(self):
        """
        Uses shortest path alg to return to base to return patient
        """
        self.current_path = ()
        x, y = self.pos
        if self.pos[0] > 0:
            self.move_agent((x - 1, y))
        elif self.pos[1] > 0:
            self.move_agent((x, y - 1))

    def step(self):
        """
        One step of the Scout, function is run multiple times each step in the simulation to increase the scout speed.
        """
        for x in range(2):

            if self.stamina > 0:
                self.stamina = self.stamina - 1

            # get contents and information of surrounding
            cell_cross_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)  # coords
            cell_cross = self.model.grid.get_cell_list_contents(cell_cross_coords)  # contents
            own_cell = self.model.grid.get_cell_list_contents([self.pos])  # own cell contents
            patient = [obj for obj in cell_cross if isinstance(obj, Patient)]  # patient classes in surrounding
            medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]  # medcamp classes on location

            # mode when constantly sharing information with all other agents
            if self.mode == "constant_info_share":
                self.get_info()

            # mode of sharing information with all other agents when met
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

            # mode of sharing information whenever an agent is at the medic base
            if self.mode == "info_share_medbase" and self.stamina <= 0 and len(medcamp) <= 0:
                self.goBase()  # when the stamina is low the scout will go to the medic base

                # message played once when scout is out of the game
                if self.outMessage is False:
                    print("Scout " + str(self.unique_id) + " is out")
                    self.outMessage = True

            # will only wander when there no patients in their surrounding
            if len(patient) == 0 and self.stamina > 0:
                self.wander()

            # will save info of patient when found
            elif len(patient) > 0:
                for p in patient:
                    if p.pos not in [i[0] for i in self.known_p]:
                        if not p.dead:
                            self.known_p.append((p.pos, p))
                            self.amount_found_p = self.amount_found_p + 1
                        if p.dead:
                            if (p.pos, p) in self.known_p:
                                self.known_p.remove((p.pos, p))
                            self.known_p_removed.append((p.pos, p))
                self.wander()  # wander after information gathering

            elif len(medcamp) == 1:
                pass

            # mode when constantly sharing information with all other agents
            if self.mode == "constant_info_share":
                self.share_info()

            # mode of sharing information whenever an agent is at the medic base
            if self.mode == "info_share_medbase" and len(medcamp) > 0:
                self.merge_info()


class MedCamp(Agent):
    """
    MedCamp is where Medic will start from and go to, to retrieve Patient or to store
    information.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.saved_patients_amount = 0
        self.field = []

    def step(self):
        pass
