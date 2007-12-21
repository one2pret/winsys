import os, sys
import ConfigParser
import fnmatch
import glob
import re

import pyodbc
import pysvn
import sql
import sqldmo

def databases (server):
  return sqldmo.databases (server)

def servers ():
  return sqldmo.servers ()

def database_connection (server, database):
  """Attempt to create a database context equivalent
  to that of Query Analyzer."""
  INITIAL_SQL = """
set nocount off
set arithabort off
set concat_null_yields_null off

set ansi_nulls off

set cursor_close_on_commit off
set ansi_null_dflt_on off
set implicit_transactions off
set ansi_padding off

set ansi_warnings off
set quoted_identifier off
set lock_timeout -1
"""
  db = sql.pyodbc_connection (server, database)
  db.execute (INITIAL_SQL)
  return db

r1 = re.compile (r"(?:alter|create|drop)\s+(table|procedure|view|function|trigger)\s+(?:\S+\.)?(\S+)(?:(?:\s+on\s+)(\S+))?", re.IGNORECASE)
def db_objects (sql_text):
  found = r1.findall (sql_text.lower ())
  for type, name, table_affected in found:
    if name.startswith ("#") or name.startswith ("_") or name.startswith ("z"):
      continue
    else:
      yield type, name.strip ("[]"), table_affected

def release (db, sql_text):
  OUTPUT_WIDTH = 60
  for n, statement in enumerate (sql_text.split ("\nGO")):
    statement = statement.lstrip ()
    if not statement: continue
    if len (statement) > OUTPUT_WIDTH:
      output_statement = statement[:OUTPUT_WIDTH] + "..."
    else:
      output_statement = statement
    print "%03d => %s" % (1+n, output_statement.replace ("\n", " "))
    try:
      sql.execute_sql (db, sql_text)
    except sql.pyodbc.Error, (error_code, error_details):
      print "\n".join (error_details.split (";"))
      return

def find_release_directory (start_from="."):
  svn = pysvn.Client ()
  try:
    svn.info (start_from)
  except pysvn.ClientError:
    #
    # Not a subversion checkout; don't try
    # to guess.
    #
    return None
  else:
    directory = os.path.abspath (start_from)
    parts = [part.lower () for part in directory.split (os.sep)]
    try:
      n_releases = parts.index ("release")
      releases = os.sep.join (parts[:n_releases+1])
      release = os.path.join (releases, "..", "base")
    except ValueError:
      return None

    if os.path.isdir (release):
      return os.path.abspath (release)
    else:
      return None

def get_release_candidates (release_path):
  if release_path:
    return [os.path.basename (filepath) for filepath in glob.glob (os.path.join (release_path, "*.sql"))]
  else:
    return []

def rescript_objects ((server, database), objects_affected):
  #
  # Attempt to find an ancestory called "releases". Then
  # find that directory's "release" sibling. If that fails
  # at any stage, don't try to script.
  #
  release_directory = find_release_directory ()
  if release_directory is None:
    print "No release directory found; not scripting"
  else:
    print "Scripting to", release_directory
    
    dmo = sqldmo.Database (server, database)
    for type, name, extra_info in objects_affected:
      print type, name
      type_directory = os.path.join (release_directory, type.lower () + "s")
      if not os.path.exists (type_directory): os.mkdir (type_directory)
      f = open (os.path.join (type_directory, "%s.sql" % name), "wb")
      try:
        f.write (dmo.scripted (type, name, extra_info))
      finally:
        f.close ()

def main (directory, (server, database)):
  print "Working in", os.path.abspath (directory)
  
  db = database_connection (server, database)
  try:
    objects_affected = set ()
    if os.path.isfile ("release.cfg"):
      filepaths = open ("release.cfg").read ().splitlines ()
    else:
      filepaths = glob.glob (os.path.join (directory, "*.sql"))
      
    print "Releasing..."
    for filepath in sorted (filepaths):
      print
      print filepath
      sql_text = "\n".join (line for line in open (filepath).read ().splitlines () if not line.startswith ("--"))
      objects_affected.update (db_objects (sql_text))
      release (db, sql_text)
  finally:
    db.close ()
    
  print
  print "Scripting..."
  rescript_objects ((server, database), sorted (objects_affected))

class ReleaseConfig (object):

  def __init__ (self, filename=None):
    self.ini_filename = filename
    self.ini = ConfigParser.ConfigParser ()
    self.ini.read (filename)

    if self.ini.has_section ("files"):
      if self.ini.has_option ("files", "directory"):
        self.directory = self.ini.get ("files", "directory")
      else:
        self.directory = ""
      self.filenames = [self.ini.get ("files", i) for i in self.ini.options ("files")]
    else:
      self.directory = ""
      self.filenames = []
      
    if self.ini.has_section ("database"):
      db_options = dict (self.ini.items ("database"))
    else:
      db_options = {}    
    self.server = db_options.get ("server", "")
    self.database = db_options.get ("database", "")
    
    if self.ini.has_section ("scripting"):
      scripting_options = dict (self.ini.items ("scripting"))
    else:
      scripting_options = {}
    self.script_to = scripting_options.get ("script_to", "")

if __name__ == '__main__':
  if len (sys.argv) > 1:
    directory = sys.argv[1]
  else:
    directory = "."
  if len (sys.argv) > 2:
    server, database = sys.argv[2].split (".")
  else:
    server, database = "VODEV1", "DEV"
  
  main (directory, (server, database))
