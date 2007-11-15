from distutils.core import setup
from Pyrex.Distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(
  name = 'PyDump',
  ext_modules=[
    Extension (
      "pydump", ["pydump.pyx"],
      include_dirs = [r"c:\msys\1.0\local\include"],
      library_dirs = [r"c:\msys\1.0\local\lib"],
      libraries = [r"avformat", r"avcodec", r"avutil", r"wsock32"]
    ),
  ],
  cmdclass = {'build_ext': build_ext}
)
