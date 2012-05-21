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
# convert.py - A Python module that contains unit conversions and 
#               coordinate conversions for astronomical data
#               processing and analysis
#

"""
TODO: 
    - any function that takes RA and Dec should accept a string of the form HH:MM:SS.SS
    - define __all__ so importing all from this script doesn't carry all of 'math'
    - unit tests for all functions
    - TODO: conversion functions should accept arrays of numbers!!
"""

__author__ = 'Adrian Price-Whelan <adrn@astro.columbia.edu>'

# Standard library dependencies
import math
import re
import os.path
import calendar
from inspect import stack
import datetime as py_datetime

# Third-party libraries
import numpy as np

# Project Dependencies
from astrodatetime import astrodatetime, gmt
import geometry as g
from custom_errors import *

# Assumed Constants:
epochOffsetT = 0.0
ee = 23.0 + 26.0/60.0 + 21.45/3600.0 - 46.815/3600.0*epochOffsetT - 0.0006/3600.0*epochOffsetT**2 + 0.00181/3600.0*epochOffsetT**3

def intTimezoneToTzinfo(timezone):
    class TZ(py_datetime.tzinfo):
        def utcoffset(self, dt):
            return py_datetime.timedelta(hours=int(timezone))
        def tzname(self,dt): 
            return "GMT {0}".format(int(tz)) 
        def dst(self,dt): 
            return py_datetime.timedelta(0)
    tz = TZ()
    return tz

# HOURS (time or angle)
def _checkHourRange(hrs):
    if not -24 < hrs < 24:
        raise IllegalHourError("Error: hours not in range (-24,24) ({0}).".format(hrs))

def _checkMinuteRange(min):
    if not 0 <= min < 60:
        raise IllegalMinuteError("Error: minutes not in range [0,60) ({0}).".format(min))

def _checkSecondRange(sec):
    if not 0 <= sec < 60:
        raise IllegalSecondError("Error: seconds not in range [0,60) ({0}).".format(sec))

def checkHMSRanges(h, m, s):
    _checkHourRange(h)
    _checkMinuteRange(m)
    _checkSecondRange(s)
    return None
    
def parseHours(hours, outputHMS=False):
    """ Parses an input "hour" value to decimal hours or an hour, minute, second tuple.
        
        Convert hours given in any parseable format (float, string, tuple, list, or Angle) into 
        hour, minute, and seconds components or decimal hours.
        
        Parameters
        ----------
        hours : float, str
            If a string, accepts values in these formats:
                * HH:MM:SS.sss (string), e.g. 12:52:32.423
                * HH.dddd (float, string), e.g. 12.542326
                * HH MM SS.sss (string, array), e.g. 12 52 32.423
            Whitespace may be spaces and/or tabs.
        outputHMS : bool
            If True, returns a tuple of (hour, minute, second)

    """
    
    # either a string or a float
    x = hours

    if isinstance(x, float) or isinstance(x, int):
        parsedHours = x
        parsedHMS = hoursToHMS(parsedHours)
    
    elif isinstance(x, str):
        x = x.strip()
        
        try:
            parsedHours = float(x)
            parsedHMS = hoursToHMS(parsedHours)
        except ValueError:

            string_parsed = False
            div = '[:|/|\t|\-|\sHhMmSs]{1,2}' # accept these as (one or more repeated) delimiters: :, whitespace, /
            
            # First look for a pattern where h,m,s is specified
            pattr = '^([+-]{0,1}\d{1,2})' + div + '(\d{1,2})' + div + '(\d{1,2}[\.0-9]+)' + '[Ss]{0,1}' + '$'

            try:
                elems = re.search(pattr, x).groups()
                string_parsed = True
            except:
                pass # try again below
                #raise ValueError("convert.parseHours: Invalid input string, can't parse to HMS. ({0})".format(x))
            
            if string_parsed:
                parsedHours = hmsToHours(elems[0], elems[1], elems[2])
                parsedHMS = (int(elems[0]), int(elems[1]), float(elems[2]))
            
            else:
                
                # look for a pattern where only d,m is specified
                pattr = '^([+-]{0,1}\d{1,2})' + div + '(\d{1,2})' + '[Mm]{0,1}' + '$'
                
                try:
                	elems = re.search(pattr, x).groups()
                	string_parsed = True
                except:
                    raise ValueError("convert.parseHours: Invalid input string, can't parse to HMS. ({0})".format(x))

                parsedHours = hmsToHours(elems[0], elems[1], 0.)
                parsedHMS = (int(elems[0]), int(elems[1]), 0.)

    elif isinstance(x, g.Angle):
        parsedHours = x.hours
        parsedHMS = hoursToHMS(parsedHours)
    
    elif isinstance(x, py_datetime.datetime):
        parsedHours = datetimeToDecimalTime(x)
        parsedHMS = hoursToHMS(parsedHours)
        
    elif isinstance(x, tuple):
        if len(x) == 3:
            parsedHours = hmsToHours(*x)
            parsedHMS = x
        else:
            raise ValueError("{0}.{1}: Incorrect number of values given, expected (h,m,s), got: {2}".format(os.path.basename(__file__), stack()[0][3], x))

    elif isinstance(x, list):
        if len(x) == 3:
            try:
                h = float(x[0])
                m = float(x[1])
                s = float(x[2])
            except ValueError:
                raise ValueError("{0}.{1}: Array values ([h,m,s] expected) could not be coerced into floats. {2}".format(os.path.basename(__file__), stack()[0][3], x))

            parsedHours = hmsToHours(h, m, s)
            parsedHMS = (h, m, s)
            if outputHMS:
                return (h, m, s)
            else:
                return hmsToHours(h, m, s)

        else:
            raise ValueError("{0}.{1}: Array given must contain exactly three elements ([h,m,s]), provided: {2}".format(os.path.basename(__file__), stack()[0][3], x)) # current filename/method should be made into a convenience method
    
    else:
        raise ValueError("parseHours: could not parse value of type {0}.".format(type(x).__name__))
    
    if outputHMS:
        return parsedHMS
    else:
        return parsedHours
    
def hoursToHMS(h):
    """ Convert any parseable hour value (see: parseHours) into an hour,minute,second tuple """
    sign = math.copysign(1.0, h)
        
    (hf, h) = math.modf(abs(h)) # (degree fraction, degree)
    (mf, m) = math.modf(hf * 60.) # (minute fraction, minute)
    s = mf * 60.
    
    checkHMSRanges(h,m,s) # throws exception if out of range
    
    return (int(sign*h), int(m), s)

def hoursToDecimal(h):
    """ Convert any parseable hour value (see: parseHours) into a float value """
    return parseHours(h, outputHMS=False)

def hmsToHours(h, m, s):
    """ Convert hour, minute, second to a float hour value. """
    try:
        h = int(h)
        m = int(m)
        s = float(s)
    except ValueError:
        raise ValueError("convert.HMStoHours: HMS values ({0[0]},{0[1]},{0[2]}) could not be converted to numbers.".format(h,m,s))
    return h + m/60. + s/3600.

def hmsToDegrees(h, m, s):
    """ Convert hour, minute, second to a float degrees value. """
    return hmsToHours(h, m, s)*15.

