#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import array
import sys
from math import sin, pi

import ssc
from ssc.aux import max_int, min_int, WIDTH_TYPE

MAX_8 = max_int(1)
MAX_16 = max_int(2)
MAX_32 = max_int(4)

MIN_8 = max_int(1)
MIN_16 = min_int(2)
MIN_32 = min_int(4)

# Defines Sample frecuency/bitrate and test_data subsections 
TEST_FS = 44100
TEST_T = 0.5

'''
        # test_t seconds of 440 hz sinouidal sound at 0.9 amplitude
        freq = 440.0 * 2 * pi / TEST_FS
        for i in range(samples):
            f = 0.9 * sin(freq * i)
            raw8.append(int(MAX_8 * f))
            raw16.append(int(MAX_16 * f))
            raw32.append(int(MAX_32 * f))
'''

class Lin2dmBadInput(unittest.TestCase):
    '''Test bad input in lin2dm'''

    def setUp(self):
        '''Fills test data'''
        raw8 = array.array(WIDTH_TYPE[1])
        raw16 = array.array(WIDTH_TYPE[2])
        raw32 = array.array(WIDTH_TYPE[4])
        samples = int(TEST_T // TEST_FS)

        # test_t seconds of pure silence
        for i in range(samples):
            raw8.append(0)
            raw16.append(0)
            raw32.append(0)

        if sys.version_info[0] >= 3: # Python 3 or 2.x ?
            self.test_data8 = raw8.tobytes()
            self.test_data16 = raw16.tobytes()
            self.test_data32 = raw32.tobytes()
        else:
            self.test_data8 = raw8.tostring()
            self.test_data16 = raw16.tostring()
            self.test_data32 = raw32.tostring()


    def test_missing_input(self):
        '''lin2dem should fail with missing fragment data'''
        self.assertRaises(Exception, ssc.dm.lin2dm, None, 1)


    def test_invalid_width(self):
        '''lin2dm should fail with invalid width'''
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 0)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, -1)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 40)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, '4')
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, None)
        

    def test_invalid_a(self):
        '''lin2dm should fail with invalid A value'''
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, a_cte=-0.5)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, a_cte=1.5)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, a_cte=0)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, a_cte=-2)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, a_cte='0.5')
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, a_cte=None)


    def test_invalid_delta(self):
        '''lin2dm should fail with invalid Delta value'''
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, delta=0)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, delta=-1)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, delta='32')
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data8, 1, delta=MAX_8)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data16, 2, delta=MAX_16)
        self.assertRaises(Exception, ssc.dm.lin2dm, self.test_data32, 4, delta=MAX_32)


class Dm2linBadInput(unittest.TestCase):
    '''Test bad iput in dm2lin'''
    
    def setUp(self):
        '''Fills test data'''
        self.test_data = []
        
        # Generates test_t seconds of 01 sequence aka silence
        samples = int(TEST_T // TEST_FS)
        for i in range(samples):
            self.test_data.append(i%2)


    def test_missing_input(self):
        '''dm2lin should fail with missing fragment data'''
        self.assertRaises(Exception, ssc.dm.dm2lin, None, 1)

    
    def test_invalid_width(self):
        '''dm2lin should fail with invalid width'''
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 0)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, -1)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 40)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, '4')
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, None)
        

    def test_invalid_a(self):
        '''dm2lin should fail with invalid A value'''
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, a_cte=-0.5)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, a_cte=1.5)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, a_cte=0)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, a_cte=-2)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, a_cte='0.5')
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, a_cte=None)


    def test_invalid_delta(self):
        '''dm2lin should fail with invalid Delta value'''
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, delta=0)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, delta=-1)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, delta='32')
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 1, delta=MAX_8)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 2, delta=MAX_16)
        self.assertRaises(Exception, ssc.dm.dm2lin, self.test_data, 4, delta=MAX_32)


