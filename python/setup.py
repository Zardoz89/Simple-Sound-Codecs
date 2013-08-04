#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import Command, setup

import re
import sys

VERSIONFILE="ssc/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


METADATA = dict(
    name='ssc',
    description='Simple Sound Codecs like Delta Modulation, ADM, etc',
    license='BSD',
    keywords='sound codec DM ADM BTC',
    version=verstr,
    long_description=open('README').read(),

    author='Luis Panadero Guardeño',
    author_email='luis.panadero@gmail.com',
    url='https://github.com/Zardoz89/BTc-Sound-Codecs.git',

    packages=['ssc'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Classifier: License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Embedded Systems',
    ],
)

# test and 2to3 take from intelhex setup.py

class test(Command):
    description = "unittest for ssc"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import unittest
        import ssc.test
        verbosity = 1
        if self.verbose:
            verbosity = 2
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        suite.addTest(loader.loadTestsFromModule(ssc.test))
        runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity)
        result = runner.run(suite)
        if result.errors or result.failures:
            return 1


def main():
    metadata = METADATA.copy()
    metadata['cmdclass'] = {
        'test': test,
        }
    if sys.version_info[0] >= 3:
        from distutils.command.build_py import build_py_2to3
        metadata['cmdclass']['build_py'] = build_py_2to3
        from distutils.command.build_scripts import build_scripts_2to3
        metadata['cmdclass']['build_scripts'] = build_scripts_2to3

    setup(**metadata)


if __name__ == '__main__':
    main()

