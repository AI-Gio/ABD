from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from Triage.agents import *
from Triage.model import Triage

def simulation_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "Color":"#ffffff",
                 "Filled": "true",
                 "r": 1}

    if type(agent) is Medic:
        portrayal["text"] = "👨"
        portrayal["Color"] = "#ffffff"
        portrayal["Layer"] = 5

    elif type(agent) is Patient:
        portrayal["text"] = "🤕"
        portrayal["Color"] = "Black"
        portrayal["Layer"] = 0

    elif type(agent) is Cure:
        portrayal["text"] = "💉"
        portrayal["Layer"] = 0

    elif type(agent) is Radio:
        portrayal["text"] = "📻"
        portrayal["Layer"] = 0

    elif type(agent) is Static:
        portrayal["text"] = "🔊"
        portrayal["Layer"] = 0

    elif type(agent) is Scream:
        portrayal["text"] = "💤"
        portrayal["Layer"] = 3

    return portrayal

# radius moet deelbaar zijn in width en height
sim = CanvasGrid(simulation_portrayal, 5, 5, 500, 500)

server = ModularServer(Triage, [sim],
                       "Triage")
server.launch()