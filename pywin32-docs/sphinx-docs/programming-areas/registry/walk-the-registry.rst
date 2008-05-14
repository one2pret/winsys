.. highlight:: python
   :linenothreshold: 5

=================
Walk the Registry
=================

**The requirement:** to walk down the registry in the style of the
os.walk function, yielding the current location, keys and values.

**The code**::

  import _winreg

  class RegKey:

    def __init__ (self, name, key):
      self.name = name
      self.key = key

    def __str__ (self):
      return self.name

  def walk (top, topdown=True):
    """walk the registry starting from the key represented by
    top in the form HIVE\\key\\subkey\\..\\subkey and generating
    key, subkey_names, values at each level.

    key is a lightly wrapped registry key, including the name
    and the HKEY object.
    subkey_names are simply names of the subkeys of that key
    values are 3-tuples containing (name, data, data-type).
    See the documentation for _winreg.EnumValue for more details.
    """
    if "\\" not in top: top += "\\"
    root, subkey = top.split ("\\", 1)
    key = _winreg.OpenKey (getattr (_winreg, root), subkey, 0, _winreg.KEY_READ)

    subkeys = []
    i = 0
    while True:
      try:
        subkeys.append (_winreg.EnumKey (key, i))
        i += 1
      except EnvironmentError:
        break

    values = []
    i = 0
    while True:
      try:
        values.append (_winreg.EnumValue (key, i))
        i += 1
      except EnvironmentError:
        break

    if topdown:
      yield RegKey (top, key), subkeys, values

    for subkey in subkeys:
      for result in walk (top.rstrip ("\\") + "\\" + subkey):
        yield result

    if not topdown:
      yield RegKey (top, key), subkeys, values

  if __name__ == '__main__':
    for key, subkey_names, values in walk (r"HKEY_CURRENT_USER\Console"):
      level = key.name.count ("\\")
      print " " * level, key
      for name, data, datatype in values:
        print " ", " " * level, name, "=>", data
      print
