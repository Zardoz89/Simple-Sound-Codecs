===================
Simple Sound Codecs
===================

Introduction
-------------
Implementation of some simple and low CPU usage sound codecs like Delta Modulation, Adaptative Delta 
Modulation, Binary Time constant, etc

For more information about BTc codec, read more about it in original author page (Roman Black): 
http://www.romanblack.com/btc_alg.htm


License
-------
The code distributed under BSD license. See LICENSE.txt in sources archive.
Download
--------
https://github.com/Zardoz89/BTc-Sound-Codecs.git

Install
-------
python setup.py install

Documentation
-------------

Sub packages
~~~~~~~~~~~~

ssc.dm
=======
Contains **lin2btc** and **btc2lin** to convert from/to mono audio fragments (same bytestrings that uses audioop) to/from a stream of bits (a list of booleans) with **Delta Modulation audio codec**.

ssc.btc
=======
Contains **lin2btc** and **btc2lin** to convert from/to mono audio fragments (same bytestrings that uses audioop) to/from a stream of bits (a list of booleans) with **BTc audio codec**.

ssc.aux
=======
Contains **pack** and **unpack** functions to pack/unpack a bitstream in a bytestream with choosable bit-endiannes.

See pydoc ssc.btc, ssc.dm and ssc.aux for more detail


