import argparse
import glob

argumentParser = argparse.ArgumentParser("TemperaturePumper")

argumentParser.add_argument('--fileName', 
							required=True,
			                help="Fully qualified filename for temperature file")

argumentParser.add_argument('--address', 
							required=True,
			                help="Fully qualified filename for temperature file")

arguments = argumentParser.parse_args()

fileName = arguments.fileName

f = open(fileName)

for line in f:
	tokens = line.split(',')
	
	message = {}
	readings = {}
	temperature = {}
	supply_voltage = {}
	
	temperature["value"] = tokens[2]
	temperature["units"] = "degrees F"

	readings["temperature"] = temperature

	supply_voltage["value"] = tokens[3]
	supply_voltage["units"] = "volts"

	message["readings"] = readings
	message["time_stamp"] = tokens[1] + "T" + tokens[0]
	message["supply_voltage"] = supply_voltage
	message["name"] = "WeatherSensor"
	message["address"] = arguments.address

	print message






