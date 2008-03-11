import os, sys
from elixir import *
options_defaults['shortnames'] = True

DB_FILENAME = os.path.abspath ("masses.db")
metadata.bind = "sqlite:///%s" % DB_FILENAME

class Day (Entity):
  
  code = Field (Unicode (1), primary_key=True)
  name = Field (Unicode (60), required=True)

class Church (Entity):
  
  id = Field (Integer, primary_key=True)
  name = Field (Unicode (60), required=True)
  alias = Field (Unicode (60))
  is_parish = Field (Boolean, required=True)
  is_shrine = Field (Boolean, required=True)
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
  email = Field (Unicode (100))
  is_persistent_offender = Field (Boolean)
  last_updated_on = Field (Date)
  areas = ManyToMany ('Area')
  mass_times = OneToMany ('MassTime')

class MassTime (Entity):
  
  church = ManyToOne (Church, required=True)
  day = ManyToOne (Day, required=True)
  hh24 = Field (String (4), required=True)
  eve = Field (Boolean, required=True, default=False)
  restrictions = Field (Unicode (100))

class Area (Entity):
  
  code = Field (Unicode (60), unique=True, required=True)
  name = Field (Unicode (60), unique=True, required=True)
  details = Field (Unicode (100))
  weekday_website = Field (Unicode (200))
  sunday_website = Field (Unicode (200))
  saturday_website = Field (Unicode (200))
  holy_day_of_obligation_website = Field (Unicode (200))
  is_external = Field (Boolean, required=True)
  area_order = Field (Integer)
  in_area = ManyToOne ("Area")
  areas = OneToMany ("Area")
  churches = ManyToMany (Church)
  
  def all_areas (self):
    areas = set (self.areas)
    for area in self.areas:
      areas.update (area.all_areas ())
    return areas
  
  def all_churches (self):
    churches = set (self.churches)
    for area in self.all_areas ():
      churches.updated (area.all_churches ())
    return churches
    
class Link (Entity):
  
  subject = Field (Unicode (50))
  title = Field (Unicode (100))
  link = Field (Unicode (150), required=True)
  sequence = Field (Integer)

class HDO (Entity):
  
  area = ManyToOne (Area, required=True)
  name = Field (Unicode (60), required=True)
  yyyymmdd = Field (String (8), required=True)
  notes = Field (Text)

class WhatsNew (Entity):
  
  updated_on = Field (Date, required=True)
  text = Field (Text, required=True)

class PostcodeCoords (Entity):
  
  area = ManyToOne (Area, required=True)
  outcode = Field (Unicode (10), required=True)
  os_x = Field (Integer)
  os_y = Field (Integer)
  latitude = Field (Numeric)
  longitude = Field (Numeric)
  
class MotorwayChurches (Entity):
  
  church = ManyToOne (Church, required=True)
  motorway = Field (Unicode (10), required=True)
  junction = Field (Unicode (10), required=True)
  distance = Field (Numeric)
  notes = Field (Unicode (100))

class SearchScores (Entity):
  
  church = ManyToOne (Church, required=True)
  word = Field (Unicode (100), required=True)
  score = Field (Integer, required=True)
