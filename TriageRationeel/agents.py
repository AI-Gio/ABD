from mesa import Agent


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

    def inspect(self):
        """
        Medic inspects patient how severe the situation is and decides then what to do next
        :return:
        """
        # todo: hier komt assesment of patient meegenomen moet worden terug naar kamp of niet
        pass

    def wander(self):
        """
        Medic wanders through field mostly away from base and tries to explore yet haven't found locations
        """
        # todo: gaat opzoek naar vakjes die nog niet bezocht zijn
        pass

    def walk(self):
        """
        Medic walks straight to a coordinate
        :return:
        """
        # todo: medic loopt ergens naar een punt straight toe
        pass

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
        while self.pos != (0.0):
            if [self.pos[0] - 1, self.pos[1]] in self.path:
                self.model.grid.move_agent(self, (self.pos[0] - 1, self.pos[1])) #naar links als het pad er is
            elif [self.pos[0], self.pos[1] - 1] in self.path:
                self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - 1))#naar onder als het pad er is
            elif self.pos[0] > 0:
                self.model.grid.move_agent(self, (self.pos[0] - 1, self.pos[1]))#naar links als de coordinaten meer zijn dan 0
            else:
                self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - 1))#naar onder
        # todo: Medic gaat meteen met shortest path naar medcamp
        pass

    def step(self):
        """
        Searches for patients and bring them back decided by calculations
        """
        # todo: keuze gemaakt worden of patient terug gebracht word of niet
        # every interaction is going to be coded here
        if len(self.brancard) > 0:
            self.goBase()
            if self.brancard[0].health == 0:
                self.brancard = []
                self.wander()

        if len(self.known_p) > 0:
            self.walk()

        nb_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        self.path.extend(nb_coords)

        cell_cross = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        own_cell = self.model.grid.get_cell_list_contents([self.pos])

        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

        if len(patient) > 0:
            self.pickupPatient(patient[0])

        if len(medcamp) > 0:
            self.brancard = []


class Patient(Agent):
    """
    Person that is stuck somewhere in the field after a disaster
    """
    def __int__(self, unique_id, model, severity: int):
        super().__init__(unique_id, model)
        self.severity = severity
        # todo: patient heeft een type severity en met die severity krijgt hij ook een health (prob met formule)

    def step(self):
        pass

class MedCamp(Agent):
    """
    MedCamp is where Medic will start from and go to, to retrieve Patient
    """
    # todo: here are the patients being counted that are retrieved so that you can hover over medcamp in sim and see that number
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
