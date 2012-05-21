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
# Geometry.py - A Python module with convenience classes for dealing with 
#               geometric objects
#

"""
TODO:
    - More unit tests!
    - Finish CoordinateSystem and subclasses
"""

__author__ = 'Adrian Price-Whelan <adrn@astro.columbia.edu>'
__all__ = ["Angle", "RA", "Dec", "RADec"]

# Standard library dependencies (e.g. sys, os)
#from math import cos, acos, sin, radians, degrees
import math
import copy

# Project Dependencies
import convert
import astrodatetime
from custom_errors import *
import globals

class Angle(object):
    """ This class represents an Angle. 
        
        The units must be specified by the units parameter.
        Degrees and hours both accept either a string like '15:23:14.231,' or a
        decimal representation of the value, e.g. 15.387. For more explicit calls,
        use the convenience functions `fromDegrees`, `fromRadians`, and `fromHours`.
        
        Parameters
        ----------
        angle : float, int, str
            The angle value
        units : {'degrees', 'radians', 'hours'}

    """
    
    def __init__(self, angle, units):
        # Make the `units` string lower case, and validate the `units`
        lowUnits = units.lower()
                
        try:
            if lowUnits == "degrees":
                self.radians = math.radians(convert.parseDegrees(angle))
                
            elif lowUnits == "radians":
                self.radians = float(angle)
                
            elif lowUnits == "hours":
                # can accept string or float in any valid format
                self.radians = convert.hoursToRadians(convert.parseHours(angle))
            
            else:
                raise IllegalUnitsError(units)
        except ValueError:
            raise ValueError("{1}: the angle value given couldn't be parsed (was of type {0})".format(type(angle).__name__, type(self).__name__))
    
    @classmethod
    def fromDegrees(cls, val): 
        """ Create an `Angle` object with input units of Degrees """
        return cls(val, units="degrees")
        
    @classmethod
    def fromHours(cls, val):
        """ Create an `Angle` object with input units of Hours """
        return cls(val, units="hours")
        
    @classmethod
    def fromRadians(cls, val):
        """ Create an `Angle` object with input units of Radians """
        return cls(val, units="radians")
    
    @classmethod
    def fromAngle(cls, angle):
        """ Creates an `Angle` object from an `Angle` object """
        return cls(angle.radians, units="radians")
        
    @classmethod
    def fromDatetime(cls, dt):
        """ Create an `Angle` object with a Python `datetime.datetime` object """
        return cls(convert.datetime2decimalTime(dt), units="hours")

    def __repr__(self):
        return "<{2}: {0} degrees ({1})>".format(math.degrees(self.radians), convert.degreesToString(self.degrees), type(self).__name__)
    
    @property
    def degrees(self):
        """ Returns the angle's value in degrees (read-only property). """
        return math.degrees(self.radians) # converts radians to degrees
    
    @property
    def hours(self):
        """ Returns the angle's value in hours (read-only property). """
        return convert.radiansToHours(self.radians)

    @property
    def hms(self):
        """ Returns the angle's value in hours, and print as an (h,m,s) tuple (read-only property). """
        return convert.hoursToHMS(convert.radiansToHours(self.radians))

    def string(self, units="degrees", decimal=False, sep=" ", precision=5, pad=False): 
        """ Returns a string representation of the angle.
        
            Parameters
            ----------
            units : str
                Specifies the units, value should be one of the allowed units values (see: `Angle`)
            decimal : bool
                Specifies whether to return a sexagesimal representation (e.g. a tuple 
                (hours, minutes, seconds)), or decimal
            sep : str
                The separator between numbers in a sexagesimal representation, e.g. 12:41:11.1241
                where the separator is ":". Also accepts 2 or 3 separators, e.g. 12h41m11.1241s would be sep="hms",
                or 11-21:17.124 would be sep="-:"
        """
        
        lowUnits = units.lower()
        
        if lowUnits == "degrees":
            if decimal:
                return ("{0:0." + str(precision) + "f}").format(self.degrees)
            else:
                return convert.degreesToString(self.degrees, precision=precision, sep=sep, pad=pad)
                
        elif lowUnits == "radians":
            return str(self.radians)
                
        elif lowUnits == "hours":
            if decimal:
                return ("{0:0." + str(precision) + "f}").format(self.hours)
            else:
                return convert.hoursToString(self.hours, precision=precision, sep=sep, pad=pad)
        else:
            raise IllegalUnitsError(units)
            
    def normalize(self, bounds, units, inplace=False):
        """ Normalize the angle to be within the bounds specified. If inplace==True, 
            this replace the internal values, otherwise it returns a new Angle object.
            
            Parameters
            ----------
            bounds : tuple
                A tuple with 2 values (low, hi) where this is the range you would like
                to normalize the angle to. For example, if you have an angle value of 
                752.1834 but you want it to be within the range -180 -> +180, you can
                specifiy `Angle.normalize((-180, 180), units="degrees")`.
        """
        
        # Validate the units
        lowUnits = units.lower()
        convert.parseDegrees(bounds[1])
        if lowUnits == "degrees":
            radianBounds = (math.radians(convert.parseDegrees(bounds[0])), math.radians(convert.parseDegrees(bounds[1])))
        elif lowUnits == "radians":
            radianBounds = (float(bounds[0]), float(bounds[1]))
        elif lowUnits == "hours":
            radianBounds = (convert.hoursToRadians(convert.parseHours(bounds[0])), convert.hoursToRadians(convert.parseHours(bounds[1])))
        
        if inplace:
            obj = self
        else:
            obj = copy.copy(self)
        
        if obj.radians < radianBounds[0]:
            obj.radians = obj.radians % radianBounds[1]
            
        elif obj.radians >= radianBounds[1]:
            if radianBounds[0] == 0:
                obj.radians = obj.radians % radianBounds[1]
            else:
                obj.radians = obj.radians % radianBounds[0]
        
        return obj
    
    def __radians__(self): return self.radians
    def __degrees__(self): return self.degrees
    
    # Addition
    def __add__(self, other, option='left'):
        if not isinstance(otherCopy, Angle): 
            raise TypeError("Can't add an {1} object and a {0}!".format(otherCopy.__class__, type(self).__name__))
            
        if option == 'left':
            return Angle.fromRadians(self.radians + other.radians)
        elif option == 'right':
            return Angle.fromRadians(other.radians + self.radians)
    def __radd__(self, other): return self.__add__(other, 'right')
    
    # Subtraction
    def __sub__(self, other, option='left'):
        if not isinstance(other, Angle): 
            raise TypeError("Can't subtract an {1} object and a {0}!".format(other.__class__, type(self).__name__))
        
        if option == 'left':
            return Angle.fromRadians(self.radians - other.radians)
        elif option == 'right':
            return Angle.fromRadians(other.radians - self.radians)
    def __rsub__(self, other): return self.__sub__(other, 'right')
    
    # Multiplication
    def __mul__(self, other, option='left'):
        if isinstance(other, Angle):
            raise TypeError("Multiplication is not supported between two {0} objects!".format(type(self).__name__))
        else:
            return Angle.fromRadians(self.radians * other)
    def __rmul__(self, other): return self.__mul__(other, option='right')
    
    # Division
    def __div__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two {0} objects!".format(type(self).__name__))
        else:
            return Angle.fromRadians(self.radians / other)
    def __rdiv__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two {0} objects!".format(type(self).__name__))
        else:
            return Angle.fromRadians(other / self.radians)
    
    def __truediv__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two {0} objects!".format(type(self).__name__))
        else:
            return Angle.fromRadians(self.radians / other)
    def __rtruediv__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two {0} objects!".format(type(self).__name__))
        else:
            return Angle.fromRadians(other / self.radians)

    def __neg__(self):
        return Angle.fromRadians(-self.radians)

