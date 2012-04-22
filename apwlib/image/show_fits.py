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
# ShowFITS.py - A simple Tkinter based FITS viewer written in Python
#

"""
TODO:   
        - Add invert button
        - scaleImage should detect screen resolution instead of 1680 x 1050 (my screen)
        - Build in point source finder?
    
"""

__author__ = 'Adrian Price-Whelan <adrn@astro.columbia.edu>'

# Standard library dependencies
import sys, os

# Third-party
import Image
import pyfits as pf
import numpy as np
import scipy.ndimage as snd
import ImageTk
import Tkinter as Tk
import tkFileDialog, tkMessageBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Project Dependencies
import util

scalingTypes = {"arcsinh" : util.arcsinhStretch,\
                "linear" : util.linearStretch,\
                "sqrt" : util.sqrtStretch}
        
class FITSImageViewer:
    
    def __init__(self, master):
        self.master = master
        self.imageSessions = dict()
        self.start()
    
    def browseFiles(self):
        """ This is a helped function that provides the file browser dialog """
        self.filename.set(tkFileDialog.askopenfilename(title="Open FITS file..."))
        self.filenameBasename.set(os.path.basename(self.filename.get()))
        self.submit.focus_set()
        
        """
        imageHDUs = []
        try:
            hdulist = pf.open(self.filename)
            for ii,hdu in enumerate(hdulist):
                try:
                    if not (hdu.header['XTENSION'] == 'BINTABLE'):
                        imageHDUs.append(ii)
                    else:
                        print "not an image"
                except:
                    pass
                        
        except:
            return
        
        m = self.hduOption.children['menu']
        m.delete(0, Tk.END)
        for val in imageHDUs:
            m.add_command(label="{0}".format(val), command=lambda v=self.hduValue,l=val: v.set(l))
        self.hduValue.set(imageHDUs[0])
        """
    
    def start(self):
        """ """
        self.master.title("FITS Image Viewer / Editor")
        
        Tk.Label(self.master, text="Select a FITS file to open").grid(row=0, column=0, columnspan=3)
        
        Tk.Label(self.master, text="File: ").grid(row=1, column=0)
        self.filename = Tk.StringVar()
        self.filenameBasename = Tk.StringVar()
        filePathTextBox = Tk.Entry(self.master, width=35, textvariable=self.filenameBasename)
        filePathTextBox.grid(row=1, column=1)
        openFile = Tk.Button(self.master, text="Browse...", command=self.browseFiles)
        openFile.grid(row=1, column=2)
        
        Tk.Label(self.master, text="HDU: ").grid(row=2, column=0)
        self.hduValue = Tk.IntVar(None)
        #self.hduOption = Tk.OptionMenu(self.master, self.hduValue, 0)
        #self.hduOption.grid(row=2, column=1)
        hduBox = Tk.Entry(self.master, width=6, textvariable=self.hduValue)
        hduBox.grid(row=2, column=1, columnspan=2, sticky="W")

        self.submit = Tk.Button(self.master, text="Show file", command=self.createSession)
        self.submit.bind("<Return>", self.createSession)
        self.submit.grid(row=3, column=1, columnspan=2)
        
        """
        for ii, filename in enumerate(self.imageSessions.keys()):
            Tk.Label(self.master, text=os.path.basename(filename)).grid(row=3+ii, columnspan=2)
            reShowButton = Tk.Button(self.master, text="Show", command=self.imageSessions[filename].createWindow)
            reShowButton.grid(row=3+ii, column=2)
            closeButton = Tk.Button(self.master, text="Close", command=lambda: self.destroySession(filename))
            closeButton.grid(row=3+ii, column=3 )
        """
        
        # Bottom padding
        #Tk.Label(self.master, text="").grid(row=2)
    
    def createSession(self, event=None):
        """ """
        strFilename = self.filename.get()
        hduNumber = self.hduValue.get()
        try:
            self.imageSessions[strFilename] = ImageSession(self.master, strFilename, hdu=hduNumber)
            self.start()
        except util.ImageSessionError:
            pass
        except util.NotAnImageHDUError:
            pass
    
    def destroySession(self, filename):
        """ """
        self.imageSessions.pop(filename)
        self.start()
        self.master.update()

