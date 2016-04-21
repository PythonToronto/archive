#!/usr/bin/python
__author__ = 'Michael J Moorhose'
"""
P4-spotTrack.py

This work is licensed under a Creative Commons Attribution 4.0 International License.
See: http://creativecommons.org/licenses/by/4.0/

This code demostrates the tracking of the brightest circle-like object seen on the 'Red' channel.
Compared its sister programs P2 & P3 it uses the absolute intensity of the spots - constrst enhanced using
the 'strecht()' method and the summation of the RGB components of each obecjt selecting the first one 
with a total value > 700 (magic number).  This is highlighted with a dark green circle and the x, y coordinates
stored in a simple Python list.

This is then used to 'replay' the observed positions at the end of the sampling time (~7s when tested)
over the image target.


A movie demonstrating operating accompanies (P4-spot_track.ogv)

It is part of a discussion about combined audio and vision analysis related to a 'home-brew' system of the SCATT system 
(see http://www.scatt.com/ ) for target training.

This is program "P4" in the accompanying presentation; in the series of code P1, P2, P3, P4 that
demonstrate increasing complexity.  Note that the code contains many 'magic numbers' that are seemingly 
very specific for the test setup (camera, lighting, target); this is an ongoing theme in the program series.
Expect these values to need adjusting for your local setup an application.

"""

from SimpleCV import *  # The magic library
import time;  # So we can sleep

startTime = time.time()
cam = Camera()  # Access the USB camera
disp = Display()  # Create a display panel so we can see the output
time.sleep(1);  # Wait 1s for the camera to stabilise its auto-magical everything
runCount = 1  # loop counter
MAX_CYLCES = 80 # ~ 8s
#So we can annotate afterwards:
BackGroundImage = cam.getImage().colorDistance(Color.RED)
pointList = list()

while disp.isNotDone() and runCount <= MAX_CYLCES:  # ~ 10 frames / s
    runCount = runCount + 1
    # Get an image from the camera and optimise for the Red channel only:
    img = cam.getImage().colorDistance(Color.RED)
    # Demonstrate skewing the sensitivity to the top of the range (max white / red):
    segmented = img.stretch(200, 255)
    # (alternative to binarize() - softer and preserves some color info)

    # Find blobs: >231 intensity and not too large or small
    blobs = segmented.findBlobs(220, minsize=90, maxsize=250)  # Find feature 'blobs'

    print runCount, "\t", " time: ", round((time.time() - startTime), 2), " s"
    if blobs:
        print "Found ", len(blobs), " blobs"
        blobs.draw(Color.GREEN)
        # Filter 'blobs' for mostly circular things using a list comprehension:
        circles = blobs.filter([b.isCircle(2) for b in blobs])

        if circles:  # Assuming found some circles (ROIs):
            # Sort the circles based on distance to the color red
            circles.sortColorDistance(Color.RED)
            print "--->Found ", len(circles), " circles"

            for C_Circle in circles[:3]:  # Print out the top 3 circles, along with their color info:
                x = C_Circle.x;
                y = C_Circle.y;
                RGBSum = int(sum(C_Circle.meanColor())) #Sum the RGB components (all the same actually)
                # If the circle was really bright: note the x,y coordinates
                if RGBSum > 700:
                    print x, y, ": ", C_Circle.area(), " (area px ), sum RGB: ", str(RGBSum)

                # Mark-up on the image: thick FORESTGREEN circle(s):
                    img.dl().circle((x, y), 30, color=(Color.FORESTGREEN), width=7)
                #Save the result for later 'replay'
                    pointList.append((x, y))
                    continue # Next; we have our marker
    img.save(disp)  # 'Save' the result back to the display window
    print "-"
    # time.sleep(1);  # Wait a 1s
###
#Replay:

print "All Done!  Entering replay mode (if possible):"
if len(pointList) >=0:
    print "Got ", str(len(pointList)+1), " points stored out of possible ", str(MAX_CYLCES)
    for i in pointList:
        x,y = i #Convenience!
        BackGroundImage.dl(0).circle((x, y), 15, color=(Color.FORESTGREEN), filled=True)
        BackGroundImage.save(disp)
        time.sleep(0.1)
