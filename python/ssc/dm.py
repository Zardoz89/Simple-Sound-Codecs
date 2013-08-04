# -*- coding: utf-8 -*-
"""
Implements Delta Modulation sound codecs in Python
"""

from __future__ import division

import array
from ssc.aux import max_int, min_int

__WIDTH_TYPE = {1 : 'b',
                2 : 'h',
                4 : 'l',
                }

def lin2dm(fragment, width, delta = None, a_cte = 1.0, state = None):
    """
    Convert samples from Lineal PCM to 1 bit Delta Modulation encoding

    Parameters
    ----------

    fragment : iterable
               Iterable that contains a bytestring representation of the sound
               data in signed integer samples.
    width : int, {1, 2, 4}
            Size in bytes of each sample.
    delta : int
            Delta constant of DM modulation. By default it's 1/21 of Max sample
            value
    a_cte : float
            Sets Integrator decay value. By default it's 1.0 (no decay)
    state : dicctionary, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None
    
    Returns
    -------
    Returns a tuple of (bitstream, newstate) and newstate should be passed to
    the next call of lin2dm.
    """
   
    if width != 1 and width != 2 and width != 4:
        raise Exception('Invalid width %d' % width, width)

    MAX = max_int(width)
    MIN = min_int(width)
    
    if a_cte > 1.0:
        raise Exception('Invalid a value %d. Must be <= 1' % a_cte, a_cte)

    if delta and delta <= 0:
        raise Exception('Invalid delta value %d. Must be > 0' % delta, delta)
    elif delta is None:
        delta = MAX // 21

    raw = array.array(__WIDTH_TYPE[width])
    raw.fromstring(fragment)
    
    if state == None:
        integrator = MAX//2
    else:
        integrator = state['integrator']
    
    stream = []
    for sample in raw:
        highval = integrator + delta
        lowval = integrator - delta

        disthigh = abs(highval - sample)
        distlow = abs(lowval - sample)
        
        # Choose integrator with less diference to sample value
        if disthigh >= distlow:
            stream.append(False)
            integrator = lowval
        else:
            stream.append(True)
            integrator = highval

        integrator = max(integrator, MIN)
        integrator = min(integrator, MAX)
        integrator = int(integrator * a_cte)
   
    newstate = {'integrator' : integrator}
    return stream, newstate


def dm2lin(dmfragment, width, delta = None, a_cte = 1.0, state = None):
    """
    Convert samples from 1 bit Delta Modulation encoding to Lineal PCM

    Parameters
    ----------

    fragment : iterable
               Iterable that contains a bytestring representation of the sound
               data in signed integer samples.
    width : int, {1, 2, 4}
            Size in bytes of each sample.
    delta : int
            Delta constant of DM modulation. By default it's 1/21 of Max sample
            value
    a_cte : float
            Sets Integrator decay value. By default it's 1.0 (no decay)
    state : dicctionary, optional
            State of previus call if it's used to process chunks of sound data.
            In the first call state can be None. By default it's None

    Returns
    -------
    Returns a tuple of (fragment, newstate) and newstate should be passed to
    the next call of dm2lin.
    """
    if width != 1 and width != 2 and width != 4:
        raise Exception('Invalid width %d' % width, width)

    MAX = max_int(width)
    MIN = min_int(width)
    
    if a_cte > 1.0:
        raise Exception('Invalid a value %d. Must be <= 1' % a_cte, a_cte)

    if delta and delta <= 0:
        raise Exception('Invalid delta value %d. Must be > 0' % delta, delta)
    elif delta is None:
        delta = MAX // 21
    
    if state == None:
        integrator = MAX//2
    else:
        integrator = state['integrator']

    audio = array.array(__WIDTH_TYPE[width])

    for bit in dmfragment:
        if bit:
            integrator = integrator + delta
        else:
            integrator = integrator - delta

        # Clamp to signed 16 bit
        integrator = max(integrator, MIN)
        integrator = min(integrator, MAX)

        integrator = int(integrator * a_cte)

        audio.append(integrator)

    newstate = {'integrator' : integrator}
    return audio.tostring(), newstate


def calc_a_value(bitrate, tau = 0.001):
    from math import exp
    """
    Calculates A value for leaky integrator in function of bitrate and decay
    time

    Paramaters
    ----------
    bitrate : int
              Desired bitrate
    tau : float, optional
          Time Constant of leaky integrator in seconds. By default is 0.001 s

    Returns
    -------
    float
        A constant value for the desired decay time at desired bitrate
    """
    if decaytime <= 0:
        raise Exception("Invalid decaytime value %f. Must be > 0" % decaytime, \
                        decaytime)

    return exp( -1.0 / (tau * bitrate))
