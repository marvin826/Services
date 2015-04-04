import sqlite3
import argparse
import glob

argumentParser = argparse.ArgumentParser("build_tables")

argumentParser.add_argument('--dbTableDir', 
							required=True,
			                help="Path to directory that contains datbase table definitions")

argumentParser.add_argument('--dbFileName', 
							required=True,
			                help="Fully qualified filename for SQLite database file")

arguments = argumentParser.parse_args()

table_files = glob.glob(arguments.dbTableDir + "/*.sql")

print "Opening database file: " + arguments.dbFileName

conn = sqlite3.connect(arguments.dbFileName)
c = conn.cursor()

for table_file in table_files:
	print "Building table " + table_file + "..."

	try:
		f = open(table_file)
		sqlcmds = f.read()
		f.close()

		c.execute(sqlcmds)
	except Exception, e:
		print "Error : " + str(e)

conn.commit()



