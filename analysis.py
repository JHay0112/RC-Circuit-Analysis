'''
    Analysis of raw data from voltage across RC circuit
'''

# - Imports

import matplotlib.pyplot as plt
import math
from typing import List
from jmath import Uncertainty

# - Functions

def data_from_file(filename: str) -> List:
    '''Reads data from a file'''

    # Get file contents
    with open(filename) as file:
        rawdata = file.readlines()

    data = []

    for line in rawdata:
        # Process lines stripping off unneeded stuff
        line = line[1:-3]
        line = line.split(", ")
        # Add uncertainties to voltages
        line = [float(line[0])] + [Uncertainty(float(data), 0.00005) for data in line[1:]]
        data.append(line)

    return data

def main():
    '''Main'''

    # Get data
    data = data_from_file("rawdata.txt")

    # Store attributes
    times = []
    start_voltages = []
    end_voltages = []
    currents = []

    # Values with estimated uncertainties
    resistance = Uncertainty(220, 10)
    capacitance = Uncertainty(100e-6, 5e-6)
    supply_voltage = Uncertainty(5, 0.00005)
    
    # Starting time
    initial_time = data[0][0]

    # Do a little more data processing
    for row in data:
        # Get time
        time = row[0] - initial_time
        times.append(time)
        # Get voltages
        start_voltages.append(row[1])
        end_voltages.append(row[2])
        currents.append((row[1] - row[2])/resistance)

    # Split out currents and current uncertainties
    current_uncertainties = [current.abs_uncertainty() for current in currents]
    currents = [current.value for current in currents]

    # Generate model
    model_currents = []
    model_times = range(600)

    for time in model_times:
        # Move to milliseconds
        time = time/1000
        # Try to calculate with theoretical model
        try:
            model_currents.append((supply_voltage/resistance) * (-time/(resistance*capacitance)).apply(math.exp))
        except:
            # For values that equal zero we need to have a special case for zero division errors in rel_uncertainty()
            model_currents.append(Uncertainty(0, 0))

    # Split out model uncertainties and model currents
    model_uncertainties = [current.abs_uncertainty() for current in model_currents]
    model_currents = [current.value for current in model_currents]

    # Plot
    axes = plt.axes()
    
    # Plot with error bars
    axes.errorbar(model_times, model_currents, yerr = model_uncertainties, label = "Predicted")
    axes.errorbar(times, currents, yerr = current_uncertainties, fmt = ".", label = "Measured")

    #axes.plot(times, end_voltages, label = "Final Voltage")

    axes.set_xlabel("Time (ms)")
    axes.set_ylabel("Current (A)")
    #axes.set_title("Current in a charging RC Circuit")

    axes.legend()
    axes.grid()

    plt.show()


# - Main

if __name__ == "__main__":
    main()