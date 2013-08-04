# -*- coding: utf-8 -*-
"""
Some auxiliar functions to work with bitstreams

"""
import array


WIDTH_TYPE = {1 : 'b',
              2 : 'h',
              4 : 'l',
             }

def max_int(width):
    """ Returns Max signed Int of desired width """
    return 2 ** (width*8 -1) - 1


def min_int(width):
    """ Returns Max signed Int of desired width """
    return -(2 ** (width*8 -1)) + 1


def pack(bitstream, bitendianness = 'MSB'):
    """
    Converts a Bitstream to a Bytestring and return it
    
    Parameters
    ----------
    
    bitstream : iterable 
                Iterable that contains a bit stream
    bitendianness : {'MSB', 'LSB'} optinal
                    How should fill each byte. Can be 'MSB' or 'LSB'. By 
                    default it's MSB
    
    Returns
    -------
    bytes
        A Bytestring representation of the Bitstream
    """

    output = array.array('B')
    byte = 0
    
    if bitendianness == 'LSB':
        i = 0
        for bit in bitstream:
            byte = (byte >> 1) | bit    # Fills a Byte from LSB to MSB
            i += 1
            if i > 7:
                i = 0
                output.append(byte)
                byte = 0

        if i != 0:                      # Parcial data in the last byte
            output.append(byte)
    else:
        i = 7
        for bit in bitstream:
            byte = (byte << 1) | bit    # Fills a Byte from MSB to LSB
            i -= 1
            if i < 0:
                i = 7
                output.append(byte)
                byte = 0

        if i != 7:                      # Parcial data in the last byte
            output.append(byte)

    return output.tostring()


def unpack(bytestring, bitendianness = 'MSB'):
    """
    Converts a Bytestring to a Bitstream and return it
    
    Parameters
    ----------
    
    bytestring : iterable 
                 Iterable that contains a bytestring
    bitendianness : {'MSB', 'LSB'} optinal
                    How should fill each byte. Can be 'MSB' or 'LSB'. By 
                    default it's MSB
    
    Returns
    -------
    list of bool
        A Bitstream representation of the Bytestring
    """

    input = array.array('B')
    input.fromstring(bytestring)
    output = []

    if bitendianness == 'LSB':
        for byte in input:
            for i in range(0, 7):
                bit = byte & (1 << i)   # Get I bit
                output.append(bit)

    else:
        for byte in input:
            for i in range(7, 0, -1):
                bit = byte & (1 << i)   # Get I bit
                output.append(bit)

    return output.tostring()
