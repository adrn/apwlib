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
    - doxypy style documentation
    - fix __all__ to contain the actual classes
    - setBounds is wrong!
    - EquatorialCoordinates should accept a J1241+134134 whatever string
"""

__author__ = 'Adrian Price-Whelan <adrn@astro.columbia.edu>'
__all__ = ["Angle", "RA", "Dec"]

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
    """ \brief This class represents an Angle. 
        
        Set the bounds by specifying angleObject.bounds = (lower, upper). Detailed 
        description here! [APW]
    
    """
    
    _customBounds = False
    
    @classmethod
    def fromDegrees(cls, val): 
        """ \brief Create an \em Angle() object with input units of Degrees """
        return cls(val, units="degrees")
        
    @classmethod
    def fromHours(cls, val):
        """ \brief Create an \em Angle() object with input units of Hours """
        return cls(val, units="hours")
        
    @classmethod
    def fromRadians(cls, val):
        """ \brief Create an \em Angle() object with input units of Radians """
        return cls(val, units="radians")
        
    @classmethod
    def fromDatetime(cls, dt):
        """ \brief Create an \em Angle() object with a Python datetime.datetime() object """
        return cls(convert.datetime2decimalTime(dt), units="hours")
    
    def __init__(self, angle, units):
        """ Accepts an angle value. The angle parameter accepts degrees, hours, or
            radians and the units must be specified by the units parameter.
            Degrees and hours both accept either a string like '15:23:14.231,' or a
            decimal representation of the value, e.g. 15.387.
    
        \param angle (\c float, \c int) the angle value
        \param units (\c string) the units of the angle value
            
        """
        
        lowUnits = units.lower()
        if lowUnits not in globals.VALIDUNITS:
            raise IllegalUnitsError(units)
        
        if lowUnits == "degrees":
            #try:
            #    self.radians = math.radians(float(angle))
            #except ValueError:
            #    raise ValueError("geometry.Angle: the value given for degrees couldn't be converted into a float (was of type {0})".format(type(degrees).__name__))
            self.radians = math.radians(convert.parseDegrees(angle))
            
        elif lowUnits == "radians":
            try:
                self.radians = float(angle)
            except ValueError:
                raise ValueError("geometry.Angle: the value given for radians couldn't be converted into a float (was of type {0})".format(type(radians).__name__))
            
        elif lowUnits == "hours":
            # can accept string or float in any valid format
            self.radians = convert.hoursToRadians(convert.parseHours(angle))

        else:
            raise IllegalUnitsError(units)
        
        self.setBounds(0., 2.*math.pi)

    def __repr__(self):
        return "<Angle: {0} degrees ({1})>".format(math.degrees(self.radians), convert.degreesToString(self.degrees))
    
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
    
    @property
    def degrees(self):
        """ Returns the angle's value in degrees (read-only property). """
        return math.degrees(self.radians) # converts radians to degrees

    def string(self, units="hours", decimal=False, sep=" ", precision=5, pad=False): 
        """ \brief Returns a string representation of the angle.
        
        Parameters
        ----------
        \param units (\c str) Specifies the units, value should be one of "degrees", "radians", "hours"
        \param decimal (\c bool) Specifies whether to return a sexagesimal representation (e.g. a tuple 
            (hours, minutes, seconds)), or decimal
        \param sep (\c str) The separator between numbers in a sexagesimal representation, e.g. 12:41:11.1241
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
    
    def setBounds(self, low, hi, units="radians"):
        """ \brief Allows the user to specify the bounds of the angle.
        
            By default, these bounds are {0,2π}, but this can be modulated. For example, if you
            want to change the bounds to {-π,π}, you can specify angle.setBounds(-pi, pi). The 
            default units are radians, but alternatively you can specify the range in degrees or
            hours.
            
            Parameters
            ----------
            \param low (\c float, \c int) The lower bound.
            \param hi (\c float, \c int) The upper bound.
            \param units (\c str) The units, value should be one of "degrees", "radians", "hours"
        """
        
        lowUnits = units.lower()
        
        try:
            if lowUnits == "degrees":
                low = math.radians(float(low))
                hi = math.radians(float(hi))
            elif lowUnits == "radians":
                low = float(low)
                hi = float(hi)
            elif lowUnits == "hours":
                low = math.radians(float(low)*15.)
                hi = math.radians(float(hi)*15.)
            else:
                raise IllegalUnitsError(units)
        except ValueError:
            raise ValueError("Angle.bounds() Invalid bound input! You specified: {0},{1}".format(low, hi))    
        
        self._customBounds = True
        self._bounds = (low, hi)
            
    def normalize(self):
        """ \brief Normalize the angle to be within the set bounds (self._bounds), and 
            replace the internal values.
        """
        if self.radians < self._bounds[0]:
            self.radians = self.radians % self._bounds[1]
            
        elif self.radians >= self._bounds[1]:
            if self._bounds[0] == 0:
                self.radians = self.radians % self._bounds[1]
            else:
                self.radians = self.radians % self._bounds[0]
    
    def __radians__(self): return self.radians
    def __degrees__(self): return self.degrees
    
    # Addition
    def __add__(self, other, option='left'):
        selfCopy = copy.copy(self)
        otherCopy = copy.copy(other)
        
        if not isinstance(otherCopy, Angle): 
            raise TypeError("Can't add an Angle object and a {0}!".format(otherCopy.__class__))
        if option == 'left':
            selfCopy.units = otherCopy.units
            return Angle.fromUnits(selfCopy._value + otherCopy._value, selfCopy.units)
        elif option == 'right':
            otherCopy.units = selfCopy.units
            return Angle.fromUnits(otherCopy._value + selfCopy._value, otherCopy.units)
    def __radd__(self, other): return self.__add__(other, 'right')
    
    # Subtraction
    def __sub__(self, other, option='left'):
        if not isinstance(other, Angle): 
            raise TypeError("Can't subtract an Angle object and a %s!" % other.__class__)
        
        selfCopy = copy.copy(self)
        otherCopy = copy.copy(other)
        
        if option == 'left':
            selfCopy.units = otherCopy.units
            return Angle.fromUnits(selfCopy._value - otherCopy._value, selfCopy.units)
        elif option == 'right':
            otherCopy.units = selfCopy.units
            return Angle.fromUnits(otherCopy._value - selfCopy._value, otherCopy.units)
    def __rsub__(self, other): return self.__sub__(other, 'right')
    
    # Multiplication
    def __mul__(self, other, option='left'):
        if isinstance(other, Angle):
            raise TypeError("Multiplication is not supported between two Angle objects!")
        else:
            return Angle.fromUnits(self.degrees * other, "degrees")
    def __rmul__(self, other): return self.__mul__(other, option='right')
    
    # Division
    def __div__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two Angle objects!")
        else:
            return Angle.fromUnits(self.degrees / other, "degrees")
    def __rdiv__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two Angle objects!")
        else:
            return Angle.fromUnits(other / self.degrees, "degrees")
    
    def __truediv__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two Angle objects!")
        else:
            return Angle.fromUnits(self.degrees / other, "degrees")
    def __rtruediv__(self, other):
        if isinstance(other, Angle):
            raise TypeError("Division is not supported between two Angle objects!")
        else:
            return Angle.fromUnits(other / self.degrees, "degrees")

    def __neg__(self):
        return Angle.fromRadians(-self.radians)

class RA(Angle):
    """ Represents a J2000 Right Ascension """
    
    def __init__(self, angle, units="hours"):
        """ Accepts a Righ Ascension angle value. The angle parameter accepts degrees, 
            hours, or radians and the default units are hours.
            Degrees and hours both accept either a string like '15:23:14.231,' or a
            decimal representation of the value, e.g. 15.387.
    
        \param angle (\c float, \c int) the angle value
        \param units (\c string) the units of the angle value
            
        """
        
        lowUnits = units.lower()
        if lowUnits not in globals.VALIDUNITS:
            raise IllegalUnitsError(units)
        
        if lowUnits == "degrees":
            #try:
            #    self.radians = math.radians(float(angle))
            #except ValueError:
            #    raise ValueError("geometry.RA: the value given for degrees couldn't be converted into a float (was of type {0})".format(type(degrees).__name__))
            self.radians = math.radians(convert.parseDegrees(angle))
            
        elif lowUnits == "radians":
            try:
                self.radians = float(angle)
            except ValueError:
                raise ValueError("geometry.RA: the value given for radians couldn't be converted into a float (was of type {0})".format(type(radians).__name__))
            
        elif lowUnits == "hours":
            # can accept string or float in any valid format
            self.radians = convert.hoursToRadians(convert.parseHours(angle))

        else:
            raise IllegalUnitsError(units)
        
        self.setBounds(0., 2.*math.pi)

    def ha(self, lst, units="hours"):
        """ \brief Given a Local Sidereal Time (LST), calculate the hour angle for this RA
    
        \param lst (\c float, \c string, \c Angle) A Local Sidereal Time (LST)
        \param units (\c string) The units of the LST, if not an Angle object
        
            \li if lst is *not* an Angle object, you can specify the units by passing a 'units'
                parameter into the call
            \li units can be "radians", "degrees", or "hours"
            \li this function always returns an Angle object
        """
        # [APW] : this should return an HA() object, and accept an Angle or LST object
        if not isinstance(lst, Angle):
            lst = Angle(lst, units)
        
        return Angle(lst.radians - self.radians, units="radians")
    
    def hourAngle(self, lst, units="hours"):
        return ha(self, lst, units)
    
    def lst(self, ha, units="hours"):
        """ \brief Given an Hour Angle, calculate the Local Sidereal Time (LST) for this RA
    
        Parameters
        ----------
        \param ha (\c float, \c string, \c Angle) An Hour Angle
        \param units (\c string) The units of the ha, if not an Angle object
        
        Notes
        -----
            - if ha is *not* an Angle object, you can specify the units by passing a 'units'
                parameter into the call
            - 'units' can be radians, degrees, or hours
            - this function always returns an Angle object
        """
        if not isinstance(ha, Angle):
            ha = Angle(ha, units)
            
        return Angle(ha.radians + self.radians, units="radians")

class Dec(Angle):
    """ \brief Represents a J2000 Declination """
    
    def __init__(self, angle, units="degrees"):
        """ Accepts a Declination angle value. The angle parameter accepts degrees, 
            hours, or radians and the default units are hours.
            Degrees and hours both accept either a string like '15:23:14.231,' or a
            decimal representation of the value, e.g. 15.387.
    
        \param angle (\c float, \c int) the angle value
        \param units (\c string) the units of the angle value
            
        """
        
        lowUnits = units.lower()
        if lowUnits not in globals.VALIDUNITS:
            raise IllegalUnitsError(units)
        
        if lowUnits == "degrees":
            #try:
            #    self.radians = math.radians(float(angle))
            #except ValueError:
            #    raise ValueError("geometry.Dec: the value given for degrees couldn't be converted into a float (was of type {0})".format(type(degrees).__name__))
            self.radians = math.radians(convert.parseDegrees(angle))
            
        elif lowUnits == "radians":
            try:
                self.radians = float(angle)
            except ValueError:
                raise ValueError("geometry.Dec: the value given for radians couldn't be converted into a float (was of type {0})".format(type(radians).__name__))
            
        elif lowUnits == "hours":
            # can accept string or float in any valid format
            self.radians = convert.hoursToRadians(convert.parseHours(angle))

        else:
            raise IllegalUnitsError(units)
        
        self.setBounds(0., 2.*math.pi)

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

class EquatorialCoordinate(SphericalCoordinate):
    """ Represents an RA, Dec coordinate system. """
    
    def __init__(self, ra, dec):
        """ A few notes: 
            - if the ra/dec specified are not geometry.Angle() objects, they are 
                assumed to be in units degrees, and converted to Angle() objects.
        
        """
        
        if not isinstance(ra, RA):
            self.ra = Angle.fromDegrees(ra)
        else:
            self.ra = ra

        if not isinstance(ra, RA):
            # If dec is not an RA object
            if isinstance(ra, Angle):
                # If it is an Angle object, preserve units
                self.ra = RA.fromDegrees(ra.degrees)
            else:
                # Otherwise, assume units = degrees
                self.ra = RA.fromDegrees(ra)
        else:
            self.ra = ra

        if not isinstance(dec, Dec):
            # If dec is not a Dec object
            if isinstance(dec, Angle):
                # If it is an Angle object, preserve units
                self.dec = Dec.fromDegrees(dec.degrees)
            else:
                # Otherwise, assume units = degrees
                self.dec = Dec.fromDegrees(dec)
        else:
            self.dec = dec
    
    def subtends(self, other):
        """ Calculate the angle subtended by 2 coordinates on a sphere
    
        Parameters
        ----------
        other : EquatorialCoordinates
        
        Returns
        -------
            Angle
            
        """
        if not isinstance(other, EquatorialCoordinates):
            raise ValueError("You must pass another 'EquatorialCoordinates' into this function to calculate the angle subtended.")
        
        x1 = cos(self.ra.radians)*cos(self.dec.radians)
        y1 = sin(self.ra.radians)*cos(self.dec.radians)
        z1 = sin(self.dec.radians)
        
        x2 = cos(other.ra.radians)*cos(other.dec.radians)
        y2 = sin(other.ra.radians)*cos(other.dec.radians)
        z2 = sin(other.dec.radians)
        
        angle = Angle.fromRadians(acos(x1*x2 + y1*y2 + z1*z2))
        angle.units = 'degrees'
        return angle
    
    def convertTo():
        pass

class GalacticSphericalCoordinate(SphericalCoordinate):
    pass

class GalacticCartesianCoordinate(CartesianCoordinate):
    pass


# Standalone functions
def subtends(a1,b1,a2,b2,units="radians"):
    """ \brief Calculate the angle subtended by 2 positions on the surface of a sphere.
        
        \param a1 (\c float, \c Angle)
        \param b1 (\c float, \c Angle)
        \param a2 (\c float, \c Angle)
        \param a2 (\c float, \c Angle)
        \param units (\c str) Specify the units for input / output. Must be either radians, degrees, or hours.
        
        \return (\c Angle)
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