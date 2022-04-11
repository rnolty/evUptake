from model.defaultGlobalParameters import globalParameters

from model import specificModel, genericModel
genericModel.globalParameters = globalParameters
specificModel.globalParameters = globalParameters

thisYear = 2022
cars = specificModel.initializeCars(thisYear)
#print("\n\nCars:\n", cars)

# initialize population for this year, including what cars they own
population = specificModel.initializePopulation(cars, thisYear)
#print("\n\nPopulation:\n", population)

for incomeLevel in population[thisYear].keys():
    theSum = sum(v['fraction'] for k,v in population[thisYear][incomeLevel]['cars'].items())
    print("***", population[thisYear][incomeLevel]['fraction'], theSum)

#population, cars = genericModel.determinePrices(*genericModel.initializeYear(population, cars))

#print("\n\nPopulation:\n", population, "\n\nCars:\n", cars, "\n\n\n")

print("\n\n\n")