def hmsToRadians(h, m, s):
    """ Convert hour, minute, second to a float radians value. """
    return math.radians(hmsToDegrees(h, m, s))

def hmsToDMS(h, m, s):
    """ Convert degrees, arcminutes, arcseconds to an hour, minute, second tuple """
    return degreesToDMS(hmsToDegrees(h, m, s))

def hoursToRadians(h):
    """ Convert an angle in Hours to Radians """
    return math.radians(h*15.)

def hoursToString(h, precision=5, pad=False, sep=("h", "m", "s")):
    """ Takes a decimal hour value and returns a string formatted as hms with separator
        specified by the 'sep' parameter. 
        
        More detailed description here!
    """
    if pad:
        hPad = ":02"
    else:
        hPad = ""
        
    if len(sep) == 1 or len(sep) == 0:
        literal = "{0[0]" + hPad + "}"+ str(sep) + "{0[1]:02d}" + str(sep) + "{0[2]:0" + str(precision+3) + "." + str(precision) + "f}"
    elif len(sep) == 2:
        literal = "{0[0]" + hPad + "}"+ str(sep[0]) + "{0[1]:02d}" + str(sep[1]) + "{0[2]:0" + str(precision+3) + "." + str(precision) + "f}"
    elif len(sep) == 3:
        literal = "{0[0]" + hPad + "}"+ str(sep[0]) + "{0[1]:02d}" + str(sep[1]) + "{0[2]:0" + str(precision+3) + "." + str(precision) + "f}" + str(sep[2])
    else:
        raise ValueError("Invalid separator specification for converting angle to string.")
        
    return literal.format(hoursToHMS(h))

# DEGREES
def parseDegrees(degrees, outputDMS=False):
    """ Parses an input "degrees" value into decimal degrees or a 
        degree,arcminute,arcsecond tuple.
        
        Convert degrees given in any parseable format (float, string, or Angle) into 
        degrees, arcminutes, and arcseconds components or decimal degrees.
        
        Parameters
        ----------
        degrees : float, str
            If a string, accepts values in these formats:
                * [+|-]DD:MM:SS.sss (string), e.g. +12:52:32.423 or -12:52:32.423
                * DD.dddd (float, string), e.g. 12.542326
                * DD MM SS.sss (string, array), e.g. +12 52 32.423
            Whitespace may be spaces and/or tabs.
        outputDMS : bool
            If True, returns a tuple of (degree, arcminute, arcsecond)
    
        Returns degrees in decimal form unless the keyword "outputDMS" is True, in which
        case returns a tuple: (d, m, s).
        
    """
    
    # either a string or a float
    x = degrees
    
    if isinstance(x, float) or isinstance(x, int):
        parsedDegrees = x
        parsedDMS = degreesToDMS(parsedDegrees)
    
    elif isinstance(x, str):
        x = x.strip()
        
        try:
            parsedDegrees = float(x)
            parsedDMS = degreesToDMS(parsedDegrees)
        except ValueError:
        
            string_parsed = False
            div = '[:|/|\t|\-|\sDdMmSs]{1,2}' # accept these as (one or more repeated) delimiters: :, whitespace, /

            # First look for a pattern where d,m,s is specified
            pattr = '^([+-]{0,1}\d{1,3})' + div + '(\d{1,2})' + div + '(\d{1,2}[\.0-9]+)' + '[Ss]{0,1}' + '$'
    
            try:
                elems = re.search(pattr, x).groups()
                string_parsed = True
            except:
                pass # try again below
                #raise ValueError("convert.parseDegrees: Invalid input string! ('{0}')".format(x))
            
            if string_parsed:
                parsedDMS = (int(elems[0]), int(elems[1]), float(elems[2]))
                parsedDegrees = dmsToDegrees(int(elems[0]), int(elems[1]), float(elems[2]))

            else:

				# look for a pattern where only d,m is specified
				pattr = '^([+-]{0,1}\d{1,3})' + div + '(\d{1,2})' + '[Mm]{0,1}' + '$'
				
				try:
					elems = re.search(pattr, x).groups()
					string_parsed = True
				except:
					raise ValueError("convert.parseDegrees: Invalid input string! ('{0}')".format(x))
	
				parsedDMS = (int(elems[0]), int(elems[1]), 0.0)
				parsedDegrees = dmsToDegrees(int(elems[0]), int(elems[1]), 0.0)

    elif isinstance(x, g.Angle):
        parsedDegrees = x.degrees
        parsedDMS = degreesToDMS(parsedDegrees)
        
    elif isinstance(x, tuple):
        parsedDegrees = dmsToDegrees(*x)
        parsedDMS = x
        
    else:
        raise ValueError("convert.parseDegrees: could not parse value of {0}.".format(type(x)))
    
    if outputDMS:
        return parsedDMS
    else:
        return parsedDegrees


def degreesToDMS(d):
    """ Convert any parseable degree value (see: parseDegrees) into a 
        degree,arcminute,arcsecond tuple 
    """    
    sign = math.copysign(1.0, d)
        
    (df, d) = math.modf(abs(d)) # (degree fraction, degree)
    (mf, m) = math.modf(df * 60.) # (minute fraction, minute)
    s = mf * 60.
    
    _checkMinuteRange(m)
    _checkSecondRange(s)

    return (int(sign * d), int(m), s)

def degreesToDecimal(d):
    """ Convert any parseable degrees value (see: parseDegrees) into a float value """
    return parseDegrees(d, outputDMS=False)

def dmsToDegrees(d, m, s):
    """ Convert degrees, arcminute, arcsecond to a float degrees value. """

    # determine sign
    sign = math.copysign(1.0, d)

    try:
        d = int(abs(d))
        m = int(abs(m))
        s = float(abs(s))
    except ValueError:
        raise ValueError("convert.dmsToDegrees: dms values ({0[0]},{0[1]},{0[2]}) could not be converted to numbers.".format(d,m,s))

    return sign * (d + m/60. + s/3600.)

def dmsToHours(d, m, s):
    """ Convert degrees, arcminutes, arcseconds to a flout hour value """
    return dmsToDegrees(d, m, s) / 15.

def dmsToRadians(d, m, s):
    """ Convert degrees, arcminute, arcsecond to a float radians value. """
    return math.radians(dmsToDegrees(d, m, s))
    
def dmsToHMS(d, m, s):
    """ Convert degrees, arcminutes, arcseconds to an hour, minute, second tuple """
    return hoursToHMS(dmsToHours(d, m, s))

def degreesToRadians(d):
    """ Convert an angle in Degrees to Radians """
    return math.radians(d)

def degreesToString(d, precision=5, pad=False, sep=":"):
    """ Takes a decimal hour value and returns a string formatted as dms with separator
        specified by the 'sep' parameter. 
    """
    if pad:
        dPad = ":02"
    else:
        dPad = ""
        
    if len(sep) == 1 or len(sep) == 0:
        literal = "{0[0]" + dPad + "}" + str(sep) + "{0[1]:02d}" + str(sep) + "{0[2]:0" + str(precision+3) + "." + str(precision) + "f}"
    elif len(sep) == 2:
        literal = "{0[0]" + dPad + "}"+ str(sep[0]) + "{0[1]:02d}" + str(sep[1]) + "{0[2]:0" + str(precision+3) + "." + str(precision) + "f}"
    elif len(sep) == 3:
        literal = "{0[0]" + dPad + "}"+ str(sep[0]) + "{0[1]:02d}" + str(sep[1]) + "{0[2]:0" + str(precision+3) + "." + str(precision) + "f}" + str(sep[2])
    else:
        raise ValueError("Invalid separator specification for converting angle to string.")
        
    return literal.format(degreesToDMS(d))

