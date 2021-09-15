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
        self.cure_poss = None

    def move(self):
        """
        :return:
        """
        # TODO: here must come the logic from the medic what to do based on information of the past and informations surrounding him

    def step(self):
        """
        Own actions of Medic
        :return:
        """
        # self.move()

        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])

        # Medic is on one of the instances
        patient = [obj for obj in this_cell if isinstance(obj, Patient)]
        radio = [obj for obj in this_cell if isinstance(obj, Radio)]
        static = [obj for obj in this_cell if isinstance(obj, Static)]
        scream = [obj for obj in this_cell if isinstance(obj, Scream)]

        # g = self.model.grid.coord_iter()
        # print(list(g))

        if len(patient) > 0:
            self.model.grid.remove_agent(self)
            print("You lost!")
            quit()

        # als je radio hebt dan krijg je coords van de cure
        elif len(radio) > 0:
            g = self.model.grid.coord_iter()
            for (obj, x, y) in g:
                if len(obj) > 0:
                    if isinstance(obj[0], Cure):
                        self.cure_poss = (x, y)
                        print(f"Cure is at {self.cure_poss}")
                    else:
                        continue












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