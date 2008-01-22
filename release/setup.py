import sys
from distutils.core import setup
import py2exe

sys.argv.append ("py2exe")
setup (
  console=[
    dict (script="install.py"),
  ],
  windows=[
    dict (script="release.pyw"),
  ],
  data_files=[
    (".", ["scripter.exe"]),
  ],
  options={
    "py2exe" : {
      "includes" : ["decimal"]
    }
  }
)