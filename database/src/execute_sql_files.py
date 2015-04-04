import sqlite3
import argparse
import glob

argumentParser = argparse.ArgumentParser("execute_sql_files")

argumentParser.add_argument('--dbSQLDir', 
							required=True,
			                help="Path to directory that contains datbase SQL definitions")

argumentParser.add_argument('--dbFileName', 
							required=True,
			                help="Fully qualified filename for SQLite database file")

arguments = argumentParser.parse_args()

sql_files = glob.glob(arguments.dbSQLDir + "/*.sql")

print "Opening database file: " + arguments.dbFileName

conn = sqlite3.connect(arguments.dbFileName)
c = conn.cursor()

for sql_file in sql_files:
	print "Executing SQL file " + sql_file + "..."

	try:
		f = open(sql_file)
		sqlcmds = f.read()
		f.close()

		print sqlcmds

		c.executescript(sqlcmds)

	except Exception, e:
		print "Error : " + str(e)

conn.commit()



