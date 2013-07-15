#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
  Reads a WAV file and convert it to BTC 1.0 bit stream format

  BTc Sound Compression Algortithm created by Roman Black
  http://www.romanblack.com/btc_alg.htm

"""

from __future__ import division

VERSION = '0.1b'

CHUNK = 1024        # How many samples send to player
BYTES = 2           # N bytes arthimetic
MAX = 2**(BYTES*8 -1) -1
MIN = -(2**(BYTES*8 -1)) +1   

COLUMN = 12         # Prety print of values


import sys
import time
import os.path

import array
from math import log, exp, floor, ceil
import fpformat

import pyaudio
import wave
import audioop

def ReadWAV (file):
  """Reads a wave file and return sample rate and mono audio data """

  # Make header info
  sys.stderr.write('Openining : ' + file + '\n\n')
  wf = wave.open(file, 'rb')
  
  info = "\tWAV file: " + file + "\n"
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


def Play(sr, samples):
  """Plays an audio data

  Keywords arguments:
  sr -- Sample Rate
  samples -- Audio data in a string byte array (array.trostring())

  """
  stream = p.open(format=p.get_format_from_width(BYTES), \
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


def PredictiveBTC1_0 ( samples, sr, soft):
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
  info += "\tUsing BTc 1.0\n"

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
  
  info = "\tR= " + fpformat.fix(r, 1) + " Ohms\tC = " + \
        fpformat.fix((c/(10**-6)), 3) + "uF\n"
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

def force_stream_binary(stream):
    """Force binary mode for stream on Windows. (take from intelhex module)"""
    import os
    if os.name == 'nt':
        f_fileno = getattr(stream, 'fileno', None)
        if f_fileno:
            fileno = f_fileno()
            if fileno >= 0:
                import msvcrt
                msvcrt.setmode(fileno, os.O_BINARY)


def CArrayPrint (bytedata, head, f, bias =0):
    """ Prints a Byte Array in a pretty C array format. """
    sys.stderr.write('Writing C Array to : ' + f.name + '\n\n')

    f.write("/*\n" + head + "*/\n\n")
     
    data_str = map(lambda x: "0x%02X" % x, bytedata)
    f.write("data_len = " + str(len(data_str)) + "; /* Num. of Bytes */\n")

    # Print Bytedata
    f.write("data = {\n")
    blq = data_str[:COLUMN]
    
    i = 0
    while i < len(data_str): 
      f.write(', '.join(blq) + ',\n')
      i += COLUMN
      blq = data_str[i:min(i+COLUMN, len(data_str))]

    f.write("}; \n")


def RAWoutput (bytedata, head, f, bias =0):
  """ Writes RAW binary Byte Array to a file. """
  print(head)
  
  sys.stderr.write('Writing RAW binary to : ' + f.name + '\n\n')
  force_stream_binary(f)
  
  for i in range (bias): # Desired padding
    f.write(chr(0))

  data_len = len(bytedata)
  f.write(chr(data_len >> 24))
  data_len = data_len & 0x00FFFFFF
  
  f.write(chr(data_len >> 16))
  data_len = data_len & 0x0000FFFF
  
  f.write(chr(data_len >> 8))
  data_len = data_len & 0x000000FF
  
  f.write(chr(data_len))

  for b in bytedata:
    f.write(chr(b))


def BTLoutput (bytedata, head, f, bias =0):
  """ Writes to a BTL library file. """
  print(head)
  
  sys.stderr.write('Writing BTL binary to : ' + f.name + '\n\n')
  force_stream_binary(f)
  
  for i in range (bias): # Desired padding
    f.write(chr(0))

  # Writes the header
  f.write(chr(0))         # First byte it's cero

  data_len = (1024 + len(bytedata)) & 0x00FFFFFF
  f.write(chr(data_len >> 16))
  data_len = data_len & 0x0000FFFF
  
  f.write(chr(data_len >> 8))
  data_len = data_len & 0x000000FF
  
  f.write(chr(data_len))

  for b in range(1020): # Fills the header
    f.write(chr(0))

  for b in bytedata:
    f.write(chr(b))


def IHEXoutput (bytedata, head, f, bias =0):
  """ Write Byte Array to a IHEX file. """
  from intelhex import IntelHex
  print(head)
  
  ih = IntelHex()
  
  data_len = len(bytedata)

  ih[bias] = (data_len >> 24)
  data_len = data_len & 0x00FFFFFF
  
  bias +=1
  ih[bias] = data_len >> 16
  data_len = data_len & 0x0000FFFF
  
  bias +=1
  ih[bias] = data_len >> 8
  data_len = data_len & 0x000000FF
  
  bias +=1
  ih[bias] = data_len
  
  bias +=1
  for b in bytedata:
    ih[bias] = b
    bias +=1

  ih.write_hex_file(f)


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

  parser.add_argument('-f', '--format', choices=['c', 'btl', 'ihex', 'raw'], \
      default='c', help='Output format. c -> C Array, ihex -> Intel IHEX, ' + \
      'raw -> binary RAW, btl -> BotTalk Library. Default: %(default)s')

  # Maps output format wich options
  formats = { 'c'     : CArrayPrint,
              'raw'   : RAWoutput,
              'ihex'  : IHEXoutput,
              'btl'   : BTLoutput,
              }

  parser.add_argument('-b', '--bias', metavar='N', type=int, default=0 , \
      help='Bias or Padding of the output file. In raw BIN insert N padding' +\
      " bytes. In Intel HEX, it's the initial address. Default: %(default)s ")


  parser.add_argument('-p', action='store_true', default=False, help='Plays procesed file')
  parser.add_argument('--playorig', action='store_true', default=False, help='Plays original file')
  parser.add_argument('--version', action='version',version="%(prog)s version "+ VERSION)

  args = parser.parse_args()
 
  print(args)

  # Check input values
  if args.soft < 2:
    print("Invalid value of softness constant. Must be > 2.")
    sys.exit(0)

  if args.bias < 0:
    print("Invalid value of bias/padding. Muste a positive value.")
    sys.exit(0)

  for fname in args.infile:
    if not os.path.exists(fname):
      print("The input file %s don't exists." % fname)
      sys.exit(0)

  # Read WAV file and parses softness
  sr, samples, info = ReadWAV(args.infile[0])
  soft = args.soft

  if args.playorig or args.p:
    p = pyaudio.PyAudio() # Initiate audio system

  if args.playorig:
    Play(sr, samples)     # Plays original audio

  # Encode to BTc1.0
  bitstream, coinfo = PredictiveBTC1_0(samples, sr, soft)
  r, c, rcinfo = CalcRC(sr, soft)

  # Extra info for pretty output
  info += coinfo + rcinfo
  
  if args.p:
    # Decodes BTc data to play it
    output = DecodeBTC1_0(bitstream, sr, r, c)
    Play(sr, output)

  if args.playorig or args.p:
    p.terminate()

  data = BStoByteArray(bitstream)

  #Apply output format
  if args.output:
    with open(args.output, 'wb') as f: 
      formats[args.format](data, info, f, args.bias )
  else:
    formats[args.format](data, info, sys.stdout, args.bias )
