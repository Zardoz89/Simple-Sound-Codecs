Simple Sound Codecs lib and tools
=================================
Implementation of some simple audio codecs like Delta Modulation, etc

List of actual audio codecs:
*   Delta Modulation (DM)
*   Binary Time constant (BTc) [Roman Black's BTc](http://www.romanblack.com/btc_alg.htm)

Python implementation includes scripts to convert WAV to RAW and basic sound lib formats with implementated sound codecs

Directory Structure
===================
*   ./ansi c             ANSI C implementation of decoder and encoder of BTc1.x
*   ./python             Python package and tool scripts

How use the converter wav2ssc
=============================

wav2ssc.py it's in python subdir. It allows to compress a Wave sound file to BTc1.x codec and generte output file that can be a C Array, BTC binary file or a BTL BotTalk Library file. BTC and BTL can be writeen in a IntelHex file instead of a RAW binary file.

    usage: wav2ssc.py [-h] [-o OUTPUT] [-c {BTc1.0,BTc1.7}] [-s SOFT]
                      [-f {c,btl,btl_ihex,btc,btc_ihex}] [-b N] [-r BR] [-p]
                      [--playorig] [--version]
                      file.wav [file.wav ...]

positional arguments:

*   file.wav              WAV filed to be procesed

optional arguments:

*   -h, --help                          Show this help message and exit
*   -o OUTPUT, --output OUTPUT          Output file. By default output to stdout
*   -c {DM,BTc1.0,BTc1.7}               Desired Codec. Defaults: BTc1.0
*   -s SOFT, --soft SOFT                Softness constant. How many charge/discharge Capacitor in each time period. Only is meangniful with BTc codecs. Must be >2. Default: 24
*   -d DELTA, --delta DELTA             Delta constant. Only is meangniful with DM codec. Must be > 0. Default: 1560
*   -f {c,lib,lib_ihex,raw,raw_ihex}    Output format. c -> C Array; lib -> BotTalk Library; lib_ihex -> BotTalk Library in IHEX format; raw -> Headerless RAW binary; raw_ihex -> Headerless RAW in IHEX format; Default: c
*   -b N, --bias N                      Bias or Padding of the output file. In RAW files inserts N padding bytes before any data. In Intel HEX, it's the initial address. Default: 0
*   -r BR, --rate BR                    Desired BitRate of procesed sound. Defaults: 22000 bit/sec
*   -p                    Plays procesed file
*   --playorig            Plays original file
*   --version             show program's version number and exit

Examples : 

*   wav2ssc.py robby.wav -o robby.h Generates a .H file with a C array with the data
*   wav2ssc.py robby.wav r2d2.wav -o mylib.btl -f lib - r 44100 Generates a BotTalk Lib with two sounds resampled at 44,1Khz
*   wab2ssc.py robby.wav -o robby.hex -c DM -f raw_ihex -p Generates a RAW DM file and plays the compresed sound

 
