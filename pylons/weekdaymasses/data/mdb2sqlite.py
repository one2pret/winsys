from __future__ import generators
import os, sys
import datetime
from decimal import Decimal
import re
import string

import adodbapi

import database
import sql
import areas, days
from distance import Distance
import utils

SOURCE_DB_NAME = "data/masses.mdb"

def populate_churches (source_db, target_db, log=False):
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

  INSERT_SQL = """
    INSERT INTO
      churches
    (
      id,
      name,
      alias,
      is_parish,
      is_shrine,
      address,
      postcode,
      directions,
      phone,
      public_transport,
      x_coord,
      y_coord,
      zoom_level,
      map_link,
      website,
      weekday_mass_times,
      sunday_mass_times,
      saturday_mass_times,
      holy_day_of_obligation_mass_times,
      latitude,
      longitude,
      scale,
      email,
      is_persistent_offender,
      last_updated_on
    )
    VALUES
    (
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?
    )
  """
  print "Populating churches"
  for church in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print church.Parish.encode (sys.getdefaultencoding (), "ignore")
    data = church.asTuple ()
    last_updated_on = data[-1]
    if isinstance (last_updated_on, datetime.datetime):
      last_updated_on = last_updated_on.date ()
    database.execute (INSERT_SQL, data[:-1] + (last_updated_on,))

def populate_areas (source_db, target_db, log=False):
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
  INSERT_SQL1 = """
    INSERT INTO
      areas
    (
      code,
      name,
      details,
      weekday_website,
      sunday_website,
      saturday_website,
      holy_day_of_obligation_website,
      is_external,
      area_order
    )
    VALUES
    (
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?,
      ?
      )
  """
  INSERT_SQL2 = """
    INSERT INTO
      area_areas
    (
      area_id,
      in_area_id
    )
    SELECT
      a1.id,
      a2.id
    FROM
      areas AS a1,
      areas AS a2
    WHERE
      a1.name = ? AND
      a2.name = ?
  """
  print "Populating areas"
  areas = {}
  in_areas = {}
  for area in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print area.area.encode (sys.getdefaultencoding (), "ignore")
    areas[area.area] = (
      utils.as_code (area.area),
      area.area,
      area.description,
      area.weekday_website,
      area.sunday_website,
      area.saturday_website,
      area.holy_day_of_obligation_website,
      area.external,
      area.area_order
    )
    in_areas.setdefault (area.area, set ()).add (area.in_area)

  for area_info in areas.values ():
    if log: print str (area_info).encode (sys.getdefaultencoding (), "ignore")
    database.execute (INSERT_SQL1, area_info)
  for out_area in in_areas.keys ():
    if log: print out_area.encode (sys.getdefaultencoding (), "ignore")
    for in_area in in_areas[out_area]:
      if log: print "  ", (in_area or "").encode (sys.getdefaultencoding (), "ignore")
      database.execute (INSERT_SQL2, (out_area, in_area))

def populate_church_areas (source_db, target_db, log=False):
  SELECT_SQL = """
    SELECT
      ChurchId,
      Area
    FROM
      Church2Area
  """
  INSERT_SQL = """
    INSERT INTO
      church_areas
    (
      church_id,
      in_area_id
    )
    SELECT
      c.id,
      a.id
    FROM
      areas AS a,
      churches AS c
    WHERE
      c.id = ? AND
      a.name = ?
  """
  print "Populating church areas"
  for church2area in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print str (church2area).encode (sys.getdefaultencoding (), "ignore")
    database.execute (INSERT_SQL, church2area.asTuple ())

def populate_mass_times (source_db, target_db, log=False):
  SELECT_SQL = "SELECT * FROM MassTimes"
  INSERT_SQL = """
    INSERT INTO
      mass_times
    (
      church_id,
      day,
      hh24,
      eve,
      restrictions
    )
    VALUES
    (
      ?,
      ?,
      ?,
      ?,
      ?
    )
  """
  print "Populate mass times"
  for mass_time in sql.fetch_query (source_db, SELECT_SQL, ()):
    if log: print mass_time.ParishId, mass_time.Day.encode (sys.getdefaultencoding (), "ignore")
    database.execute (INSERT_SQL, [x or "" for x in mass_time.asTuple ()])

