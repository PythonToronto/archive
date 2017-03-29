#!/usr/bin/python
__author__ = 'Michael J Moorhose'

"""
P1-blob_test.py

This work is licensed under a Creative Commons Attribution 4.0 International License.
See: http://creativecommons.org/licenses/by/4.0/

This program demonstrates the used of the 'simpleCV' image analysis library and demonstrated 
the detection of simple 'circle' like 'blobs' which are then annotated onto the image using
red circles.  A movie demonstrating operating accompanies (P1-blob-test.ogv).

It is part of a discussion about combined audio and vision analysis related to a 'home-brew' system of the SCATT system 
(see http://www.scatt.com/ ) for target training.

This is program "P1" in the accompanying presentation; it is the first of the series of code P1, P2, P3, P4 that
demonstrate increasing complexity.  Note that the code contains many 'magic numbers' that are seemingly 
very specific for the test setup (camera, lighting, target); this is an ongoing theme in the program series.
Expect these values to need adjusting for your local setup an application.

In overview the code:
 *) Loads the SimpleCV library and creates Camera and Display object
 *) Enters a loop ending when the display window is closed
 *) Gets aimage frame from the camera proiritised to detect Black - White constracst object
 *) Thresholds the image at 80 intensity
 *) fidnds 'blobs' uisngthe SimpleCV method
 *) filters for 'near circles' using a list comprehension and the isCircle() method
 *) If there are some circles demonstrates access to their object paramters via an iterative loop and 
    prints details to the CLI, extraction to 'convenience variables'
 *) Marks up the 'circles' on the display in RED
 *) The resultant image is 'saved' to the display and the program waits 1s

Typical output to the CLI is for a 4 circle registration mark system:

 -----
 Timestamp is:  1461124347.61
 SimpleCV.Features.Blob.Blob object at (499, 403) with area 29
 SimpleCV.Features.Blob.Blob object at (154, 95) with area 43
 SimpleCV.Features.Blob.Blob object at (476, 54) with area 62
 SimpleCV.Features.Blob.Blob object at (166, 422) with area 69
 -----
 Timestamp is:  1461124348.78
 SimpleCV.Features.Blob.Blob object at (499, 402) with area 15
 SimpleCV.Features.Blob.Blob object at (154, 95) with area 43
 SimpleCV.Features.Blob.Blob object at (476, 55) with area 57
 SimpleCV.Features.Blob.Blob object at (166, 422) with area 74
 -----
 ..etc..

"""
	
from SimpleCV import *		#The magic library
import time;			# So we can sleep
cam = Camera()			#Access the USB camera
disp = Display()		#Create a display panel so we can see the output

while disp.isNotDone():		#Go until somebody closes the window
    #Get an image from the camera and optimise for the Black / White:
    img = cam.getImage().colorDistance(Color.BLACK)
    #Thershold white/black at 80 / 255; then close the worst of the holes:
    img= img.binarize(80).morphClose()
    blobs = img.findBlobs()	#Find feature 'blobs'
    if blobs == None:
        time.sleep(1); continue
    #Filter 'blobs' for mostly circular things using a list comprehension:
    circles = blobs.filter([b.isCircle(1) for b in blobs])
    if circles:	#Assuming found some circles (ROIs):
        print "Timestampe is: ", time.time()
        for C_Circle in circles:
            #Print out the details of each circle in human readable format:
            print C_Circle
            #Demonstrate access to each 'Circle' object:
            x = C_Circle.x
            y = C_Circle.y
            #Markup each 'Circle' object on the image in red, 20 px diameter, 3 px circle
            # on a the image's 'dl' {drawing layer}:
            img.dl().circle ( (x, y), 20, color=(255,0,0),width=3)
    img.save(disp)	#'Save' the result back to the display window
    time.sleep(1);	#Wait a 1s
    print "-----"


