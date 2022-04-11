from model.defaultGlobalParameters import globalParameters
from model import specificModel, genericModel
specificModel.globalParameters = globalParameters
genericModel.globalParameters = globalParameters

thisYear = 2022

cars = specificModel.initializeCars(thisYear)
population = specificModel.initializePopulation(cars, thisYear)

for i in range(10):
    population, cars = genericModel.determinePrices(*genericModel.initializeYear(population, cars))

print("\n\nPopulation:\n", population)
print("\n\nCars:\n", cars)
print("\n\n\n")