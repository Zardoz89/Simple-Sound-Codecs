#!/usr/bin/env python

""" 
  Reads a WAV file and convert it to BTC 1.0 bit stream format

  BTc Sound Compression Algortithm created by Roman Black
  http://www.romanblack.com/btc_alg.htm

"""

CHUNK = 1024        # How many samples send to player
BYTES = 2           # N bytes arthimetic
MAX = 2**(BYTES*8 -1) -1
MIN = -(2**(BYTES*8 -1)) +1   

COLUMN = 12         # Prety print of values


import sys
import time
import argparse

import array
from math import log, exp, floor
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
  info += "\tOriginal Size: " + str(total_samples*wf.getsampwidth()) + " Bytes (" + \
      fpformat.fix(floor(seconds), 0) +":"+ fpformat.fix(ms_seconds, 3) + ") seconds \n"
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

  
  return stream


def DecodeBTC1_0 (stream, br, r, c):
  """Decode a BitStream in a list to a string byte array (array.tostring)

  Keywords arguments:
  stream -- List with the BitStrem
  br -- BitRate (and output SampleRate)
  r -- Resistor value
  c -- Capacitor value

  """

  audio = array.array('h')
  last = 0
  tau = r*c
  deltaT = 1.0/br

  for bit in stream:
    if bit >= 1:  #Charge!
      last = ( 1 + (last -1) * (exp(-deltaT/tau)))
    else:         #Discharge!
      last = ( last * (exp(-deltaT/tau)))
    
    audio.append(int(last * MAX) )

  return audio.tostring()


def CalcRC (br, soft, c=0.22*(10**-6)):
  """Calculate R and C values from a softnes constant and desired BitRate. """

  r = -1.0 / (log(-1.0/soft +1)*br*c)
  return r, c


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


def CArrayPrint (bytedata, head):
  """ Convert a Byte Array to a pretty C array format. """
  output =  "/*" + head + "*/\n\n"
   
  data_str = map(lambda x: "0x%02X" % x, bytedata)
  output += "data_len = " + str(len(data_str)) + "; /* Num. of Bytes */\n"

  # Print Bytedata
  output += "data = {\n"
  blq = data_str[:COLUMN]
  i = 0
  while i < len(data_str): 
    output += ', '.join(blq) + '\n'
    i += COLUMN
    blq = data_str[i:min(i+COLUMN, len(data_str))]

  output += "}; \n"

  return output



# Args parsing
parser = argparse.ArgumentParser(description="Reads a WAV file, play it and" +\
    " play BTc1 conversion. Finally return C array BTC enconde data")

parser.add_argument('infile', type=str, \
    metavar='file.wav', help='WAV file to be procesed')

parser.add_argument('-o', '--output', type=argparse.FileType('w'), \
    default=sys.stdout, help="Output file. By default output to stdout")

parser.add_argument('-s', '--soft', type=int, default=32 , \
    help='Softness constant. How many charge/discharge C in each time period.' + \
    ' Default: %(default)s ')

parser.add_argument('-f', '--format', choices=['c', 'ihex', 'raw'], \
    default='c', help='Output format. C -> C Array, ihex -> Intel IHEX, ' + \
    'raw -> binary RAW. Default: %(default)s')

parser.add_argument('-p', action='store_const', const=True, help='Plays procesed file')
parser.add_argument('--play-orig', action='store_const', const=True, help='Plays original file')

args = parser.parse_args()

# Read WAV file and parses softness
sr, samples, info = ReadWAV(args.infile)
soft = args.soft

p = pyaudio.PyAudio() # Initiate audio system

Play(sr, samples)     # Plays original audio

# Encode to BTc1.0
bitstream = PredictiveBTC1_0(samples, sr, soft)
r, c = CalcRC(sr, soft)

# Extra info for pretty output
info += "\tR= " + fpformat.fix(r, 1) + " Ohms\tC = " + \
      fpformat.fix((c/(10**-6)), 3) + "uF\n"
info += "\t Softness constant = %d" % soft

# Decodes BTc data to play it
output = DecodeBTC1_0(bitstream, sr, r, c)
Play(sr, output)
p.terminate()

data = BStoByteArray(bitstream)

# pretty print
args.output.write(CArrayPrint(data, info))

