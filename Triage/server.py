from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from Triage.agents import *
from Triage.model import Triage

def simulation_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "Color":"red",
                 "Filled": "true"}

    if type(agent) is Medic:
        portrayal["text"] = "👨"
        portrayal["r"] = 0.8
        portrayal["Layer"] = 1

    elif type(agent) is Patient:
        portrayal["r"] = 0.5
        portrayal["Layer"] = 2

    elif type(agent) is Cure:
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    elif type(agent) is Radio:
        portrayal["Layer"] = 5

    elif type(agent) is Static:
        portrayal["Layer"] = 4

    elif type(agent) is Scream:
        portrayal["Layer"] = 3

    return portrayal

sim = CanvasGrid(simulation_portrayal, 20, 20, 500, 500)

server = ModularServer(Triage, [sim],
                       "Triage")
server.launch()