========================================
apwlib
========================================

This `Python <http://www.python.org/>`_ package contains code that has been 
useful for my own research, but I believe is extensible to many other projects
across a variety of disciplines. I am happy to collaborate on new additions to
the package, as well as share code and algorithms with anyone interested. See 
for example: `Open Science <http://en.wikipedia.org/wiki/Open_research>`_.

To install, use the standard
::
    python setup.py install

** Examples / Help **
For help and examples, start with the *examples/* path within the project.

**1_coordinates.py**

    contains some examples of how to create and use the coordinate 
    system tools such as:
    
    * Creating RA/Dec objects from any reasonable units or formatting (e.g. "04:13:25.1412" or 136.2352)
    * (TODO) Demonstrate using coordinate systems
    * (TODO) Demonstrate transforming between coordinate systems

**2_astrodatetime.py**

    demonstrates how to use the Python datetime.datetime() subclass
    called astrodatetime() to handle JD/MJD and Sidereal Time.
    
    * Using *astrodatetime* to create a Python datetime object that knows about astronomical date formats
    * Creating an *astrodatetime()* object with a JD, MJD, or Local Sidereal Time (LST)

Any questions can be directed to me via email at **adrn at astro.columbia.edu**
