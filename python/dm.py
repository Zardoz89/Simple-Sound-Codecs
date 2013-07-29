#!/usr/bin/env python3

import array

BYTES = 2   # N bytes arthimetic
MAX = 2 ** (BYTES * 8 - 1) - 1
MIN = - (2 ** (BYTES * 8 - 1)) + 1

CHUNK= 1024

def predictive_dm(samples, delta = MAX//21, a = 1):
    """
    Encodes audio bytearray data with Delta Modulation. Return a BitStream in a
    list

    Keyword arguments:
        samples -- Signed 16 bit Audio data in a byte array
        delta - Delta constant of DM modulation. By default it's 1/21 of Max
        Sample value
        a - Sets Integrator decay value. By default it's 1

    """
    raw = array.array('h')
    raw.frombytes(samples)
    stream = []
    integrator = MAX//2

    for sample in raw:
        highval = integrator + delta
        lowval = integrator - delta

        disthigh = abs(highval - sample)
        distlow = abs(lowval - sample)
        
        # Choose integrator with less diference to sample value
        if disthigh >= distlow:
            stream.append(0)
            integrator = lowval
        else:
            stream.append(1)
            integrator = highval

        integrator = round(integrator * a)
    
    return stream


def decode_dm(stream, delta = MAX//21, a = 1):
    """
    Decodes a Delta Modulation BitStream in Signed 16 bit Audio data in a
    ByteArray.

    Keywords arguments:
        stream -- List with the BitStream
        delta - Delta constant of DM modulation. By default it's 1/21 of Max
        Sample value
        a - Sets Integrator decay value. By default it's 1
    """

    audio = array.array('h')
    integrator = 0

    for bit in stream:
        if bit:
            integrator = integrator + delta
        else:
            integrator = integrator - delta

        # Clamp to signed 16 bit
        integrator = max(integrator, MIN)
        integrator = min(integrator, MAX)

        integrator = round(integrator * a)

        audio.append(integrator)

    return audio.tobytes()

# Main !
if __name__ == '__main__':
    try:
        import pyaudio
    except ImportError:
        print("Wops! We need PyAudio")
        sys.exit(0)

    import random
    import audioop
    import wave
    import sys
    import time
    from math import exp

    random.seed()
    
    p = pyaudio.PyAudio() # Init PyAudio

    wf = wave.open(sys.argv[1], 'rb')
    print("Filename: %s" % sys.argv[1])
    Fm = wf.getframerate()
    print("Sample Rate: %d" % Fm)
    bits = wf.getsampwidth()
    channels = wf.getnchannels()

    samples = wf.readframes(wf.getnframes())    # Get all data from wave file
    wf.close()

    if bits != BYTES:   # Convert to Signed 16 bit data
        samples = audioop.lin2lin(samples, bits, BYTES)
        if bits == 1 and min(samples) >= 0:     # It was 8 bit unsigned !
            samples = audioop.bias(samples, BYTES, MIN)

    if channels > 1:    # Convert to Mono
        samples = audioop.tomono(samples, BYTES, 0.75, 0.25)
    
    # Normalize at 0.9
    maxsample = audioop.max(samples, BYTES)
    samples = audioop.mul(samples, BYTES, MAX * 0.9 / maxsample)

    # Calc A value
    a = pow(0.0001, 1.0/(0.001 * Fm) )
    print("A value = %f, Integrator decays in 0.001s" % a)

    # Convert to Delta Modulation
    bitstream = predictive_dm(samples, a = a)

    # Swap random bits (simulate bit errors)
    ERROR_RATE = 0.1
    BIT_PROB = 0.5
    print("Error rate %f" % ERROR_RATE)

    for i in range(len(bitstream)):
        if random.random() <= ERROR_RATE:
            if random.random() <= BIT_PROB:
                bitstream[i] = 0
            else:
                bitstream[i] = 1


    # Reconvert to PCM
    audio = decode_dm(bitstream, a = a)

    # Play it!
    stream = p.open(format=p.get_format_from_width(BYTES), \
                        channels=1, rate=Fm, output=True)
    data = audio[:CHUNK]
    i = 0
    while i < len(audio):
        stream.write(data)
        i += CHUNK
        data = audio[i:min(i+CHUNK, len(audio))]

    time.sleep(0.5)

    stream.stop_stream()
    stream.close()

    p.terminate()

