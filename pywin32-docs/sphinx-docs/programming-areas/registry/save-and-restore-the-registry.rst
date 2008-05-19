.. highlight:: python
   :linenothreshold: 5

=============================
Save and restore the Registry
=============================

---------------
The requirement
---------------

To save a portion of the registry to disk to be restored later.

------------
Introduction
------------

Within regedit there is a useful option called Export which saves
a tree within the registry as a text file which can be restored 
later by passing it as a parameter to regedit.exe. (Which effect
can be achieved by double-clicking on it usually). Sadly this
particular form of serialisation does not seem to be available
programatically. Instead, the functions RegSaveKey and RegLoadKey
use a binary format. These are exposed in _winreg as SaveKey and
RestoreKey respectively.

Note that a tree saved to disk can be restored to a different place
in the registry. This can also be achieved by calling SHCopyKey.

------
Saving
------

.. literalinclude:: save_the_registry.py

-----
Notes
-----

* The documentation for RegSaveKey specifies that the calling
  process must have enabled the SE_BACKUP_NAME privilege enabled.

  
---------
Restoring
---------

.. literalinclude:: restore_the_registry.py

-----
Notes
-----

* The documentation for RegRestoreKey specifies that the calling
  process must have enabled the SE_RESTORE_NAME and SE_BACKUP_NAME 
  privileges enabled.


-------
Copying
-------

.. literalinclude:: copy_the_registry.py

----------
References
----------

.. seealso::

   `_winreg <http://docs.python.org/lib/module--winreg.html>`_
     The _winreg module at python.org
   `RegSaveKey <http://msdn.microsoft.com/en-us/library/ms724917(VS.85).aspx>`_
     The RegSaveKey function at microsoft.com
   `RegRestoreKey <http://msdn.microsoft.com/en-us/library/ms724915(VS.85).aspx>`_
     The RegRestoreKey function at microsoft.com
   `SHCopyKey <http://msdn.microsoft.com/en-us/library/bb773482(VS.85).aspx>`_
     The SHCopyKey function at microsoft.com
