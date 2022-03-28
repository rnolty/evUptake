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

import itertools, functools, copy

def addYearToCar(year, car):
    age = year - car['year']
    initialValue = globalParameters['carInitialValues'][car['model']]

    depreciatedValue = initialValue * globalParameters['carDepreciationCurve'][car['model']][age] if (
        age in globalParameters['carDepreciationCurve'][car['model']]) else 0
    # now add new year to car history
    car['history'][year] = {
        'price': car['history'][year-1]['price'],    # start with last year's price; a later function will update for this year
        'quality': depreciatedValue,
        'batteryValue': 0
    }


def initializeYear(population, cars):
    # just copy the most recent year forward; then other functions will depreciate and purchase cars
    lastYear = sorted(population.keys())[-1]
    # to be a true pure function we should copy population and add the new data to the copy; but I
    #    don't think that buys us anything...  A later function will change car ownership statistics byj
    #    simulating the market for the new year
    population[lastYear+1] = copy.deepcopy(population[lastYear])

    addThisYearToCar = functools.partial(addYearToCar, lastYear+1)   # prefill first argument of addYearToCar
    list(map(addThisYearToCar, list(cars.values())))              # every value in the cars dict is a dict representing one model-year
    return population, cars

