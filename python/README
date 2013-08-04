===================
Simple Sound Codecs
===================

Introducction
-------------
Implementation of some simple and low CPU usage sound codecs like Delta Modulation, Adaptative Delta 
Modulation, Binary Time constant, etc

For more information about BTc codec, read more about it in original author page (Roman Black): 
http://www.romanblack.com/btc_alg.htm

The distribution package includes scripts for converting wav files to any implementated codec in 
binary, intel hex or .H header files, plus includes a tool for playing it from binary files

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

How use the converter wav2ssc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wav2ssc.py it's in python subdir. It allows to compress a Wave sound file to BTc1.x codec and 
generate output file that can be a C Array, BTC binary file or a BTL BotTalk Library file. BTC and
BTL can be writeen in a IntelHex file instead of a RAW binary file.

Usage::
    
    wav2ssc.py [-h] [-o OUTPUT] [-c {BTc1.0,BTc1.7}] [-s SOFT]
                      [-f {c,btl,btl_ihex,btc,btc_ihex}] [-b N] [-r BR] [-p]
                      [--playorig] [--version]
                      file.wav [file.wav ...]

Positional arguments:

file.wav                    WAV filed to be procesed

Optional arguments:

-h, --help                  Show this help message and exit
-o OUTPUT, --output OUTPUT  Output file. By default output to stdout
-c {DM,BTc1.0,BTc1.7}  Desired Codec. Defaults: BTc1.0
-s SOFT, --soft SOFT  Softness constant. How many charge/discharge C in each
                      time period. Only is meangniful with BTc codecs. Must
                      be >2. Default: 21
-d DELTA, --delta DELTA  Delta constant. Only is meangniful with DM codec. Must be > 0. Default: 1560                        
-f {c,lib,lib_ihex,raw,raw_ihex}  Output format. c -> C Array; lib -> BotTalk Library;
                                  lib_ihex -> BotTalk Library in IHEX format; 
                                  raw -> headerless RAW binary; 
                                  raw_ihex -> Headerless RAW in IHEX format; Default: c                              
-b N, --bias N              Bias or Padding of the output file. In RAW files inserts N padding bytes
                            before any data. In Intel HEX, it's the initial address. Default: 0
-r BR, --rate BR            Desired BitRate of procesed sound. Defaults: 22000 bit/sec
-p                          Plays procesed file
--playorig                  Plays original file
--version                   Show program's version number and exit

Examples : 

*   wav2ssc.py robby.wav -o robby.h  Generates a .H file with a C array with the data
*   wav2ssc.py robby.wav r2d2.wav -o mylib.btl -f btl - r 44100  Generates a BotTalk Lib with two sounds resampled at 44,1Khz
*   wab2ssc.py robby.wav -o robby.hex -f btc_ihex -p -c DM  Generates a RAW DM file and plays the compresed sound


