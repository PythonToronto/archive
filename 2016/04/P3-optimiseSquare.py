#!/usr/bin/python
__author__ = 'Michael J Moorhose'
"""
P3-optimiseSquare.py

This work is licensed under a Creative Commons Attribution 4.0 International License.
See: http://creativecommons.org/licenses/by/4.0/

This code extends P3 with an implemention of the cosine rule in in two functions and using thes - semi-sucessfully - 
with the skew() / warp() image methods.  This corrects any other points / ROI present into the same 
plane coordinate space as registration marks (assumes they themselves are planar).
A movie demonstrating operating accompanies (P3-optimiseSquare.ogv)

The approach defines a 'datum' line across the center left to center of the image and then compute the angles of
the 4 marker (registration) points to this so they can be sorted by angle and supplied in the correct order to 
the skew() method, specifically: top left, top right, bottom right, bottom left - the corners of the new image.
Supplying the centers of the marker points doesn't work so much code is devoted to the simple calculations
needed to determine the actual points.  This is complicated by the fact to that to change the image in the x-direction
the y-coordinates need to be adapted and vice versa and by different amounts on each side of the image.  
It is suspected that the poor result is due to trying to do both dimensions at the same time without 
compensating for this: hence 3 of 4 points align to the corners of a suare and the 4th is 'nearly' right.

The skew() / warp() function has sparse documention which doesn't help!

It is part of a discussion about combined audio and vision analysis related to a 'home-brew' system of the SCATT system 
(see http://www.scatt.com/ ) for target training.

This is program "P3" in the accompanying presentation; in the series of code P1, P2, P3, P4 that
demonstrate increasing complexity.  Note that the code contains many 'magic numbers' that are seemingly 
very specific for the test setup (camera, lighting, target); this is an ongoing theme in the program series.
Expect these values to need adjusting for your local setup an application.

"""


from SimpleCV import *  # The magic library
import time;  # So we can sleep
from itertools import combinations
from statistics import median
from statistics import mean
#Functions....for angle calculations:
def pdist(vA, vB):
    return math.sqrt((vA[0]-vB[0])**2 + (vA[1]-vB[1])**2)
#Angle between two points: >180 degrees allowed, base on cosine rule
def compute_angle(a,b,c):
    #supply as point a,b,c though...
    angle = math.acos((pdist(a,b)**2 + pdist(b,c)**2 - pdist(a,c)**2) / (2 * pdist(a,b) * pdist(b,c)))
    #x= 0; y =1;
    if c[1] < b[1] :
        return math.degrees(angle)
    elif c[1] > b[1] and c[0] > b[0]:
        return math.degrees(angle)+ 90
    else:
        return math.degrees(angle) + 90 + 180

#End functions:
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

            #New Section!!!
            #Summary: We know four circles will be in this list - our reg. points: can we use these to 'warp' the image?
            #(i.e. make the square 'Square'?
        #So we have persistence:
            markerOrder = list ()   #When we sort on angle
            corners = list()        #What we supply to the transform
            #Get the coordinates of the image:
            (ImageWidth, ImageHeight) = img.size()
        #This section sorts the 4 markers into order Top left [0], Top right[1], Bot right[2], Bot Left[3]
            LeftDatum = (0,int(ImageHeight/2)); RightDatum = (int(ImageWidth/2), int (ImageHeight/2))
            #Enable if you want these drawn:
            img.drawText("LD", x = LeftDatum[0], y = LeftDatum[1], color = (Color.YELLOW), fontsize=20); img.drawText("RD", x = RightDatum[0], y = RightDatum[1], color = (Color.YELLOW), fontsize=20);             print "Datums are: ", LeftDatum, " & ", RightDatum
            img.drawLine(LeftDatum, RightDatum, Color.YELLOW)
            c = 0
            for C_Marker in bestMarkers:
                print C_Marker
                angle = compute_angle(LeftDatum, RightDatum, (C_Marker.x, C_Marker.y))
                print "Angle to marker = ", angle, " degrees"
                #Store the angle and link it to the marker / circle / blob object:
                markerOrder.append ([angle, C_Marker])
                #Visual markup for demonstration
                img.dl().circle((C_Marker.x, C_Marker.y), 40, color=(Color.CYAN), width=6)
                img.drawLine(RightDatum, (C_Marker.x, C_Marker.y), Color.BEIGE, thickness=3)

            #Sort on angle
            markerOrder.sort(key=lambda x: x[0])

            for C_Marker in markerOrder:
                img.drawText(str(int(C_Marker[0])) + " " + str(c), x = C_Marker[1].x+5, y = C_Marker[1].y+5, color = (Color.FUCHSIA), fontsize=60)
                c = c+1
        #Calculate some crude- and imperfect corrections:
            horz_Start_Correct = (markerOrder[0][1].x- markerOrder[3][1].x)
            vert_Start_Correct = (markerOrder[0][1].y- markerOrder[1][1].y)

            horz_Dist_Adjust  = (markerOrder[1][1].x- markerOrder[2][1].x) - (markerOrder[0][1].x- markerOrder[3][1].x)
            vert_Dist_Adjust = (markerOrder[0][1].y- markerOrder[1][1].y) - (markerOrder[3][1].y- markerOrder[2][1].y)


            print "Correction for x (horz_Start_Correct) = ", horz_Start_Correct;             print "Correction for x (              horz_Dist_Adjust) = ", horz_Dist_Adjust;            print "Correction for y (vert_Start_Correct ) = ", vert_Start_Correct;            print "Correction for y (              vert_Dist_Adjust) = ", vert_Dist_Adjust;
        #Build the 'corners' list: (this sort-of works):
            corners.append((-horz_Start_Correct, -vert_Start_Correct)) # top left [0]
            corners.append((ImageWidth,vert_Start_Correct))    # top right [1]
            corners.append((ImageWidth + horz_Start_Correct + horz_Dist_Adjust, ImageHeight+vert_Start_Correct-vert_Dist_Adjust)) # bot right [2]
            corners.append((-horz_Start_Correct, ImageHeight+vert_Start_Correct)) # bot left [3]
        #One would have thought it sho
            corners.append((markerOrder[0][1].x- vert_Start_Correct, markerOrder[0][1].y))
            corners.append((markerOrder[1][1].x - vert_Start_Correct, markerOrder[1][1].y))
            corners.append((markerOrder[2][1].x - vert_Start_Correct, markerOrder[2][1].y))
            corners.append((markerOrder[3][1].x - vert_Start_Correct, markerOrder[3][1].y))
        #Mark
            # for C_Marker in markerOrder:
            #     print "With angle: ", C_Marker [0], ": center is at: (", C_Marker [1].x, ",",C_Marker [1].y,")"
            #     #corners.append ((C_Marker [1].x, C_Marker [1].y))
            #     img.drawText(str(int(C_Marker[0])), x = C_Marker [1].x, y = C_Marker [1].y, color = (Color.YELLOW), fontsize=20)

            print "Corners are:", corners

            img.save(disp)
            time.sleep(2);  # Wait a 1s
            corrected = img.warp(corners)
            corrected.show()
            #corrected.save(disp)
            time.sleep(2);  # Wait a 1s
            #Ok, now try to optimise the 'square'

    #img.save(disp)  # 'Save' the result back to the display window
    print "-----"