class RA(Angle):
    """ Represents a J2000 Right Ascension 
    
        Accepts a Righ Ascension angle value. The angle parameter accepts degrees, 
        hours, or radians and the default units are hours.
        Degrees and hours both accept either a string like '15:23:14.231,' or a
        decimal representation of the value, e.g. 15.387.
        
        Parameters
        ----------
        angle : float, int
            The angle value
        units : string
            The units of the angle value
    
    """
    
    def __init__(self, angle, units=None):
        # Default units for Righ Ascension are hours
        if units == None:
            units = "hours"

        super(RA, self).__init__(angle, units)
    
    def hourAngle(self, lst, units="hours"):
        """ Given a Local Sidereal Time (LST), calculate the hour angle for this RA
        
            Parameters
            ----------
            lst : float, str, `Angle`
                A Local Sidereal Time (LST)
            units : str
                The units of the LST, if not an `Angle` object or datetime.datetime object
                .. note::
                    * if lst is **not** an `Angle`-like object, you can specify the units by passing a `units` parameter into the call
                    * this function currently returns an `Angle` object
        """
        # TODO : this should return an HA() object, and accept an Angle or LST object
        if not isinstance(lst, Angle):
            lst = Angle(lst, units)
        
        return Angle(lst.radians - self.radians, units="radians")
    
    def lst(self, hourAngle, units="hours"):
        """ Given an Hour Angle, calculate the Local Sidereal Time (LST) for this RA
    
            Parameters
            ----------
            ha :  float, str, `Angle`
                An Hour Angle
            units : str
                The units of the ha, if not an `Angle` object
            
            .. note:: if ha is *not* an Angle object, you can specify the units by passing a 'units' parameter into the call
                'units' can be radians, degrees, or hours
                this function always returns an Angle object
        """
        # TODO : I guess this should return an HA() object, and accept an Angle or LST object
        if not isinstance(ha, Angle):
            ha = Angle(ha, units)
            
        return Angle(ha.radians + self.radians, units="radians")
    
    def string(self, **kwargs):
        """ Re-implements the default Angle.string() method to ensure
            default units of hours
        """
        
        if not kwargs.has_key("units"):
            kwargs["units"] = "hours"
        
        return super(RA, self).string(**kwargs)

