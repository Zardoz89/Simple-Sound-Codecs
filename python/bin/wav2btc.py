#!/usr/bin/env python
""" 
  Reads a WAV file and convert it to BTC 1.0 bit stream format

  BTc Sound Compression Algortithm created by Roman Black
  http://www.romanblack.com/btc_alg.htm

"""
from __future__ import division

VERSION = '0.4'


import ssc

import array
import sys
import time
import os.path
import wave
import audioop

from intelhex import IntelHex

CHUNK = 1024        # How many samples send to player

COLUMN = 8          # Prety print of values
PAD_FILL = b'\x00'  # Padding fill of 32 byte blocks


# Try to grab pyaudio
try:
    import pyaudio
    _AUDIO = True
except ImportError:
    _AUDIO = False


class SoundsLib(object):
    """ Creates a sound lib of BTc encode sounds """

    def __init__(self, bitrate =22000, soft=21, codec='BTc1.0'):
        """
        Initiate a BTc SoundLib

        Keyword Arguments:
            bitrate -- Desired bitrate (Default 22000Hz)
            soft -- Desired softness constant (Default 21)
            codec -- Desired BTc codec (Default 'BTc1.0')
        """
        
        self.__btc_codec  = codec     # Sound codec
        self.__bitrate    = bitrate   # BitRate
        self.__soft       = soft      # Desired softness constant
        self.sounds     = {}
        # Dict 'filename' : {inputwave, resultwave, bitstream, info}
        self.__snames     = []        # Sound names in insertion order

        rval, cval = ssc.calc_rc(self.__bitrate, soft) 
        self.__info = "\tUsing %s at BitRate %d\n" % (codec, bitrate)
        self.__info += "\tC = %.3f uF\tR = %.1f Ohm\n" % (cval / 10 ** -6, rval)
        if _AUDIO:
            self.paudio = pyaudio.PyAudio()

    def __del__(self):
        if _AUDIO and self.paudio:
            self.paudio.terminate()

    def add_wav_sound(self, name):
        """ Adds a WAV file to the sound library """

        if not name in self.sounds:
            if not os.path.exists(name):
                raise IOError ("File %s don't exists" % name)

            sr, samples, info = read_wav(name)

            # Resample to lib bitrate
            if sr != self.__bitrate:
                samples, state = audioop.ratecv(samples, ssc.BYTES, 1, sr, \
                                                self.__bitrate, None)

            name = name.split('.')[0]

            self.sounds[name] = {'inputwave': samples, 'resultwave': None, \
                                    'bitstream': None, 'info': info}
            self.__snames.append(name)

            return True
        else:
            return False

    
    def __delitem__(self, index):
        """ Remove a sound from the lib """
        if index in self.__snames:
            del self.sounds[index]
            self.__snames.remove(index)



    def process(self):
        """ Process all sound with the desired codec and softness """
        from math import ceil

        for name in self.sounds.keys():
            if self.sounds[name]['resultwave'] is None:
                if self.__btc_codec == 'BTc1.7':
                    tmp = ssc.lin2btc1_7 ( \
                                self.sounds[name]['inputwave'], self.__soft)
                else:
                    tmp = ssc.lin2btc1_0 ( \
                                self.sounds[name]['inputwave'], self.__soft)
                self.sounds[name]['bitstream'] = tmp
                self.sounds[name]['info'] += "\tSize: %d (bytes)\n" % \
                        ceil(len(tmp)/8.0)


    def play_original(self, name):
        """ Plays Original sound if exists """
        if _AUDIO and name in self.sounds:
            play(self.paudio, self.__bitrate, self.sounds[name]['inputwave'])


    def play_procesed(self, name):
        """ Plays Procesed sound if exists """
        if _AUDIO and name in self.sounds:

            if self.sounds[name]['resultwave'] is None:
                if self.__btc_codec == 'BTc1.7':
                    self.sounds[name]['resultwave'] = \
                    ssc.btc1_7_2lin (self.sounds[name]['bitstream'], \
                                       self.__soft)
                else:
                    self.sounds[name]['resultwave'] = \
                    ssc.btc1_0_2lin (self.sounds[name]['bitstream'], \
                                       self.__soft)

            play(self.paudio, self.__bitrate, self.sounds[name]['resultwave'])


    def write_to_file(self, filen, output_format, bias=0):
        """ Write to a file the Sound Lib using a output format function """

        try:
            # Opening file
            if filen is None: # Try to open the file
                fich = sys.stdout
            else:
                print(self.__info)

                if output_format == 'btl' or output_format == 'btc':
                    fich = open(filen, 'wb')
                else:
                    fich = open(filen, "w")

            # Writting
            if output_format == 'btl_ihex' or output_format == 'btl':
                ptr_addr = 0      # Were write Ptr to sound data end
                addr = 1024       # Were write sound data
                ih = IntelHex()
                
                for name in self.__snames:
                    if not fich is sys.stdout:
                        print(self.sounds[name]['info'])
                  
                    data = ssc.pack(self.sounds[name]['bitstream'])
                    while len(data) % 32 != 0:  #Padding to fill 32 byte blocks
                        data += PAD_FILL

                    btl_output(data, ih, addr, ptr_addr, bias)
                    ptr_addr += 4
                    addr += len(data)
                    # Fills the header with 0s
                    for n in range(ptr_addr, 1024):
                        ih[n] = 0
                
                # Binary o IntelHEX output
                if output_format == 'btl':
                    ih.tofile(fich, 'bin')
                else:
                    ih.tofile(fich, 'hex')

            elif output_format == 'btc_ihex' or output_format == 'btc':
                addr = 0          # Were write sound data
                ih = IntelHex()
            
                for name in self.__snames:
                    if not fich is sys.stdout:
                        print(self.sounds[name]['info'])
              
                    data = ssc.pack(self.sounds[name]['bitstream'])
                    while len(data) % 32 != 0: # Padding to fill 32 byte blocks
                        data += PAD_FILL

                    btc_output(data, ih, addr, bias)
                    addr += len(data)
            
                # Binary or IntelHEX output
                if output_format == 'btc':
                    ih.tofile(fich, 'bin')
                else:
                    ih.tofile(fich, 'hex')
          
            elif output_format == 'c':
                fich.write('#include <stdlib.h>\n\n')
                fich.write('/*\n' + self.__info + '/*\n\n')
                for name in self.__snames:
                    if not fich is sys.stdout:
                        print(self.sounds[name]['info'])
                    
                    data = ssc.pack(self.sounds[name]['bitstream'])
                    c_array_print(data, fich, self.sounds[name]['info'], name)


        finally:
            if fich != sys.stdout:
                fich.close()


