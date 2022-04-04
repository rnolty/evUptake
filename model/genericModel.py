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

# takes a complete cars dict, returns a list of keys ("model-year-EV") sorted by quality
def carsSortedByQuality(cars, year):
    allModels = list(cars.keys())
    def modelSorter(model):
        return cars[model]['history'][year]['quality']
    allModels.sort(key=modelSorter)
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

def addNewCar(year, isEV, model):
    key = model + "-" + str(year) + "-" + str(isEV)    # e.g. "luxury-2022-False"
    quality = globalParameters['carTypes'][model]['initialQuality']
    value = {'model': model, 'year': year, 'EV': isEV, 'history': {year: {'price': quality, 'quality': quality, 'batteryValue': 0}}}
    return {key: value}

def initializeYear(population, cars):
    # just copy the most recent year forward; then other functions will depreciate and purchase cars
    lastYear = sorted(population.keys())[-1]
    # to be a true pure function we should copy population and add the new data to the copy; but I
    #    don't think that buys us anything...  A later function will change car ownership statistics byj
    #    simulating the market for the new year
    population[lastYear+1] = copy.deepcopy(population[lastYear])

    addThisYearToCar = functools.partial(addYearToCar, lastYear+1, cars)   # prefill first argument of addYearToCar
    list(map(addThisYearToCar, list(cars.values())))              # every value in the cars dict is a dict representing one model-year

    # now add new cars for this year
    [cars.update(addNewCar(lastYear+1, False, model)) for model in globalParameters['carTypes'].keys()]

    return population, cars

def determineSellers(year, population, cars, sortedCarNames, carName):
    # consider all people groups that own any of this car as potential sellers -- they will sell if the utility
    #    of buying a new car exceeds the utility of holding
    priceThisCar = cars[carName]['history'][year]['price']
    qualityThisCar = cars[carName]['history'][year]['quality']
    higherQualityCarNames = sortedCarNames[0:sortedCarNames.index(carName)]
    transactionCost = globalParameters['transactionCost']    # may later try making it proportional to prices

    numSold = 0
    for (incomeLevel, peopleGroup) in [(k,v) for (k,v) in population[year].items() if (carName in v['cars'].keys())]:
        utilityFunction = [thing['utilityFunction'] for thing in globalParameters['peopleGroups'] if thing['income'] == incomeLevel][0]
        numerator = 0
        denominator = math.exp(utilityFunction(qualityThisCar))
        for otherCarName in higherQualityCarNames:
            priceOtherCar = cars[otherCarName]['history'][year]['price']
            qualityOtherCar = cars[otherCarName]['history'][year]['quality']
            numerator += math.exp(utilityFunction(qualityOtherCar) + priceThisCar - priceOtherCar - transactionCost)
            denominator += math.exp(utilityFunction(qualityOtherCar) + priceThisCar - priceOtherCar - transactionCost)
        numSold += peopleGroup['cars'][carName]['fraction'] * numerator / denominator
    return numSold

def determineBuyers(year, population, cars, sortedCarNames, carName):
    priceThisCar = cars[carName]['history'][year]['price']
    qualityThisCar = cars[carName]['history'][year]['quality']
    lowerQualityCarNames = sortedCarNames[sortedCarNames.index(carName)+1:]
    transactionCost = globalParameters['transactionCost']    # may later try making it proportional to prices

    numBought = 0
    for (incomeLevel, peopleGroup) in population[year].items():
        # if the people group have no utility for a car this expensive, skip them
        utilityFunction = [thing['utilityFunction'] for thing in globalParameters['peopleGroups'] if thing['income'] == incomeLevel][0]
        if (utilityFunction(qualityThisCar) == 0): continue

        for otherCarName in lowerQualityCarNames:
            if (otherCarName in peopleGroup['cars'].keys()):     # candidate to buy this car
                priceOtherCar = cars[otherCarName]['history'][year]['price']
                qualityOtherCar = cars[otherCarName]['history'][year]['quality']
                numerator = math.exp(utilityFunction(qualityThisCar) - priceThisCar + priceOtherCar - transactionCost)
                denominator = math.exp(utilityFunction(qualityOtherCar))
                higherQualityCarNames = sortedCarNames[0:sortedCarNames.index(otherCarName)]
                for thirdCarName in higherQualityCarNames:
                    priceThirdCar = cars[thirdCarName]['history'][year]['price']
                    qualityThirdCar = cars[thirdCarName]['history'][year]['quality']
                    denominator += math.exp(utilityFunction(qualityThirdCar) - priceThirdCar + priceOtherCar - transactionCost)
                    numBought += population[year][incomeLevel]['cars'][thirdCarName]['fraction'] * numerator / denominator
    return numBought



