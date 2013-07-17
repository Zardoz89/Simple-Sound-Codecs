BTc-Sound-Codecs
================

Implementation of [Roman Black's BTc](http://www.romanblack.com/btc_alg.htm) (Binary Time constant) Sound Codecs.

Includes a tool to convert from WAV to BTc in C Array / BTL libray / BTC raw in binary and Intel HEX

Directory Structure
===================
*   ./ansi c             ANSI C implementation of decoder and encoder of BTc1.x
*   ./python             Python implementation and Python tools

How use the converter wav2btc
=============================

wav2btc.py it's in python subdir. It allows to compress a Wave sound file to BTc1.x codec and generte output file that can be a C Array, BTC binary file or a BTL BotTalk Library file. BTC and BTL can be writeen in a IntelHex file instead of a RAW binary file.

    usage: wav2btc.py [-h] [-o OUTPUT] [-c {BTc1.0,BTc1.7}] [-s SOFT]
                      [-f {c,btl,btl_ihex,btc,btc_ihex}] [-b N] [-r BR] [-p]
                      [--playorig] [--version]
                      file.wav [file.wav ...]

positional arguments:

*   file.wav              WAV filed to be procesed

optional arguments:

*   -h, --help                          Show this help message and exit
*   -o OUTPUT, --output OUTPUT          Output file. By default output to stdout
*   -c {BTc1.0,BTc1.7}                  Desired Codec. Defaults: BTc1.0
*   -s SOFT, --soft SOFT                Softness constant. How many charge/discharge Capacitor in each                         time period. Must be >2. Default: 24
*   -f {c,btl,btl_ihex,btc,btc_ihex}    Output format. c -> C Array; btl -> BotTalk Library; btl_ihex -> BotTalk Library in IHEX format; btc -> Headerless RAW binary; btc_ihex -> Headerless RAW in IHEX format; Default: c
*   -b N, --bias N                      Bias or Padding of the output file. In RAW files inserts N padding bytes before any data. In Intel HEX, it's the initial address. Default: 0
*   -r BR, --rate BR                    Desired BitRate of procesed sound. Defaults: 22000 bit/sec
*   -p                    Plays procesed file
*   --playorig            Plays original file
*   --version             show program's version number and exit

Examples : 

*   wav2btc.py robby.wav -o robby.h Generates a .H file with a C array with the data
*   wav2btc.py robby.wav r2d2.wav -o mylib.btl -f btl - r 44100 Generates a BotTalk Lib with two sounds resampled at 44,1Khz
*   wab2btc.py robby.wav -o robby.hex -f btc_ihex -p Generates a RAW BTC file and plays the compresed sound

 
