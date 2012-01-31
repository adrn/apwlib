#!/usr/bin/env python

"""
This example demonstrates some of the functionality of astrodatetime, a subclass of the built-in
Python datetime.datetime() object. For documentation on Python's datetime object, see:
    http://docs.python.org/library/datetime.html
"""

import os, sys
sys.path.append(os.path.join(sys.path[0], ".."))

from datetime import datetime
from apwlib.astrodatetime import astrodatetime

# Ways to use astrodatetime objects:
# ----------------------------------
dt = astrodatetime.now(timezone=-5)
print "Current Date: {0}".format(dt.strftime("%Y-%m-%d, %H:%M"))
print "Current MJD: {0:0.5f}".format(dt.mjd)
print "Current JD: {0:0.5f}".format(dt.jd)
print "Current Local Sidereal Time in New York (Longitude 73:58:00 W): {0}".\
    format(dt.lst("73:58:00", longitudeDirection="W", longitudeUnits="degrees"))
print "Get the decimal hour from an astrodatetime object: {0:0.5f}".format(dt.decimalTime)
print 

# Ways to create astrodatetime objects:
# -------------------------------------
dt = astrodatetime.now()
print "Create an object using the now() method: {0}".format(dt.strftime("%Y-%m-%d, %H:%M"))

dt = astrodatetime.fromJD(2455556.11351)
print "Create an object from a Julian Date (JD): {0}".format(dt.strftime("%Y-%m-%d, %H:%M"))

dt = astrodatetime.fromMJD(55555.61351)
print "Create an object from a Modified Julian Date (MJD): {0}".format(dt.strftime("%Y-%m-%d, %H:%M"))

dt = astrodatetime.fromDatetime(datetime.now())
print "Create an astrodatetime object from a datetime object: {0}".format(dt.strftime("%Y-%m-%d, %H:%M"))