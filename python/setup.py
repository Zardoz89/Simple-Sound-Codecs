# -*- coding: utf-8 -*-
from distutils.core import setup
import re
VERSIONFILE="ssc/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
    name='ssc',
    description='Simple Sound Codecs like Delta Modulation, ADM, etc',
    license='BSD',
    keywords='sound codec DM ADM BTC',
    version=verstr,
    long_description=open('README.rst').read(),

    author='Luis Panadero Guardeño',
    author_email='luis.panadero@gmail.com',
    url='https://github.com/Zardoz89/BTc-Sound-Codecs.git',

    packages=['ssc'],
    scripts=['bin/wav2ssc.py'],
    install_requires=[
        "intelhex >= 1.4",
    ],
)