class lin2btcBadInput(unittest.TestCase):
    '''Test bad input in lin2btc'''

    def setUp(self):
        '''Fills test data'''
        raw8 = array.array(WIDTH_TYPE[1])
        samples = int(TEST_T // TEST_FS)

        # test_t seconds of pure silence
        for i in range(samples):
            raw8.append(0)

        if sys.version_info[0] >= 3: # Python 3 or 2.x ?
            self.test_data8 = raw8.tobytes()
        else:
            self.test_data8 = raw8.tostring()


    def test_missing_input(self):
        '''lin2btc should fail with missing fragment data'''
        self.assertRaises(Exception, ssc.btc.lin2btc, None, 1, 21)


    def test_invalid_width(self):
        '''lin2btc should fail with invalid width'''
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 0, 21)
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, -1, 21)
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 40, 21)
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, '4', 21)
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, None, 21)
        

    def test_invalid_soft(self):
        '''lin2btc should fail with invalid soft value'''
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, 1)
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, -2)
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, '16')
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, None)


    def test_invalid_codec(self):
        '''lin2btc should fail with invalid Codec value'''
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, 21, \
                          codec=None)
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, 21, \
                          codec='caca')
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, 21, \
                          codec='4.0')
        self.assertRaises(Exception, ssc.btc.lin2btc, self.test_data8, 1, 21, \
                          codec=1.0)


class Btc2linBadInput(unittest.TestCase):
    '''Test bad iput in btc2lin'''
    
    def setUp(self):
        '''Fills test data'''
        self.test_data = []
        
        # Generates test_t seconds of 01 sequence aka silence
        samples = int(TEST_T // TEST_FS)
        for i in range(samples):
            self.test_data.append(i%2)


    def test_missing_input(self):
        '''btc2lin should fail with missing fragment data'''
        self.assertRaises(Exception, ssc.btc.btc2lin, None, 1, 21)

    
    def test_invalid_width(self):
        '''btc2lin should fail with invalid width'''
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 0, 21)
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, -1, 21)
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 40, 21)
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, '4', 21)
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, None, 21)
        

    def test_invalid_soft(self):
        '''btc2lin should fail with invalid A value'''
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, 1)
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, -2)
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, '16')
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, None)


    def test_invalid_codec(self):
        '''btc2lin should fail with invalid codec value'''
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, 21, \
                          codec=None)
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, 21, \
                          codec='caca')
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, 21, \
                          codec='4.0')
        self.assertRaises(Exception, ssc.btc.btc2lin, self.test_data, 1, 21, \
                          codec=1.0)


class Calc_rcBadInput(unittest.TestCase):
    '''Test bad input in calc_rc'''

    def test_invalid_bitrate(self):
        '''calc_rc should only accept bitrate >= 50'''
        self.assertRaises(Exception, ssc.btc.calc_rc, -1, 21)
        self.assertRaises(Exception, ssc.btc.calc_rc, 10, 21)
        self.assertRaises(Exception, ssc.btc.calc_rc, None, 21)


    def test_invalid_soft(self):
        '''calc_rc should fail with invalid softness constant'''
        self.assertRaises(Exception, ssc.btc.calc_rc, TEST_FS, 1)
        self.assertRaises(Exception, ssc.btc.calc_rc, TEST_FS, -2)
        self.assertRaises(Exception, ssc.btc.calc_rc, TEST_FS, '16')
        self.assertRaises(Exception, ssc.btc.calc_rc, TEST_FS, None)

    def test_invalid_cval(self):
        '''calc_rc should fail with invalid capacitor value'''
        self.assertRaises(Exception, ssc.btc.calc_rc, TEST_FS, 21, 0)
        self.assertRaises(Exception, ssc.btc.calc_rc, TEST_FS, 21, -1)
        self.assertRaises(Exception, ssc.btc.calc_rc, TEST_FS, 21, None)


# MAIN
if __name__ == '__main__':
    unittest.main()

