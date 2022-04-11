# copyright 2022 Bob Nolty
# if you are interested in using it, hit me up on github (rnolty)

# Many of the Functional Programming functions pass around a 'population' object.
#    It is a dict of lists of plain old data (JSON-compatible).
#    At the top level is a dict keyed by year.  The value of each year is a 
#    summary of all the people and all their cars in the model.
#    The next level is a dict keyed by income groups.  The value of an income
#    group is a dict with the percentage of population in that group, plus
#    a cars group.  A cars item gives the type of car, its age, its current
#    depreciated value, and the percentage of population with this kind of
#    car.

# Example:
# {2022: 
#    {10000:         # people who make less than $10,000 per year
#      {'fraction': 0.12,
#       'cars':
#       [
#           {'model': 'midrange', 'year': 2012, 'carValue': 2500, 'batteryValue': 3200, 'EV': true, fraction: 0.023}, ...
#       ]
#      }
#    }, 2023: {...}, ...
# }

# There is also a globalParameters object which gives the variable parameters to seed and progress
#    the model

# {'incomeProportions': 
#    {10000: 0.18, 20000: 0.24, ...},   # 18% make less than $10,000/yr, 24% 10,000-20,000
#  'carPreferences':    # what fraction of income do they want to spend on cars?  e.g. 10% = 30% every three years
#      {10000:  {0.1: 0.3, 0.2: 0.25, ...} # 30% of people want to spend 10%; 25% of people want to spend 20%
#       20000:  {...}, ...
#      },
#   'discountRates': {10000: 0.25, 20000, 0.22, ...},
#   'carDepreciationCurve':
#      { 'luxury': {1: 0.7, 2: 0.55, ...},  # after 1 year, luxury car retains 70% of its original value
#        'midrange': {...}, 'economy': {...}
#      },
#   'batteryDepreciationCurve': {1: 0.8, 2: 0.73, ...},
#   'batteryPriceCurve': {2022: 1.0, 2023: 0.93, ...},
#   'newCarEVMandate': {2022: 0.1, ... 2035: 1.0, 2036: 1.0, ...},
# }

import itertools, functools, copy, math

globalParameters = {}                             # the program that loads us will replace this

def _scaledExp(scale, x): return math.exp(x/scale)

def scaledExpCurried(scale):
    return functools.partial(_scaledExp, scale)  # return function of x, which is _scaledExp with scale already filled in

# takes a complete cars dict, returns a list of keys ("model-year-EV") sorted by quality
def carsSortedByQuality(cars, year, reverse=True):
    allModels = list(cars.keys())
    def modelSorter(model):
        return cars[model]['history'][year]['quality']
    allModels.sort(key=modelSorter, reverse=reverse)
    #print("***", [(s, cars[s]['history'][year]['quality']) for s in allModels])
    return allModels

# for a particular car (in the 'cars' data structure with key "model-year-isEV"), update the dict by adding
#    year to the history key
def addYearToCar(year, cars, car):
    age = year - car['year']
    initialValue = globalParameters['carTypes'][car['model']]['initialQuality']

    depreciatedValue = initialValue * globalParameters['carTypes'][car['model']]['depreciationCurve'][age] if (
        age in globalParameters['carTypes'][car['model']]['depreciationCurve']) else 0
    # for the initial price this year, use the price of a car of this model and age from last year's history
    # As part of the simulation, a later function will update this initial price based on market conditions
    key = car['model'] + "-" + str(car['year']-1) + "-" + str(car['EV'])    # for example, 'luxury-2021-False'
    comparableCar = cars[key] if key in cars else {'history': {year-1: {'price': 0}}}
    # now add new year to car history
    car['history'][year] = {
        'price': comparableCar['history'][year-1]['price'],
        'quality': depreciatedValue,
        'batteryValue': 0
    }

# for a car that is new this model year, returns the relevant entry for the cars data structure
def addNewCar(year, isEV, model):
    key = model + "-" + str(year) + "-" + str(isEV)    # e.g. "luxury-2022-False"
    quality = globalParameters['carTypes'][model]['initialQuality']
    value = {'model': model, 'year': year, 'EV': isEV, 'history': {year: {'price': quality, 'quality': quality, 'batteryValue': 0}}}
    return {key: value}

# the first step for setting prices and doing sales for a new year is to create the new year in the population data structure, and
#    for each car, add the new year to the history
def initializeYear(population, cars):
    # just copy the most recent year forward; then other functions will price and purchase cars
    lastYear = sorted(population.keys())[-1]
    # to be a true pure function we should copy population and add the new data to the copy; but I
    #    don't think that buys us anything...  A later function will change car ownership statistics by
    #    simulating the market for the new year
    population[lastYear+1] = copy.deepcopy(population[lastYear])

    addThisYearToCar = functools.partial(addYearToCar, lastYear+1, cars)   # prefill first argument of addYearToCar
    # list() causes map object to evaluate
    list(map(addThisYearToCar, list(cars.values())))              # every value in the cars dict is a dict representing one model-year

    # now add new cars for this year
    [cars.update(addNewCar(lastYear+1, False, model)) for model in globalParameters['carTypes'].keys()]

    return population, cars





