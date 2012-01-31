#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# custom_errors.py - A Python module that contains custom errors for use in
#               conversions and coordinate conversions for astronomical data
#               processing and analysis
#

import globals

class IllegalHourError(ValueError):
    """
    Usage:
        if not 0 <= hr < 24:
            raise IllegalHourError(hour)
    """
    def __init__(self, hour):
        self.hour = hour
    def __str__(self):
        return "Bad hour value %r; hour must be in the range [0,24)" % self.hour

class IllegalMinuteError(ValueError):
    """
    Usage:
        if not 0 <= min < 60:
            raise IllegalMinuteError(minute)
    """
    def __init__(self, minute):
        self.minute = minute
    def __str__(self):
        return "Bad minute value %r; must be in the range [0,60)" % self.minute

class IllegalSecondError(ValueError):
    """
    Usage:
        if not 0 <= sec < 60:
            raise IllegalSecondError(second)
    """
    def __init__(self, second):
        self.second = second
    def __str__(self):
        return "Bad second value %r; must be in the range [0,60)" % self.second

class IllegalUnitsError(ValueError):
    """
    Usage:
        if units not in VALIDUNITS:
            raise IllegalUnitsError("")
    """
    def __init__(self, units):
        self.units = units
    def __str__(self):
        return "The units specified must be one of the following: {0}. You specified: \'{1}\'".format(",".join(globals.VALIDUNITS), self.units)
