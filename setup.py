from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy

extensions = [
    Extension("c_heuristics", ["c_heuristics.pyx"], include_dirs=[numpy.get_include()])
]

setup(
    cmdclass = {'build_ext':build_ext},
    ext_modules = cythonize(extensions),
)
