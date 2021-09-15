from mesa import Agent
import random


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
        self.radio_possible = [] # hier komen coords in waar mogelijk radio is
        self.patient_possible = [] # hier komen coords in waar mogelijk patient is
        self.pos_patients = [] # de posities van de patients wanneer cure is gevonden
        self.path = [] # format = ((x,y))
        self.curr_cell_status = None

    def move(self):
        """
        :return:
        """
        # x,y = self.pos
        # self.model.grid.move_agent(self, (x+1,y))

        # if self.curr_cell_status is None:
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, False)
        next_move = random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)

        # if self.curr_cell_status is Static:


        # TODO: here must come the logic from the medic what to do based on information of the past and informations surrounding him


    def step(self):
        """
        Own actions of Medic
        :return:
        """
        self.move()
        print(self.pos)
        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        self.path.append((x,y))

        # Medic is on one of the instances
        patient = [obj for obj in this_cell if isinstance(obj, Patient)]
        radio = [obj for obj in this_cell if isinstance(obj, Radio)]
        static = [obj for obj in this_cell if isinstance(obj, Static)]
        scream = [obj for obj in this_cell if isinstance(obj, Scream)]
        cure = [obj for obj in this_cell if isinstance(obj, Cure)]

        g = self.model.grid.coord_iter()


        if len(patient) > 0:
            self.curr_cell_status = Patient
            self.model.grid.remove_agent(self)
            print("You lost!")
            quit()

        # als je radio hebt dan krijg je coords van de cure
        if len(radio) > 0:
            self.curr_cell_status = Radio
            self.radio_possible = []
            g = self.model.grid.coord_iter()
            for (obj, x, y) in g:
                if len(obj) > 0:
                    if isinstance(obj[0], Cure):
                        self.cure_poss = (x, y)
                        print(f"Cure is at {self.cure_poss}")
                    else:
                        continue

        # als je cure hebt dan krijg je de coords van de patienten
        if len(cure) > 0 :
            print("Cure")
            self.curr_cell_status = Cure
            g = self.model.grid.coord_iter()
            for (obj, x, y) in g:
                if len(obj) > 0:
                    if isinstance(obj, Patient):
                        self.pos_patients.append((x,y))
                    else:
                        continue


        # als je static tegenkomt dan zijn een van de vakjes radio, op von nuemann manier
        if len(static) > 0:
            self.curr_cell_status = Static
            print("Static")
            nb = self.model.grid.get_neighborhood(
                self.pos,
                moore=False,
                include_center=False
            )
            # look through neighbors poss and remove ones that are known in path
            for n in nb:
                if n in self.path:
                    continue
                else:
                    self.radio_possible.append(n)

        # als je scream tegenkomt dan zijn een van de vakjes patient, op von nuemann manier
        if len(scream) > 0:
            self.curr_cell_status = Scream
            print("Scream")
            nb = self.model.grid.get_neighborhood(
                self.pos,
                moore=False,
                include_center=False,
            )
            # look through neighbors poss and remove ones that are known in path
            for n in nb:
                if n in self.path:
                    continue
                else:
                    self.patient_possible.append(n)
        else:
            self.curr_cell_status = None


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
    Cure can be obtained by Medic
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass

class Radio(Agent):
    """
    Radio gives info about the location of the cure
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass

class Static(Agent):
    """
    Static surrounds radio with von nuemann
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass

class Scream(Agent):
    """
    Scream surrounds patient with von nuemann
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)

    def step(self):
        pass