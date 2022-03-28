genericParameters = {}    # this will be replaced by whoever calls us

def initializeCarsForModelType(year, modelType, isEV):
    initialQuality = globalParameters['carTypes'][modelType]['initialQuality']
    depreciationCurve = globalParameters['carTypes'][modelType]['depreciationCurve']
    numYears = len(depreciationCurve) - 1   # -1 since last entry is 0
    carsThisModel = {}
    for age in range(numYears):
        name = modelType + "-" + str(year - age) + "-" + str(isEV)
        # arbitrary assumption -- initially, price = quality
        carsThisModel[name] = {'model': model, 'year': year - age, 'EV': isEV,
            'history': {'year': year, 'price': initialQuality*depreciationCurve[age],
                'quality': initialQuality*depreciationCurve[age], 'batteryValue': 0
            }
        }
    return carsThisModel

# create the cars object -- just called once per simulation
def initializeCars(year):
    # arbitrary assumptions -- equal shares of each model type and each year until the quality is 0.
    numModelTypes = len(genericParameters['carTypes'].keys())