# RADIANS
def parseRadians(radians):
    """ Parses an input "radians" value into a float number.
        
        Convert radians given in any parseable format (float or Angle) into float radians.
        
        ..Note::
            This function is mostly for consistency with the other "parse" functions, like
            parseHours and parseDegrees. 
        
        Parameters
        ----------
        radians : float, int, Angle
            The input angle.
    """
    x = radians
    
    if isinstance(x, float) or isinstance(x, int):
        return float(x)
    
    elif isinstance(x, g.Angle):
        return x.radians
    
    else:
        raise ValueError("convert.parseRadians: could not parse value of type {0}.".format(type(x).__name__))

def radiansToDegrees(r):
    """ Convert an angle in Radians to Degrees """
    try:
        r = float(r)
    except ValueError:
        raise ValueError("convert.radiansToHours: degree value ({0[0]}) could not be converted to a float.".format(r))
    return math.degrees(r)

def radiansToHours(r):
    """ Convert an angle in Radians to Hours """
    return radiansToDegrees(r) / 15.

def radiansToHMS(r):
    """ Convert an angle in Radians to an hour,minute,second tuple """
    hours = radiansToHours(r)
    return hoursToHMS(hours)
 
def radiansToDMS(r):
    """ Convert an angle in Radians to an degree,arcminute,arcsecond tuple """
    degrees = math.degrees(r)
    return degreesToDMS(degrees)  

# Combinations
def parseRADecString(radec, ra_units="hours", dec_units="degrees"):
    """ Parses a string representing both an RA and Dec, for 
        example a Jstring such as J141213.23+161252.12 or
        03:14:15.9 +26:37:10.11
        
        Parameters
        ----------
        radec : str
            The string representing an RA and Dec
    
    """
    
    div = '[:/\t\shdms°\'\"]{0,2}' # accept these as (one or more repeated) delimiters: :, whitespace, /
    ra_pattr = '^[J]{0,1}([+-]{0,1}\d{1,2})' + div + '(\d{1,2})' + div + '(\d{1,2}[\.0-9]+)' + div
    dec_pattr = '([+-]{0,1}\d{1,3})' + div + '(\d{1,2})' + div + '(\d{1,2}[\.0-9]+)' + div + '$'
    pattr = ra_pattr + "[\s|_]*" + dec_pattr
    try:
        elems = re.search(pattr, radec).groups()
    except:
        raise ValueError("parseRADecString: Invalid input string! ('{0}')".format(radec))

    ra = g.RA(hmsToHours(*map(float,elems[:3])), units=ra_units)
    dec = g.Dec(dmsToDegrees(*map(float,elems[3:])), units=dec_units)
    
    return (ra,dec)
    
# Time Conversions:
def datetimeToDecimalTime(datetimeObj=None):
    """ Converts a Python datetime.datetime object into a decimal hour """
    if datetimeObj == None:
        datetimeObj = datetime.datetime.now()
    return hmsToHours(datetimeObj.hour, datetimeObj.minute, datetimeObj.second + datetimeObj.microsecond/1.E6)

def hmsToStringTime(h, m, s, precision=5, sep=":", pad=True):
    """ Convert a sexagesimal time to a formatted string.
        
        Parameters
        ----------
    	hour : int, float
    	min : int, float
    	sec : int, float
    	precision : int
    	    This controls how many decimal places to display in Seconds.
    	sep : str, tuple, list
    	    This specifies what separator to place between the hour, 
            minute, and seconds. e.g. sep=':' means a string like "13:27:15.1412". You can also specify 
            a string, tuple, or list of length 2 or 3 to control each separator. For length 2, e.g.
            sep=':-', this means a string like "13:27-15.1412". For length 3, e.g. ("h","m","s"), this
            means a string like "13h27m15.1412s".
    	pad : bool
    	    Specify whether to pad value with spaces or zeros so values line up
    
    """
    if h >= 0:
        sign = ""
    else:
        sign = "-"
        
    formString = "%s%02d:%02d:%0" + str(precision+3) + "." + str(precision) + "f"
    return formString % (sign, abs(h), abs(m), abs(s))

def decimalToStringTime(decim, precision=5, sep=":", pad=True):
    """ Convert a decimal time or coordinate to a formatted string.
    
        Parameters
        ----------
    	decim : int, float
    	    The decimal time value to convert.
    	precision : int
    	    This controls how many decimal places to display in Seconds.
    	sep : str, tuple, list
    	    This specifies what separator to place between the hour, 
            minute, and seconds. e.g. sep=':' means a string like "13:27:15.1412". You can also specify 
            a string, tuple, or list of length 2 or 3 to control each separator. For length 2, e.g.
            sep=':-', this means a string like "13:27-15.1412". For length 3, e.g. ("h","m","s"), this
            means a string like "13h27m15.1412s".
    	pad : bool
    	    Specify whether to pad value with spaces or zeros so values line up
    
    """

    return hmsToStringTime(*hoursToHMS(decim), precision=precision, sep=sep, pad=pad)

# JD / MJD conversions
def ymdToJD(year, month, day):
    """ Converts a year, month, and day to a Julian Date.
    
        This function uses an algorithm from the book "Practical Astronomy with your 
        Calculator" by Peter Duffet-Smith (Page 7)
    
        Parameters
        ----------
        year : int
            A Gregorian year
        month : int
            A Gregorian month
        day : int
            A Gregorian day
    
    """
    if month == 1 or month == 2:
        yprime = year - 1
        mprime = month + 12
    else:
        yprime = year
        mprime = month
    
    if year > 1582 or (year == 1582 and (month >= 10 and day >= 15)):
        A = int(yprime / 100)
        B = 2 - A + int(A/4.0)
    else:
        B = 0   
        
    if yprime < 0:
        C = int((365.25 * yprime) - 0.75)
    else:
        C = int(365.25 * yprime)
    
    D = int(30.6001 * (mprime + 1))
    
    return B + C + D + day + 1720994.5

def ymdToMJD(year, month, day):
    """ Converts a year, month, and day to a Modified Julian Date.
    
        This function uses an algorithm from the book "Practical Astronomy with your 
        Calculator" by Peter Duffet-Smith (Page 7)
        
        Parameters
        ----------
        year : int
            A Gregorian year
        month : int
            A Gregorian month
        day : int
            A Gregorian day
    
    """
    return jdToMJD(ymdToJD(year, month, day))

def mjdToJD(mjd):
    """ Converts a Modified Julian Date to Julian Date
        
        Parameters
        ----------
        mjd : float, int
            A Modified Julian Date
    
    """
    return mjd + 2400000.5

def jdToMJD(jd):
    """ Converts a Julian Date to a Modified Julian Date

        Parameters
        ----------
        jd : float, int
            A Julian Date
    
    """
    return float(jd - 2400000.5)