def populate_area_day_church_masses (log=False):
  SELECT_SQL = """
    SELECT
      ?, IFNULL (mti.day, '*'), cha.church_id, IFNULL (mti.hh24, '0000'), IFNULL (mti.eve, 0), IFNULL (mti.restrictions, '')
    FROM
      church_areas AS cha
    LEFT OUTER JOIN mass_times AS mti ON
      mti.church_id = cha.church_id
    WHERE
      cha.in_area_id = ?
    UNION ALL SELECT ?, 'K', NULL, NULL, NULL, NULL FROM areas WHERE id = ? AND ifnull (weekday_website, '') > ''
    UNION ALL SELECT ?, 'U', NULL, NULL, NULL, NULL FROM areas WHERE id = ? AND ifnull (sunday_website, '') > ''
    UNION ALL SELECT ?, 'A', NULL, NULL, NULL, NULL FROM areas WHERE id = ? AND ifnull (saturday_website, '') > ''
    UNION ALL SELECT ?, 'H', NULL, NULL, NULL, NULL FROM areas WHERE id = ? AND ifnull (holy_day_of_obligation_website, '') > ''
  """
  INSERT_SQL = """
    INSERT INTO
      area_day_church_masses
    (
      area_id,
      day_code,
      church_id,
      hh24,
      eve,
      restrictions
    )
    VALUES (?, ?, ?, ?, ?, ?)
  """

  print "Populate flattened structure"
  data = set ()
  for this_area in database.select ("SELECT id FROM areas ORDER BY name"):
    for sub_area_id in areas.areas_in (this_area.id):
      rows = list (
        database.select (
          SELECT_SQL,
          (
            this_area.id, sub_area_id,
            this_area.id, sub_area_id,
            this_area.id, sub_area_id,
            this_area.id, sub_area_id,
            this_area.id, sub_area_id,
          )
        )
      )
      data.update ([tuple (row) for row in rows])

  for datum in data:
    if log: print str (datum).encode (sys.getdefaultencoding (), "ignore")
    database.execute (INSERT_SQL, datum)

def populate_whats_new (source_db, target_db, log=False):
  SELECT_SQL = """
    SELECT
      updated_on,
      text
    FROM
      whatsnew
  """
  INSERT_SQL = """
    INSERT INTO
      whats_new
    (
      updated_on,
      text
    )
    VALUES
    (
      ?,
      ?
    )
  """
  print "Populate what's new"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.text[:50].encode (sys.getdefaultencoding (), "ignore")
    updated_on = row.updated_on
    if isinstance (updated_on, datetime.datetime):
      updated_on = updated_on.date ()
    database.execute (INSERT_SQL, (updated_on, row.text))

def populate_postcode_coords (source_db, target_db, log=False):
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
  INSERT_SQL = """
    INSERT INTO
      postcode_coords
    (
      id,
      outcode,
      os_x,
      os_y,
      latitude,
      longitude
    )
    VALUES
    (
      ?,
      ?,
      ?,
      ?,
      ?,
      ?
    )
  """
  UPDATE_SQL = """
    UPDATE
      postcode_coords
    SET
      area_id = (
        SELECT id
        FROM areas
        WHERE name = 'GB'
      )
  """
  print "Populate postcode coords"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.postcode_outcode.encode (sys.getdefaultencoding (), "ignore")
    database.execute (INSERT_SQL, row.asTuple ())
  database.execute (UPDATE_SQL)

