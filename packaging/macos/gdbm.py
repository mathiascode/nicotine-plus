from distutils.core import setup, Extension

module1 = Extension('_gdbm',
                    sources=['_gdbmmodule.c'],
                    library_dirs=['/usr/local/Cellar/gdbm/1.19/lib'],
                    libraries=['gdbm'])

setup(name='gdbm_extension',
      version='1.0',
      description='gdbmmodule.c from Python 3 packaged for macOS',
      ext_modules=[module1])
