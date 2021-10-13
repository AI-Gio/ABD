
# Project Title

ABD Challenge: De Triage Simulatie

## Description

This is an agent based simulation where multiple agents try to complete a simulation by achieving or either failing their goal. In our current and final version of the simulation, agents try to help patients in the world. These patients have their own visible health and true health so the agents, lets call them medics, can't figure out there true health. Their job is to find patients, inspect them, consider bringing them to safety or letting them die and bringing them back or continue looking/wandering. The medics get a little help with finding patients by the scout agents. These can't help the patients, but can help finding them quicker, because of their lack of medic equipment. These scouts use all their effort to walk faster, but after a while they become tired and return to the medcamp. The medics might seem physically strong, but mentally after seeing too many dead bodies or estimated the health poorly (so the patient dies in their hands), the medics become crazy and wont move and are considered dead and will not return to the medcamp. The medcamp is where the medics and scouts start and end. The medcamp is always in the left corner. 

The scouts and medics have their own wanderaround statements to find patients. This process is the most important and can really help the outcome of the simulation. There are 4 modes who can help improve this process:
* None: They share no information
* Constant info share: Having communication devices keeps everyone up-to-date
* Medbase info share: Agents consider finding each other near the medcamp to share information of patients and path
* Meet info share: Agents wont try to find each other, but when they do, they share information so they have more time to look for more patients

Our job is to know which mode is the most successful in capturing patients and which one let the most patients die

## Getting Started

### Dependencies

* Libraries: Mesa, random (Library install tutorial: https://docs.python.org/3/installing/index.html)
* IDE: Pycharm https://www.jetbrains.com/pycharm/

### Installing

* To install, simply download the entire file in a zip, unpack it or clone it in a IDE or Github for Windows.
* After that you can open up the TriageRational Folder to python files.
* Run and only run the server.py file

### Executing program

* Install libraries
```
pip install mesa
pip installrandom
pip install numpy
pip install scipy
```
* download the code and run it inside an IDE


## Authors

Contributors:
* [@Guy](https://github.com/AI-Gio)
* [@Ruben](https://github.com/GameModes)
* [@Quinn](https://google.com)
* [@Adam](https://google.com)


## Version History
* 4 - 15-9-21
    * Model changes & patient, cure & radio agent created
    
* 3 - 15-9-21
    * Triage Python file added
    * Untouched Wolf_Sheep mesa example
       
* 2 - 14-9-21
    * TheorieBoekSamenvatting.pdf 

* 1 - 13-9-21
    * Empty Readme added 


## Sources

* [WolfSheep Mesa Example](https://github.com/projectmesa/mesa-examples/tree/master/examples/WolfSheep)