def jdToDatetime(fracJD, timezone=gmt):
    """ Converts a Julian Date to a Python datetime object. The resulting time is in UTC, unless a
        time zone is supplied.
    
        This function uses an algorithm from the book "Practical Astronomy with your Calculator" 
        by Peter Duffet-Smith (Page 8)
        
        Parameters
        ----------
        jd : float, int
            A Julian Date
        timezone : int, datetime.tzinfo
            An integer representing the timezone to convert to in hours offset
            from Greenwich Mean Time. Also accepts a datetime.tzinfo object. If no timezone is specified, it assumes
            GMT time.
    
    """
    
    if isinstance(timezone, int) or isinstance(timezone, float):
        class TZ(py_datetime.tzinfo):
            def utcoffset(self, dt):
                return py_datetime.timedelta(hours=int(timezone))
            def tzname(self,dt): 
                return "GMT {0}".format(int(tz)) 
            def dst(self,dt): 
                return py_datetime.timedelta(0)
        tz = TZ()
    elif isinstance(timezone, py_datetime.tzinfo):
        tz = timezone
    else:
        raise ValueError("You entered an invalid 'timezone': {0}".format(timezone))
    
    jdTmp = fracJD + 0.5
    I = int(jdTmp)
    F = jdTmp - I
    if I > 2299160:
        A = int((I - 1867216.25)/36524.25)
        B = I + 1 + A - int(A/4)
    else:
        B = I
    
    C = B+1524
    D = int((C-122.1)/365.25)
    E = int(365.25*D)
    G = int((C-E)/30.6001)
    
    d = C - E + F - int(30.6001*G)
    
    if G < 13.5:
        m = G - 1
    else:
        m = G - 13
    
    if m > 2.5:
        y = D - 4716
    else:
        y = D - 4715
    
    year = int(y)
    month = int(m)
    day = int(d)
    hour, min, sec = hoursToHMS((d - int(d)) * 24.)
    sf, s = math.modf(sec)
    ms = sf*1.E6
    
    dtObj = astrodatetime(year, month, day, int(hour), int(min), int(sec), int(ms), tzinfo=gmt)
    return dtObj.astimezone(tz)
    
def mjdToDatetime(mjd, timezone=gmt):
    """ Converts a Modified Julian Date to a Python datetime object. 
    
        The resulting time is in UTC, unless a time zone is supplied.
        This function uses an algorithm from the book "Practical Astronomy with your Calculator" 
        by Peter Duffet-Smith (Page 8)
        
        Parameters
        ----------
        mjd : float, int
            A Modified Julian Date
        timezone : int, datetime.tzinfo
            An integer representing the timezone to convert to in hours offset
            from Greenwich Mean Time. Also accepts a datetime.tzinfo object. If no timezone is specified, it assumes
            GMT time.
    """
    jd = mjdToJD(mjd)
    return jdToDatetime(jd, timezone=timezone)

def datetimeToJD(datetimeObj, timezone=None):
    """ Converts a Python datetime object to a float Julian Date (JD).
    
        The JD is calculated using an algorithm from the book "Practical Astronomy with your 
        Calculator" by Peter Duffet-Smith (Page 7)
        
        Parameters
        ----------
        datetimeObj : datetime.datetime
            A Python datetime.datetime object
        timezone : int, `datetime.tzinfo`
            Either an integer specifying the offset from UTC of
            the datetime object, or a `tzinfo` object.
    
    """

    if datetimeObj.utcoffset() == None and timezone == None:
        raise ValueError("Either the input datetime object must know it's timezone (see: datetime.tzinfo), or you must supply a timezone!")
    elif datetimeObj.utcoffset() == None and timezone != None:
        if isinstance(timezone, int):
            class TZ(py_datetime.tzinfo):
                def utcoffset(self, dt):
                    return py_datetime.timedelta(hours=int(timezone))
                def tzname(self,dt): 
                    return "GMT {0}".format(int(tz)) 
                def dst(self,dt): 
                    return py_datetime.timedelta(0)
            tz = TZ()
            datetimeObj = datetimeObj.replace(tzinfo=tz)
            
        elif isinstance(timezone, py_datetime.tzinfo):
            datetimeObj = datetimeObj.replace(tzinfo=timezone)
        else:
            raise ValueError("Invalid timezone! You entered: {0}".format(timezone))
        
    utcDatetime = datetimeObj.astimezone(gmt)
    
    A = ymdToJD(utcDatetime.year, utcDatetime.month, utcDatetime.day)
    B = datetimeToDecimalTime(utcDatetime.time()) / 24.0
    return A + B

def datetimeToMJD(datetimeObj, timezone=None):
    """ Converts a Python datetime object to a float Modified Julian Date (MJD).
    
        The MJD is calculated using an algorithm from the book "Practical Astronomy with your 
        Calculator" by Peter Duffet-Smith (Page 7)
        
        Parameters
        ----------
        datetimeObj : datetime.datetime
            A Python datetime.datetime object
        timezone : int, `datetime.tzinfo`
            Either an integer specifying the offset from UTC of
            the datetime object, or a `tzinfo` object.
        
    """
    jd = datetimeToJD(datetimeObj, timezone=timezone)
    return jdToMJD(jd)

# UTC / GMST / LST
def datetimeToGMST(datetimeObj, timezone=None):
    """ Converts a datetime object to Greenwich Mean Sidereal Time.
    
        Either the datetime object (datetimeObj) must contain timezone information, or the
        timezone parameter must be specified.
        
        This function uses an algorithm from the book "Practical Astronomy with your 
        Calculator" by Peter Duffet-Smith (Page 17)
        
        Parameters
        ----------
        datetimeObj : `datetime.datetime`
            A Python datetime.datetime object representing
            a time in UTC
        timezone : int, `datetime.tzinfo`
            Either an integer specifying the offset from UTC of
            the datetime object, or a \c tzinfo object.
    
    """
    
    jd = datetimeToJD(datetimeObj, timezone=timezone)
    
    # algorithm described on USNO web site http://aa.usno.navy.mil/faq/docs/GAST.php
    jd0 = np.round(jd-.5)+.5
    h = (jd - jd0) * 24.0
    d = jd - 2451545.0
    d0 = jd0 - 2451545.0
    t = d/36525
    
    #mean sidereal time @ greenwich
    gmst = 6.697374558 + 0.06570982441908*d0 + 0.000026*t**2 + 1.00273790935*h
    #- 1.72e-9*t**3 #left off as precision to t^3 is unneeded
    
    eps =  np.radians(23.4393 - 0.0000004*d) #obliquity
    L = np.radians(280.47 + 0.98565*d) #mean longitude of the sun
    omega = np.radians(125.04 - 0.052954*d) #longitude of ascending node of moon
    dpsi = -0.000319*np.sin(omega) - 0.000024*np.sin(2*L) #nutation longitude
    return (gmst + dpsi*np.cos(eps)) % 24.0

