from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from TriageRationeel.agents import *
from TriageRationeel.model import Triage

def sim_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape":"circle",
                 "Color":"#ffffff",
                 "Filled":"true",
                 "Layer":0,
                 "r": 1}

    if type(agent) is Medic:
        if agent.pickedup:
            portrayal["text"] = "⚕️"
        elif agent.emotional_state <= 0:
            portrayal["text"] = "☠️"
        else:
            portrayal["text"] = "👨"
        portrayal["Color"] = "#d44e4e"
        portrayal["Emotional state"] = Medic.__getattribute__(agent, 'emotional_state')
        portrayal["unique_id"] = Medic.__getattribute__(agent, 'unique_id')
        if len(Medic.__getattribute__(agent, 'brancard')) > 0:
            portrayal["Brancard"] = Medic.__getattribute__(agent, 'brancard')[0].unique_id
        else:
            portrayal["Brancard"] = "empty"


    elif type(agent) is Patient:
        portrayal["id"] = Patient.__getattribute__(agent, 'unique_id')
        if agent.dead:
            portrayal["text"] = "💀️"
            portrayal["Color"] = "#e3e3e3"
            portrayal["externHealth"] = Patient.__getattribute__(agent, 'externHealth')
            portrayal["trueHealth"] = Patient.__getattribute__(agent, 'trueHealth')
        else:
            portrayal["text"] = "🤕"
            portrayal["Color"] = "#e3e3e3"
            portrayal["externHealth"] = Patient.__getattribute__(agent, 'externHealth')
            portrayal["trueHealth"] = Patient.__getattribute__(agent, 'trueHealth')

    elif type(agent) is MedCamp:
        portrayal["text"] = "🏥"
        portrayal["Color"] = "#ff9e9e"
        portrayal["Saved Patients"] = len(MedCamp.__getattribute__(agent, 'saved_patients'))

    elif type(agent) is Scout:
        portrayal["text"] = "🏃"
        portrayal["Color"] = "#d44e4e"
        portrayal["Stamina"] = Scout.__getattribute__(agent, "stamina")
        portrayal["Amount Found Patients"] = Scout.__getattribute__(agent, 'amount_found_p')

    return portrayal

sim = CanvasGrid(sim_portrayal, 20, 20, 500, 500)
chart_element = ChartModule(
    [{"Label": "Dead_patients", "Color": "red"},
     {"Label": "Saved_Patients", "Color": "blue"}], data_collector_name="datacollector"
)

model_params = {
    "init_patient":UserSettableParameter("slider", "Init_patients", value=2,
                                     min_value=1, max_value=sim.grid_width*sim.grid_height-(sim.grid_height+sim.grid_width), step=1),
    "init_medic": UserSettableParameter("slider", "Init_medics", value=1, min_value=1, max_value=5, step=1),
    "init_scouts": UserSettableParameter("slider", "Init_scouts", value=0, min_value=0, max_value=10, step=1),
    "mode":UserSettableParameter("choice", "Sim_Mode", value="None", choices=["None","constant_info_share", "info_share_medbase","info_share_meet"])
}#bron: https://github.com/projectmesa/mesa/issues/419

server = ModularServer(Triage, [sim, chart_element],
                       "Triage", model_params)


server.launch()