def read_wav(filename):
    """ Reads a wave file and return sample rate and mono audio data """
    from math import floor

    # Make header info
    sys.stderr.write('Openining : ' + filename + '\n\n')
    wf = wave.open(filename, 'rb')

    info = "\tWAV file: " + filename + "\n"
    channels = wf.getnchannels()
    info += "\tOriginal Channels: " + str(channels)
    bits = wf.getsampwidth()
    info += "\tOriginal Bits: " + str(bits*8) + "\n"
    sr = wf.getframerate()
    total_samples = wf.getnframes()
    seconds = float(total_samples)/sr
    ms_seconds = (seconds - floor(seconds)) * 1000
    info += "\tOriginal Size: " + str(total_samples*wf.getsampwidth())
    info += " Bytes ( %d" % floor(seconds)
    info += ":%05.1f" % ms_seconds
    info += ") seconds \n"
    info += "\tSample Rate: " + str(sr) + "\n"


    samples = wf.readframes(total_samples)
    wf.close()
    if bits != ssc.BYTES: # It isn't 16 bits, convert to 16
        samples = audioop.lin2lin(samples, bits, ssc.BYTES)
    if bits == 1 and min(samples) >= 0: # It's unsigned 8 bits
        samples = audioop.bias(samples, 2, ssc.MIN ) 

    if channels > 1:
        samples = audioop.tomono(samples, ssc.BYTES, 0.75, 0.25)

    # Normalize at 50%
    maxsample = audioop.max(samples, ssc.BYTES)
    samples = audioop.mul(samples, ssc.BYTES, ssc.MAX * 0.5 / float(maxsample))

    return sr, samples, info


def play(audio, sr, samples):
    """Plays an audio data

    Keywords arguments:
    audio -- PyAduio Object
    sr -- Sample Rate
    samples -- Audio data in a string byte array (array.trostring())

    """
    stream = audio.open(format=audio.get_format_from_width(ssc.BYTES), \
                channels=1, rate=sr, output=True)

    data = samples[:CHUNK]
    i = 0
    while i < len(samples):
        stream.write(data)
        i += CHUNK
        data = samples[i:min(i+CHUNK, len(samples))]

    time.sleep(0.5) # delay half second

    stream.stop_stream()
    stream.close()


def c_array_print(bytedata, f, head, name, ):
    """ Prints a Byte Array in a pretty C array format. 
    
    Keywords arguments:
    bytedata -- Stream of bytes to write
    f -- File were to write
    head -- Pretty comment text for the bytedata array
    name -- Name of the bytedata array

    """
    if head:
        f.write("/*\n" + head + "*/\n\n")
    
    data = array.array('B')
    data.fromstring(bytedata)

    data_str = [("0x%02X" % byte) for byte in data]
    # map(lambda x: "0x%02X" % x, data)
    
    f.write('size_t ' +name + "_len = " + str(len(data)) + "; /* Num. of Bytes */\n")

    # Print Bytedata
    f.write('unsigned char ' +  name + "_data  = {\n")
    
    blq = data_str[:COLUMN]
    i = 0
    while i < len(data_str): 
        f.write(', '.join(blq) + ',\n')
        i += COLUMN
        if i % 32 == 0:
            f.write('/*---------------- %8d ----------------*/\n' % i)

        blq = data_str[i:min(i + COLUMN, len(data_str))]

    f.write("}; \n")


