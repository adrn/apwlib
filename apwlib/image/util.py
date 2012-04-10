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

def fitsToBands(imPath, rggb=False, bayer=True):
    """ 
    This function takes a path to a FITS file as an input, and decomposes 
    the image into separate bands. This function assumes the image is in
    the Primary HDU (HDU 0) of the specified file, and makes some 
    assumptions about what to return depending on the number of axes in 
    the image. If NAXIS=1, the 1D array is simply returned. If NAXIS=2, 
    it by default assumes a Bayer pattern, but this can be controlled by
    the 'bayer' parameter (True or False). If Bayer is False, the full 2D
    array is returned. If 'bayer' is True, and 'rggb' is False (default), 
    the function combines G1 and G2. If 'rggb' is True, G1 and G2 are 
    returned separately. If NAXIS=3, return a 2D array for each element in
    NAXIS3. If NAXIS > 3, an error is thrown. 

    Parameters
    ----------
    imPath : string
        A string representing a path to a FITS file.
    rggb : Boolean
        If NAXIS=2 and the image is stored in a Bayer pattern, this 
        parameter controls whether G1 and G2 are averaged or not.
    bayer : Boolean
        If NAXIS=2, this parameter controls whether the full array is
        returned, or if it is decomposed into individual bands.

    Examples
    --------
    >>> 

    """
    
    if not os.path.exists(imPath): raise IOError("Image: %s not found! Is the path correct? \n\n" % imPath)
    
    im = pf.open(imPath)
    naxis = im[0].header['NAXIS']
    imData = im[0].data
    im.close()
    
    if naxis == 1:
        return imData.astype(float)
        
    elif naxis == 2:
        if bayer:
            # The image is saved in a Bayer pattern
            R = imData[::2,::2].astype(float)
            G1 = imData[1::2,::2].astype(float)
            G2 = imData[::2,1::2].astype(float)
            B = imData[1::2,1::2].astype(float)
            
            # Sometimes CCD's don't have an even number of pixels (WTF??),
            #   e.g. the (old?) Nikon D40 X. This corrects for any shape
            #   mismatching by throwing out a row or column so that all 
            #   of the bands have the same shape
            if (R.shape[0] % 2) != 0: R = R[:-1,:]
            if (R.shape[1] % 2) != 0: R = R[:,:-1]
            
            if (G1.shape[0] % 2) != 0: G1 = G1[:-1,:]
            if (G1.shape[1] % 2) != 0: G1 = G1[:,:-1]
            
            if (G2.shape[0] % 2) != 0: G2 = G2[:-1,:]
            if (G2.shape[1] % 2) != 0: G2 = G2[:,:-1]
                
            if (B.shape[0] % 2) != 0: B = B[:-1,:]
            if (B.shape[1] % 2) != 0: B = B[:,:-1]
            
            if rggb:
                return (R, G1, G2, B)
            else:
                G = (G1 + G2) / 2.0
                return np.array([R, G, B])
        else:
            # The image is grayscale
            return imData.astype(float)
            
    elif naxis == 3:
        # NAXIS3 appears as the **first** index in the returned data
        return np.array([oneBand.astype(float) for oneBand in imData])

def splitNEF(filename):
    """ Assuming `filename` is a FITS file produces by running rawtofits on a NEF file,
        (Nikon raw file), this script splits the FITS file into 3 separate -- one for 
        each band.
    """
    filebase = os.path.splitext(os.path.splitext(filename)[0])[0]
    
    r,g,b = fitsToBands(filename, bayer=True)
    
    rFile = pf.PrimaryHDU(r)
    rFile.writeto("{0}_R.fits".format(filebase))
    
    gFile = pf.PrimaryHDU(g)
    gFile.writeto("{0}_G.fits".format(filebase))
    
    bFile = pf.PrimaryHDU(b)
    bFile.writeto("{0}_B.fits".format(filebase))

class ImageSessionError(IOError):
    """ raise ImageSessionError(hour) """
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return self.string

class NotAnImageHDUError(ValueError):
    """ raise NotAnImageHDUError(hour) """
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return self.string