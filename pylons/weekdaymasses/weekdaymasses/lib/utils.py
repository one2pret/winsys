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
