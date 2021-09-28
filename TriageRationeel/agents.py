from mesa import Agent
import random

class Medic(Agent):
    """
    Searches for patients in the field and brings them back to camp, if statistically possible
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.brancard = []
        self.path = []
        self.known_p = []
        # hier word coords opgeslagen van onderweg gevonden patients en dan met walk gaat de medic daar bij de volgende stap ernaartoe

    def inspect(self, patient):
        """
        Medic inspects patient how severe the situation is and decides then what to do next
        :return:
        """
        if self.pos[0] + self.pos[1] > patient.status:
            print("Fuck this guy")
        else:
            print("Come. this is no place to die")
        # todo: hier komt assesment of patient meegenomen moet worden terug naar kamp of niet
        pass

    def wander(self, surround):
        """
        Medic wanders through field mostly away from base and tries to explore yet haven't found locations
        """
        # todo: gaat opzoek naar vakjes die nog niet bezocht zijn
        choices = {}
        for loc in surround:
            sursuround = self.model.grid.get_neighborhood(loc, moore=False, include_center=True)
            score = 0
            for surloc in sursuround:
                if surloc not in self.path:
                    score += 1
            choices[loc] = score

        # get all best choices, shuffle and pick one randomly
        possible_choices = [k for k, v in choices.items() if v == max(choices.values())]
        choice = random.choice(possible_choices)
        self.model.grid.move_agent(self, choice)

        # add new locations to database of known locations
        new_loc = self.model.grid.get_neighborhood(choice, moore=False, include_center=True)
        self.path = self.path + list(set(new_loc) - set(self.path))  # removes duplicates

    def walk(self, point): # point = (3,3)
        """
        Medic walks straight to a coordinate
        :return:
        """
        if self.pos[0] != point[0]:
            if point[0] - self.pos[0] > 0 and (self.pos[0] + 1, self.pos[1]) in self.path: #naar rechts moet en op pad
                self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1]))
            elif point[0] - self.pos[0] < 0 and (self.pos[0] - 1, self.pos[1]) in self.path:#naar links moet en op pad
                self.model.grid.move_agent(self, (self.pos[0] - 1, self.pos[1]))
            elif point[1] - self.pos[1] > 0 and (self.pos[0], self.pos[1] + 1) in self.path:#naar boven moet en op pad
                self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1] + 1))
            elif point[1] - self.pos[1] < 0 and (self.pos[0], self.pos[1] - 1) in self.path:#naar onder moet en op pad
                self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1] - 1))

            elif point[0] - self.pos[0] > 0 and (self.pos[0] + 1, self.pos[1]) in self.path: #naar rechts moet
                self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1]))
            elif point[0] - self.pos[0] < 0 and (self.pos[0] - 1, self.pos[1]) in self.path:#naar links moet
                self.model.grid.move_agent(self, (self.pos[0] - 1, self.pos[1]))
            elif point[1] - self.pos[1] > 0 and (self.pos[0], self.pos[1] + 1) in self.path:#naar boven moet
                self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1] + 1))
            elif point[1] - self.pos[1] < 0 and (self.pos[0], self.pos[1] - 1) in self.path:#naar onder moet
                self.model.grid.move_agent(self, (self.pos[0] + 1, self.pos[1] - 1))
        # x, y = self.pos


        # todo: medic loopt ergens naar een punt straight toe

    def pickupPatient(self, patient):
        """
        Medic picks up patient from field
        """
        # todo: patient word opgepakt en toegevoegd aan brancard
        self.brancard.append(patient)
        self.model.grid.remove_agent(patient)    # not sure if patient is still in schedule after removing

    def goBase(self):
        """
        Uses shortest path alg to return to base to return patient
        :return:
        """
        # todo: Medic gaat meteen met shortest path naar medcamp
        x, y = self.pos
        if self.pos[0] > 0:
            self.model.grid.move_agent(self, (x-1,y))
        elif self.pos[1] > 0:
            self.model.grid.move_agent(self, (x,y-1))


    def step(self):
        """
        Searches for patients and bring them back decided by calculations
        """
        # todo: keuze gemaakt worden of patient terug gebracht word of niet
        # every interaction is going to be coded here
        nb_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        self.path.extend(nb_coords)

        if len(self.brancard) > 0:
            self.goBase()
            self.brancard[0].healthReduce()
            if self.brancard[0].health == 0:
                self.brancard = []
                self.wander()

        if len(self.known_p) > 0:
            self.walk(self.known_p[0])#

        if len(self.brancard) == 0 and len(self.known_p) == 0:
            self.wander(nb_coords)

        cell_cross = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        own_cell = self.model.grid.get_cell_list_contents([self.pos])

        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

        if len(patient) > 0 and len(self.brancard) == 0:
            self.pickupPatient(patient[0])
        elif len(patient) > 0 and len(self.brancard) > 0:
             self.known_p.append(patient[0].pos)

        if len(medcamp) > 0:
            self.brancard = []


class Patient(Agent):
    """
    Person that is stuck somewhere in the field after a disaster
    """
    health = 100
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.severity = random.randint(1, 5)

        # todo: patient heeft een type severity en met die severity krijgt hij ook een health (prob met formule)

    def step(self):
        pass

    def createHealth(self, gridSize:list):
        healthChart = [100, 80, 60, 40, 20]
        if gridSize[0] > gridSize[1]:
            self.health = gridSize[0] / 100 * healthChart[self.severity-1]
        else:
            self.health = gridSize[1] / 100 * healthChart[self.severity-1]

    def healthReduce(self):
        if self.health > 0:
            self.health = self.health - 1
        else:
            print("Haha Man I'm dead")

class MedCamp(Agent):
    """
    MedCamp is where Medic will start from and go to, to retrieve Patient
    """
    # todo: here are the patients being counted that are retrieved so that you can hover over medcamp in sim and see that number
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
