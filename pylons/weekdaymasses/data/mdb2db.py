import os, sys
from decimal import Decimal

import adodbapi

import sql
from distance import Distance
import utils

import model

SOURCE_DB_NAME = "masses.mdb"

def decimalise (string):
  return None if string is None else Decimal (string.strip ())

def populate_days (log=False):
  model.Day (code=u"K", name=u"Weekday")
  model.Day (code=u"U", name=u"Sunday")
  model.Day (code=u"A", name=u"Saturday")
  model.Day (code=u"H", name=u"Holy Day of Obligation")
  model.session.flush ()

def populate_churches (source_db, log=False):
  SELECT_SQL = """
    SELECT
      id,
      Parish,
      Alias,
      IsParish,
      IsShrine,
      Address,
      Postcode,
      Directions,
      Phone,
      Tube,
      XCoord,
      YCoord,
      Zoom,
      map_link,
      website,
      WeekdayMassTimes,
      SundayMassTimes,
      SaturdayMassTimes,
      HDOMassTimes,
      latitude,
      longitude,
      scale,
      email,
      is_persistent_offender,
      last_updated_on
    FROM
      Churches
    LEFT OUTER JOIN Parishes ON
      Parishes.ChurchId = Churches.id
    ORDER BY
      id
  """
  print "Populating churches"
  for church in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print church.Parish.encode (sys.getdefaultencoding (), "ignore")
    model.Church (
      id=church.id,
      name=church.Parish,
      alias=church.Alias,
      is_parish=church.IsParish,
      is_shrine=church.IsShrine,
      address=church.Address,
      postcode=church.Postcode,
      directions=church.Directions,
      phone=church.Phone,
      public_transport=church.Tube,
      x_coord=church.XCoord,
      y_coord=church.YCoord,
      zoom_level=church.Zoom,
      map_link=church.map_link,
      website=church.website,
      weekday_mass_times=church.WeekdayMassTimes,
      sunday_mass_times=church.SundayMassTimes,
      saturday_mass_times=church.SaturdayMassTimes,
      holy_day_of_obligation_mass_times=church.HDOMassTimes,
      latitude=decimalise (church.latitude),
      longitude=decimalise (church.longitude),
      scale=church.scale,
      email=church.email,
      is_persistent_offender=church.is_persistent_offender,
      last_updated_on=church.last_updated_on
    )
  model.session.flush ()

def populate_areas (source_db, log=False):
  SELECT_SQL = """
    SELECT
      area,
      in_area,
      description,
      [external],
      weekday_website,
      sunday_website,
      saturday_website,
      holy_day_of_obligation_website,
      area_order
    FROM
      areas
    ORDER BY
      area
  """
  print "Populating areas"
  areas = {}
  in_areas = {}
  for area in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print area.area.encode (sys.getdefaultencoding (), "ignore")
    this_area = model.Area (
      code=utils.as_code (area.area),
      name=area.area,
      description=area.description,
      weekday_website=area.weekday_website,
      sunday_website=area.sunday_website,
      saturday_website=area.saturday_website,
      holy_day_of_obligation_website=area.holy_day_of_obligation_website,
      is_external=area.external,
      area_order=area.area_order
    )
    in_areas[this_area] = area.in_area
  model.session.flush ()

  for area, in_area_name in in_areas.items ():
    area.in_area = model.Area.get_by (name=in_area_name)
  model.session.flush ()

def populate_church_areas (source_db, log=False):
  SELECT_SQL = """
    SELECT
      ChurchId,
      Area
    FROM
      Church2Area
    ORDER BY
      ChurchId,
      Area
  """
  print "Populating church areas"
  for church2area in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print str (church2area).encode (sys.getdefaultencoding (), "ignore")
    church = model.Church.get_by (id=church2area.ChurchId)
    church.areas.append (model.Area.get_by (name=church2area.Area))
  model.session.flush ()

def populate_mass_times (source_db, log=False):
  SELECT_SQL = "SELECT * FROM MassTimes"
  print "Populate mass times"
  for mass_time in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print mass_time.ParishId, mass_time.Day.encode (sys.getdefaultencoding (), "ignore")
    model.MassTime (
      church=model.Church.get_by (id=mass_time.ParishId),
      day=model.Day.get_by (code=mass_time.Day),
      hh24=mass_time.hh24,
      eve=mass_time.eve,
      restrictions=mass_time.restrictions
    )
  model.session.flush ()