class Dec(Angle):
    """ Represents a J2000 Declination """
    
    def __init__(self, angle, units="degrees"):
        """ Accepts a Declination angle value. The angle parameter accepts degrees, 
            hours, or radians and the default units are hours.
            Degrees and hours both accept either a string like '15:23:14.231,' or a
            decimal representation of the value, e.g. 15.387.
        
            Parameters
            ----------
            angle : float, int
                The angular value
            units : str 
                The units of the specified declination
            
        """
        
        # Default units for Declination are degrees
        if units == None:
            units = "degrees"
        
        super(Dec, self).__init__(angle, units)
    
    def string(self, **kwargs):
        """ Re-implements the default Angle.string() method to ensure
            default units of degrees
        """
        
        if not kwargs.has_key("units"):
            kwargs["units"] = "degrees"
        
        return super(Dec, self).string(**kwargs)

class RADec(object):
    """ Represents a J2000 Equatorial coordinate system. """
    
    def __init__(self, radec, ra_units="hours", dec_units="degrees"):
        """ """
        if isinstance(radec, tuple):
            if isinstance(radec[0], RA):
                self.ra = radec[0]
            else:
                self.ra = RA(radec[0], ra_units)
            
            if isinstance(radec[1], Dec):
                self.dec = radec[1]
            else:
                self.dec = Dec(radec[1], dec_units)
        elif isinstance(radec, str):
            ra, dec = convert.parseRADecString(radec)
            self.ra = ra
            self.dec = dec
        else:
            raise ValueError("RADec: Invalid format! Must initilalize with a tuple (ra,dec) or a string.")
    
    def __repr__(self):
        """ """
        return "<RA: {0} (degrees) | Dec: {1} (degrees)>".format(self.ra.string(sep=":"), self.dec.string(sep=":", units="degrees"))
    
    def string(self, radec_sep=",", ra_units="hours", dec_units="degrees", **kwargs):
        """ """
        if not kwargs.has_key("decimal"):
            kwargs["decimal"] = True
        
        return "{0}{2}{1}".format(self.ra.string(units=ra_units, **kwargs), self.dec.string(units=dec_units, **kwargs), radec_sep)
    
    def Jstring(self):
        """ Returns a string formatted in the J2000 IAU standard:
            JHHMMSS.ss+DDMMSS.s
        """
        if self.dec.degrees > 0: dec_sep = "+"
        else: dec_sep = ""
         
        return "J{0}{2}{1}".format(self.ra.string(sep="", precision=2), self.dec.string(sep="", precision=1), dec_sep)
         
    
    def subtends(self, other):
        """ Calculate the angle subtended by two coordinates on a sphere using
            Vincenty's formula.
            
            Parameters
            ----------
            other : RADec
                The other set of coordinates.
            
        """
        if not isinstance(other, RADec):
            raise ValueError("You must pass another RADec object into this function to calculate the angle subtended.")
        
        # This is the law of cosines, which suffers from rounding errors at small distances.
        #loc_ang = math.acos(math.sin(self.dec.radians)*math.sin(other.dec.radians) + math.cos(self.dec.radians)*math.cos(other.dec.radians)*math.cos(self.ra.radians - other.ra.radians))
        
        # -------------------------------------------------------------------------------
        # This implementation is Vincenty's formula. While obviously a little more
        # computationally expensive than the formula above, it is more accurate at all scales.
        # -------------------------------------------------------------------------------
        from math import sqrt, cos, sin, atan2
        
        # abbreviate for readability and to avoid the multiple stack calls
        (r1, d1) = (self.ra.radians, self.dec.radians)
        (r2, d2) = (other.ra.radians, other.dec.radians)
        dr = r1-r2
        
        X_nom = sqrt( (cos(d1)*sin(dr))**2 + (cos(d2)*sin(d1) - sin(d2)*cos(d1)*cos(dr))**2 )
        X_denom = sin(d2)*sin(d1) + cos(d2)*cos(d1)*cos(dr)
        ang = atan2(X_nom, X_denom)
                
        return Angle.fromRadians(ang)
    
    def convertTo(self, new_coordinates_class):
        raise NotImplementedError("This function has not been implemented yet.")
    
    def galactic(self):
        """ Convert the RA and Dec to Galactic latitude and longitude """
        return convert.j2000ToGalactic(self.ra, self.dec)
    

