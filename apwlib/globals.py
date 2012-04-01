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

VALIDUNITS = ["radians", "degrees", "hours"]

# Used to color output
_okColor = '\033[92m'
_warnColor = '\033[93m'
_errorColor = '\033[91m'
_ENDC = '\033[0m'

def greenText(text):
    return "{0}{1}{2}".format(_okColor, text, _ENDC)
    
def yellowText(text):
    return "{0}{1}{2}".format(_warnColor, text, _ENDC)

def redText(text):
    return "{0}{1}{2}".format(_errorColor, text, _ENDC)