debugCarName = "luxury-2022-False"





# how many owners of lower-quality cars would buy this car if the price were at its initial value?  Later the price, and the number
#    of buyers, will be adjusted
def determineBuyers(year, population, cars, sortedCarNames, carName):
    priceThisCar = cars[carName]['history'][year]['price']
    qualityThisCar = cars[carName]['history'][year]['quality']
    lowerQualityCarNames = sortedCarNames[sortedCarNames.index(carName)+1:]
    transactionCost = globalParameters['transactionCost']    # may later try making it proportional to prices

    buyerMemory = {}                 # for efficiency only - remember some intermediate results and return them
    numBought = 0
    for (incomeLevel, peopleGroup) in population[year].items():
        utilityFunction = [thing['utilityFunction'] for thing in globalParameters['peopleGroups'] if thing['income'] == incomeLevel][0]
        utilityScale = globalParameters['utilityScale'] * cars[carName]['history'][year]['quality']
        scaledExp = scaledExpCurried(utilityScale)    # scaledExp(x) = exp(x/scale)
        # if the people group has no utility for a car this expensive (or this cheap), skip them
        if (utilityFunction(qualityThisCar) == 0): continue

        for otherCarName in lowerQualityCarNames:
            if (otherCarName not in peopleGroup['cars'].keys()): continue

            priceOtherCar = cars[otherCarName]['history'][year]['price']
            qualityOtherCar = cars[otherCarName]['history'][year]['quality']
            numerator = scaledExp(utilityFunction(qualityThisCar) - priceThisCar + priceOtherCar - transactionCost) # TODO: operating costs
            if (utilityFunction(qualityOtherCar) > 0):
                denominator = scaledExp(utilityFunction(qualityOtherCar))   # probability of keeping other car
            else:
                denominator = 0                                             # other car has no utility, no chance of keeping it
            # now add to denominator probability of buying any other higher-quality car (including carName)
            higherQualityCarNames = sortedCarNames[0:sortedCarNames.index(otherCarName)]
            for thirdCarName in higherQualityCarNames:
                priceThirdCar = cars[thirdCarName]['history'][year]['price']
                qualityThirdCar = cars[thirdCarName]['history'][year]['quality']
                denominator += scaledExp(utilityFunction(qualityThirdCar) - priceThirdCar + priceOtherCar - transactionCost)
            # now numerator/denominator is probability owner of thirdCarName chose to buy carName
            #print("***", peopleGroup)
            numBought += peopleGroup['cars'][otherCarName]['fraction'] * numerator / denominator
            # if (carName == debugCarName):
            #     print("   ***", "Owners of", otherCarName, ": ", peopleGroup['cars'][otherCarName]['fraction'], "tentatively buy", 
            #        peopleGroup['cars'][otherCarName]['fraction'] * numerator / denominator)
            #     print("      ", numerator, denominator)
            # if (otherCarName == debugCarName):
            #     print("***","Owners of", debugCarName, ": ", peopleGroup['cars'][otherCarName]['fraction'], "tentatively sell", 
            #        peopleGroup['cars'][otherCarName]['fraction'] * numerator / denominator)
            if (incomeLevel not in buyerMemory): buyerMemory[incomeLevel] = {'cars': []}
            buyerMemory[incomeLevel]['cars'].append( {'model': otherCarName, 'numerator': numerator, 'denominator': denominator} )
        # end of loop over cars owned by this peopleGroup
    # end of loop over people groups
    return numBought, buyerMemory


