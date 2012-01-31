################################################################################
# astrodatetime.py - A subclass of the Python class 'datetime.datetime' to 
#                    include support for Modified Julian Date's and Julian Dates
#
"""
TODO: 
    - Should astrodatetime.lst() return an Angle object, a datetime object, or a number?
"""

__author__ = 'Adrian Price-Whelan <adrn@astro.columbia.edu>'

# Standard Library
#from datetime import datetime, tzinfo, timedelta
import datetime as py_datetime

class GMT0(py_datetime.tzinfo):
    """ \brief This is a tzinfo subclass that represents the timezone in Greenwich,
        or Greenwich Mean Time (GMT+0). 
        
        This is used internally.
    """
    def utcoffset(self, dt):
        return py_datetime.timedelta(hours=0)
    def tzname(self,dt): 
        return "GMT +0" 
    def dst(self,dt): 
        return py_datetime.timedelta(0)

gmt = GMT0()

class astrodatetime(py_datetime.datetime):
    """
        \brief astrodatetime is a subclass of Python's datetime.datetime() object that
        supports astronomical dates and times such as JD and MJD, as well as Local 
        Sidereal Time.
    """
    
    @property
    def mjd(self):
        """ Calculate the Modified Julian Date (MJD) using the datetime object """
        return convert.datetimeToMJD(self)
    
    @property
    def jd(self):
        """ Calculate the Julian Date (JD) using the datetime object """
        return convert.datetimeToJD(self)
    
    def lst(self, longitude, longitudeDirection="w", longitudeUnits="degrees", outputHMS=False):
        """ \brief Compute the Local Sidereal Time for the datetime object 
            given the a longitude.
            
            \param longitude (\c float, \c int, \c Angle, \c str) The longitude in the specified units.
            \param longitudeDirection (\c str) The direction from Greenwich that the longitude is measured in. 
                Can be "E" or "W" (east or west), but by default is WEST.
            \param longitudeUnits (\c str) Can be 'degrees', 'radians', or 'hours'
            \param outputHMS (\c boolean) If True, will print the LST as an HMS tuple (hr, min, sec).
        """
        
        try:
            utcSelf = self.astimezone(gmt)
        except ValueError:
            raise ValueError("In order to calculate the Local Sidereal Time, you must specify the timezone of the datetime object.\nYou must create a tzinfo() object, and do datetimeObject = datetimeObject.replace(tzinfo=someTimeZone)")
        
        gmst = convert.utcDatetimeToGMST(utcSelf)
        return convert.gmstToLST(convert.datetimeToDecimalTime(gmst), longitude, longitudeDirection=longitudeDirection, longitudeUnits=longitudeUnits, outputHMS=outputHMS)
    
    @staticmethod
    def fromMJD(mjd):
        """ Create an astrodatetime object from a Modified Julian Date (MJD) """
        dt = convert.mjdToDatetime(mjd)
        return astrodatetime.fromDatetime(dt.replace(tzinfo=gmt))
        
    @staticmethod
    def fromJD(jd, tz=None):
        """ Create an astrodatetime object from a Julian Date (JD) """
        dt = convert.jdToDatetime(jd)
        return astrodatetime.fromDatetime(dt.replace(tzinfo=gmt))
    
    @property
    def decimalTime(self):
        """ Return the decimal time in hours """
        return convert.datetimeToDecimalTime(self)
    
    @staticmethod
    def now(timezone=gmt):
        """ \brief Overwrite the built-in now() method to return an astrodatetime object instead. 
            
            \param timezone (\c int, \c datetime.tzinfo) An integer representing the timezone to convert to in hours offset
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
        
        now = py_datetime.datetime.now(tz)#.astimezone(gmt)
        return astrodatetime.fromDatetime(now)
    
    @staticmethod
    def fromDatetime(datetimeObj):
        """ Create an astrodatetime object from a Python datetime object"""
        return astrodatetime(datetimeObj.year, datetimeObj.month, datetimeObj.day, datetimeObj.hour, datetimeObj.minute, datetimeObj.second, datetimeObj.microsecond, tzinfo=datetimeObj.tzinfo)

# Have to put this here to deal with circular imports
import convert

if __name__ == "__main__":
    # Functional and unit tests
    import unittest, sys, math
    
    jd = 2455893.68753
    mjd = convert.jdToMJD(jd)
    y = 2011
    m = 11
    d = 28
    hr,min,seconds = convert.hoursToHMS(convert.parseHours("04:30:02.6"))
    sf, sec = math.modf(seconds)

    class TestAstrodatetime(unittest.TestCase):
        def test_jd(self):
            dt = astrodatetime.fromJD(jd)
            self.assertEqual(y, dt.year)
            self.assertEqual(m, dt.month)
            self.assertEqual(d, dt.day)
            self.assertEqual(hr, dt.hour)
            self.assertEqual(min, dt.minute)
            self.assertEqual(sec, dt.second)
            self.assertAlmostEqual(sf, dt.microsecond/1.E6, 1)
        
        def test_mjd(self):
            dt = astrodatetime.fromMJD(mjd)
            self.assertEqual(y, dt.year)
            self.assertEqual(m, dt.month)
            self.assertEqual(d, dt.day)
            self.assertEqual(hr, dt.hour)
            self.assertEqual(min, dt.minute)
            self.assertEqual(sec, dt.second)
            self.assertAlmostEqual(sf, dt.microsecond/1.E6, 1)
        
        def test_lst(self):
            dt = astrodatetime.fromJD(2455893.66045)
            self.assertAlmostEqual(dt.lst(172.235, longitudeDirection="e"), convert.hmsToHours(19,46,48.8), 5)
        
    unittest.main()