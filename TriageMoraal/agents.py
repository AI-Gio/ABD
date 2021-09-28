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
        self.walked = [(0, 0), (0, 1), (1, 0)]  # known locations (every walked loc + their surroundings)
        self.current_path = ()
    def inspect(self):
        """
        Medic inspects patient how severe the situation is and decides then what to do next
        :return:
        """
        pass

    # todo: hier komt assesment of patient meegenomen moet worden terug naar kamp of niet
    def wander_choice_maker(self, locations, counter=0):
        choices = {}
        for pos in locations:
            sur = self.model.grid.get_neighborhood(list(pos)[-1], moore=False, include_center=False)
            for loc in sur:
                sursuround = self.model.grid.get_neighborhood(loc, moore=False, include_center=True)
                score = 0
                for surloc in sursuround:
                    if surloc not in self.walked:
                        score += 1
                path = list(pos)
                path.append(loc)
                choices[tuple(path)] = score

        possible_choices = [k for k, v in choices.items() if v == max(choices.values())]

        if (len(possible_choices) > 1 and counter < 10) and max(choices.values()) < 4:
            possible_choices = self.wander_choice_maker(possible_choices, counter+1)
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

        self.model.grid.move_agent(self, self.current_path[0])
        # add new locations to database of known locations
        new_loc = self.model.grid.get_neighborhood(self.current_path[0], moore=False, include_center=True)
        self.walked = self.walked + list(set(new_loc) - set(self.walked))  # removes duplicates
        del self.current_path[0]
        pass

    def walk(self, destination):
        """
        Medic
        :return:
        """
        self.current_path = ()
        opened = [[self.pos, None, 0, 0]]
        closed = []
        paths = {}
        while len(opened) > 0:
            curnode = opened[0].copy()
            for i in opened:
                if i[-1] < curnode[-1]:
                    curnode = i.copy()

            opened.remove(curnode)
            closed.append(curnode)
            paths[curnode[0]] = [curnode[1], curnode[2], curnode[3]]

            if curnode[0] == destination:
                shortpath = [destination]
                prev = paths[destination][0]
                while prev:
                    shortpath.append(prev)
                    prev = paths[prev][0]
                print(shortpath)
                self.model.grid.move_agent(self, shortpath[-2])
                break

            curcor = curnode[0]
            next = self.model.grid.get_neighborhood(curcor, moore=False, include_center=False)
            for j in next:
                if j in self.walked and j not in paths.keys():
                    destdist = abs(j[0] - destination[0]) ** 2 + abs(j[1] - destination[1]) ** 2
                    nextnode = [j, curcor, curnode[2] + 1, (curnode[2] + 1) + destdist]
                    for k in opened:
                        if k[0] == nextnode[0] and k[-2] < nextnode[-2]:
                            continue
                    opened.append(nextnode)
        pass
        # todo: medic loopt ergens naar een punt straight toe

    def pickupPatient(self, patient):
        """
        Medic picks up patient from field
        :return:
        """
        self.brancard.append(patient)
        self.model.grid.remove_agent(patient)
        if patient in self.known_p:
            self.known_p.remove(patient)
        pass
        # todo: patient word opgepakt en toegevoegd aan brancard

    def goBase(self):
        camploc = (0, 0)
        self.current_path = ()
        opened = [[self.pos, None, 0, 0]]
        closed = []
        paths = {}
        while len(opened) > 0:
            curnode = opened[0].copy()
            for i in opened:
                if i[-1] < curnode[-1]:
                    curnode = i.copy()

            opened.remove(curnode)
            closed.append(curnode)
            paths[curnode[0]] = [curnode[1], curnode[2], curnode[3]]

            if curnode[0] == camploc:
                shortpath = [camploc]
                prev = paths[camploc][0]
                while prev:
                    shortpath.append(prev)
                    prev = paths[prev][0]
                print(shortpath)
                self.model.grid.move_agent(self, shortpath[-2])
                break

            curcor = curnode[0]
            next = self.model.grid.get_neighborhood(curcor, moore=False, include_center=False)
            for j in next:
                if j in self.walked and j not in paths.keys():
                    destdist = abs(j[0] - camploc[0]) ** 2 + abs(j[1] - camploc[1]) ** 2
                    nextnode = [j, curcor, curnode[2] + 1, (curnode[2] + 1) + destdist]
                    for k in opened:
                        if k[0] == nextnode[0] and k[-2] < nextnode[-2]:
                            continue
                    opened.append(nextnode)
        """
        Uses shortest path alg to return to base to return patient
        :return:
        """
        pass
        # todo: Medic gaat meteen met shortest path naar medcamp

    def step(self):
        """
        Searches for patients and bring them back decided by calculations
        """
        # todo: medic neemt zoiezo patient mee en als patient dood gaat onderweg dan gaat zijn emotianal_staat naar beneden
        # todo: als patient doodgaat onderweg word hij misschien wel of niet meegenomen naar medcamp
        print(self.brancard)
        # if len(self.brancard) > 0:
        #     self.goBase()
        #
        # else:
        #     pass

        nb_coords = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)

        self.path.extend(nb_coords)

        cell_cross = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        # print(cell_cross)
        own_cell = self.model.grid.get_cell_list_contents([self.pos])
        print(own_cell)

        patient = [obj for obj in cell_cross if isinstance(obj, Patient)]
        medcamp = [obj for obj in own_cell if isinstance(obj, MedCamp)]

        # if len(patient) > 0:
        #     print('ik pak een patient op')
        #     self.pickupPatient(cell_cross[0])
        if len(medcamp) > 0:
            print('op camp')
            self.brancard = []

        if len(patient) > 0:
            if len(self.brancard) > 0:
                for p in range(len(patient)):
                    if p not in self.known_p:
                        self.known_p.append(p)
                self.goBase()
            elif len(patient) > 1:
                for p in range(1, len(patient)):
                    if p not in self.known_p:
                        self.known_p.append(p)
                self.pickupPatient(patient[0])
            else:
                print('ik pak een patient op')
                self.pickupPatient(patient[0])
        elif len(self.brancard) > 0:
            print('ben niet bij camp maar heb patient')
            self.goBase()
        elif len(self.known_p) > 0:
            self.walk(self.known_p[0].pos)
        else:
            self.wander()



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
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # todo: here are the patients being counted that are retrieved so that you can hover over medcamp in sim and see that number

    def step(self):
        pass