def determinePriceAndBuyers(year, population, cars, sortedCarNames, carName):
    # for all owners of a lower-quality car, decide if they choose to buy this car (at its current price)
    # we maintain some intermediate results in buyerMemory, for efficiency only
    (numBuyers, buyerMemory) = determineBuyers(year, population, cars, sortedCarNames, carName)
    if (cars[carName]['year'] == year):               # this is a new car -- all buyers will buy at pre-set price
        numSellers = numBuyers                        # this causes deltaP (calculated momentarily) to be zero
    else:
        # number of sellers is already determined by those who have decided to buy a higher-quality car
        numSellers = cars[carName]['numSellers']
    # now adjust price so that
    #    adjusted_buyers = sellers
    #    exp(-delta_P) * buyers = sellers (see notes)
    #    exp(-delta_P) = sellers / buyers
    deltaP = -math.log(numSellers / numBuyers)     # could be a rise or a fall in price                                     # TODO: * scale
    # to this point we haven't changed population or cars; now update cars with the new price
    cars[carName]['history'][year]['price'] += deltaP
    # now update population for buyers of this car, and move their lower-quality car to the must-sell list
    # format of buyerMemory: {incomeLevel: {'cars': [{'model': 'luxury-2020-False', 'numerator': 123, 'denominator': 246}, ...]}}
    for incomeLevel in buyerMemory.keys():
        for previouslyOwnedCarRecord in buyerMemory[incomeLevel]['cars']:
            previousModelName = previouslyOwnedCarRecord['model']
            numerator = previouslyOwnedCarRecord['numerator'] * math.exp(deltaP)       # adjust buy probability by new price    # TODO: scale
            denominator = previouslyOwnedCarRecord['denominator']
            tradeProbability = numerator / denominator                                                              # TODO: scale
            numToTrade = population[year][incomeLevel]['cars'][previousModelName]['fraction'] * tradeProbability
            population[year][incomeLevel]['cars'][previousModelName]['fraction'] -= numToTrade  # number not traded
            if (carName not in population[year][incomeLevel]['cars']):
                population[year][incomeLevel]['cars'][carName] = {'fraction: 0'}
            population[year][incomeLevel]['cars'][carName]['fraction'] += numToTrade
            cars[previousModelName]['numSellers'] += numToTrade
    return (population, cars)


def determinePrices(population, cars):
    thisYear = sorted(population.keys())[-1]                # this function runs after population has been updated for this year

    # Create a field in cars to keep track of number that must be sold because owner has already decided to buy a higher-quality car
    for car in cars.values(): car['numSellers'] = 0 

    # Process one car at a time in quality-order, determining price so # sellers = # buyers, and number of sales at that price.
    #    Except for new cars, #sellers is already set, as number of people who own this car who have already committed to buying 
    #    a higher-quality car
    sortedCarNames = carsSortedByQuality(cars, thisYear)    # this function runs after cars has been updated for this year
    for carName in sortedCarNames:
        (population, cars) = determinePriceAndBuyers(thisYear, population, cars, sortedCarNames, carName)