from mesa import Agent
import random

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

        # hier word coords opgeslagen van onderweg gevonden patients en dan met walk gaat de medic daar bij de volgende stap ernaartoe

    def inspect(self, patient):
        """
        Medic inspects patient how severe the situation is and decides then what to do next
        :return:
        """
        print('Patient ' + str(patient.unique_id) + ': ' + str(patient.health) + "hp")
        if self.pos[0] + self.pos[1] >= patient.health and patient.dead == False:
            self.emotional_state = self.emotional_state - 20
            # print("Let's help this guy out of his misery...")
            print("Medic: Omae wa mou, shindeiru\nPatient: NANI???\n*Patient died*")
            patient.health = 0
            patient.dead = True
            # self.model.grid.remove_agent(patient)
        elif patient.dead == False:
            print("Come. this is no place to die")
            self.brancard.append(patient)
            self.pickedup = True
            self.model.grid.remove_agent(patient)

    def wander_choice_maker(self, locations, counter=0):
        choices = {}
        for pos in locations:
            print(list(pos)[-1])
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

        if (len(possible_choices) > 1 and counter < 3) and max(choices.values()) < 1:
            possible_choices = self.wander_choice_maker(possible_choices, counter+1)

        return possible_choices

    def wander(self):
        """
        Medic wanders through field mostly away from base and tries to explore yet haven't found locations
        """
        # todo: gaat opzoek naar vakjes die nog niet bezocht zijn
        if len(self.current_path) < 1:
            # get all best choices, shuffle and pick one randomly
            original_path = [[]]
            original_path[0].append(self.pos)
            possible_choices = self.wander_choice_maker(original_path)
            self.current_path = list(random.choice(possible_choices)[1::])

        self.previous_location = self.pos
        self.model.grid.move_agent(self, self.current_path[0])
        # add new locations to database of known locations
        new_loc = self.model.grid.get_neighborhood(self.current_path[0], moore=False, include_center=True)
        self.path = self.path + list(set(new_loc) - set(self.path))  # removes duplicates
        del self.current_path[0]

    def walk(self, point):
        """
        Medic walks straight to a coordinate
        :return:
        """
        self.current_path = ()
        x, y = self.pos
        if x > point[0]:
            # moet naar links
            self.model.grid.move_agent(self, (x-1,y))
        elif x < point[0]:
            # moet naar rechts
            self.model.grid.move_agent(self, (x+1, y))
        elif y > point[1]:
            # naar beneden
            self.model.grid.move_agent(self, (x, y-1))
        elif y < point[1]:
            # naar boven
            self.model.grid.move_agent(self, (x, y+1))

    def pickupPatient(self, patient):
        """
        Medic inpsects patient and (possibly) picks up patient from field
        """
        self.inspect(patient)

    def goBase(self):
        """
        Uses shortest path alg to return to base to return patient
        :return:
        """
        self.current_path = ()
        x, y = self.pos
        if self.pos[0] > 0:
            self.model.grid.move_agent(self, (x-1,y))
        elif self.pos[1] > 0:
            self.model.grid.move_agent(self, (x,y-1))

    def step(self):
        """
        Searches for patients and bring them back decided by calculations
        """
        if self.emotional_state <= 0:
            print(f"Medic is traumatized")
            quit()
        cell_cross_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True) # coords
        cell_cross = self.model.grid.get_cell_list_contents(cell_cross_coords)
        own_cell = self.model.grid.get_cell_list_contents([self.pos])
        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

        if len(patient) > 0 and len(self.brancard) == 0: # als er een patient om medic heen staat en de brancard is leeg
            self.pickupPatient(patient[0])
            if self.known_p != []:
                for i, p in enumerate(self.known_p):
                    if patient[0] == p[1]:
                        self.known_p.pop(i)
            patient.pop(0)

        if len(patient) > 0 and len(self.brancard) > 0: # als er een patient om medic heen staat en de brancard is vol
            for p in patient:
                if p.pos not in [p[0] for p in self.known_p]:
                    self.known_p.append((p.pos, p))

        if len(medcamp) > 0 and len(self.brancard) > 0: # als medic op medcamp staat word brancard geleegd
            medcamp[0].saved_patients.append(self.brancard[0])
            self.brancard = []
            self.pickedup = False

        nb_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        self.path.extend(nb_coords)

        if len(self.brancard) > 0: # als de brancard vol is
            self.goBase()
            self.brancard[0].healthReduce()
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
        pass

    def createHealth(self, gridSize:list):
        healthChart = [100, 80, 60, 40, 20]
        if gridSize[0] > gridSize[1]:
            self.health = gridSize[0] / 50 * healthChart[self.severity-1]
        else:
            self.health = gridSize[1] / 50 * healthChart[self.severity-1]

    def healthReduce(self):
        if self.health > 0:
            self.health = self.health - 1
        else:
            print("Haha Man I'm dead")
            self.dead = True
            # self.model.grid.remove_agent(self)


class MedCamp(Agent):
    """
    MedCamp is where Medic will start from and go to, to retrieve Patient
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.saved_patients = []

    def step(self):
        pass
