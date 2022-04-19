from model import specificModel

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
            'initialQuality': 70000, 'salvageValue': 2000, 'mpg':30, 'mpkwh': 2.5, 'gasRepairs': 1000, 'evRepairs': 700,
            'depreciationCurve': {0: 1.0, 1: 0.7, 2: 0.6, 3: 0.5, 4: 0.42, 5: 0.36, 6: 0.3, 7: 0.25, 8: 0.18, 9: 0.1, 10: 0}
        },
        'midrange': {
            'initialQuality': 30000, 'salvageValue': 2000, 'mpg': 35, 'mpkwh': 3.0, 'gasRepairs': 800, 'evRepairs': 560,
            'depreciationCurve': {0: 1.0, 1: 0.7, 2: 0.6, 3: 0.5, 4: 0.42, 5: 0.36, 6: 0.3, 7: 0.25, 8: 0.18, 9: 0.1, 10: 0}
        },
        'economy': {
            'initialQuality': 15000, 'salvageValue': 2000, 'mpg': 40, 'mpkwh': 3.5, 'gasRepairs': 600, 'evRepairs': 420,
            'depreciationCurve': {0: 1.0, 1: 0.7, 2: 0.6, 3: 0.5, 4: 0.42, 5: 0.36, 6: 0.3, 7: 0.25, 8: 0.18, 9: 0.1, 10: 0}
        }
    },
    'peopleGroups': {
        10000:  {'fraction': 0.05,  'utilityFunction': specificModel.peakedUtility(2000),  'discountRate': 0.10},
        20000:  {'fraction': 0.125, 'utilityFunction': specificModel.peakedUtility(4000),  'discountRate': 0.09},
        30000:  {'fraction': 0.20,  'utilityFunction': specificModel.peakedUtility(6000),  'discountRate': 0.08},
        40000:  {'fraction': 0.25,  'utilityFunction': specificModel.peakedUtility(10000), 'discountRate': 0.07},
        60000:  {'fraction': 0.20,  'utilityFunction': specificModel.peakedUtility(20000), 'discountRate': 0.06},
        80000:  {'fraction': 0.09,  'utilityFunction': specificModel.peakedUtility(40000), 'discountRate': 0.05},
        100000: {'fraction': 0.085, 'utilityFunction': specificModel.peakedUtility(70000), 'discountRate': 0.04}
    },
    'electricityCost': {2022: 0.10, 2023: 0.10, 2024: 0.10, 2025: 0.10, 2026: 0.10, 2027: 0.10, 2028: 0.10, 2029: 0.10, 2030: 0.10, 2031: 0.10,
                        2032: 0.10, 2033: 0.10, 2034: 0.10, 2035: 0.10, 2036: 0.10, 2037: 0.10, 2038: 0.10, 2039: 0.10, 2040: 0.10, 2041: 0.10,
                        2042: 0.10, 2043: 0.10, 2044: 0.10, 2045: 0.10, 2046: 0.10, 2047: 0.10, 2048: 0.10, 2049: 0.10, 2050: 0.10, 2051: 0.10},
    'gasCost':{2022: 3.50, 2023: 3.50, 2024: 3.50, 2025: 3.50, 2026: 3.50, 2027: 3.50, 2028: 3.50, 2029: 3.50, 2030: 3.50, 2031: 3.50,
               2032: 3.50, 2033: 3.50, 2034: 3.50, 2035: 3.50, 2036: 3.50, 2037: 3.50, 2038: 3.50, 2039: 3.50, 2040: 3.50, 2041: 3.50,
               2042: 3.50, 2043: 3.50, 2044: 3.50, 2045: 3.50, 2046: 3.50, 2047: 3.50, 2048: 3.50, 2049: 3.50, 2050: 3.50, 2051: 3.50},
    'transactionCost': 500,
    'utilityScale': 0.15
}
