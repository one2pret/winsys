import re

from elixir import *
options_defaults['shortnames'] = True

__all__ = [
  'Day', 'Church', 'MassTime', 'Area', 'Link',
  'HDO', 'WhatsNew', 'PostcodeCoords', 'MotorwayChurches',
  'SearchScores'
]

#~ DB_FILENAME = os.path.abspath ("masses.db")
#~ metadata.bind = "sqlite:///%s" % DB_FILENAME

class Day (Entity):
  
  code = Field (Unicode (1), primary_key=True)
  name = Field (Unicode (60), required=True)
  
  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.code)
    
  def __str__ (self):
    return self.name

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
  
  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
  def __str__ (self):
    return self.fullname

  def _full_name (self):
    if self.alias:
      return "%s (%s)" % (self.name, self.alias)
    else:
      return self.name
  full_name = property (_full_name)
  
  def all_areas (self):
    for area in self.areas:
      for next_area, next_level in area.tree_up (0):
        yield next_area, next_level
  
  def has_mass (self, day_code):
    return any (mass for mass in self.mass_times if mass.day_code == day_code)

class MassTime (Entity):
  
  church = ManyToOne (Church, required=True)
  day = ManyToOne (Day, required=True)
  hh24 = Field (String (4), required=True)
  eve = Field (Boolean, required=True, default=False)
  restrictions = Field (Unicode (100))

  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
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
  
  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
  def __str__ (self):
    return self.name

  def tree (self, level=0):
    yield self, level
    for area_in in self.areas:
      for next_area, next_level in area_in.tree (level+1):
        yield next_area, next_level
        
  def tree_up (self, level=0):
    yield self, level
    if self.in_area:
      for next_area, next_level in self.in_area.tree_up (level+1):
        yield next_area, next_level
  
  def all_churches (self):
    churches = set ()
    for area, level in self.tree ():
      churches.update (area.churches)
    return churches

class Link (Entity):
  
  subject = Field (Unicode (50))
  title = Field (Unicode (100))
  link = Field (Unicode (150), required=True)
  sequence = Field (Integer)

  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
  def __str__ (self):
    return self.title

class HDO (Entity):
  
  area = ManyToOne (Area, required=True)
  name = Field (Unicode (60), required=True)
  yyyymmdd = Field (String (8), required=True)
  notes = Field (Text)
  
  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
  def __str__ (self):
    return "%s - %s" % (self.area, self.name)

class WhatsNew (Entity):
  
  updated_on = Field (Date, required=True)
  text = Field (Text, required=True)

  def linked_text (self):
    text = self.text
    church_match = re.search (u"\[(.*)\]", self.text)
    if church_match:
      church_name = church_match.group (1)
      if "," in church_name:
        name, alias = [i.strip () for i in church_name.split (",", 1)]
        kwargs = dict (name=name, alias=alias)
      else:
        kwargs = dict (name=church_name)
      church = Church.query ().filter_by (**kwargs).first ()
      if church:
        for area, level in church.all_areas ():
          link = "/en/area/%s/churches/%d#p%d" % (area.code, church.id, church.id)
          href = u'<a href="%s">%s</a>' % (link, church.full_name)
          text = text.replace (u"[%s]" % church_name, href)
          break
        else:
          text = text.replace (u"[", u"").replace (u"]", u"")
          text += u"<!-- No area found for church id %d -->" % church.id
      else:
        text = text.replace (u"[", u"").replace (u"]", u"")
    return text

  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
  def __str__ (self):
    return "%s: %s" % (self.updated_on, self.text)

class PostcodeCoords (Entity):
  
  area = ManyToOne (Area, required=True)
  outcode = Field (Unicode (10), required=True)
  os_x = Field (Integer)
  os_y = Field (Integer)
  latitude = Field (Numeric)
  longitude = Field (Numeric)
  
  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
class MotorwayChurches (Entity):
  
  church = ManyToOne (Church, required=True)
  motorway = Field (Unicode (10), required=True)
  junction = Field (Unicode (10), required=True)
  distance = Field (Numeric)
  notes = Field (Unicode (100))

  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
    
class SearchScores (Entity):
  
  church = ManyToOne (Church, required=True)
  word = Field (Unicode (100), required=True)
  score = Field (Integer, required=True)

  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.id)