def populate_whats_new (source_db, log=False):
  SELECT_SQL = """
    SELECT
      updated_on,
      text
    FROM
      whatsnew
  """
  print "Populate what's new"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.text[:50].encode (sys.getdefaultencoding (), "ignore")
    model.WhatsNew (
      updated_on=row.updated_on,
      text=row.text
    )
  model.session.flush ()

def populate_postcode_coords (source_db, log=False):
  SELECT_SQL = """
    SELECT
      id,
      postcode_outcode,
      os_x,
      os_y,
      latitude,
      longitude
    FROM
      Postcode_Lat_Long_Lookup
  """
  print "Populate postcode coords"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.postcode_outcode.encode (sys.getdefaultencoding (), "ignore")
    model.PostcodeCoords (
      area=model.Area.get_by (name=u"GB"),
      outcode=row.postcode_outcode,
      os_x=row.os_x,
      os_y=row.os_y,
      latitude=row.latitude,
      longitude=row.longitude
    )
  model.session.flush ()

def populate_hdos (source_db, log=False):
  SELECT_SQL = """
    SELECT
      ID,
      Name,
      Area,
      Holy_day_date,
      Notes
    FROM
      holy_days_of_obligation
  """
  print "Populate HDOs"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.Name.encode (sys.getdefaultencoding (), "ignore")
    model.HDO (
      area=model.Area.get_by (name=row.Area),
      name=row.Name,
      yyyymmdd=row.Holy_day_date,
      notes=row.Notes
    )
  model.session.flush ()

def populate_motorways (source_db, log=False):
  SELECT_SQL = """
    SELECT
      ID,
      Church_ID,
      Motorway,
      Junction,
      Distance_Miles,
      Notes
    FROM
      Motorways
  """
  print "Populate motorways"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.Motorway.encode (sys.getdefaultencoding (), "ignore"), row.Junction.encode (sys.getdefaultencoding (), "ignore")
    if row.Distance_Miles:
      #
      # For some bizarre reason, Distance_Miles is coming in as Unicode
      #
      distance_metres = Distance (Decimal (row.Distance_Miles), "MILES").as_metres ()
    else:
      distance_metres = None
    model.MotorwayChurches (
      church=model.Church.get_by (id=row.Church_ID),
      motorway=row.Motorway,
      junction=row.Junction,
      distance=distance_metres,
      notes=row.Notes
    )
  model.session.flush ()

def populate_links (source_db, log=False):
  SELECT_SQL = """
    SELECT
      ID,
      [Subject Heading] AS subject,
      Title,
      Link,
      [Sort Order] AS sequence
    FROM
      [Useful Links]
  """
  print "Populate links"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.Title
    model.Link (
      subject=row.subject,
      title=row.Title,
      link=row.Link,
      sequence=row.sequence
    )
  model.session.flush ()
    
def populate_search_scores (log=False):
  SELECT_SQL1 = """
    SELECT
      id,
      name,
      alias,
      address,
      postcode
    FROM
      churches
  """
  print "Populate search scores"
  for church in model.Church.query ():
    words = {}
    words.setdefault (10, []).extend (utils.filter_search_words (church.name))
    words.setdefault (10, []).extend (utils.filter_search_words (church.alias or ""))
    words.setdefault (2, []).extend (utils.filter_search_words (church.address or ""))
    for area in set (area for area, level in church.all_areas ()):
      words.setdefault (5, []).extend (utils.filter_search_words (area.name))
      
    scores = {}
    for score, wordlist in words.items ():
      for word in wordlist:
        if word in scores:
          scores[word] += score
        else:
          scores[word] = score

    if log: print repr (church.name), "=>", scores
    for word, score  in scores.items ():
      model.SearchScores (church=church, word=word, score=score)
      
    model.session.flush ()

def get_source_db (name=SOURCE_DB_NAME):
  dsn = [
    ("Provider", "Microsoft.Jet.OLEDB.4.0"),
    ("Data Source", SOURCE_DB_NAME),
    ("User Id", "admin"),
    ("Password", "")
  ]
  return adodbapi.connect (";".join ("%s=%s" % (x, y) for (x, y) in dsn))

if __name__ == '__main__':
  print "Create structure"
  source_db = get_source_db (SOURCE_DB_NAME)
  if os.path.exists ("masses.db"): os.remove ("masses.db")
  model.setup_all (True)

  try:
    populate_days (source_db)
    populate_areas (source_db)
    populate_postcode_coords (source_db)
    populate_whats_new (source_db)
    populate_churches (source_db)
    populate_motorways (source_db)
    populate_church_areas (source_db)
    populate_mass_times (source_db)
    populate_hdos (source_db)
    populate_links (source_db)
    populate_search_scores ()
  finally:
    model.session.flush ()
    model.session.close ()
