from distutils.core import setup, Extension

setup (
  name="extension",
  version="0.a",
  ext_modules=[
    #~ Extension ("extension", ["extension.c"], libraries=['Advapi32']),
    Extension ("extension2", ["extension2.c"], libraries=['Advapi32']),
  ]
)
