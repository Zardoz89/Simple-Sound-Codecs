#!/usr/bin/env python

"""
Implements Binary Time constant sound codecs in Python

BTc Sound Compression Algortithm created by Roman Black
http://www.romanblack.com/btc_alg.htm

"""
from __future__ import division

import array
from configure import *

# Calcs Upper and Lower bounds whe lastbit != ThisBit in BTc1.7
__UPFRAC = 2 * MAX * (4 / 5.33) + MIN
__DWFRAC = 2 * MAX * (1.33 / 5.33) + MIN
__VUP = 4.0 / 5.33
__VDW = 1.33 / 5.33


def lin2btc1_0(samples, soft):
    """
    Encode audio data with BTc 1.0 audio codec. Returns a BitStream in a list

    Keywords arguments:
    samples -- Audio data in a string byte array (array.trostring())
    soft -- BTc softnes constant or how the capactiro charge/discharge in each
            T unit

    """
    raw = array.array('h')
    raw.fromstring(samples)
    stream = []
    lastbtc = 0

    for sample in raw:
        # Generate a high (1) outcome
        dist = (MAX - lastbtc) / soft     # Calc total distance to charge
        # BTC only charge to 1/soft distance
        highbtc = lastbtc + dist

        # Generate a low (0) outcome
        dist = (lastbtc - MIN) / soft     # Calc total distance to discharge
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


def lin2btc1_7(samples, soft):
    """
    Encode audio data with BTc 1.7 audio codec. Returns a BitStream in a list

    Keywords arguments:
    samples -- Audio data in a string byte array (array.trostring())
    soft -- BTc softnes constant or how the capactiro charge/discharge in each 
            T unit

    """
    raw = array.array('h')
    raw.fromstring(samples)

    stream = [0]
    lastbtc = 0

    for sample in raw:
        if stream[-1] >= 1:
            # Generate a high (1) outcome
            dist = (MAX- lastbtc) / soft    # Calc total distance to charge
            # BTC only charge to 1/soft distance
            highbtc = lastbtc + dist

            # Generate a low (0) outcome
            dist = (lastbtc - __DWFRAC) / soft
            # Calc total distance to discharge
            # BTC only discharge to 1/soft distance
            lowbtc = lastbtc - dist

        else:
            # Generate a high (1) outcome
            dist = (__UPFRAC - lastbtc) / soft # Calc total distance to charge
            # BTC only charge to 1/soft distance
            highbtc = lastbtc + dist

            # Generate a low (0) outcome
            dist = (lastbtc - MIN) / soft
            # Calc total distance to discharge
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

    return stream


def btc1_0_2lin(stream, soft):
    """
    Decode a BTc1.0 BitStream in a list to a string byte array (array.tostring)

    Keywords arguments:
    stream -- List with the BitStrem
    soft -- Softness constant or how charge/discharge in each bit
    """
    
    audio = array.array('h')
    last = 0.5

    for bit in stream:
        if bit >= 1:  # Charge!
            last = (1 - last) / soft + last
        else:         # Discharge!
            last -= last / soft

        audio.append(int((last - 0.5) * 2 * MAX))

    return audio.tostring()


def btc1_7_2lin(stream, soft):
    """
    Decode a BTc1.7 BitStream in a list to a string byte array (array.tostring)

    Keywords arguments:
    stream -- List with the BitStrem
    soft -- Softness constant or how charge/discharge in each bit

    """

    audio = array.array('h')
    last = 0.5

    lastbit = 0

    for bit in stream:
        if bit >= 1 and lastbit >= 1:    # Charge to Vcc
            last = (1 - last) / soft + last
        elif bit >= 1 and lastbit < 1:    # Pull to 3/4 of Vcc
            if last <= __VUP:
                # Charge to VUp
                last = (__VUP - last) / soft + last
            else:
                # Discharge to VUp
                last = last - (last - __VUP) / soft
        elif bit < 1 and lastbit >= 1:   # Pull to 1/4 of Vcc
            if last <= __VDW:
                # Charge to VDw
                last = (__VDW - last) / soft + last
            else:
                # Discharge to VDw
                last -= (last - __VDW) / soft
        elif bit < 1 and lastbit < 1:    # Discharge to GND
            last -= last / soft

        audio.append(int((last - 0.5) * 2 * MAX))
        lastbit = bit

    return audio.tostring()


def calc_rc(bitrate, soft, cval=0.22*(10**-6)):
    """
    Calculate R and C values from a softnes constant and desired BitRate.

    Keyword arguments:
    bitrate -- Desired bitrate to use
    soft -- Desire softness constant to use
    cval -- Desire capacitor value (Default to 0.22 uF)

    Returns Resistos value in Ohms and Capacitor value in Farads
    """

    from math import log

    rval = -1.0 / (log(-1.0 / soft + 1) * bitrate * cval)

    return rval, cval


def pack(stream):
    """Convert a BitStream to a ByteArray. Fills each Byte from MSB to LSB. """

    output = array.array('B')
    i = 7
    byte = 0
    for bit in stream:
        byte = (byte << 1) | bit    # Fills a Byte from MSB to LSB
        i -= 1
        if i < 0:
            i = 7
            output.append(byte)
            byte = 0

    if i != 7:                      # Parcial data in the last byte
        output.append(byte)

    return output.tostring()

