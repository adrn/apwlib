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
# image/util.py - A set of functions and utilities for handling and modifying 
#                 astronomical images
#

"""
TODO: 
"""

__author__ = 'Adrian Price-Whelan <adrn@astro.columbia.edu>'

# Standard library dependencies
import sys, os
import warnings
import math

# Third-party
import Image
import pyfits as pf
import numpy as np

# Project Dependencies
from apwlib.globals import *

def bitpixToPILMode(bitpix):
    """ Converts a FITS bitpix value into a PIL image mode
        
        Parameters
        ----------
        bitpix : int
            A FITS image header BITPIX value
    """
    if bitpix == 8:
        return "L"
    elif bitpix == 16 or bitpix == 32:
        return "I"
    elif bitpix == -32:
        return "L"
    elif bitpix == -64:
        raise ValueError("Unfortunately 64 Bit images aren't supported by PIL. Complain to them!")
    else:
        raise ValueError("Invalid FITS image.")

def _validateMinMax(data, min, max):
    """ Helper function for any stretching routine """
    if min == None:
        min = data.min()
    else:
        if min < data.min():
            warnings.warn(yellowText("Warning: ") + "user min value ({0}) is less than the minimum data value ({1})".format(min, data.min()))
    
    if max == None:
        max = data.max()
    else:
        if math.floor(max) > math.floor(data.max()):
            warnings.warn(yellowText("Warning: ") + "user max value ({0}) is greater than the maximum data value ({1})".format(max, data.max()))
    
    return min, max

def linearStretch(data, min=None, max=None, clip=False, **kwargs):
    """ Scales an array of numbers to be from 0 to 1
        
        Parameters
        ----------
        data : `numpy.array`, list
            The array of values to be scaled
        min : float, int
            The value to be mapped to 0
        max : float, int
            The value to be mapped to 1
    
    """
    data = np.array(data, dtype=float)
    min, max = _validateMinMax(data, min, max)
    
    scaledData = (data - min) / (max - min)
    if clip:
        scaledData[scaledData < 0.0] = 0.0
        scaledData[scaledData > 1.0] = 1.0
        return scaledData
    else:
        return scaledData

def arcsinhStretch(data, beta=1.0, min=None, max=None, clip=False, **kwargs):
    """ Scales an array of numbers using an arcsinh stretch
        
        Parameters
        ----------
        data : `numpy.array`, list
            The array of values to be scaled
        beta : float, in
            The nonlinearity of the arcsinh stretch, e.g. newValues = arcsinh(beta * oldValues)
        min : float, int
            The value to be mapped to 0
        max : float, int
            The value to be mapped to 1
    
    """
    data = np.array(data, dtype=float)
    min, max = _validateMinMax(data, min, max)
    
    scaledData = np.arcsinh(beta*(data - min) / (max - min))
    if clip:
        scaledData[scaledData < 0.0] = 0.0
        scaledData[scaledData > 1.0] = 1.0
        return scaledData
    else:
        return scaledData

def sqrtStretch(data, beta=1.0, min=None, max=None, clip=False, **kwargs):
    """ Scales an array of numbers using a sqrt stretch
        
        Parameters
        ----------
        data : `numpy.array`, list
            The array of values to be scaled
        beta : float, in
            The nonlinearity of the arcsinh stretch, e.g. newValues = arcsinh(beta * oldValues)
        min : float, int
            The value to be mapped to 0
        max : float, int
            The value to be mapped to 1
    
    """
    data = np.array(data, dtype=float)
    min, max = _validateMinMax(data, min, max)
    
    scaledData = np.sqrt(beta*(data - min) / (max - min))
    if clip:
        scaledData[scaledData < 0.0] = 0.0
        scaledData[scaledData > 1.0] = 1.0
        return scaledData
    else:
        return scaledData

class ImageSessionError(IOError):
    """ raise ImageSessionError(hour) """
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return self.string