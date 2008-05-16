.. highlight:: python
   :linenothreshold: 5

=====================
Write to the Registry
=====================

---------------
The requirement
---------------

To write keys and values into the registry, including the default value
for a key.

------------
Introduction
------------

The registry is organised into keys, subkeys and their values. A key
can have one default value (one without a name), any number of named
values, and any number of subkeys. Each subkey can itself have subkeys
and values. And so ad infinitum.

The type of each value must be specified from the list of those understood
by the registry. In practice most values will be strings (REG_SZ) or integers
(REG_DWORD). There are other possiblities, but anything else can always be
stuffed into a Blob and registered as binary (REG_BINARY).

The code below uses CreateKey to ensure the key you're requesting
exists. If you're not specifying a value then that's all you get: just
the key. If you specify a named value, this is created: an empty string
for the name gives you a default value. The code applies simple heuristics
to infer the registry type of the value, but you can always override it
and sometimes you'll have to.

--------
The code
--------

.. literalinclude:: write_the_registry.py

-----
Notes
-----

* Rather than mess with the _winreg hive constants, you specify the
  hive (HKEY_LOCAL_MACHINE etc.) as the first part of the registry path
  string.

* CreateKey will in fact return a key you can use, but you can't
  specify the access mode, so you won't be able to write back to
  it later. OpenKey allows you to specify access, but won't create the
  key if it's not there. Hence the two-handed approach.
  
* As a best-guess, if the value is a string REG_SZ is used; if it's an
  integer REG_DWORD is used. Otherwise, "refuse the temptation to guess".

* The only way to get a non-integer number into the registry is to
  store its representation as a binary type. The struct module's pack
  function generate the right bytes for a floating-point numnber. Or
  you can use Python's pickle to serialize arbitrary objects.