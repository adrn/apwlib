#!/usr/bin/env python

""" TODO:
    - Single list of units available to convert
"""

import os, sys
sys.path.append(os.path.join(sys.path[0], ".."))

from apwlib.geometry import Angle, RA, Dec

# ++++++++++++++++++++++++++++
# |     Angle() objects      |
# ++++++++++++++++++++++++++++
#   Angle objects simply represent a single angular coordinate. More specific 
#   angular coordinates (e.g. RA, Dec) are subclasses of Angle, and thus all 
#   of the functionaliy described below applies to them as well (with a few 
#   caveats explained in the RA, Dec section).

# | Creating Angle objects |
# --------------------------

angle = Angle(54.12412, units="degrees")
angle = Angle("54.12412", units="degrees")
angle = Angle("54:07:26.832", units="degrees")

angle = Angle(3.60827466667, units="hours")
angle = Angle("3:36:29.7888000120", units="hours")

angle = Angle(0.944644098745, units="radians")

# or, equivalently:
angle = Angle.fromDegrees(54.12412)
angle = Angle.fromHours("3:36:29.7888000120")
angle = Angle.fromRadians(0.944644098745)

# | Converting units |
# --------------------
angle = Angle("54.12412", units="degrees")
print "Angle in hours: {0}.".format(angle.hours)
print "Angle in radians: {0}.".format(angle.radians)
print "Angle in degrees: {0}.".format(angle.degrees)
print "Angle in HMS: {0}".format(angle.hms) # returns a tuple, e.g. (12, 21, 2.343)

# | String formatting |
# ---------------------
print "Angle as HMS: {0}".format(angle.string(units="hours"))
print "Angle as HMS: {0}".format(angle.string(units="hours", sep=":"))
print "Angle as HMS: {0}".format(angle.string(units="hours", sep=":", precision=2))

# Also note that you can provide one, two, or three separators.
print "Demonstrating one, two, or three separators when converting an Angle object to a string."
print "Angle as HMS: {0}".format(angle.string(units="hours", sep=("h","m","s"), precision=4))
print "Angle as HMS: {0}".format(angle.string(units="hours", sep="-|", precision=4))
print "Angle as HMS: {0}".format(angle.string(units="hours", sep="-", precision=4))

# The next three lines demonstrate three ways you can specify a separator.
print "Demonstrating different ways of specifying separators when converting an Angle object to a string."
print "Angle as HMS: {0}".format(angle.string(units="hours", sep=("h","m","s"), precision=4))
print "Angle as HMS: {0}".format(angle.string(units="hours", sep=["h","m","s"], precision=4))
print "Angle as HMS: {0}".format(angle.string(units="hours", sep="hms", precision=4))

# +++++++++++++++++++++++++++++++
# |     RA()/Dec() objects      |
# +++++++++++++++++++++++++++++++
#   The RA() objects represents a Right Ascension in an equatorial coordinate system. 
#   RA is a subclass of Angle, so any of the above examples apply. Here we will focus 
#   on the extra functionality implemented in the RA class.

# | Creating RA/Dec objects |0
# -----------------------

# Creating RA objects is basically identical to creating Angle objects. The only difference
#   is if no units are specified, it assumes "hours".

ra = RA("4:08:15.162342")
# is equivalent to:
ra = RA("4:08:15.162342", units="hours")
ra = RA.fromHours("4:08:15.162342")

# Creating Dec objects is basically identical to creating Angle objects. The only difference
#   is if no units are specified, it assumes degrees.

dec = Dec("-41:08:15.162342")
# is equivalent to:
dec = Dec("-41:08:15.162342", units="degrees")
dec = Dec.fromDegrees("-41:08:15.162342")