class ImageSession:
    def __init__(self, master, filename, hdu=0):
        # filename should be a string!
        self.filename = filename
        self.hdu = hdu
        
        # The master window?
        self.master = master
        
        if not os.path.exists(self.filename):
            tkMessageBox.showerror("File not found", "File {0} doesn't exist!".format(file))
            return
        
        self.openFile()
        self.createWindow()
    
    def openFile(self):
        # Try to open the file and read in the data from HDU
        try:
            hdulist = pf.open(self.filename)
            try:
                if hdulist[self.hdu].header['XTENSION'] == 'BINTABLE':
                    tkMessageBox.showerror("HDU Error", "The HDU {0} is not an ImageHDU!".format(self.hdu))
                    raise util.NotAnImageHDUError("The HDU {0} is not an ImageHDU!".format(self.hdu))
                # HDU is a table -- throw an error!
            except KeyError:
                # HDU is an image, carry on!
                pass
            
            self.rawData = hdulist[self.hdu].data
            self.rawData.shape
        except IOError:
            tkMessageBox.showerror("FITS file error ", "File {0} does not appear to be a valid FITS file!".format(self.filename))
            raise util.ImageSessionError("File {0} does not appear to be a valid FITS file!".format(self.filename))
        except AttributeError:
            tkMessageBox.showerror("FITS file error ", "File {0} does not appear to have data in HDU 0.".format(self.filename))
            raise util.ImageSessionError("File {0} does not appear to have data in HDU 0.".format(self.filename))
    
    def createWindow(self):
        # Create the actual window to draw the image and scale controls
        self.ImageWindow = Tk.Toplevel(self.master)
        self.ImageWindow.title(self.filename)
        #self.ImageWindow.protocol("WM_DELETE_WINDOW", self.closeImage)
        
        # TODO: THIS SHOULD DETECT SCREEN RESOLUTION
        screenSize = (1050/1.5, 1680/1.5)
        if self.rawData.shape[0] > screenSize[0] and self.rawData.shape[1] > screenSize[1]:
            factor1 = screenSize[0] / self.rawData.shape[0]
            factor2 = screenSize[1] / self.rawData.shape[1]
            self.zoomFactor = min([factor1, factor2])
        elif self.rawData.shape[1] > screenSize[0]:
            self.zoomFactor = screenSize[0]/ self.rawData.shape[1]
        elif self.rawData.shape[0] > screenSize[1]:
            self.zoomFactor = screenSize[1] / self.rawData.shape[0]
        else:
            self.zoomFactor = 1.
        
        # Create the image tools
        scaleTypeLabel = Tk.Label(self.ImageWindow, text="Scaling: ")
        scaleTypeLabel.grid(row=0, column=0)
        self.scalingName = Tk.StringVar()
        self.scalingName.set("arcsinh")
        self.scalingOption = Tk.OptionMenu(self.ImageWindow, self.scalingName, "arcsinh","linear","sqrt", command=self.setRescaler)
        self.scalingOption.grid(row=0, column=1)
        
        rescaleLabel = Tk.Label(self.ImageWindow, text="Rescale: ")
        rescaleLabel.grid(row=1, column=0)
        self.scaleValue = Tk.Scale(self.ImageWindow, from_=-4, to=6, resolution=0.05, orient=Tk.HORIZONTAL, showvalue=1, length=300)
        self.scaleValue.set(1.0)
        self.scaleValue.grid(row=1, column=1)
        
        minLabel = Tk.Label(self.ImageWindow, text="Min Pixel Value: ")
        minLabel.grid(row=2, column=0)
        self.minValue = Tk.Scale(self.ImageWindow, resolution=0.05, orient=Tk.HORIZONTAL, showvalue=1, length=300)
        self.minValue.set(1.0)
        self.minValue.grid(row=2, column=1)
        
        maxLabel = Tk.Label(self.ImageWindow, text="Max Pixel Value: ")
        maxLabel.grid(row=3, column=0)
        self.maxValue = Tk.Scale(self.ImageWindow, resolution=0.05, orient=Tk.HORIZONTAL, showvalue=1, length=300)
        self.maxValue.set(1.0)
        self.maxValue.grid(row=3, column=1)
        
        # Set the min/max slider boundaries
        self.minValue.config(from_=self.rawData.min(), to=self.rawData.max())
        self.minValue.set(self.rawData.min())
        self.maxValue.config(from_=self.rawData.min(), to=self.rawData.max())
        self.maxValue.set(self.rawData.max())
        
        # Set the default rescaler
        self.rescaler = util.arcsinhStretch
        
        self.scaleImage()
        self.drawImage()
        
        # Bind the sliders to the scaleImage() method
        self.scaleValue.bind("<ButtonRelease-1>", self.redraw)
        self.minValue.bind("<ButtonRelease-1>", self.redraw)
        self.maxValue.bind("<ButtonRelease-1>", self.redraw)
        self.scalingOption.bind("<ButtonRelease-1>", self.redraw)
        
    def setRescaler(self, event):
        self.rescaler = scalingTypes[self.scalingName.get()]
    
    def redraw(self, event=None):
        """ This rescales and redraws the image using the current values for scaling """
        self.scaleImage()
        self.drawImage()
    
    def updateThumbnail(self, event):
        """ """
        self.lastMousePosition = (event.x, event.y)
        self.pilThumbnail = self.pilImage.transform(self.pilImage.size, Image.EXTENT, (event.x-25,event.y-25,event.x+25,event.y+25))
        self.thumbnailImage = ImageTk.PhotoImage(self.pilThumbnail.resize((200,200)))
        self.thumbnailImageLabel.configure(image=self.thumbnailImage)
        
    def scaleImage(self):
        """ This method re-scales the image data """
        self.scaledData = 255.0*self.rescaler(self.rawData, beta=10.**self.scaleValue.get(), min=self.minValue.get(), max=self.maxValue.get(), clip=True)
    
    def plotContour(self, event):
        """ If the 'c' key is pressed, generate a contour plot of whatever is in the thumbnail zoom box """
        self.contourPlot = Tk.Toplevel(self.master)
        self.contourPlot.title("Contour plot for: {0}".format(self.filename))
        
        rawShape = self.rawData.shape
        
        lastx, lasty = self.lastMousePosition
        lastx = round(lastx/self.zoomFactor)
        lasty = round(lasty/self.zoomFactor)
        boxHalfSize = 25/self.zoomFactor
        x1,y1,x2,y2 = [x for x in map(round, (lastx-boxHalfSize,lasty-boxHalfSize,lastx+boxHalfSize,lasty+boxHalfSize))]
        
        if x1 < 0:
            x1 = 0
            x2 = boxHalfSize*2
        if x2 > rawShape[1]:
            x2 = rawShape[1]
            x1 = x2 - boxHalfSize*2
        if y1 < 0:
            y1 = 0
            y2 = boxHalfSize*2
        if y2 > rawShape[0]:
            y2 = rawShape[0]
            y1 = y2 - boxHalfSize*2
        
        thumbData = self.rawData[y1:y2, x1:x2]
        shp = thumbData.shape
        x,y = np.meshgrid(range(shp[0]), range(shp[1]))

        self.fig = Figure(figsize=(5,5))
        ax = self.fig.add_subplot(111)
        ax.contour(x, y, thumbData)
        ax.set_ylim(ax.get_ylim()[::-1])
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.contourPlot)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        
    def drawImage(self):
        """ This method will draw the image into a PhotoImage object in the new image window """
        
        self.pilImage = Image.fromarray(self.scaledData.astype(np.uint8))
        newSize = (int(self.pilImage.size[0]*self.zoomFactor), int(self.pilImage.size[1]*self.zoomFactor))
        self.pilImage = self.pilImage.resize(newSize)
        self.tkImage = ImageTk.PhotoImage(self.pilImage)
        self.canvas = Tk.Canvas(self.ImageWindow, width=newSize[0], height=newSize[1], bd=0)
        self.canvas.create_image(0, 0, image=self.tkImage, anchor="nw")
        self.canvas.grid(row=0, column=2, rowspan=5, sticky="nswe")
        self.canvas.bind("<Motion>", self.updateThumbnail)
        self.canvas.bind("c", self.plotContour)
        self.canvas.focus_set()
        
        """ # Code for source detection:
        numSigma = 2.
        labels, num = snd.label(self.rawData > (numSigma*np.std(self.rawData)), np.ones((3,3)))
        coords = snd.center_of_mass(self.rawData, labels, range(1,num+1))
        rad = 5.
        for coord in coords:
            y,x = coord
            x = x*self.zoomFactor
            y = y*self.zoomFactor
            circ1 = self.canvas.create_oval(x-rad,y-rad,x+rad,y+rad, outline='red')
        """
        
        self.pilThumbnail = self.pilImage.transform(self.pilImage.size, Image.EXTENT, (0,0,50,50))
        self.pilThumbnail = self.pilThumbnail.resize((200,200))
        self.thumbnailImage = ImageTk.PhotoImage(self.pilThumbnail)
        self.thumbnailImageLabel = Tk.Label(self.ImageWindow, image=self.thumbnailImage, command=None)
        self.thumbnailImageLabel.grid(row=4, column=0, columnspan=2, rowspan=5)

root = Tk.Tk()
app = FITSImageViewer(root)
root.mainloop()


"""
    For PTF mask
    BIT00   =                    0 / AIRCRAFT/SATELLITE TRACK                       
    BIT01   =                    1 / OBJECT (detected by SExtractor)                
    BIT02   =                    2 / HIGH DARK-CURRENT                              
    BIT03   =                    3 / RESERVED FOR FUTURE USE                        
    BIT04   =                    4 / NOISY                                          
    BIT05   =                    5 / GHOST                                          
    BIT06   =                    6 / CCD BLEED                                      
    BIT07   =                    7 / RAD HIT                                        
    BIT08   =                    8 / SATURATED                                      
    BIT09   =                    9 / DEAD/BAD                                       
    BIT10   =                   10 / NAN (not a number)                             
    BIT11   =                   11 / DIRTY (10-sigma below coarse local median)     
    BIT12   =                   12 / HALO                                           
    BIT13   =                   13 / RESERVED FOR FUTURE USE                        
    BIT14   =                   14 / RESERVED FOR FUTURE USE                        
    BIT15   =                   15 / RESERVED FOR FUTURE USE
"""