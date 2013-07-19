#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Implements Binary Time constant sound codecs in Python

  BTc Sound Compression Algortithm created by Roman Black
  http://www.romanblack.com/btc_alg.htm

"""

from __future__ import division

import array
from math import log, ceil, exp


BYTES = 2           # N bytes arthimetic
MAX = 2**(BYTES*8 -1) -1
MIN = -(2**(BYTES*8 -1)) +1   

def PredictiveBTC1_0 ( samples, soft):
  """Encode audio data with BTc 1.0 audio codec. Returns a BitStream in a list

  Keywords arguments:
  samples -- Audio data in a string byte array (array.trostring())
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


def PredictiveBTC1_7 ( samples, soft):
  """Encode audio data with BTc 1.7 audio codec. Returns a BitStream in a list

  Keywords arguments:
  samples -- Audio data in a string byte array (array.trostring())
  soft -- BTc softnes constant or how the capactiro charge/discharge in each T unit

  """

  raw = array.array('h')
  raw.fromstring(samples)
  
  stream = [0]
  lastbtc = 0
   # Calcs Upper and lower bounds whe LastBit != ThisBit
  UpFrac = 2*MAX*(4/5.33) + MIN      
  DwFrac = 2*MAX*(1.33/5.33) + MIN


  for sample in raw:
    if stream[-1] >= 1:
      # Generate a high (1) outcome
      dist = (MAX - lastbtc) / soft             # Calc total distance to charge
      # BTC only charge to 1/soft distance
      highbtc = lastbtc + dist

      # Generate a low (0) outcome
      dist = (lastbtc - DwFrac) / soft          # Calc total distance to discharge
      # BTC only discharge to 1/soft distance
      lowbtc = lastbtc - dist

    else:
      # Generate a high (1) outcome
      dist = (UpFrac - lastbtc) / soft          # Calc total distance to charge
      # BTC only charge to 1/soft distance
      highbtc = lastbtc + dist

      # Generate a low (0) outcome
      dist = (lastbtc - MIN) / soft             # Calc total distance to discharge
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

  stream = stream[1:]
  info =  "\tSize: %d (bytes)\n" % ceil(len(stream)/8.0) 

  return stream, info


def DecodeBTC1_0 (stream, br, r, c):
  """Decode a BTc1.0 BitStream in a list to a string byte array (array.tostring)

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


def DecodeBTC1_7 (stream, soft):
  """Decode a BTc1.7 BitStream in a list to a string byte array (array.tostring)

  Keywords arguments:
  stream -- List with the BitStrem
  soft -- Softness constant or how charge/discharge in each bit

  """

  audio = array.array('h')
  last = 0.5

  VUp = 4/5.33
  VDw = 1.33/5.33
  LastBit = 0
  
  for bit in stream:
    if bit >= 1 and LastBit >=1:    # Charge to Vcc
      last = (1 - last)/soft + last
    elif bit >=1 and LastBit <1:    # Pull to 3/4 of Vcc
      if last <= VUp:
        # Charge to VUp
        last = (VUp - last)/soft + last
      else:
        # Discharge to VUp
        last = last - (last - VUp)/soft
    elif bit < 1 and LastBit >=1:   # Pull to 1/4 of Vcc
      if last <= VDw:
        # Charge to VDw
        last = (VDw - last)/soft + last
      else:
        # Discharge to VDw
        last = last - (last - VDw)/soft
    elif bit < 1 and LastBit <1:    # Discharge to GND
      last = last - last/soft

    audio.append(int((last-0.5) * 2 * MAX) )
    LastBit = bit

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