''' This is all experimental 
class Coordinate(object):
    """ A generic coordinate system class. Support n > 0 dimensions. This class is an 'abtract' class,
        and should really only be used in the below subclasses.
    """
    def __init__(self, *args):
        if len(args) == 0: raise ValueError("You must specify at least one coordinate!")
        
        self.coordinates = []
        for angle in args:
            if not isinstance(angle, Angle): raise ValueError("Input not a geometry.Angle() object!")
            self.coordinates.append(angle)

class SphericalCoordinate(Coordinate):
    pass

class CartesianCoordinate(Coordinate):
    pass

class GalacticSphericalCoordinate(SphericalCoordinate):
    pass

class GalacticCartesianCoordinate(CartesianCoordinate):
    pass
'''

# Standalone functions
def subtends(a1,b1,a2,b2,units="radians"):
    """ Calculate the angle subtended by 2 positions on the surface of a sphere.
        
        Parameters
        ----------
        a1 : float, `Angle`
        b1 : float, `Angle`
        a2 : float, `Angle`
        b2 : float, `Angle`
        units : str
            Specify the units for input / output. 
    """
    
    if units.lower() == "degrees":
        a1 = math.radians(a1)
        b1 = math.radians(b1)
        a2 = math.radians(a2)
        b2 = math.radians(b2)
    elif units.lower() == "radians":
        pass
    elif units.lower() == "hours":
        a1 = math.radians(convert.parseHours(a1)*15.)
        b1 = math.radians(convert.parseHours(b1)*15.)
        a2 = math.radians(convert.parseHours(a2)*15.)
        b2 = math.radians(convert.parseHours(b2)*15.)
    else:
        raise IllegalUnitsError("units must be 'radians', 'degrees', or 'hours' -- you entered: {0}".format(units))
    
    x1 = math.cos(a1)*math.cos(b1)
    y1 = math.sin(a1)*math.cos(b1)
    z1 = math.sin(b1)
    
    x2 = math.cos(a2)*math.cos(b2)
    y2 = math.sin(a2)*math.cos(b2)
    z2 = math.sin(b2)
    
    # [APW] Should this return an Angle object, or a float with units specified above? I think for
    #           a standalone function, it should be the latter...
    #theta = Angle.fromDegrees(math.degrees(math.acos(x1*x2+y1*y2+z1*z2)))
    
    if units.lower() == "degrees":
        return math.degrees(math.acos(x1*x2+y1*y2+z1*z2))
    elif units.lower() == "radians":
        return math.acos(x1*x2+y1*y2+z1*z2)
    elif units.lower() == "hours":
        return math.degrees(math.acos(x1*x2+y1*y2+z1*z2))/15.
    else:
        raise IllegalUnitsError("units must be 'radians', 'degrees', or 'hours' -- you entered: {0}".format(units))

