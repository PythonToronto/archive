#!/usr/bin/python
__author__ = 'Michael J Moorhouse'

"""
P0-audio_test.py

This work is licensed under a Creative Commons Attribution 4.0 International License.
See: http://creativecommons.org/licenses/by/4.0/


Originally the work of http://stackoverflow.com/users/1405612/user1405612
as described in the post:
http://stackoverflow.com/questions/4160175/detect-tap-with-pyaudio-from-live-mic/4160733#4160733

Adapted by Michael Moorhouse for a presentation to the Toronto Python Meetup group on 2016-04-21

This program demonstrates the used of the 'pyaudio' library- with optimised parameters for detecting
short events (a finger 'snap' / click) as part of a discussion about combined audio and vision analysis
related to a 'home-brew' system of the SCATT system (see http://www.scatt.com/ ) for target training.

This is program "P0" in the accompanying presentation; it was not discussed in detail due to time constraints.

In general overview it:
 *) Loads libraries
 *) Sets the sampling parameters
 *) Defines a function that when passed a 'block' of audio data stream calculates the RMS (averages it)
 *) Opens an audio stream / declares new audio object to the microphone jack interface
 *) Enters a long-duration loop to get blocks from the audio stream, calculate the RMS value and decide if 
    there is a 'trigger' event - if so then print the word "Tap!" to the Console with a timestamp

  A feature is 'dynamic / adaptive gain control' where if the 'tap' is too loud or none are detected then 
  future threashold is tweaked using an algorithm that assesses the ratio of 'quiet' and 'noisy' blocks.

With the settings a typical output for 'one finger snap every 2s' is:

 /usr/bin/python P0-audio_test.py 
ALSA lib pcm.c:2239:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
ALSA lib pcm.c:2239:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
ALSA lib pcm.c:2239:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
bt_audio_service_open: connect() failed: Connection refused (111)
bt_audio_service_open: connect() failed: Connection refused (111)
bt_audio_service_open: connect() failed: Connection refused (111)
bt_audio_service_open: connect() failed: Connection refused (111)
tap! at:  1461261124.57
tap! at:  1461261126.58
tap! at:  1461261128.76
tap! at:  1461261130.91
tap! at:  1461261133.04
tap! at:  1461261135.24
tap! at:  1461261137.5
tap! at:  1461261139.57
tap! at:  1461261141.51
tap! at:  1461261143.68
tap! at:  1461261145.98
tap! at:  1461261148.07
tap! at:  1461261150.4
...etc...

"""

import pyaudio
import struct
import math
import time;

INITIAL_TAP_THRESHOLD = 0.1
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 22000
INPUT_BLOCK_TIME = 0.01
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)

OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME

UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME # if we get this many quiet blocks in a row, decrease the threshold

MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME # if the noise was longer than this many blocks, it's not a 'tap'

def get_rms(block):

    # RMS amplitude is defined as the square root of the
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into
    # a string of 16-bit samples...

    # we will get one short out for each
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
    # sample is a signed short in +/- 32768.
    # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

pa = pyaudio.PyAudio()                                 #]
                                                       #|
stream = pa.open(format = FORMAT,                      #|
         channels = CHANNELS,                          #|---- You always use this in pyaudio...
         rate = RATE,                                  #|
         input = True,                                 #|
         frames_per_buffer = INPUT_FRAMES_PER_BLOCK)   #]

tap_threshold = INITIAL_TAP_THRESHOLD                  #]
noisycount = MAX_TAP_BLOCKS+1                          #|---- Variables for noise detector...
quietcount = 0                                         #|
errorcount = 0                                         #]

for i in range(10000):
    try:                                                    #]
        block = stream.read(INPUT_FRAMES_PER_BLOCK)         #|
    except IOError, e:                                      #|---- just in case there is an error!
        errorcount += 1                                     #|
        print( "(%d) Error recording: %s"%(errorcount,e) )  #|
        noisycount = 1                                      #]

    amplitude = get_rms(block)

    if amplitude > tap_threshold: # if its to loud...
        quietcount = 0
        noisycount += 1
        if noisycount > OVERSENSITIVE:
            tap_threshold *= 1.1 # turn down the sensitivity

    else: # if its to quiet...

        if 1 <= noisycount <= MAX_TAP_BLOCKS:
            print 'tap! at: ', time.time();

        noisycount = 0
        quietcount += 1
        if quietcount > UNDERSENSITIVE:
            tap_threshold *= 0.9 # turn up the sensitivity