def gmstToDatetime(datetimeObj, timezone=None):
    """ Converts a datetime object representing a Greenwich Mean Sidereal Time 
        to UTC time. 
    
        This function uses an algorithm from the book "Practical Astronomy with your Calculator" 
        by Peter Duffet-Smith (Page 18)
        
        Parameters
        ----------
        datetimeObj : datetime.datetime
            A Python datetime.datetime object representing
            a time in GMST
    
    """
    jd = datetimeToJD(datetimeObj, timezone=timezone)
    
    S = jd - 2451545.0
    T = S / 36525.0
    T0 = 6.697374558 + (2400.051336*T) + (0.000025862*T**2)
    T0 = T0 % 24
    
    GST = (datetimeToDecimalTime(datetimeObj.time()) - T0) % 24
    UT = GST * 0.9972695663
    
    h,m,s = hoursToHMS(UT)
    sf, s = math.modf(s)
    ms = sf*1.E6
    
    if isinstance(timezone, int):
        tz = intTimezoneToTzinfo(timezone)
    else:
        tz = timezone
    return astrodatetime(year=datetimeObj.year, month=datetimeObj.month, day=datetimeObj.day, hour=h, minute=m, second=int(s), microsecond=int(ms), tzinfo=gmt).astimezone(tz)

def sphericalAnglesToCartesian(a, b, units="radians"):
    """ Converts two angles on the surface of a (unit) sphere into Cartesian 
        coordinates
        
        This can be used as an intermediary step with RA,Dec to use a rotation
        matrix to convert to Galactic, for instance.
        
        Parameters
        ----------
        a : `Angle`, `numpy.array`
        b : `Angle`, `numpy.array`
        units : str, {'radians', 'degrees', 'hours'}
        
        Notes
        -----
        If an Array, the data can either be an array of Angle objects or an array
        of RADIAN values.
        
    """
    
    if isinstance(a, list) or isinstance(b, list):
        a = np.array(a)
        b = np.array(b)
    
    if isinstance(a, np.ndarray):
        if not isinstance(a[0], g.Angle) or not isinstance(b[0], g.Angle):
            a = np.array([g.Angle(x, units=units) for x in a])
            b = np.array([g.Angle(x, units=units) for x in b])
            
        ar = np.array([x.radians for x in a])
        br = np.array([x.radians for x in b])
        #resultVector = np.zeros((3,len(ar)), dtype=float)
    else:
        if not isinstance(a, g.Angle) or not isinstance(b, g.Angle):
            a = g.Angle(a, units=units)
            b = g.Angle(b, units=units)
            
        ar = a.radians
        br = b.radians
        #resultVector = np.zeros(3, dtype=float)
    
    #resultVector[0] = np.cos(ar) * np.cos(br)
    #resultVector[1] = np.sin(ar) * np.cos(br)
    #resultVector[2] = np.sin(br)
    
    resultVector = []
    resultVector.append(np.cos(ar) * np.cos(br))
    resultVector.append(np.sin(ar) * np.cos(br))
    resultVector.append(np.sin(br))
    
    return tuple(resultVector)

def cartesianToSphericalAngles(x, y, z):
    """ Converts Cartesian coordinates into two angles on the surface of a 
        (unit) sphere
        
        This can be used as an intermediary step with RA,Dec to use a rotation
        matrix to convert to Galactic, for instance.
        
        Parameters
        ----------
        x : float, `numpy.array`
        y : float, `numpy.array`
        z : float, `numpy.array`
        
        Returns an array of Angle objects
        
    """
    """
    double x, y, z, r;
 
    x = v[0];
    y = v[1];
    z = v[2];
    r = sqrt ( x * x + y * y );
 
    *a = ( r != 0.0 ) ? atan2 ( y, x ) : 0.0;
    *b = ( z != 0.0 ) ? atan2 ( z, r ) : 0.0;
    """
    
    r = np.sqrt(x**2 + y**2)
    a = np.arctan2(y, x)
    b = np.arctan2(z, r)
    
    return (g.Angle.fromRadians(a), g.Angle.fromRadians(b))

def j2000ToGalactic(ra, dec):
    """ Takes an ra,dec and converts it to Galactic coordinates
        
        ra must be an RA object or an Angle object, and dec must
        be a Dec object or an Angle object
        
        Parameters
        ----------
        ra : `RA`, `Angle`
        dec : `Dec`, `Angle`
        
    """
    xyz = np.array(sphericalAnglesToCartesian(ra, dec))
    rotMatrix = np.array([[-0.054875539, 0.494109454, -0.867666136],\
                          [-0.873437105, -0.444829594, -0.198076390],\
                          [-0.483834992, 0.746982249, 0.455983795]])
    
    newxyz = np.dot(xyz, rotMatrix)
    return cartesianToSphericalAngles(*newxyz)

# =====================================
# ANYTHING BELOW HERE CAN'T BE TRUSTED!
# =====================================


def gmstToLST(gmst, longitude, gmstUnits="hours", longitudeDirection="w", longitudeUnits="degrees", outputHMS=False):
    """ 
    \brief Converts Greenwich Mean Sidereal Time to Local Sidereal Time. 
    
    Defaults are Longitude WEST and units DEGREES, but these can be changed with the optional 
    parameters longitudeDirection and longitudeUnits.
    
    \param gmst (\c float, \c int, \c Angle, \c datetime.datetime, \c str)
        The Greenwich Mean Standard Time to be converted. This can me any of the units listed above, as it is
        ultimately passed to one of the 'parse' functions (depending on the units)
    \param longitude (\c float, \c int, \c Angle, \c str) The longitude of the site to calculate 
        the Local Sidereal Time. 
    \param gmstUnits (\c str) the units of the GMST value
    \param longitudeDirection (\c str) Default is longitude WEST, 'W', but you can specify EAST by passing 'E'.
    \param longitudeUnits (\c str) Default units are 'DEGREES', but this can be switched to radians by passing
        'RADIANS' in this parameter, or 'hours'
    \param outputHMS (\c boolean) If True, returns a tuple of (hour, minute, second)
    
    \return (\c float or \c tuple) The Local Sidereal Time at the given longitude in units HOURS.
    
    [APW: Fill in examples!]
    Examples:
        \li One
        \li Two
    
    """
    
    if gmstUnits.lower() == "degrees":
        parsedHour = parseDegrees(gmst) / 15.
    elif gmstUnits.lower() == "radians":
        parsedHour = radiansToHours(parseRadians(gmst))
    elif gmstUnits.lower() == "hours":
        parsedHour = parseHours(gmst)
    else:
        raise IllegalUnitsError("{0}".format(gmstUnits))
    
    if longitudeUnits.lower() == "degrees":
        longitudeHours = parseDegrees(longitude) / 15.
    elif longitudeUnits.lower() == "radians":
        longitudeHours = radiansToHours(parseRadians(longitude))
    elif longitudeUnits.lower() == "hours":
        longitudeHours = parseHours(longitude)
    else:
        raise IllegalUnitsError("{0}".format(longitudeUnits))
        
    if longitudeDirection.lower() == "w":
        lst = parsedHour - longitudeHours
    elif longitudeDirection.lower() == "e":
        lst = parsedHour + longitudeHours
    else:
        raise AssertionError("longitudeDirection must be W or E")
    
    lst = lst % 24.0
    
    if outputHMS:
        return hoursToHMS(lst)
    else:
        return lst



