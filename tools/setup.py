#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import re

setup(
    name='ssc-tools',
    description='Tools to convert sounds using Simple Sound Codecs lib',
    license='BSD',
    keywords='sound codec DM ADM BTC',
    version='0.0.1',
    long_description=open('README.rst').read(),

    author='Luis Panadero Guardeño',
    author_email='luis.panadero@gmail.com',
    url='https://github.com/Zardoz89/BTc-Sound-Codecs.git',

    scripts=['bin/wav2ssc.py'],
    install_requires=[
        "intelhex >= 1.4",
        "ssc >= 0.0.1",
    ],
)
