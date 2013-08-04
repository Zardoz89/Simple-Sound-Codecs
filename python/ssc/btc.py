# -*- coding: utf-8 -*-
"""
Implements Binary Time constant sound codecs in Python

BTc Sound Compression Algortithm created by Roman Black
http://www.romanblack.com/btc_alg.htm

"""
from __future__ import division

import array
from ssc.aux import max_int, min_int

# PreCalcs Upper and Lower bounds whe lastbit != ThisBit in BTc1.7
__VUP = 4.0 / 5.33
__VDW = 1.33 / 5.33

# Auto sets array to apropiate format
__WIDTH_TYPE = {1 : 'b',
                2 : 'h',
                4 : 'l',
                }


def __frac_1_7(width):
    """ Calcs BTc 1.7 upper and lower fractions """
    up_frac = 2 * max_int(width) * __VUP + min_int(width)
    dw_frac = 2 * max_int(width) * __VDW + min_int(width)

    return up_frac, dw_frac


def __encode_btc1_0(fragment, width, soft, state):
    """
    Convert samples to 1 bit BTc 1.0 encoding

    Binary Time Constant (BTc) it's a variant of Delta Modulation that uses a RC
    circuiit to implement the integrator and DAC. It allow to do a quick and
    cheap sound reproduction and recording withc very low CPU power and RAM
    usage. Ideal for cheap umicros like 8bit PIC micros.

    Parameters
    ----------

    fragment : iterable
               Iterable that contains a bytestring representation of the sound
               data in signed integer samples.
    width : int, {1, 2 , 4}
            Size in bytes of each sample.
    soft : int
           Softness constant of BTc. 1/ softnees is how manyy dis/charge the 
           capacitor in each step
    state : tuple, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None

    Returns
    -------

    Returns a tuple of (bitstream, newstate) and newstate should be passed to
    the next call of __encode_btc_1_0.
    """

    raw = array.array(__WIDTH_TYPE[width])
    raw.fromstring(fragment)
    bitstream = []
    if state == None:
        lastbtc = 0
    else:
        lastbtc = state['lastbtc']

    MAX = max_int(width)
    MIN = min_int(width)

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
            bitstream.append(False)
            lastbtc = lowbtc
        else:
            bitstream.append(True)
            lastbtc = highbtc
        
        lastbtc = min(lastbtc, MAX)
        lastbtc = max(lastbtc, MIN)

    newstate = {'lastbtc' : lastbtc}
    return bitstream, newstate


def __encode_btc1_7(fragment, width, soft, state):
    """
    Convert samples to 1 bit BTc 1.7 encoding

    Binary Time Constant (BTc) it's a variant of Delta Modulation that uses a RC
    circuiit to implement the integrator and DAC. It allow to do a quick and
    cheap sound reproduction and recording withc very low CPU power and RAM
    usage. Ideal for cheap umicros like 8bit PIC micros.

    Parameters
    ----------

    fragment : iterable
               Iterable that contains a bytestring representation of the sound
               data in signed integer samples.
    width : int, {1, 2 , 4}
            Size in bytes of each sample.
    soft : int
           Softness constant of BTc. 1/ softnees is how manyy dis/charge the 
           capacitor in each step
    state : tuple, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None

    Returns
    -------

    Returns a tuple of (bitstream, newstate) and newstate should be passed to
    the next call of __encode_btc_1_7.
    """

    raw = array.array(__WIDTH_TYPE[width])
    raw.fromstring(fragment)

    bitstream = []
    if state == None:
        lastbtc = 0
        lastbit = False
    else:
        lastbtc = state['lastbtc']
        lastbit = state['lastbit']

    # Calcs upper and lower fractions
    MAX = max_int(width)
    MIN = min_int(width)
    up_frac, dw_frac = __frac_1_7(width)

    for sample in raw:
        if lastbit:
            # Generate a high (1) outcome
            dist = (MAX- lastbtc) / soft    # Calc total distance to charge
            # BTC only charge to 1/soft distance
            highbtc = lastbtc + dist

            # Generate a low (0) outcome
            dist = (lastbtc - dw_frac) / soft
            # Calc total distance to discharge
            # BTC only discharge to 1/soft distance
            lowbtc = lastbtc - dist

        else:
            # Generate a high (1) outcome
            dist = (up_frac - lastbtc) / soft # Calc total distance to charge
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
            bitstream.append(False)
            lastbit = False
            lastbtc = lowbtc
        else:
            bitstream.append(True)
            lastbit = True
            lastbtc = highbtc

        lastbtc = min(lastbtc, MAX)
        lastbtc = max(lastbtc, MIN)

    newstate = {'lastbtc' : lastbtc,
                'lastbit' : lastbit,
               }
    return bitstream, newstate