def gmstDatetimeToLSTDatetime(longitude, gmst, longitudeDirection='W', longitudeUnits='DEGREES'):
    """ 
    Converts Greenwich Mean Sidereal Time to Local Sidereal Time. 
    
    Parameters
    ----------
    longitude : float (any numeric type)
        The longitude of the site to calculate the Local Sidereal Time. Defaults are
        Longitude WEST and units DEGREES, but these can be changed with the optional 
        parameters lonDirection and lonUnits.
    gmst : datetime.datetime
        A Python datetime.datetime object representing the Greenwich Mean Sidereal Time
    lonDirection : string
        Default is longitude WEST, 'W', but you can specify EAST by passing 'E'.
    lonUnits : string
        Default units are 'DEGREES', but this can be switched to radians by passing
        'RADIANS' in this parameter.
    
    Returns
    -------
    lst : datetime.datetime
    
    """
    hours = datetimeToDecimalTime(gmst)
    
    if longitudeUnits.upper() == 'DEGREES':
        longitudeTime = longitude / 15.0
    elif longitudeUnits.upper() == 'RADIANS':
        longitudeTime = longitude * 180.0 / math.pi / 15.0
    
    if longitudeDirection.upper() == 'W':
        lst = hours - longitudeTime
    elif longitudeDirection.upper() == 'E':
        lst = hours + longitudeTime
    else:
        raise AssertionError('longitudeDirection must be W or E')
    
    lst = lst % 24.0
    h,m,s = hoursToHMS(lst)
    
    return astrodatetime.combine(gmst.date(), datetime.time(h,m,int(s)))
    
def lstToGMST(longitude, hour, minute=None, second=None, longitudeDirection='W', longitudeUnits='DEGREES'):
    """ 
    Converts Local Sidereal Time to Greenwich Mean Sidereal Time.
    
    Parameters
    ----------
    longitude : float (any numeric type)
        The longitude of the site to calculate the Local Sidereal Time. Defaults are
        Longitude WEST and units DEGREES, but these can be changed with the optional 
        parameters lonDirection and lonUnits.
    hour : int (or float)
        If an integer, the function will expect a minute and second. If a float, it
        will ignore minute and second and convert from decimal hours to hh:mm:ss.
    minute : int
        Ignored if hour is a float.
    second : int (any numeric type, to include microseconds)
        Ignored if hour is a float.
    longitudeDirection : string
        Default is longitude WEST, 'W', but you can specify EAST by passing 'E'.
    longitudeUnits : string
        Default units are 'DEGREES', but this can be switched to radians by passing
        'RADIANS' in this parameter.
    
    Returns
    -------
    hour : int
        The hour of the calculated GMST
    minute : int
        The minutes of the calculated GMST
    second: float
        The seconds of the calculated GMST
    
    Examples
    --------
	- to do
	    
    """
    if minute != None and second != None:
        hours = hmsToHours(hour, minute, second)
    elif minute == None and second == None:
        hours = hour
    else:
        raise AssertionError('minute and second must either be both set, or both unset.')
    
    if longitudeUnits.upper() == 'DEGREES':
        longitudeTime = longitude / 15.0
    elif longitudeUnits.upper() == 'RADIANS':
        longitudeTime = longitude * 180.0 / math.pi / 15.0
    
    if longitudeDirection.upper() == 'W':
        gmst = hours + longitudeTime
    elif longitudeDirection.upper() == 'E':
        gmst = hours - longitudeTime
    else:
        raise AssertionError('longitudeDirection must be W or E')
    
    gmst = gmst % 24.0
    
    return hoursToHMS(gmst)

##################################################################
# Coordinate Transformations:
#
def raLSTToHa(ra, hour, minute=None, second=None, raUnits='HOURS'):
    """ 
    Converts a Right Ascension to an Hour Angle, given the Local Sidereal Time.
    
    Parameters
    ----------
    ra : float (any numeric type)
        A right ascension. Default units are HOURS, but can be changed to DEGREES
    hour : int (or float)
        If an integer, the function will expect a minute and second. If a float, it
        will ignore minute and second and convert from decimal hours to hh:mm:ss.
    minute : int
        Ignored if hour is a float.
    second : int (any numeric type, to include microseconds)
        Ignored if hour is a float.
    raUnits : string
        Can be either HOURS or DEGREES, defaults to HOURS.
    
    Returns
    -------
    hour : int
        The hour of the calculated HA
    minute : int
        The minutes of the calculated HA
    second: float
        The seconds of the calculated HA
    
    Examples
    --------
	- to do
    
    """
    if minute != None and second != None:
        hours = hmsToHours(hour, minute, second)
    elif minute == None and second == None:
        hours = hour
    else:
        raise AssertionError('minute and second must either be both set, or both unset.')
    
    if raUnits.upper() == 'HOURS':
        HA = hours - ra
    elif raUnits.upper() == 'DEGREES':
        HA = hours - ra/15.0
    else:
        raise AssertionError('raUnits must be either HOURS or DEGREES')
    
    return HA

def haLST2ra():
    pass

def raUTC2ha():
    pass

def haUTC2ra():
    pass

def ra2transitTime():
    pass
    
def raDec2AltAz(ra, dec, latitude, longitude, datetimeObj, longitudeDirection='W'):
    """ 
    Converts an RA and Dec to Alt Az for a given datetime object.
    
    Parameters
    ----------
    ra : float (any numeric type)
        A Right Ascension, default units DEGREES
    dec : float (any numeric type)
        A Declination, default units DEGREES
    latitude : float (any numeric type)
        A latitude in DEGREES
    longitide : float (any numeric type)
        A longitude in DEGREES
    datetimeObj : datetime.datetime
        A Python datetime.datetime object
    longitudeDirection : string
        Default is longitude WEST, 'W', but you can specify EAST by passing 'E'.
        
    Returns
    -------
    alt : float
        Altitude, default units DEGREES
    az : float
        Azimuth, default units DEGREES
    
    """ 
    gmst = utcDatetimeToGMST(datetimeObj)
    h,m,s = gmstToLST(longitude, gmst.hour, gmst.minute, gmst.second)
    lst = (h + m/60.0 + s/3600.0) * 15.0
    ha = lst - ra
    
    alt_rads = asin(sin(radians(dec))*sin(radians(latitude)) + \
        cos(radians(dec))*cos(radians(latitude))*cos(radians(ha)))
    
    cos_az = (sin(radians(dec)) - sin(alt_rads)*sin(radians(latitude))) / \
        (cos(alt_rads) * cos(radians(latitude)))
        
    alt = degrees(alt_rads)
    az = degrees(acos(cos_az))
        
    if sin(radians(ha)) < 0:
        return alt, az
    else:
        return alt, (360.0 - az)
    
def altAz2RaDec():
    pass

