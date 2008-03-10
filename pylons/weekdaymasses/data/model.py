import os, sys
from elixir import *

DB_FILENAME = os.path.abspath ("masses.db")
if os.path.exists (DB_FILENAME): os.remove (DB_FILENAME)
metadata.bind = "sqlite:///%s" % DB_FILENAME
metadata.bind.echo = True

class Church (Entity):
  
  name = Field (Unicode (60))
  alias = Field (Unicode (60))
  is_parish = Field (Boolean)
  is_shrine = Field (Boolean)
  address = Field (Unicode (60))
  postcode = Field (Unicode (60))
  phone = Field (Unicode (60))
  public_transport = Field (Unicode (60))
  directions = Field (Unicode (60))
  x_coord = Field (Integer)
  y_coord = Field (Integer)
  zoom_level = Field (Integer)
  map_link = Field (Unicode (100))
  website = Field (Unicode (200))
  weekday_mass_times = Field (Unicode (100))
  saturday_mass_times = Field (Unicode (100))
  sunday_mass_times = Field (Unicode (100))
  holy_day_of_obligation_mass_times = Field (Unicode (100))
  latitude = Field (Numeric)
  longitude = Field (Numeric)
  scale = Field (Integer)
  in_area = ManyToMany ('Area')

class MassTime (Entity):
  
  church = ManyToOne (Church)
  day = Field (String (1))
  hh24 = Field (String (4))
  eve = Field (Boolean)
  restrictions = Field (Unicode (100))

class Area (Entity):
  
  code = Field (Unicode (60))
  name = Field (Unicode (60))
  details = Field (Unicode (100))
  weekday_website = Field (Unicode (200))
  sunday_website = Field (Unicode (200))
  saturday_website = Field (Unicode (200))
  holy_day_of_obligation_website = Field (Unicode (200))
  is_external = Field (Boolean)
  area_order = Field (Integer)
  in_area = ManyToMany ("Area")

#~ class AreaAreas (Entity):
  
  #~ area = ManyToOne (Area)
  #~ in_area = ManyToOne (Area)

class Link (Entity):
  
  subject = Field (Unicode (50))
  title = Field (Unicode (100))
  link = Field (Unicode (150))
  sequence = Field (Integer)

  def __repr__ (self):
    return "<Link %d: %s>" % (self.sequence, self.subject)
    
class HDO (Entity):
  
  area = ManyToOne (Area)
  name = Field (Unicode (60))
  yyyymmdd = Field (String (8))
  notes = Field (Text)

class WhatsNew (Entity):
  
  updated_on = Field (Date)
  text = Field (Text)

class PostcodeCoords (Entity):
  
  area = ManyToOne (Area)
  outcode = Field (Unicode (10))
  os_x = Field (Integer)
  os_y = Field (Integer)
  latitude = Field (Numeric)
  longitude = Field (Numeric)
  
class MotorwayChurches (Entity):
  
  church = ManyToOne (Church)
  motorway = Field (Unicode (10))
  junction = Field (Unicode (10))
  distance = Field (Numeric)
  notes = Field (Unicode (100))

class SearchScores (Entity):
  
  church = ManyToOne (Church)
  word = Field (Unicode (100))
  score = Field (Integer)

if __name__ == '__main__':
  setup_all ()
  create_all ()
