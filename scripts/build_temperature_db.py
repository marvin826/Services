import sqlite3
import argparse

argumentParser = argparse.ArgumentParser("build_temperature_db")

argumentParser.add_argument('--dbFile', 
							required=True,
			                help="Path to file for SQLite database")
arguments = argumentParser.parse_args()

conn = sqlite3.connect(arguments.dbFile)

c = conn.cursor()

c.execute('''CREATE TABLE sensors
	         (sensor_address text, sensor_id integer)''')

c.execute('''INSERT INTO sensors
	         VALUES
	         ("0013 a200 408b 4307", 100)''')

c.execute('''CREATE TABLE temperatures
	         (time integer, temperature real, sensor_id integer)''')

conn.commit()



