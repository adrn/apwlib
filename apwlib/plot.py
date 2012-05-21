# -*- coding: utf-8 -*-

""" apwlib
    ------
    
    Copyright (C) 2012 Adrian Price-Whelan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

################################################################################
# plot.py - Various plotting help 
#

"""
TODO:
    - ?
"""

__author__ = 'Adrian Price-Whelan <adrn@astro.columbia.edu>'
__all__ = ["floatToRGB"]

# Standard library dependencies (e.g. sys, os)
import math

# Project Dependencies
from custom_errors import *
import globals

def floatToRGB(h):
    """ Convert a floating point number between 0 and 1 to an
        RGB tuple. This is useful for plotting and changing the
        color of a point based on some parameter!
    """
    h = float(h)
    s = 1.0
    v = 1.0
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    #r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return (r, g, b)

if __name__ == "__main__":
    # Unit tests..
    pass