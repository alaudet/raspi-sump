""" Module to write water level reading to a database."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
# Module by: USAF_Pride
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html


import sqlite3

# here just in case
try:
    import ConfigParser as configparser  # Python2
except ImportError:
    import configparser  # Python3

config = configparser.RawConfigParser()
config.read("/home/pi/raspi-sump/raspisump.conf")

configs = {
}

database_path = "/home/pi/raspi-sump/data/"


def write_database(water_depth, databasename):
# -----------------------------------------------------------------------------$
#   Create our database & table if it doesn't already exist...

    sqliteDB = databasepath + databasename
# Connecting to the database file
    conn = sqlite3.connect( sqliteDB, isolation_level=None)
    c = conn.cursor()

# Here be Dragons!!!
# Set to "1 == 1" to drop an existing table...
# This will remove all existing data with no warning!
# You have been warned!!!!!!
    if ( 1 == 0):   # <--- Dragon lies here!!!
        sqlStmt = "'DROP TABLE IF EXISTS '" + databasename + "';'"
        c.execute( sqlStmt )
        conn.commit()

    sqlStmt = """
        CREATE TABLE IF NOT EXISTS " + databasename + " (
        insDate		datetime,
        waterdepth	real,
        """

#    print 'sqlStmt = "' + sqlStmt + '"'
    c.execute( sqlStmt)
    conn.commit()

# -----------------------------------------------------------------------------$

#   Insert data into the DB...
    sqlStmt = 'insert into ' + databasename + ' values ( (DATETIME('now'), ' + waterdepth + ');'
    #print 'sqlStmt: ', sqlStmt

    try:
	c.execute( sqlStmt)
    except sqlite3.IntegrityError:
	True
	print ( '\t      >>>----> ERROR: PK violation...' )

# Committing changes...
conn.commit()
#   End DB insert...

conn.close
