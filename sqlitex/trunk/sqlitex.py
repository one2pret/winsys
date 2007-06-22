try:
  import sqlite3 as sqlite
  from sqlite3 import *
except ImportError:
  from pysqlite2 import dbapi2 as sqlite
  from pysqlite2.dbapi2 import *

import decimal

def adapt_decimal (decimal):
  return str (decimal)
  
def convert_decimal (s):
  return decimal.Decimal (s.strip ())

#
# sqlite registers converters for date and timestamp.
# But the matching is case-sensitive, and since I
# always use uppercase datetypes, reregister the
# uppercase variants here.
#
register_converter("DATETIME", converters["TIMESTAMP"])
register_adapter (decimal.Decimal, adapt_decimal)
register_converter ("DECIMAL", convert_decimal)

import math

def _set (instance, attr, value):
  instance.__dict__[attr] = value

class Row (object):
  
  def __init__ (self, cursor, row):
    names = [d[0] for d in cursor.description]
    _set (self, 'description', dict ((name, index) for index, name in enumerate (names)))
    _set (self, "row", list (row))
    
  def __getitem__ (self, index):
    if isinstance (index, int):
      return self.row[index]
    else:
      return self.row[self.description[index]]
    
  def __setitem__ (self, index, value):
    if isinstance (index, int):
      self.row[index] = value
    else:
      self.row[self.description[index]] = value
    
  def __getattr__ (self, key):
    return self.row[self.description[key]]
    
  def __setattr__ (self, key, value):
    self.row[self.description[key]] = value
    
  def __repr__ (self):
    return "<Row: %s>" % self.as_string ()
    
  def __str__ (self):
    return self.as_string ()
  
  def as_tuple (self):
    return tuple (self.row)
    
  def as_dict (self):
    return dict ((name, self.row[index]) for name, index in self.description.items ())
    
  def as_string (self):
    return str (self.as_tuple ())
  
  def columns (self):
    columns = [(index, name) for name, index in self.description.items ()]
    columns.sort ()
    return [name for index, name in columns]

def distance (x1, y1, x2, y2):
  return math.sqrt (((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2)))

def connect (*args, **kwargs):
  #
  # Create a standard connection but with the built-in
  #  date/time handling enabled.
  #
  # NB DECLTYPES looks for the first word of the declared type,
  #  so you can declare a column of type DATE or TIMESTAMP, and
  #  pysqlite will automatically convert to and from a datetime.
  #
  connection = sqlite.connect (
    detect_types=sqlite.PARSE_DECLTYPES | sqlite.PARSE_COLNAMES, 
    *args, 
    **kwargs
  )
  
  #
  # Add a row-handler to allow attribute, index and dict-based columns
  #
  connection.row_factory = Row
  
  #
  # Add convenience functions to database
  #
  connection.create_function ("sqrt", 1, math.sqrt)
  connection.create_function ("distance", 4, distance)
  
  return connection
