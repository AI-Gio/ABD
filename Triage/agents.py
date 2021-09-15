from mesa import Agent

class Medic(Agent):
    """
    Medic walks around the grid to find patients, to obtain the cure/radio and to cure patients
    Medic dies when it gets on patients square
    """
    def __init__(self, pos, model, moore=False):
        super().__init__(pos, model)
        self.pos = pos
        self.moore = moore

    def move(self):
        """
        :return:
        """
        # TODO: here must come the logic from the medic what to do based on information of the past and informations surrounding him

    def step(self):
        # self.move()

        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        medic = [obj for obj in this_cell if isinstance(obj, Medic)]


class Patient(Agent):
    """
    Patient has an uncurable disease that makes him very agressive and dangarous towards Medic
    Patient kills Medic if he doesnt have the cure
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.cured = False

    def step(self):
        """
        Patient kills Medic if on same pos
        """
        pass
class Cure(Agent):
    """
    Cure/Radio/Static/Scream
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass

class Radio(Agent):
    """
    Cure/Radio/Static/Scream
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass

class Static(Agent):
    """
    Cure/Radio/Static/Scream
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass

class Scream(Agent):
    """
    Cure/Radio/Static/Scream
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass