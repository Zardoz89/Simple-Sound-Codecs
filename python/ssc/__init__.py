# outer __init__.py
"""
Implementation of some simple and dumb audio codecs, like Delta Modualtion
"""

from .aux import pack, unpack
from .dm import lin2dm, dm2lin, calc_a_value
from .btc import lin2btc, btc2lin, calc_rc
from ._version import __version__
