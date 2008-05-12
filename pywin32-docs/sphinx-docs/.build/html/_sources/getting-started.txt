===============
Getting Started
===============

---------------------------
What do I need to download?
---------------------------

~~~~~~
Python
~~~~~~

Strictly speaking, the only thing you *need* to download is Python itself
(and that's assuming it's not already instaled on your machine). You have
a few choices here:

* python.org - this is the simplest option and unless you have reason to
  do otherwise, go for this. The python.org site has hosted .msi or .exe
  files containing everything you'll need to get up and running with Python
  for some years now. The package includes core Python, the standard library
  and the core documentation set.
* ActiveState - this bundle of Python, usually lagging a little behind the
  official release from python.org, contains everything that the python.org
  bundle contains, plus the pywin32 extensions (see below), the documentation
  for both plus additional documentation, all tied together in a neat .chm.
* svn.python.org - if you want the bleeding edge release, or someone's branch,
  you can checkout the latest sources from Python's subversion repository.
  As of May 2008, the Subversion sources contain everything you need to build
  Python from scratch using Visual Studio 2008, including the free [beer] Express
  Edition.
    
~~~~~~~
pywin32
~~~~~~~

For years, Mark Hammond and others have contributed this huge bundle of
wrapped API modules to the Python community, and they continue to refine,
add and bring up to date as Microsoft's APIs change and grow. At the time
of writing, they are still using SourceForge's CVS repositories rather
than Subversion but binary releases are always available from the project's
SourceForge files page.

While the range of APIs and objects it exposes is extensive, the range
of APIs and objects dreamt up by Microsoft's engineers is even more
extensive. You won't find everything here and you may have to use
ctypes / comtypes to interface with Windows.

~~~~~~~~
comtypes
~~~~~~~~

This extension package developed and maintained by Thomas Heller uses his ctypes package,
now part of the Python standard library, to allow arbitrary COM objects and interfaces
to be implemented. It therefore gives greater flexibility than the pywin32 objects do,
since you're not limited by what another developer has already done, but you have to
do for yourself a lot of plumbing which would otherwise be done for you.

-----------------
Now what do I do?
-----------------

Assuming you're looking at the most recent binary downloads of each of the
packages above, you'll need to run the .msi or .exe in order to install
them. Unless you have reason to do otherwise, accept the standard locations
for each one. One reason you *might* have to do otherwise is that Python
by default installs in a c:\pythonxx (where xx is the version) and subdirectories
of the root of the c:\ drive have restricted security. However, there are
also problems installing to the conventional "Program Files" directory
because of its embedded space. You'll have to work something out.

------------------------
And how do I use Python?
------------------------

At this point, we defer to the recently-added section in the Python docs:
Using Python on Windows. This guides you through several of the issues
involved in running Python programs on Windows, including setting up
the environment and the different ways to run scripts.