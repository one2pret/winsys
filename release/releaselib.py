import os, sys
import ConfigParser
import fnmatch
import glob
import re
import subprocess

import pyodbc
import pysvn
import sql
import sqldmo

def databases (server):
  try:
    return sqldmo.databases (server)
  except sqldmo.SQLDMO_Exception:
    return []

def servers ():
  return sqldmo.servers ()

def database_connection (server, database, username=None, password=None):
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
  db = sql.pyodbc_connection (server, database, username, password)
  db.execute (INITIAL_SQL)
  return db

r1 = re.compile (r"(?:alter|create|drop)\s+(table|procedure|view|function|trigger)\s+(?:\S+\.)?(\S+)(?:(?:\s+on\s+)(\S+))?", re.IGNORECASE)
def db_objects (sql_text):
  found = r1.findall (sql_text.lower ())
  for type, name, table_affected in found:
    if name.startswith ("#") or name.startswith ("_") or name.startswith ("z"):
      continue
    elif len (name) < 3:
      continue
    else:
      yield type, name.strip ("[]"), table_affected

def release (db, sql_text, callback=None):
  OUTPUT_WIDTH = 60
  for n, statement in enumerate (sql_text.split ("\nGO")):
    statement = statement.lstrip ()
    if not statement: continue
    if len (statement) > OUTPUT_WIDTH:
      output_statement = statement[:OUTPUT_WIDTH] + "..."
    else:
      output_statement = statement
    try:
      sql.execute_sql (db, sql_text)
    except sql.pyodbc.Error, (error_code, error_details):
      raise Exception ("\n".join (error_details.split (";")))

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
  if os.path.isdir (release_path):
    return [os.path.basename (filepath) for filepath in glob.glob (os.path.join (release_path, "*.sql"))]
  else:
    raise Exception ("%s is not a directory" % release_path)

def rescript_objects ((server, database, username, password), objects_affected, release_directory, callback=None):
  if not os.path.isdir (release_directory):
    raise Exception ("Release directory not found")
  
  this_path = os.path.dirname (sys.executable) if getattr (sys, "frozen", None) else os.path.dirname (__file__)
  scripter = os.path.join (os.environ['ProgramFiles'], "scripter", "scripter.exe")
  if not os.path.exists (scripter):
    raise Exception ("Scripter not found at %s" % scripter)

  filenames = set ()
  for object_type, object_name, table_affected in objects_affected:
    if username:
      connection_string = "%s:%s@%s" % (username, password, server)
    else:
      connection_string = server
    if object_type == "trigger":
      object_name = "%s!%s" % (table_affected.replace ("dbo.", ""), object_name)
    cmd = [scripter, connection_string, database, release_directory, "%s:%s" % (object_type, object_name)]
    process = subprocess.Popen (cmd, shell=True, stdout=subprocess.PIPE)
    result = process.wait ()
    output = process.stdout.read ()
    if result == 0:
      released_filenames = output.splitlines ()
      filenames.update (os.path.normpath (f) for f in released_filenames)
    else:
      if callback: callback ("Command line: %s" % " ".join (cmd))
      raise Exception (output)
  
  return filenames

def affected_objects (filepaths):
  objects = set ()
  for filepath in filepaths:
    sql_text = "\n".join (line for line in open (filepath).read ().splitlines () if not line.lstrip ().startswith ("--"))
    objects.update (db_objects (sql_text))
  return objects

def release_objects ((server, database, username, password), filepaths, callback=None):
  db = database_connection (server, database, username, password)
  for filepath in filepaths:
    if callback: callback ("  -> %s " % filepath)
    sql_text = "\n".join (line for line in open (filepath).read ().splitlines ())
    release (db, sql_text, callback)

def commit_objects (filepaths, commit_message):
  """Objects can be added, modified or deleted. Added objects are in
  the directory but unversioned; modified are in the directory and
  modified; deleted are versioned but are not in the directory.
  svn add new objects; svn remove deleted object; ignore any unmodified objects
  Then commit the lot.
  """
  svn = pysvn.Client ()
  commit_package = set ()
  for filepath in filepaths:
    for change in svn.status (filepath):
      if change.text_status == pysvn.wc_status_kind.unversioned:
        svn.add (filepath)
        commit_package.add (filepath)
      elif change.text_status == pysvn.wc_status_kind.modified:
        commit_package.add (filepath)
      elif change.text_status == pysvn.wc_status_kind.missing:
        svn.remove (filepath)
        commit_package.add (filepath)
  
  svn.checkin (sorted (commit_package), commit_message)

def main (directory, (server, database, username, password)):
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
  rescript_objects ((server, database, username, password), sorted (objects_affected))

class ReleaseConfig (object):

  def __init__ (self, filename=None):
    self.ini_filename = filename
    self.ini = ConfigParser.ConfigParser ()
    self.ini.read (filename)

    self.directory = self.filenames = None
    if self.ini.has_section ("files"):
      if self.ini.has_option ("files", "directory"):
        self.directory = self.ini.get ("files", "directory")
      else:
        self.directory = ""
      self.filenames = [self.ini.get ("files", i) for i in self.ini.options ("files") if i not in ['directory']]
    
    if not self.directory:
      self.directory = os.path.dirname (filename)
    if not self.filenames:
      self.filenames = sorted (glob.glob (os.path.join (self.directory, "*.sql")))
      
    if self.ini.has_section ("database"):
      db_options = dict (self.ini.items ("database"))
    else:
      db_options = {}    
    self.server = db_options.get ("server", "")
    self.database = db_options.get ("database", "")
    self.username = db_options.get ("username", "")
    self.password = db_options.get ("password", "")
    
    if self.ini.has_section ("scripting"):
      scripting_options = dict (self.ini.items ("scripting"))
    else:
      scripting_options = {}
    self.script_to = scripting_options.get ("script_to", "")
    self.comment_in = scripting_options.get ("comment_in", "release.txt")

    self._heat_call = None
    
  def heat_call (self):
    """Attempt to find the HEAT call associated with this package, as follows:
    If the releasespec filename has a >=5-digit number in it, use that,
    otherwise, walk back up the tree looking for a directory which starts
    with a >=5-digit number
    """
    heat_call_re = re.compile ("(\d{5,8})")
    if self._heat_call is None:
      match = heat_call_re.search (self.ini_filename)
      if match:
        self._heat_call = int (match.group (0))
      else:
        directory = os.path.abspath (os.path.dirname (self.ini_filename))
        parts = reversed (part.lower () for part in directory.split (os.sep))
        for part in parts:
          match = heat_call_re.match (part)
          if match:
            self._heat_call = int (match.group (0))
            break

    return self._heat_call

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
