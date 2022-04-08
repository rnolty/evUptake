#import sys
#sys.path.append("..")
from matplotlib import pyplot as plt 
import numpy as np

from model.test_model import globalParameters

def plotUtilityFunctions(): 
    x = np.linspace(0, 70000, 400)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for i in range(7):
        ax.plot(   x, [globalParameters['peopleGroups'][i]['utilityFunction'](xx) for xx in x]   )

    fig.show()
    plt.savefig("foo.png")

if __name__ == "__main__":
    plotUtilityFunctions()