if __name__ == "__main__":
    # self.assertEqual(sex2dec(11, 0, 0), 11.0)
    # self.assertAlmostEqual(dec2sex(11.0000000), (11, 0, 0), 9)
    import unittest, sys
    
    # Here are parameters used during the tests
    # --> Should be accurate to pico-arcseconds
    deg = 216.23748211292319
    hrs = deg / 15.0
    rad = math.radians(deg)
    strHrs = "14:24:56.9957071015656"
    strDeg = "216:14:14.935606523484"
    
    angleFromDeg = Angle.fromDegrees(deg)
    angleFromHrs = Angle.fromHours(hrs)
    angleFromRad = Angle.fromRadians(rad)
    angleFromStrHrs = Angle.fromHours(strHrs)

    class TestAngle(unittest.TestCase):
        
        def test_unitsEqual(self):
            
            # Make sure degrees are correct
            self.assertAlmostEqual(angleFromDeg.degrees, deg, 12)
            self.assertAlmostEqual(angleFromHrs.degrees, deg, 12)
            self.assertAlmostEqual(angleFromRad.degrees, deg, 12)
            self.assertAlmostEqual(angleFromStrHrs.degrees, deg, 12)
            
            # Make sure radians are correct
            self.assertAlmostEqual(angleFromDeg.hours, hrs, 12)
            self.assertAlmostEqual(angleFromHrs.hours, hrs, 12)
            self.assertAlmostEqual(angleFromRad.hours, hrs, 12)
            self.assertAlmostEqual(angleFromStrHrs.hours, hrs, 12)
            
            # Make sure hours are correct
            self.assertAlmostEqual(angleFromDeg.radians, rad, 12)
            self.assertAlmostEqual(angleFromHrs.radians, rad, 12)
            self.assertAlmostEqual(angleFromRad.radians, rad, 12)
            self.assertAlmostEqual(angleFromStrHrs.radians, rad, 12)
            
            # Test decimal string degrees are correct
            str_deg = angleFromDeg.string(units="degrees", decimal=True, sep=":", precision=12)
            self.assertEqual(str_deg, angleFromHrs.string(units="degrees", decimal=True, sep=":", precision=12))
            self.assertEqual(str_deg, angleFromRad.string(units="degrees", decimal=True, sep=":", precision=12))
            self.assertEqual(str_deg, angleFromStrHrs.string(units="degrees", decimal=True, sep=":", precision=12))
            
            # Test decimal string hours are correct
            str_hrs = angleFromDeg.string(units="hours", decimal=True, sep=":", precision=12)
            self.assertEqual(str_hrs, angleFromHrs.string(units="hours", decimal=True, sep=":", precision=12))
            self.assertEqual(str_hrs, angleFromRad.string(units="hours", decimal=True, sep=":", precision=12))
            self.assertEqual(str_hrs, angleFromStrHrs.string(units="hours", decimal=True, sep=":", precision=12))
            
            # Test decimal string radians are correct
            str_rad = angleFromDeg.string(units="radians", decimal=True, sep=":", precision=12)
            self.assertEqual(str_rad, angleFromHrs.string(units="radians", decimal=True, sep=":", precision=12))
            self.assertEqual(str_rad, angleFromRad.string(units="radians", decimal=True, sep=":", precision=12))
            self.assertEqual(str_rad, angleFromStrHrs.string(units="radians", decimal=True, sep=":", precision=12))
            
            # Test sexagesimal string degrees are correct
            #self.assertEqual(strDeg, angleFromHrs.string(units="degrees", decimal=False, sep=":", precision=12))
            #self.assertEqual(strDeg, angleFromRad.string(units="degrees", decimal=False, sep=":", precision=12))
            #self.assertEqual(strDeg, angleFromStrHrs.string(units="degrees", decimal=False, sep=":", precision=12))
            
            # Test sexagesimal string hours are correct
            #self.assertEqual(strHrs, angleFromHrs.string(units="hours", decimal=False, sep=":", precision=12))
            #self.assertEqual(strHrs, angleFromRad.string(units="hours", decimal=False, sep=":", precision=12))
            #self.assertEqual(strHrs, angleFromStrHrs.string(units="hours", decimal=False, sep=":", precision=12))
            
        def test_bounds(self):
            boundsAngle = Angle.fromDegrees(deg)
            
            boundsAngle.setBounds(-180, 180, units="degrees")
            boundsAngle.normalize()
            self.assertAlmostEqual(boundsAngle.degrees % 360, deg, 12)
            
            boundsAngle.setBounds(-270,90, units="degrees")
            boundsAngle.normalize()
            self.assertAlmostEqual(boundsAngle.degrees % 360, deg, 12)
            
            boundsAngle.setBounds(-360,0, units="degrees")
            boundsAngle.normalize()
            self.assertAlmostEqual(boundsAngle.degrees % 360, deg, 12)
            
            boundsAngle.setBounds(0,360, units="degrees")
            boundsAngle.normalize()
            self.assertAlmostEqual(boundsAngle.degrees % 360, deg, 12)
    
    unittest.main()