def lin2btc(fragment, width, soft, codec = '1.0', state = None):
    """
    Convert samples to 1 bit BTc encoding
    
    Binary Time Constant (BTc) it's a variant of Delta Modulation that uses a RC
    circuiit to implement the integrator and DAC. It allow to do a quick and
    cheap sound reproduction and recording withc very low CPU power and RAM
    usage. Ideal for cheap umicros like 8bit PIC micros.

    Parameters
    ----------

    fragment : iterable
               Iterable that contains a bytestring representation of the sound
               data in signed integer samples.
    width : int, {1, 2 , 4}
            Size in bytes of each sample.
    soft : int
           Softness constant of BTc. 1/ softnees is how manyy dis/charge the 
           capacitor in each step
    codec : {'1.0', '1.7'}, optional
            BTc codec version to use. By default it's BTc 1.0
    state : tuple, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None

    Returns
    -------

    Returns a tuple of (bitstream, newstate) and newstate should be passed to
    the next call of lin2btc.
    """
    if width != 1 and width != 2 and width != 4:
        raise Exception('Invalid width %d' % width, width)

    if soft < 2:
        raise Exception('Invalid softness value %d. Must be >= 2' % soft, soft)
    
    chooser = {'1.0' : __encode_btc1_0,
               '1.7' : __encode_btc1_7,
              }

    if codec in chooser:
        return chooser[codec](fragment, width, soft, state)
    else:
        raise Exception('Invalid BTc version %s' % codec, codec)


def __decode_btc1_0(btcfragment, width, soft, state = None):
    """
    Convert 1 bit BTc 1.0 bitstream samples to Lineal PCM samples
    
    Binary Time Constant (BTc) it's a variant of Delta Modulation that uses a RC
    circuiit to implement the integrator and DAC. It allow to do a quick and
    cheap sound reproduction and recording withc very low CPU power and RAM
    usage. Ideal for cheap umicros like 8bit PIC micros.

    Parameters
    ----------

    btcfragment : boolean iterable
                  Iterable that contains a bitstream representation of BTc data
    width : int, {1, 2 , 4}
            Size in bytes of each output sample.
    soft : int
           Softness constant of BTc. 1/ softnees is how many dis/charge the 
           capacitor in each step
    state : tuple, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None

    Returns
    -------

    Returns a tuple of (fragment, newstate) and newstate should be passed to
    the next call of __decode_btc1_0.
    """
    
    audio = array.array(__WIDTH_TYPE[width])
    MAX = max_int(width)

    if state == None:
        last = 0.5
    else:
        last = state['last']

    for bit in btcfragment:
        if bit >= 1:  # Charge!
            last = (1 - last) / soft + last
        else:         # Discharge!
            last -= last / soft

        audio.append(int((last - 0.5) * 2 * MAX))
    
    newstate = {'last' : last}
    return audio.tostring(), newstate


def __decode_btc1_7(btcfragment, width, soft, state = None):
    """
    Convert 1 bit BTc 1.7 bitstream samples to Lineal PCM samples
    
    Binary Time Constant (BTc) it's a variant of Delta Modulation that uses a RC
    circuiit to implement the integrator and DAC. It allow to do a quick and
    cheap sound reproduction and recording withc very low CPU power and RAM
    usage. Ideal for cheap umicros like 8bit PIC micros.

    Parameters
    ----------

    btcfragment : boolean iterable
                  Iterable that contains a bitstream representation of BTc data
    width : int, {1, 2 , 4}
            Size in bytes of each output sample.
    soft : int
           Softness constant of BTc. 1/ softnees is how many dis/charge the 
           capacitor in each step
    state : tuple, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None

    Returns
    -------

    Returns a tuple of (fragment, newstate) and newstate should be passed to
    the next call of __decode_btc1_7.
    """

    audio = array.array(__WIDTH_TYPE[width])
    if state == None:
        last = 0.5
        lastbit = 0
    else:
        last = state['last']
        lastbit = state['lastbit']

    MAX = max_int(width)

    for bit in btcfragment:
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

    newstate = {'last' : last, 'lastbit' : lastbit}
    return audio.tostring(), newstate


def btc2lin(btcfragment, width, soft, codec = '1.0', state = None):
    """
    Convert 1 bit BTc bitstream samples to Lineal PCM samples
    
    Binary Time Constant (BTc) it's a variant of Delta Modulation that uses a RC
    circuiit to implement the integrator and DAC. It allow to do a quick and
    cheap sound reproduction and recording withc very low CPU power and RAM
    usage. Ideal for cheap umicros like 8bit PIC micros.

    Parameters
    ----------

    btcfragment : boolean iterable
                  Iterable that contains a bitstream representation of BTc data
    width : int, {1, 2 , 4}
            Size in bytes of each output sample.
    soft : int
           Softness constant of BTc. 1/ softnees is how many dis/charge the 
           capacitor in each step
    codec : {'1.0', '1.7'}, optional
            BTc codec version to use. By default it's BTc 1.0
    state : tuple, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None

    Returns
    -------

    Returns a tuple of (fragment, newstate) and newstate should be passed to
    the next call of btc2lin.
    """

    if width != 1 and width != 2 and width != 4:
        raise Exception('Invalid width %d' % width, width)

    if soft < 2:
        raise Exception('Invalid softness value %d. Must be >= 2' % soft, soft)
    
    chooser = {'1.0' : __decode_btc1_0,
               '1.7' : __decode_btc1_7,
              }

    if codec in chooser:
        return chooser[codec](btcfragment, width, soft, state)
    else:
        raise Exception('Invalid BTc version %s' % codec, codec)


def calc_rc(bitrate, soft, cval=0.22*(10**-6)):
    """
    Calculate R and C values from a softnes constant and desired BitRate.

    Parameters
    ----------

    bitrate : int
              Desired bitrate to use
    soft : int 
           Desire softness constant to use
    cval : float
           Desire capacitor value in Farads. By default 0.22 uF

    Returns a tuple of Resistor value in Ohms and Capacitor value in Farads
    """

    from math import log

    rval = -1.0 / (log(-1.0 / soft + 1) * bitrate * cval)

    return rval, cval