def populate_hdos (source_db, target_db, log=False):
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
  INSERT_SQL = """
    INSERT INTO
      hdos
    (
      id,
      area_id,
      name,
      yyyymmdd,
      notes
    )
    SELECT
      ?,
      a.id,
      ?,
      ?,
      ?
    FROM
      areas AS a
    WHERE
      a.name = ?
  """
  print "Populate HDOs"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.Name.encode (sys.getdefaultencoding (), "ignore")
    database.execute (INSERT_SQL, (row.ID, row.Name, row.Holy_day_date.strftime ("%Y%m%d"), row.Notes, row.Area))

def populate_motorways (source_db, target_db, log=False):
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
  INSERT_SQL = """
    INSERT INTO
      motorway_churches
    (
      id,
      church_id,
      motorway,
      junction,
      distance,
      notes
    )
    VALUES
    (
      ?,
      ?,
      ?,
      ?,
      ?,
      ?
    )
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
    database.execute (INSERT_SQL, (row.ID, row.Church_ID, row.Motorway, row.Junction, distance_metres, row.Notes))

def populate_links (source_db, target_db, log=False):
  SELECT_SQL = """
    SELECT
      ID,
      [Subject Heading],
      Title,
      Link,
      [Sort Order]
    FROM
      [Useful Links]
  """
  INSERT_SQL = """
    INSERT INTO
      links
    (
      id,
      subject,
      title,
      link,
      sequence
    )
    VALUES
    (
      ?,
      ?,
      ?,
      ?,
      ?
    )
  """
  print "Populate links"
  for row in sql.fetch_query (source_db, SELECT_SQL):
    if log: print row.Title
    database.execute (INSERT_SQL, row.asTuple ())
    
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
  SELECT_SQL2 = """
    SELECT DISTINCT
      a.name
    FROM
      areas AS a
    JOIN area_day_church_masses AS adcm ON
      adcm.area_id = a.id
    WHERE
      adcm.church_id = ?
  """
  INSERT_SQL = """
    INSERT INTO
      search_scores
    (
      church_id,
      word,
      score
    )
    VALUES
    (
      ?,
      ?,
      ?
    )
  """
  print "Populate search scores"
  for row in database.select (SELECT_SQL1):
    words = {}
    words.setdefault (10, []).extend (utils.filter_search_words (row.name))
    words.setdefault (10, []).extend (utils.filter_search_words (row.alias or ""))
    words.setdefault (2, []).extend (utils.filter_search_words (row.address or ""))
    for area in database.select (SELECT_SQL2, [row.id]):
      words.setdefault (5, []).extend (utils.filter_search_words (area.name))
      
    scores = {}
    for score, wordlist in words.items ():
      for word in wordlist:
        if word in scores:
          scores[word] += score
        else:
          scores[word] = score
      
    if log: print repr (row.name), "=>", scores
    database.executemany (INSERT_SQL, [(row.id, word, score) for word, score in scores.items ()])
    #~ for word, score in scores.items ():
      #~ database.execute (INSERT_SQL, [row.id, word, score])

def get_source_db (name=SOURCE_DB_NAME):
  dsn = [
    ("Provider", "Microsoft.Jet.OLEDB.4.0"),
    ("Data Source", SOURCE_DB_NAME),
    ("User Id", "admin"),
    ("Password", "")
  ]
  return adodbapi.connect (";".join ("%s=%s" % (x, y) for (x, y) in dsn))

if __name__ == '__main__':
  target_db = database.db
  source_db = get_source_db (SOURCE_DB_NAME)

  try:
    populate_whats_new (source_db, target_db)
    populate_churches (source_db, target_db)
    populate_motorways (source_db, target_db)
    populate_areas (source_db, target_db)
    populate_church_areas (source_db, target_db)
    populate_mass_times (source_db, target_db)
    populate_postcode_coords (source_db, target_db)
    populate_hdos (source_db, target_db)
    populate_links (source_db, target_db)
    populate_area_day_church_masses ()
    populate_search_scores ()

  finally:
    target_db.commit ()
    target_db.close ()
