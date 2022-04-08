from matplotlib import pyplot as plt
from model.test_model import globalParameters, population, cars

year = sorted(population.keys())[-1]

for incomeLevel in population[year].keys():
    frac = []
    price = []
    for (k,v) in population[year][incomeLevel]['cars'].items():
        frac.append(v['fraction'])
        price.append(cars[k]['history'][year]['price'])
    plt.scatter(price,frac)

plt.savefig("fracByPrice.png")

plt.figure()

accum = {}
for incomeLevel in population[year].keys():
    for (k,v) in population[year][incomeLevel]['cars'].items():
        if (k not in accum): accum[k] = 0
        accum[k] += v['fraction']

price = []
frac = []
for k,v in accum.items():
    price.append(cars[k]['history'][year]['price'])
    frac.append(v)
plt.scatter(price,frac)
plt.savefig("fracByPriceTotal.png")

print(sum(frac))

