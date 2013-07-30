from distutils.core import setup

setup(
    name='ssc',
    description='Simple Sound Codecs like Delta Modulation, ADM, etc',
    license='BSD',
    keywords='sound codec DM ADM BTC'
    version='0.0.1',
    long_description=open('README.txt').read(),

    author='Luis Panadero guardeño',
    author_email='luis.panadero@gmail.com',
    url='https://github.com/Zardoz89/BTc-Sound-Codecs.git',

    packages=['ssc'],
    scripts=['bin/wav2btc.py'],
    install_requires=[
        "intelhex >= 1.4",
    ],
)
