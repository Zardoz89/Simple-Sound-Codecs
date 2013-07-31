# outer __init__.py
"""
Implementation of some simple and dumb audio codecs, like Delta Modualtion
"""

from ssc.aux import pack, unpack
from ssc.dm import predictive_dm, decode_dm
from ssc.btc import lin2btc, btc2lin, calc_rc
from ssc.configure import *

