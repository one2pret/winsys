def preferred_languages (http_accept_language):
  lang_prefs = [i.strip () for i in http_accept_language.split (",")]

  languages = []
  for i, lang_pref in enumerate (lang_prefs):
    lang, pref = (lang_pref + ";").split (";")[:2]
    q, val = (pref + "=").split ("=")[:2]
    languages.append ((float (val or 1.0), -i, lang))

  languages.sort ()
  languages.reverse ()
  return [l[-1] for l in languages]

def formatted_date (date):
  """Return the date in the form: Sunday 16th December 2001
  """
  day = date.day
  if day in (1, 21, 31):
    suffix = u"st"
  elif day in (2, 22):
    suffix = u"nd"
  elif day in (3, 23):
    suffix = u"rd"
  else:
    suffix = u"th"

  return u"%s %d%s %s" % (date.strftime ("%A"), date.day, suffix, date.strftime ("%B %Y"))

def hh24_to_hh12 (hh24, eve=None):
  hrs = int (hh24[:2])
  mins = int (hh24[2:])

  if hrs < 12:
    suffix = u"am"
  elif hrs == 12 and mins == 0:
    suffix = u" noon"
    mins = None
  else:
    if hrs > 12:
      hrs -= 12
    suffix = u"pm"

  if mins is None:
    hh12 = u"%d%s" % (hrs, suffix)
  else:
    hh12 = u"%d.%02d%s" % (hrs, mins, suffix)
  if eve:
    return hh12 + u" (eve)"
  else:
    return hh12
