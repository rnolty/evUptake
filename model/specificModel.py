import functools

from genericModel import carsSortedByQuality

globalParameters = {}    # this will be replaced by whoever calls us

def initializeCarsForModelType(year, modelType, isEV):
    initialQuality = globalParameters['carTypes'][modelType]['initialQuality']
    depreciationCurve = globalParameters['carTypes'][modelType]['depreciationCurve']
    numYears = len(depreciationCurve) - 1   # -1 since last entry is 0
    carsThisModel = {}
    for age in range(numYears):
        name = modelType + "-" + str(year - age) + "-" + str(isEV)
        # arbitrary assumption -- initially, price = quality
        carsThisModel[name] = {'model': modelType, 'year': year - age, 'EV': isEV,
            'history': {
                year: {
                    'price': initialQuality*depreciationCurve[age],
                    'quality': initialQuality*depreciationCurve[age], 'batteryValue': 0
                }
            }
        }
    #print("\n\n***", "carsThisModel:", carsThisModel)
    return carsThisModel

# create the cars object -- just called once per simulation
def initializeCars(year):
    # arbitrary assumptions -- equal shares of each model type and each year until the quality is 0.
    allCars = {}
    for modelType in globalParameters['carTypes'].keys():
        allCars.update(initializeCarsForModelType(year, modelType, False))
    return allCars

# arbitrary assumption for shape of utility curve -- for qualities near the peak, utility is equal to
#    quality; curve drops to zero from 1.5*peak to 2.0*peak, and from 0.75*peak to 0.5*peak
def myUtility(peak, quality):
    if (quality < 0.5*peak):
        return 0
    if (quality < 0.75*peak):
        return 0.75*peak*(quality - 0.5*peak)/(0.75*peak - 0.5*peak)
    if (quality < 1.5*peak):
        return quality
    if (quality < 2.0*peak):
        return 1.5*peak*(2.0*peak - quality)/(2.0*peak - 1.5*peak)
    return 0

# curry myUtility -- this function returns a function of quality only; that function can be stored as the utility
#    function for a demographic group
def peakedUtility(peak):
    return functools.partial(myUtility, peak)

# arbitrary assumption for initial ownership of cars -- lowest quality cars owned by lowest income-level groups
def initializePopulation(cars, year):
    # initialize population for this year with empty car lists
    populationThisYear = {
        year: {
            peopleGroup['income']: {
                'fraction': peopleGroup['fraction'], 'cars': {}
            } for peopleGroup in globalParameters['peopleGroups']
        }
    }

    allModels = carsSortedByQuality(cars, year)

    # distribute the lowest-quality models to the lowest income demographic groups
    modelShare = 1.0 / len(allModels)           # e.g. if there are 20 models, 5% of population has each model
    currentModel = 0
    modelShareRemaining = modelShare
    # list of peopleGroups in globalParameters must be ordered by increasing income
    for incomeLevel in [peopleGroup['income'] for peopleGroup in globalParameters['peopleGroups']]:
        populationRemaining = populationThisYear[year][incomeLevel]['fraction']
        while (populationRemaining > 0.0001):     # don't continue if only roundoff error remains
            if (populationRemaining >= modelShareRemaining):
                populationThisYear[year][incomeLevel]['cars'][allModels[currentModel]] = {'fraction': modelShareRemaining}
                populationRemaining -= modelShareRemaining
                currentModel += 1
                modelShareRemaining = modelShare
            else:
                populationThisYear[year][incomeLevel]['cars'][allModels[currentModel]] = {'fraction': populationRemaining}
                modelShareRemaining -= populationRemaining
                populationRemaining = 0

    return populationThisYear