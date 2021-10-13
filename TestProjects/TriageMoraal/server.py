from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter
from TestProjects.TriageMoraal.agents import *
from TestProjects.TriageMoraal.model import Triage

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
        portrayal["Emotional state"] = Medic.__getattribute__(agent, 'emotional_state')
        if len(Medic.__getattribute__(agent, 'brancard')) > 0:
            portrayal["Brancard"] = Medic.__getattribute__(agent, 'brancard')[0].unique_id
        else:
            portrayal["Brancard"] = "empty"


    elif type(agent) is Patient:
        portrayal["text"] = "🤕"
        portrayal["Color"] = "#e3e3e3"
        portrayal["Health"] = Patient.__getattribute__(agent, 'health')

    elif type(agent) is MedCamp:
        portrayal["text"] = "🏥"
        portrayal["Color"] = "#ff9e9e"
        portrayal["Saved Patients"] = len(MedCamp.__getattribute__(agent, 'saved_patients'))

    return portrayal

sim = CanvasGrid(sim_portrayal, 10, 10, 500, 500)
model_params = {
    "init_patient":UserSettableParameter("slider", "Init_patients", value=2,
                                     min_value=1, max_value=sim.grid_width*sim.grid_height-(sim.grid_height+sim.grid_width), step=1)
}
server = ModularServer(Triage, [sim],
                       "Triage", model_params)
server.launch()