def btl_output(bytedata, ih, addr, ptr_addr, bias=0):
    """ Write BTL Lib to a IHEX datastructure. 

    Keywords arguments:
    bytedata -- Stream of bytes to write
    ih -- IntelHex Object wre to write
    addr -- Address were store the bytedata
    ptr_addr -- Address were store the pointer to the end of the data
    biar -- Offset of addresses were write all

    """
    data = array.array('B')
    data.fromstring(bytedata)
    
    ptr = len(data) + addr - 1024 # Relative to the end of header
    ptr = ptr // 32   # Points to 32 bytes block, not real address

    ptr_addr += bias
    # Writes the pointer in the header
    ih[ptr_addr] = 0 # (ptr >> 24)
    ptr = ptr & 0x00FFFFFF

    ptr_addr += 1
    ih[ptr_addr] = ptr >> 16
    ptr = ptr & 0x0000FFFF

    ptr_addr += 1
    ih[ptr_addr] = ptr >> 8
    ptr = ptr & 0x000000FF

    ptr_addr += 1
    ih[ptr_addr] = ptr

    # Writes Data
    addr += bias
    for byte in data:
        ih[addr] = byte
        addr += 1

def btc_output(bytedata, ih, addr, bias=0):
    """ Write BTC RAW to a IHEX datastructure. 

    Keywords arguments:
    bytedata -- Stream of bytes to write
    ih -- IntelHex Object wre to write
    addr -- Address were store the bytedata
    ptr_addr -- Address were store the pointer to the end of the data
    biar -- Offset of addresses were write all

    """ 
    data = array.array('B')
    data.fromstring(bytedata)
    
    # Writes Data
    addr += bias
    for byte in data:
        ih[addr] = byte
        addr += 1


# MAIN !
if __name__ == '__main__':
    import argparse

    # Args parsing
    parser = argparse.ArgumentParser(description="Reads a WAV file, play it " +\
                "and play BTc1 conversion. Finally return C array BTC enconde"+\
                " data")

    parser.add_argument('infile', type=str, nargs='+', \
      metavar='file.wav', help='WAV file to be procesed')

    parser.add_argument('-o', '--output', type=str, \
      help="Output file. By default output to stdout")

    parser.add_argument('-c', choices=['BTc1.0', 'BTc1.7'], \
      default='BTc1.0', help='Desired Codec. Defaults: %(default)s')

    parser.add_argument('-s', '--soft', type=int, default=21 , help='Softness'+\
                ' constant. How many charge/discharge C in each time period.' +\
                ' Must be >2. Default: %(default)s ')

    parser.add_argument('-f', \
                choices=['c', 'btl', 'btl_ihex', 'btc', 'btc_ihex'], \
                default='c', \
                help='Output format. c -> C Array; ' + \
                        'btl -> BotTalk Library; ' + \
                        'btl_ihex -> BotTalk Library in IHEX format; '\
                        'btc -> Headerless RAW binary; ' + \
                        'btc_ihex -> Headerless RAW in IHEX format; '\
                        ' Default: %(default)s')

    parser.add_argument('-b', '--bias', metavar='N', type=int, default=0, \
      help='Bias or Padding of the output file. In RAW files' \
      " inserts N padding bytes before. In Intel HEX, it's the initial '\
      'address. Default: %(default)s ")

    parser.add_argument('-r', '--rate', metavar='BR', type=int, default=22000, \
      help='Desired BitRate of procesed sound. Defaults: %(default)s bit/sec')

    if _AUDIO:
        parser.add_argument('-p', action='store_true', default=False, \
                            help='Plays procesed file')
        parser.add_argument('--playorig', action='store_true', default=False, \
                            help='Plays original file')
    parser.add_argument('--version', action='version', \
                        version="%(prog)s version "+ VERSION)

    args = parser.parse_args()

    # Check input values
    if args.soft < 2:
        print("Invalid value of softness constant. Must be > 2.")
        sys.exit(0)

    if args.bias < 0:
        print("Invalid value of bias/padding. Must be a positive value.")
        sys.exit(0)

    if args.rate < 1000:
        print("Invalid BitRate. Must be >= 1000.")
        sys.exit(0)

    for fname in args.infile:
        if not os.path.exists(fname):
            print("The input file %s don't exists." % fname)
            sys.exit(0)

    sl = SoundsLib(args.rate, args.soft, args.c)
    for fi in args.infile:
        sl.add_wav_sound(fi)

    if _AUDIO and args.playorig:
        for k in sl.sounds.keys():
            print("Playing Original Sound: " + k)
            sl.play_original(k)

    # Process all sounds in the lib
    sl.process()

    # Play procesed sounds
    if _AUDIO and args.p:
        for k in sl.sounds.keys():
            print("Playing Procesed Sound: " + k)
            sl.play_procesed(k)

    # Write to output
    sl.write_to_file(args.output, args.f)
      

