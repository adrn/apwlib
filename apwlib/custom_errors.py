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
# custom_errors.py - A Python module that contains custom errors for use in
#               conversions and coordinate conversions for astronomical data
#               processing and analysis
#

import globals

class IllegalHourError:
    """
    Usage:
        if not 0 <= hr < 24:
            raise IllegalHourError(hour)
    """
    def __init__(self, hour):
        self.hour = hour
    def __str__(self):
        return "Bad hour value %r; hour must be in the range [0,24)" % self.hour

class IllegalMinuteError:
    """
    Usage:
        if not 0 <= min < 60:
            raise IllegalMinuteError(minute)
    """
    def __init__(self, minute):
        self.minute = minute
    def __str__(self):
        return "Bad minute value %r; must be in the range [0,60)" % self.minute

class IllegalSecondError:
    """
    Usage:
        if not 0 <= sec < 60:
            raise IllegalSecondError(second)
    """
    def __init__(self, second):
        self.second = second
    def __str__(self):
        return "Bad second value %r; must be in the range [0,60)" % self.second

class IllegalUnitsError:
    """
    Usage:
        if units not in VALIDUNITS:
            raise IllegalUnitsError("")
    """
    def __init__(self, units):
        self.units = units
    def __str__(self):
        return "The units specified must be one of the following: {0}. You specified: \'{1}\'".format(",".join(globals.VALIDUNITS), self.units)
