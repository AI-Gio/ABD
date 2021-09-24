from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from TriageMoraal.agents import *
from TriageMoraal.model import Triage

def sim_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape":"circle",
                 "Color":"#ffffff",
                 "Filled":"true",
                 "Layer":0,
                 "r": 1}

    if type(agent) is Medic:
        portrayal["text"] = "👨"
        portrayal["Color"] = "#d44e4e"
        portrayal["Layer"] = 5


    elif type(agent) is Patient:
        portrayal["text"] = "🤕"
        portrayal["Color"] = "#e3e3e3"

    elif type(agent) is MedCamp:
        portrayal["text"] = "🏥"
        portrayal["Color"] = "#ff9e9e"

    return portrayal

sim = CanvasGrid(sim_portrayal, 10, 10, 500, 500)

server = ModularServer(Triage, [sim],
                       "Triage")
server.launch()