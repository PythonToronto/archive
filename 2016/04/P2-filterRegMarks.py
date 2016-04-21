#!/usr/bin/python
__author__ = 'Michael J Moorhose'
"""
P2-filterRegMarks.py

This work is licensed under a Creative Commons Attribution 4.0 International License.
See: http://creativecommons.org/licenses/by/4.0/

This code extends P1 by ~20 line adding and extra layer of filtering to the circles-blobs found and by 
trying all possible combinations of them (using Itertools) it selects the 4 with the most similar 
areas and highlights these in Cyan circles.
A movie demonstrating operating accompanies (P2-filterRegMarks.ogv)

The scoring system used is crude: the sum of the means and the sum of the medians for each combination
are tested and the best selected on the assumption that the distrubition of the areas will be non-skewed.
A movie demonstrating operating accompanies (P2-filterRegMarks.ogv) demonstrates operation

It is part of a discussion about combined audio and vision analysis related to a 'home-brew' system of the SCATT system 
(see http://www.scatt.com/ ) for target training.

This is program "P2" in the accompanying presentation; in the series of code P1, P2, P3, P4 that
demonstrate increasing complexity.  Note that the code contains many 'magic numbers' that are seemingly 
very specific for the test setup (camera, lighting, target); this is an ongoing theme in the program series.
Expect these values to need adjusting for your local setup an application.

"""

from SimpleCV import *  # The magic library
import time;  # So we can sleep
from itertools import combinations
from statistics import median
from statistics import mean

cam = Camera()  # Access the USB camera
disp = Display()  # Create a display panel so we can see the output
time.sleep(1);  # Wait 1s for the camera to stabilise its auto-magical everything
while disp.isNotDone():  # Go until somebody closes the window
    # Get an image from the camera and optimise for the Black / White:
    img = cam.getImage().colorDistance(Color.BLACK)
    # Thershold white/black at 80 / 255; then close the worst of the holes:
    img = img.binarize(80).morphClose()
    blobs = img.findBlobs()  # Find feature 'blobs'
    # Filter 'blobs' for mostly circular things using a list comprehension:
    if blobs:
        circles = blobs.filter([b.isCircle(2) for b in blobs])

        if circles:  # Assuming found some circles (ROIs):

            print "Timestamp is: ", time.time()
            for C_Circle in circles:
                # Print out the details of each circle in human readable format:
                print C_Circle
                # Demonstrate access to each 'Circle' object:
                x = C_Circle.x
                y = C_Circle.y
    # Markup *ALL* 'Circle' objects on the image in red, 20 px diameter, 3 px circle
    # on a the image's 'dl' {drawing layer}:
                img.dl().circle((x, y), 10, color=(Color.RED), width=2)
        # Now deduce where our 4 marker points are:
		bestScore = None		#So we retain in scope
        bestMarkers = None
        if len(circles) >= 4:  # We need more than 4 possibles to try to find the 4 best!
            for thisCombo in combinations(circles, 4):
                circleAreas = [thisc.area() for thisc in thisCombo]
                #Score is a simple way to ask if the distribution is skewed:
				#Optimal is 0: all the areas are the same,
                score = abs(median(circleAreas) - mean(circleAreas))
                #New best score or the only one we've got?
                if bestScore == None or score <= bestScore:
                    bestScore = score   #Reset the score
                    bestMarkers = thisCombo  # Are we copying the correct thing?
                    print "Better combination: score=", score
                    print "OK, our 4 best markers are:"
            #We know four circles will be in this list:
            for C_Marker in bestMarkers:
                print C_Marker
                img.dl().circle((C_Marker.x, C_Marker.y), 40, color=(Color.CYAN), width=6)

    img.save(disp)  # 'Save' the result back to the display window
    print "-----"
    time.sleep(1);  # Wait a 1s