# for a single model-year-EV, decide an equilibrium price and which owners of lower-quality cars choose to buy at that price
def determinePriceAndBuyers(year, population, cars, sortedCarNames, carName):
    # the scale of fluctuations is set to a fraction of the quality of this car; this scale of fluctuation is used for all
    #    calculations involving purchase of this car
    utilityScale = globalParameters['utilityScale'] * cars[carName]['history'][year]['quality']
    scaledExp = scaledExpCurried(utilityScale)    # scaledExp(x) = exp(scale*x)

    # for all owners of a lower-quality car, decide if they choose to buy this car (at its current price)
    # we maintain some intermediate results in buyerMemory, for efficiency only
    (numBuyers, buyerMemory) = determineBuyers(year, population, cars, sortedCarNames, carName)
    # if (carName == debugCarName):
    #     print("\n\n*** buyerMemory", buyerMemory,"\n\n")

    if (cars[carName]['year'] == year):               # this is a new car -- all buyers will buy at pre-set price
        numSellers = numBuyers                        # this causes deltaP (calculated momentarily) to be zero
    else:
        # number of sellers is already determined by those who have decided to buy a higher-quality car
        numSellers = cars[carName]['numSellers']

    # now adjust price so that
    #    adjusted_buyers = sellers
    #    exp(-delta_P) * buyers = sellers (see notes)
    #    exp(-delta_P) = sellers / buyers
    #print("***", numSellers, numBuyers)
    priceThisCar = cars[carName]['history'][year]['price']
    if ((numBuyers > 0) and (numSellers > 0)):
        deltaP = -utilityScale*math.log(numSellers / numBuyers)    # could be a rise or a fall in price
        if (deltaP < -priceThisCar):                               # don't let price drop below zero
            deltaP = -priceThisCar
    elif (numBuyers == 0):
        deltaP = -priceThisCar                                     # if no buyers, price drops to zero
    else:
        deltaP = 0                                                 # if no sellers, price is irrelevant
    # if (carName == debugCarName):
    #     print("***", "Saved numSellers for", carName, "is", numSellers, "tentative buyers is", numBuyers, "deltaP is", deltaP)
    # to this point we haven't changed population or cars; now update cars with the new price
    cars[carName]['history'][year]['price'] += deltaP
    # now update population for buyers of this car, and move their lower-quality car to the must-sell list
    totalBuy = 0
    for incomeLevel in buyerMemory.keys():
        #print("***", "Population[", incomeLevel, "]['cars']:\n", population[year][incomeLevel]['cars'].keys())
        #print("\n***", "buyerMemory[", incomeLevel, "]['cars']:\n", [c['model'] for c in buyerMemory[incomeLevel]['cars']])
        for previouslyOwnedCarRecord in buyerMemory[incomeLevel]['cars']:
            # format of buyerMemory: {incomeLevel: {'cars': [{'model': 'luxury-2020-False', 'numerator': 123, 'denominator': 246}, ...]}}
            previousModelName = previouslyOwnedCarRecord['model']
            numerator = previouslyOwnedCarRecord['numerator'] * scaledExp(-deltaP)       # adjust buy probability by new price
            denominator = previouslyOwnedCarRecord['denominator']
            tradeProbability = numerator / denominator
            if (tradeProbability > 1):
                # for some low-valued cars, there are more sellers than even possible buyers
                tradeProbability = 1            # this will leave a few cars being sold but not bought, i.e. retired
            numToTrade = population[year][incomeLevel]['cars'][previousModelName]['fraction'] * tradeProbability
            # if (previousModelName == debugCarName):
            #     print("***", "Owners of", previousModelName, ": ", population[year][incomeLevel]['cars'][previousModelName]['fraction'],
            #        "finally sell", numToTrade)
            #     print("   ", numerator, denominator)
            population[year][incomeLevel]['cars'][previousModelName]['fraction'] -= numToTrade  # leaving number not traded
            # if (previousModelName == debugCarName):
            #     print("***", "Leaving", population[year][incomeLevel]['cars'][previousModelName]['fraction'])
            if (carName not in population[year][incomeLevel]['cars']):
                population[year][incomeLevel]['cars'][carName] = {'fraction': 0}
            population[year][incomeLevel]['cars'][carName]['fraction'] += numToTrade
            # if (carName == debugCarName):
            #     print("***", "Previous owners of", previousModelName, "now own", numToTrade, "of", carName)
            #     print("   ", numerator, denominator)
            cars[previousModelName]['numSellers'] += numToTrade
            totalBuy += numToTrade
    if (abs(totalBuy - numSellers) > 0.005):
        print("!!! Discrepancy for", carName, "sellers:", numSellers, "adjusted buyers:", totalBuy, "deltaP:", deltaP)
    # if (carName == debugCarName):
    #     print("***", "final buyers of", carName, ":", totalBuy)
    return (population, cars)


def determinePrices(population, cars):
    thisYear = sorted(population.keys())[-1]                # this function runs after population has been updated for this year

    # Create a field in cars to keep track of number that must be sold because owner has already decided to buy a higher-quality car
    for car in cars.values(): car['numSellers'] = 0 

    # Process one car at a time in quality-order, determining price (so # sellers = # buyers), and number of sales at that price.
    #    Except for new cars, #sellers is already set, as number of people who own this car who have already committed to buying 
    #    a higher-quality car
    sortedCarNames = carsSortedByQuality(cars, thisYear)    # this function runs after cars has been updated for this year
    for carName in sortedCarNames:
        (population, cars) = determinePriceAndBuyers(thisYear, population, cars, sortedCarNames, carName)

    return population, cars

if __name__ == "__main__":
    import test_model
