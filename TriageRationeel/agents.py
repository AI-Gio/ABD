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

    def inspect(self):
        """
        Medic inspects patient how severe the situation is and decides then what to do next
        :return:
        """
        pass

    def wander(self):
        """
        Medic wanders through field mostly away from base and tries to explore yet haven't found locations
        """
        # todo:
        pass

    def walk(self):
        """
        Medic
        :return:
        """
        pass

    def pickupPatient(self):
        """
        Medic picks up patient from field
        :return:
        """
        pass

    def percieve(self):
        """
        Gets information from squares surrounding him
        :return:
        """
        pass

    def goBase(self):
        """
        Uses shortest path alg to return to base to return patient
        :return:
        """
        pass

    def step(self):
        """
        Searches for patients and bring them back decided by calculations
        """
        if len(self.brancard) > 0:
            self.goBase()

        else:
            pass

        nb_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        self.path.extend(nb_coords)

        cell_cross = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        own_cell = self.model.grid.get_cell_list_contents([self.pos])

        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

        if len(patient) > 0:
            self.pickupPatient()

        if len(medcamp) > 0:
            self.brancard = []







class Patient(Agent):
    """
    Person that is stuck somewhere in the field after a disaster
    """
    def __int__(self, unique_id, model, severity: int):
        super().__init__(unique_id, model)
        self.severity = severity
        # todo: hier moet iets van een calc komen hoeveel vakjes de patient heeft voordat hij dood gaat

    def step(self):
        pass

class MedCamp(Agent):
    """
    MedCamp is where Medic will start from and go to, to retrieve Patient
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
