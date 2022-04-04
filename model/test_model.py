import specificModel

# population = {2021:
#                 {10000:
#                     {'fraction': 0.05, 'cars':
#                         {
#                             'midrange-2013-False': {'fraction': 0.025},
#                             'economy-2015-False':  {'fraction': 0.025}
#                         }
#                     }, # end of income cohort 10000
#                  20000:
#                     {'fraction': 0.05, 'cars':
#                         [
#                             'midrange-2015-False': {'fraction': 0.03},
#                             'economy-2016-False':  {'fraction': 0.02}
#                         ]
#                     }, # end of income cohort 20000
#                 } # end of 2022
#             } # end of population


# cars is a dictionary of all cars.  The dict is keyed by the car identity, which is a string consisting of model, year, EV (True or False)
#    The values of the dict are a dict of car characterstics, including history which is a dict keyed by year and containing the price
#    for that year, as well as the quality, i.e. perceived value (depreciated predictably from the purchase price) and the depreciated battery
#    value (which is always 0 for non-EV cars)
# cars = {
#     'midrange-2013-False': {
#         'model': 'midrange', 'year': 2013, 'EV': False,
#         'history': {
#             2013: {'price': 30000, 'quality': 30000, 'batteryValue': 0},
#             2014: {'price': 24000, 'quality': 21000, 'batteryValue': 0},
#             2015: {'price': 18000, 'quality': 18000, 'batteryValue': 0},
#             2021: {'price': 3500,  'quality': 6000,  'batteryValue': 0}
#          },
#     },
#     'midrange-2015-False': {
#         'model': 'midrange', 'year': 2015, 'EV': False,
#         'history': {
#             2015: {'price': 30000, 'quality': 30000, 'batteryValue': 0},
#             2016: {'price': 24500, 'quality': 21000, 'batteryValue': 0},
#             2017: {'price': 19500, 'quality': 18000, 'batteryValue': 0},
#             2021: {'price': 6000,  'quality': 10000, 'batteryValue': 0}
#         }
#     }
# }

globalParameters = {
    'carTypes': {
        'luxury': {
            'initialQuality': 70000,
            'depreciationCurve': {0: 1.0, 1: 0.7, 2: 0.6, 3: 0.5, 4: 0.42, 5: 0.36, 6: 0.3, 7: 0.25, 8: 0.18, 9: 0.1, 10: 0}
        },
        'midrange': {
            'initialQuality': 30000,
            'depreciationCurve': {0: 1.0, 1: 0.7, 2: 0.6, 3: 0.5, 4: 0.42, 5: 0.36, 6: 0.3, 7: 0.25, 8: 0.18, 9: 0.1, 10: 0}
        },
        'economy': {
            'initialQuality': 15000,
            'depreciationCurve': {0: 1.0, 1: 0.7, 2: 0.6, 3: 0.5, 4: 0.42, 5: 0.36, 6: 0.3, 7: 0.25, 8: 0.18, 9: 0.1, 10: 0}
        }
    },
    'peopleGroups': [
        {'income': 10000,  'utilityFunction': specificModel.peakedUtility(2000), 'fraction': 0.05},
        {'income': 20000,  'utilityFunction': specificModel.peakedUtility(4000), 'fraction': 0.125},
        {'income': 30000,  'utilityFunction': specificModel.peakedUtility(6000), 'fraction': 0.20},
        {'income': 40000,  'utilityFunction': specificModel.peakedUtility(10000), 'fraction': 0.25},
        {'income': 60000,  'utilityFunction': specificModel.peakedUtility(20000), 'fraction': 0.20},
        {'income': 80000,  'utilityFunction': specificModel.peakedUtility(40000), 'fraction': 0.09},
        {'income': 100000, 'utilityFunction': specificModel.peakedUtility(70000), 'fraction': 0.085}
    ],
    'transactionCost': 500
}

import genericModel
genericModel.globalParameters = globalParameters
specificModel.globalParameters = globalParameters

thisYear = 2022
cars = specificModel.initializeCars(thisYear)
#print("\n\nCars:\n", cars)

# initialize population for this year, including what cars they own
population = specificModel.initializePopulation(cars, thisYear)
#print("\n\nPopulation:\n", population)

#for incomeLevel in population[thisYear].keys():
#   theSum = sum(c['fraction'] for c in population[thisYear][incomeLevel]['cars'])
#    print("***", population[thisYear][incomeLevel]['fraction'], theSum)

population, cars = genericModel.initializeYear(population, cars)

print("\n\nPopulation:\n", population, "\n\nCars:\n", cars, "\n\n\n")

print("\n\n\n")