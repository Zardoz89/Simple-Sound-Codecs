#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
  Reads a WAV file and convert it to BTC 1.0 bit stream format

  BTc Sound Compression Algortithm created by Roman Black
  http://www.romanblack.com/btc_alg.htm

"""

from __future__ import division

VERSION = '0.2'

CHUNK = 1024        # How many samples send to player
BYTES = 2           # N bytes arthimetic
MAX = 2**(BYTES*8 -1) -1
MIN = -(2**(BYTES*8 -1)) +1   

COLUMN = 8          # Prety print of values


import sys
import time
import os.path
import array
from math import log, exp, floor, ceil
import wave
import audioop

# No stdlib modules
import pyaudio
from intelhex import IntelHex


class SoundsLib(object):
  """ Creates a sound lib of BTc codec sounds """

  def __init__(self, bitrate =22000, soft=24, codec='BTc1.0'):
    self.btc_codec  = codec     # Sound codec
    self.bitrate    = bitrate   # BitRate
    self.soft       = soft      # Desired softness constant
    self.sounds     = {}  # Dict 'filename' : {inputwave, resultwave, bitstream, info}

    self.r, self.c , self.info = CalcRC(self.bitrate, soft) 
    self.info += "\tUsing %s\n" % codec
  
  def AddWAVSound(self, name):
    """ Adds a WAV file to the sound library """
    
    if not name in self.sounds:
      if not os.path.exists(name):
        raise IOError ("File %s don't exists" % name)

      sr, samples, info = ReadWAV(name)

      # Resample to lib bitrate
      if sr != self.bitrate:
        samples, state = audioop.ratecv(samples, BYTES, 1, sr, self.bitrate, None)

      name = name.split('.')[0]

      self.sounds[name] = {'inputwave': samples, 'resultwave': None, \
                                'bitstream': None, 'info': info}

      return True
    else:
      return False


  def DelSound(self, name):
    del self.sounds[name]


  def Process(self):
    """ Process all sound with the desired codec and softness """
    for name in self.sounds.keys():
      if self.sounds[name]['resultwave'] is None: 
        tmp, info = PredictiveBTC1_0 ( self.sounds[name]['inputwave'], self.soft)
        self.sounds[name]['bitstream'] = tmp
        self.sounds[name]['info'] += info


  def PlayOriginal (self, name):
    """ Plays Original sound if exists """
    if name in self.sounds:
      p = pyaudio.PyAudio() # Initiate audio system
      Play(p, self.bitrate, self.sounds[name]['inputwave'])
      p.terminate()
 
  
  def PlayProcesed (self, name):
    """ Plays Procesed sound if exists """
    if name in self.sounds:
      p = pyaudio.PyAudio() # Initiate audio system

      if self.sounds[name]['resultwave'] is None:
         self.sounds[name]['resultwave'] = \
             DecodeBTC1_0 (self.sounds[name]['bitstream'] , self.bitrate , self.r, self.c)

      Play(p, self.bitrate, self.sounds[name]['resultwave'])
      p.terminate()

  
  def WriteToFile (self, filename, outputFormat, bias=0):
    """ Write to a file the Sound Lib using a output format function """
    # Ugly code here!

    f = None
    try:
      # Opening file
      if filename is None: # Try to open the file
        f = sys.stdout
      else:
        print(self.info)

        if outputFormat == 'btl' or outputFormat == 'raw':
          f = open(filename, 'wb')
        else:
          f = open(filename, 'w')

      # Writting
      if outputFormat == 'btl_ihex' or outputFormat == 'btl':
        ptr_addr = 0        # Were write Ptr to sound data end
        addr = 1024         # Were write sound data
        ih = IntelHex()
        
        for name in self.sounds.keys():
          data = BStoByteArray(self.sounds[name]['bitstream'])
          IHEXoutput(data, ih, addr, ptr_addr, bias)
          if not f is sys.stdout:
            print(self.sounds[name]['info'])
          ptr_addr += 4
          addr += len(data)
        
        #ih.write_hex_file(f)
        if outputFormat == 'btl': # Binary
          ih.tofile(f, 'bin')
        else:                     # IntelHex
          ih.tofile(f, 'hex')
      
      elif outputFormat == 'c':
        for name in self.sounds.keys():
          if not f is sys.stdout:
            print(self.sounds[name]['info'])
          data = BStoByteArray(self.sounds[name]['bitstream'])
          CArrayPrint(data, f, self.sounds[name]['info'], name);


    finally:
      if f != sys.stdout:
        f.close()


def ReadWAV (filename):
  """ Reads a wave file and return sample rate and mono audio data """

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
  if bits != BYTES: # It isn't 16 bits, convert to 16
    samples = audioop.lin2lin(samples, bits, BYTES)
    if bits == 1: # It's 8 bits
      samples = audioop.bias(samples, 2, -(2**(BITS*8-1)) ) # Correct from unsigned 8 bit

  if channels > 1:
    samples = audioop.tomono(samples, BYTES, 0.75, 0.25)

  # Normalize at 50%
  max = audioop.max(samples, BYTES)
  samples = audioop.mul(samples, BYTES, MAX*0.5/float(max))

  return sr, samples, info


def Play(audio, sr, samples):
  """Plays an audio data

  Keywords arguments:
  audio -- PyAduio Object
  sr -- Sample Rate
  samples -- Audio data in a string byte array (array.trostring())

  """
  stream = audio.open(format=audio.get_format_from_width(BYTES), \
    channels=1, \
    rate=sr, \
    output=True)

  data = samples[:CHUNK]
  i=0
  while i < len(samples):
    stream.write(data)
    i += CHUNK
    data = samples[i:min(i+CHUNK, len(samples))]

  time.sleep(0.5) # delay half second

  stream.stop_stream()
  stream.close()


def PredictiveBTC1_0 ( samples, soft):
  """Encode audio data with BTc 1.0 audio codec. Returns a BitStream in a list

  Keywords arguments:
  samples -- Audio data in a string byte array (array.trostring())
  sr -- Sample Rate (and output BitRate)
  soft -- BTc softnes constant or how the capactiro charge/discharge in each T unit

  """

  raw = array.array('h')
  raw.fromstring(samples)
  
  stream = []
  lastbtc = 0

  for sample in raw:
    
    # Generate a high (1) outcome
    dist = (MAX - lastbtc) / soft            # Calc total distance to charge
    # BTC only charge to 1/soft distance
    highbtc = lastbtc + dist

    # Generate a low (0) outcome
    dist = (lastbtc - MIN) / soft            # Calc total distance to discharge
    # BTC only discharge to 1/soft distance
    lowbtc = lastbtc - dist

    # Calc distance from the high outcome to new sample
    disthigh = abs(highbtc - sample)
    # Calc distance from the low outcome to new sample
    distlow = abs(lowbtc - sample)
  
    # See wath outcome it's closest to the new sample and generate bit
    if disthigh >= distlow:
      stream.append(0)
      lastbtc = lowbtc
    else:
      stream.append(1)
      lastbtc = highbtc

  info =  "\tSize: %d (bytes)\n" % ceil(len(stream)/8.0) 

  return stream, info


def DecodeBTC1_0 (stream, br, r, c):
  """Decode a BitStream in a list to a string byte array (array.tostring)

  Keywords arguments:
  stream -- List with the BitStrem
  br -- BitRate (and output SampleRate)
  r -- Resistor value
  c -- Capacitor value

  """

  audio = array.array('h')
  last = 0.5
  tau = r*c
  deltaT = 1.0/br

  for bit in stream:
    if bit >= 1:  #Charge!
      last = ( 1 + (last -1) * (exp(-deltaT/tau)))
    else:         #Discharge!
      last = ( last * (exp(-deltaT/tau)))
    
    audio.append(int((last-0.5) * 2 * MAX) )

  return audio.tostring()


def CalcRC (br, soft, c=0.22*(10**-6)):
  """Calculate R and C values from a softnes constant and desired BitRate. """

  r = -1.0 / (log(-1.0/soft +1)*br*c)
  
  info =  "\tR= %d Ohms\tC = %.3f uF\n" % (r, c/(10**-6))
  info += "\tBitRate %(br)d\tSoftness constant = %(soft)d\n" % {'br': br, 'soft': soft}

  return r, c, info


def BStoByteArray (stream):
  """Convert a BitStream to a ByteArray. Fills each Byte from MSB to LSB. """

  output = array.array('B')
  i = 7
  byte = 0
  for bit in stream:
    byte = (byte << 1) | bit  # Fills a Byte from MSB to LSB
    i -= 1
    if i < 0:
      i=7
      output.append(byte)
      byte = 0
  
  if i !=7:                   # Parcial data in the last byte
    output.append(byte)


  return output


def CArrayPrint (bytedata, f, head, name, ):
    """ Prints a Byte Array in a pretty C array format. 
    
    Keywords arguments:
    bytedata -- Stream of bytes to write
    f -- File were to write
    head -- Pretty comment text for the bytedata array
    name -- Name of the bytedata array

    """
    if head:
      f.write("/*\n" + head + "*/\n\n")
     
    data_str = map(lambda x: "0x%02X" % x, bytedata)
    f.write(name + "_len = " + str(len(data_str)) + "; /* Num. of Bytes */\n")

    # Print Bytedata
    f.write(name + "_data  = {\n")
    
    blq = data_str[:COLUMN]
    i = 0
    while i < len(data_str): 
      f.write(', '.join(blq) + ',\n')
      i += COLUMN
      if i%32 == 0:
        f.write('/*---------------- %8d ----------------*/\n' % i)

      blq = data_str[i:min(i+COLUMN, len(data_str))]

    f.write("}; \n")


def IHEXoutput (bytedata, ih, addr, ptr_addr, bias=0):
  """ Write BTL Lib to a IHEX file. 
  
  Keywords arguments:
  bytedata -- Stream of bytes to write
  ih -- IntelHex Object wre to write
  addr -- Address were store the bytedata
  ptr_addr -- Address were store the pointer to the end of the data
  biar -- Offset of addresses were write all
  
  """
  ptr = len(bytedata) + addr + bias
  
  # Writes the pointer in the header
  ih[ptr_addr] = 0 # (ptr >> 24)
  ptr = ptr & 0x00FFFFFF
  
  ptr_addr +=1
  ih[ptr_addr] = ptr >> 16
  ptr = ptr & 0x0000FFFF
  
  ptr_addr +=1
  ih[ptr_addr] = ptr >> 8
  ptr = ptr & 0x000000FF
  
  ptr_addr +=1
  ih[ptr_addr] = ptr
  
  # Writes Data
  addr += bias
  for b in bytedata:
    ih[addr] = b
    addr +=1


# MAIN !
if __name__ == '__main__':
  import argparse

  # Args parsing
  parser = argparse.ArgumentParser(description="Reads a WAV file, play it and" +\
      " play BTc1 conversion. Finally return C array BTC enconde data")

  parser.add_argument('infile', type=str, nargs='+', \
      metavar='file.wav', help='WAV file to be procesed')

  parser.add_argument('-o', '--output', type=str, \
      help="Output file. By default output to stdout")

  parser.add_argument('-s', '--soft', type=int, default=24 , \
      help='Softness constant. How many charge/discharge C in each time period.' + \
      ' Must be >2. Default: %(default)s ')

  parser.add_argument('-f', '--format', choices=['c', 'btl', 'btl_ihex'], \
      default='c', help='Output format. c -> C Array; ' + \
      'btl -> BotTalk Library; ' + \
      'btl_ihex -> BotTalk Library in IHEX format. Default: %(default)s')


  parser.add_argument('-b', '--bias', metavar='N', type=int, default=0 , \
      help='Bias or Padding of the output file. In BTL or BTL in HEX fule' \
      " inserts N padding bytes. In Intel HEX, it's the initial address." \
      " Default: %(default)s ")

  parser.add_argument('-r', '--rate', metavar='BR', type=int, default=22000 , \
      help='Desired BitRate of procesed sound. Defaults: %(default)s bit/sec')

  parser.add_argument('-p', action='store_true', default=False, help='Plays procesed file')
  parser.add_argument('--playorig', action='store_true', default=False, help='Plays original file')
  parser.add_argument('--version', action='version',version="%(prog)s version "+ VERSION)

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

  sl = SoundsLib(args.rate, args.soft)
  for f in args.infile:
    sl.AddWAVSound(f)

  if args.playorig:
    for k in sl.sounds.keys():
      print("Playing Original Sound: " + k)
      sl.PlayOriginal(k)

  # Process all sounds in the lib
  sl.Process()

  # Play procesed sounds
  if args.p:
    for k in sl.sounds.keys():
      print("Playing Procesed Sound: " + k)
      sl.PlayProcesed(k)

  # Write to output
  sl.WriteToFile(args.output, args.format)
  

