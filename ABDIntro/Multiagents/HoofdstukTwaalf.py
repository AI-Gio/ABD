import math
from collections import Counter

parties = {"A": 45, "B": 25, "C": 15, "D": 15}
method = "shapley"

def create_possiblesMethods(parties, mainParty):
    """

    @param parties: all the parties with their candidates in a dictionary
    @param mainParty: the party that the shapley value needs to be calculated for (and to delete it in the parties)
    @return:
    """
    parties.pop(mainParty) #remove it so you can't compare it with other parties
    possibleMethodsList = [[key for key in parties.keys()]] #the first method is every party except the main party
    lengthList = len(parties)
    temp_parties = parties.copy() #create a temporary parties to remove already used parties
    for firstPartyIndex in range(lengthList): #to loop over the indexs of length and get the first party
        if lengthList != 1: #if there is not only 1 party left
            for secondPartyIndex in range(lengthList): #to loop over the indexs of length and get the second party
                if list(temp_parties)[firstPartyIndex] != list(temp_parties)[secondPartyIndex]: #if they are not both the same party
                    possibleMethodsList.append([list(temp_parties)[firstPartyIndex], list(temp_parties)[secondPartyIndex]]) #add party name of the possible method to the list
            temp_parties.pop(list(temp_parties)[firstPartyIndex]) #after looping over the first party methods, delete the party in the list
            lengthList = lengthList - 1 #decrease the length because of the pop
        else:
            break
    for x in parties:
        possibleMethodsList.append([x[0]]) #to add every party indivually
    print(mainParty, ", All methods: ", possibleMethodsList)

    pass
    return possibleMethodsList

def calculate_majorityMethods(possibleMethodsList, parties, mainPartyPoints, total):
    majorityPoints = total/2 #the points requires to get the majority
    majorityMethodsList = [] #empty list where the majority methods are stored
    for coalition in possibleMethodsList: #for loop over every possible method/coalition
        otherPartyPoints = 0 #empty points to storage the other parties' points
        for party in coalition:
            otherPartyPoints += parties.get(party)
        if otherPartyPoints + mainPartyPoints > majorityPoints and otherPartyPoints < majorityPoints: #if the otherpartypoints + mainpartypoints is higher than majoritypoints
            majorityMethodsList.append(coalition) #add the coalition to the majoritymethodslist
    if mainPartyPoints > majorityPoints:
        majorityMethodsList.append([])
    print("Majority methods: ", majorityMethodsList)
    return majorityMethodsList



def main(parties:dict, method:str):
    total = sum([key for key in parties.values()]) #gets the total amount of candidates
    partyMoney = [[] for key in parties.values()] #gets the template of the amount of parties
    if method == "fair": #if using fair method
        for party in range(len(parties)):
            partyMoney.append(list(parties.values())[party]/total * total) #every party gets equally money looking at the amount of candidates
    if method == "shapley": #if using shapley method
        for party in range(len(parties)):
            temp_parties = parties.copy() #create a temporary variable for parties to remove already used partynames
            possibleMethodsList = create_possiblesMethods(temp_parties, list(parties)[party])
            majorityMethodsList = calculate_majorityMethods(possibleMethodsList, parties, list(parties.values())[party], total)
            amountOfPartiesList = dict(Counter([len(x) for x in majorityMethodsList])) #count the amount parties in every method/coalition
            print(amountOfPartiesList)

            '''the shapley formula: φi(N,v) = 1/|N| Σ(S⊆N\{i}) |S|!(|N| − |S| − 1) [v(S ∪ {i}) − v(S)]'''
            '''Where:
             N = parties
             S = len(parties) ?
             '''

            partyMoney[party] = (1/math.factorial(len(parties))) #1/|N|
            temp_party_amount_holder = 0
            for S in amountOfPartiesList: #Σ(S⊆N\{i})
                test = 0
                amountOfParties = amountOfPartiesList.get(S)
                S_N = len(parties) - S - 1
                temp_party_amount_holder += amountOfParties * (math.factorial(S) * math.factorial(S_N)) * 100
                #|S|!(|N| − |S| − 1) [v(S ∪ {i}) − v(S)]
            partyMoney[party] = partyMoney[party] * temp_party_amount_holder
            print(partyMoney)
            print('\n')
        pass
    if method == "addictief":
        pass
    return partyMoney

partyMoney = main(parties, method)
print("partyMoney: ", partyMoney)
