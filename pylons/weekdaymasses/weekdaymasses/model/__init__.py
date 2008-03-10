from pylons import config
from sqlalchemy import Column, MetaData, Table, types, create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session (
  sessionmaker (
    autoflush=True,
    transactional=True,
    bind=config['pylons.g'].default_engine
  )
)
metadata = MetaData (config['pylons.g'].default_engine)

class Area (object):
  
  def __repr__ (self):
    return "<Area: %s - %s>" % (self.code, self.name)
  
  def __str__ (self):
    return self.name
    
mapper (Area, Table ("areas", metadata, autoload=True))

class ChurchArea (object):
  pass

mapper (ChurchArea, Table ("church_areas", metadata, autoload=True))

class Church (object):
  
  def __repr__ (self):
    return "<Church: %s>" % self.name
  
  def __str__ (self):
    return "%s (%s)" % (self.name, self.alias)
    
  def areas (self):
    query = Session.query (ChurchArea).filter_by (church_id=self.id)
    return [Session.query (Area).filter_by (id=a.in_area_id).one () for a in query]

mapper (Church, Table ("churches", metadata, autoload=True))
  
class WhatsNew (object): 
  
  def linked_text (self):
    church_match = re.search (u"\[(.*)\]", self.text)
    if church_match:
      church_name = church_match.group (1)
      if "," in church_name:
        name, alias = [i.strip () for i in church_name.split (",", 1)]
        kwargs = dict (name=name, alias=alias)
      else:
        kwargs = dict (name=church_name)
      church = Session.query (Church).filter_by (**kwargs).first ()
      if church:
        for area_id in churches.church_areas (church.id):
          area = areas.area (area_id)
          link = utils.church_link (self.request, self.language, area=area, church=church)
          href = u'<a href="%s">%s</a>' % (link, churches.church_name (church))
          text = text.replace (u"[%s]" % church_name, href)
          break
        else:
          text = text.replace (u"[", u"").replace (u"]", u"")
          text += u"<!-- No area found for church id %d -->" % church.id
      else:
        text = text.replace (u"[", u"").replace (u"]", u"")

mapper (WhatsNew, Table ("whats_new", metadata, autoload=True))