def eclipticLatLon2RADec(lat, lon, latLonUnits='DEGREES', raDecUnits='DEGREES'):
    """ 
    Converts an Ecliptic Latitude and Ecliptic Longitude to a Right Ascension and 
    Declination.
    
    Parameters
    ----------
    lat : float (any numeric type)
        An ecliptic latitude, default units DEGREES
    long : float (any numeric type)
        An ecliptic longitude, default units DEGREES    
    latLonUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
    raDecUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
        
    Returns
    -------
    ra : float
        A right ascension, default units DEGREES
    dec : float
        A declination, default units DEGREES
        
    Examples
    --------
    >>> eclipticLatLon2RADec(70.3425, -11.4552)
    (143.72252629028003, 19.535734683739964)
    
    """ 
    if latLonUnits.upper() == 'HOURS':
        lambdaa = lat * 15.0
        beta = lon * 15.0
    elif latLonUnits.upper() == 'DEGREES':
        lambdaa = lat
        beta = lon
    else:
        raise AssertionError('latLonUnits must be either HOURS or DEGREES')
    
    # Python works in Radians...
    lambdaaRad = lambdaa * math.pi / 180.0
    betaRad = beta * math.pi / 180.0
    eeRad = ee * math.pi / 180.0
    
    deltaRad = math.asin(math.sin(betaRad)*math.cos(eeRad) + math.cos(betaRad)*math.sin(eeRad)*math.sin(lambdaaRad))
    
    y = math.sin(lambdaaRad)*math.cos(eeRad) - math.tan(betaRad)*math.sin(eeRad)
    x = math.cos(lambdaaRad)
    
    alphaPrime = math.atan(y/x) * 180.0 / math.pi
    
    if y > 0 and x > 0:
        alpha = alphaPrime % 90.0
    elif y > 0 and x < 0:
        alpha = (alphaPrime % 90.0) + 90.0
    elif y < 0 and x < 0:
        alpha = (alphaPrime % 90.0) + 180.0
    elif y < 0 and x > 0:
        alpha = (alphaPrime % 90.0) + 270.0
    else:
        alpha = alphaPrime
        
    if raDecUnits.upper() == 'HOURS':
        ra = alpha / 15.0
        dec = deltaRad * 180.0 / math.pi / 15.0
    elif raDecUnits.upper() == 'DEGREES':
        ra = alpha
        dec = deltaRad * 180.0 / math.pi
    else:
        raise AssertionError('raDecUnits must be either HOURS or DEGREES')
    
    return ra, dec

def raDec2EclipticLatLon(ra, dec, latLonUnits='DEGREES', raDecUnits='DEGREES'):
    """ 
    Converts a Right Ascension and Declination to an Ecliptic Latitude and 
    Ecliptic Longitude.
    
    Parameters
    ----------
    ra : float (any numeric type)
        A right ascension, default units DEGREES
    dec : float (any numeric type)
        A declination, default units DEGREES    
    latLonUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
    raDecUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
        
    Returns
    -------
    lat : float
        An ecliptic latitude, default units DEGREES
    lon : float
        An ecliptic longitude, default units DEGREES
    
    
    """
    if raDecUnits.upper() == 'HOURS':
        ra = ra * 15.0
        dec = dec * 15.0
    elif raDecUnits.upper() == 'DEGREES':
        ra = ra
        dec = dec
    else:
        raise AssertionError('raDecUnits must be either HOURS or DEGREES')
    
    # Python works in Radians...
    raRad = ra * math.pi / 180.0
    decRad = dec * math.pi / 180.0
    eeRad = ee * math.pi / 180.0
    
    betaRad = math.asin(math.sin(decRad)*math.cos(eeRad) - math.cos(decRad)*math.sin(eeRad)*math.sin(raRad))
    
    y = math.sin(raRad)*math.cos(eeRad) + math.tan(decRad)*math.sin(eeRad)
    x = math.cos(raRad)
    
    lambdaPrime = math.atan(y/x) * 180.0 / math.pi
    
    if y > 0 and x > 0:
        lambdaa = lambdaPrime % 90.0
    elif y > 0 and x < 0:
        lambdaa = (lambdaPrime % 90.0) + 90.0
    elif y < 0 and x < 0:
        lambdaa = (lambdaPrime % 90.0) + 180.0
    elif y < 0 and x > 0:
        lambdaa = (lambdaPrime % 90.0) + 270.0
    else:
        lambdaa = lambdaPrime
        
    if latLonUnits.upper() == 'HOURS':
        lat = lambdaa / 15.0
        lon = betaRad * 180.0 / math.pi * 15.0
    elif latLonUnits.upper() == 'DEGREES':
        lat = lambdaa
        lon = betaRad * 180.0 / math.pi
    else:
        raise AssertionError('latLonUnits must be either HOURS or DEGREES')
    
    return lat, lon

def raDecToGalactic(ra, dec, latLonUnits='DEGREES', raDecUnits='DEGREES'):
    """ 
    Converts a Right Ascension and Declination to an Galactic Latitude 
    and Longitude
    
    Parameters
    ----------
    ra : float (any numeric type)
        A right ascension, default units DEGREES
    dec : float (any numeric type)
        A declination, default units DEGREES    
    latLonUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
    raDecUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
        
    Returns
    -------
    b : float
        A Galactic latitude, default units DEGREES
    l : float
        An Galactic longitude, default units DEGREES
    
    """    
    if isinstance(ra, [].__class__) or isinstance(dec, [].__class__):
        ra = np.array(float(ra))
        dec = np.array(float(dec))
    elif isinstance(ra, np.array([]).__class__):
        ra = ra.astype(float)
        dec = dec.astype(float)
    else:
        ra = np.array([float(ra)])
        dec = np.array([float(dec)])

    if raDecUnits.lower() == 'degrees':
        ra = np.radians(ra)
        dec = np.radians(dec)

    raNGP = np.radians(192.85948)
    decNGP = np.radians(27.12825)
    lASCEND = np.radians(32.93192)
    
    gb = np.arcsin( np.cos(dec)*np.cos(decNGP)*np.cos(ra - raNGP) + np.sin(dec)*np.sin(decNGP) )
    gl = np.arctan2( np.sin(dec)*np.cos(decNGP) - np.cos(dec)*np.cos(ra - raNGP)*np.sin(decNGP),\
                     np.cos(dec)*np.sin(ra - raNGP) ) + lASCEND
    
    gl = np.degrees(gl)
    gb = np.degrees(gb)
    
    gl[gl < 0.] += 360.
    
    if len(gl) == 1:
        return gl[0], gb[0]
    
    return gl, gb
    
def galactic2RaDec(gl, gb, latLonUnits='DEGREES', raDecUnits='DEGREES'):
    """ 
    Converts a Galactic Latitude and Longitude to Right Ascension and Declination
    
    Parameters
    ----------
    gl : float (any numeric type)
        An Galactic longitude, default units DEGREES
    gb : float (any numeric type)
        A Galactic latitude, default units DEGREES
    latLonUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
    raDecUnits : string
        Can be either HOURS or DEGREES, defaults to DEGREES.
        
    Returns
    -------
    ra : float
        A right ascension, default units DEGREES
    dec : float
        A declination, default units DEGREES
    
    """
    
    if isinstance(gl, [].__class__) or isinstance(gb, [].__class__):
        gl = np.array(float(gl))
        gb = np.array(float(gb))
    elif isinstance(gl, np.array([]).__class__):
        gl = gl.astype(float)
        gb = gb.astype(float)
    else:
        gl = np.array([float(gl)])
        gb = np.array([float(gb)])
    
    if latLonUnits.lower() == 'degrees':
        gl = np.radians(gl)
        gb = np.radians(gb)
    
    raNGP = np.radians(192.85948)
    decNGP = np.radians(27.12825)
    lASCEND = np.radians(32.93192)
    
    dec = np.arcsin( np.cos(gb)*np.cos(decNGP)*np.sin(gl - lASCEND) + np.sin(gb)*np.sin(decNGP) )
    ra = np.arctan2( np.cos(gb)*np.cos(gl - lASCEND), \
                     np.sin(gb)*np.cos(decNGP) - np.cos(gb)*np.sin(gl - lASCEND)*np.sin(decNGP) ) + raNGP
    
    ra = np.degrees(ra)
    dec = np.degrees(dec)
    
    ra[ra > 360.] -= 360.
    
    if len(ra) == 1:
        return ra[0], dec[0]
    
    return ra, dec

if __name__ == '__main__':
    import unittest
    import sys
    
    a = g.Angle.fromDegrees(13.6146134)
    b = g.Angle.fromDegrees(63.1351344)
    
    print sphericalAnglesToCartesian(a, b)
    
    a = np.random.random(100)*180.
    b = np.random.random(100)*180.
    
    print sphericalAnglesToCartesian(a, b)
    
    a = np.array([g.Angle.fromDegrees(x) for x in np.random.random(100)*180.])
    b = np.array([g.Angle.fromDegrees(x) for x in np.random.random(100)*180.])
    
    print sphericalAnglesToCartesian(a, b)
    
    sys.exit(0)
    
    class TestCoordinateConversions(unittest.TestCase):
        def test_sphericalToCartesian(self):
            a = g.Angle.fromDegrees(13.6146134)
            b = g.Angle.fromDegrees(63.1351344)
            
            sphericalAnglesToCartesian(a, b)
    
    unittest.main()
    print "Test ran successfully!"
    sys.exit(0)
    
    class TestParseFunctions(unittest.TestCase):
        def test_parseHours(self):
            # "11:30:36.135789" = 11.010037719166666
            self.assertAlmostEqual(parseHours("11:30:36.135789"), 11.5100377191666, 12)
            self.assertAlmostEqual(parseHours(11.5100377191666), 11.5100377191666, 12)
            
            h,m,s = parseHours("11:30:36.135789", outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 12)
            
            h,m,s = parseHours(11.5100377191666, outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            h,m,s = parseHours("11 30 36.135789", outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            h,m,s = parseHours("113036.135789", outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            h,m,s = parseHours("11 30 36.135789", outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            h,m,s = parseHours("11h 30m 36.135789s", outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            h,m,s = parseHours("11h30m36.135789s", outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            h,m,s = parseHours("11-30-36.135789", outputHMS=True)
            self.assertEqual(h, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
        def test_parseDegrees(self):
            d,m,s = parseDegrees("11:30:36.135789", outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 12)
            
            d,m,s = parseDegrees(11.5100377191666, outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            d,m,s = parseDegrees("11 30 36.135789", outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            d,m,s = parseDegrees("113036.135789", outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            d,m,s = parseDegrees("11 30 36.135789", outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            d,m,s = parseDegrees("11d 30m 36.135789s", outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            d,m,s = parseDegrees("11d30m36.135789s", outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
            
            d,m,s = parseDegrees("11-30-36.135789", outputDMS=True)
            self.assertEqual(d, 11)
            self.assertEqual(m, 30)
            self.assertAlmostEqual(s, 36.135789, 5)
    
    unittest.main()
    print "Test ran successfully!"
    sys.exit(0)
    
    class TestConvertDateTime(unittest.TestCase):
        
        #def test_dec2sex(self):
        #    self.assertAlmostEqual(dec2sex(11.0000000), (11, 0, 0), 9)
        #    self.assertAlmostEqual(dec2sex(11.5000000), (11, 30, 0), 9)
        #    self.assertAlmostEqual(dec2sex(11.5100000), (11, 30, 36), 9)
        #    self.assertAlmostEqual(dec2sex(11.5101000, microsecond=True), (11, 30, 36, 360000), 9)
        #    self.assertAlmostEqual(dec2sex(11.51010001, microsecond=True), (11, 30, 36, 360036), 9)
        
        def test_sex2dec(self):
            self.assertEqual(sex2dec(11, 0, 0), 11.0)
            self.assertEqual(sex2dec(11, 30, 0), 11.5)
            self.assertEqual(sex2dec(11, 30, 36), 11.51)
            self.assertEqual(sex2dec(11, 30, 36, 360000), 11.5101)
            self.assertEqual(sex2dec(11, 30, 36, 360036), 11.51010001)
        
        def test_datetime2decimalTime(self):
            dt = py_datetime.datetime(2011, 7, 3, hour=11, minute=30, second=0, microsecond=0)
            self.assertEqual(datetimeToDecimalTime(dt), 11.5)
            
            dt = py_datetime.datetime(2011, 7, 3, hour=11, minute=30, second=36)
            self.assertEqual(datetimeToDecimalTime(dt), 11.51)
            
            dt = py_datetime.datetime(2011, 7, 3, hour=11, minute=30, second=36, microsecond=360000)
            self.assertEqual(datetimeToDecimalTime(dt), 11.5101)
            
            dt = py_datetime.datetime(2011, 7, 3, hour=11, minute=30, second=36, microsecond=360036)
            self.assertEqual(datetimeToDecimalTime(dt), 11.51010001)
        
        def test_jd2datetime(self):
            for jd in np.arange(2400018, 2500000, 0.5):
                print jd
                dt = jd2datetime(jd)
                print dt.year, dt.month, dt.day
        
        # Still need tests for:
        """
        ymd2jd 
        utcDatetime2gmst
        gmst2utcDatetime
        mjd2jd
        jd2mjd
        mjd2sdssjd
        jd2sdssjd
        sdssjd2mjd
        sdssjd2jd 
        jd2datetime
        mjd2datetime
        datetime2jd
        datetime2mjd
        gmst2lst
        gmstDatetime2lstDatetime
        lst2gmst
        datetime2decimalTime"""
    
    class TestConvertCoordinates(unittest.TestCase):
        def test_parseRA(self):
            for h,m,s in zip(np.random.random(1000),np.random.random(1000),np.random.random(1000)):
                self.assertEqual(parseRA("%02d:%02d:%05.2f" % (int(h*24.),int(m*59.3),s*59.3)), parseRA("%02d %02d %05.2f" % (int(h*24.),int(m*59.3),s*59.3)))
                self.assertEqual(parseRA("%02d:%02d:%05.2f" % (int(h*24.),int(m*59.3),s*59.3)), parseRA("%02d%02d%05.2f" % (int(h*24.),int(m*59.3),s*59.3)))
        
        def test_parseDec(self):
            for d,m,s in zip(np.random.random(1000),np.random.random(1000),np.random.random(1000)):
                if (d+m+s) > 1.5: pm = "+"
                else: pm = "-"
                self.assertEqual(parseDec("%s%d:%02d:%05.2f" % (pm, int(d*90.),int(m*59.3),s*59.3)), parseDec("%s%d %02d %05.2f" % (pm, int(d*90.),int(m*59.3),s*59.3)))
                self.assertEqual(parseDec("%s%02d:%02d:%05.2f" % (pm, int(d*90.),int(m*59.3),s*59.3)), parseDec("%s%d%02d%05.2f" % (pm, int(d*90.),int(m*59.3),s*59.3)))            
    
    unittest.main()