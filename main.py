#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import math
import json
import time
import random
import argparse
import pyglet
import fluidsynth
import launchpad
import rtmidi
import mido
from threading import Thread, Lock
from pics import CircleOfFifths, LaunchpadBox

from seagull import scenegraph as sg
from seagull.xml import parse, serialize
from seagull.opengl.utils import gl_prepare, gl_reshape, gl_display
from seagull.scenegraph.transform import product, normalized

from window import window, elements

this_dir = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(this_dir))

parser = argparse.ArgumentParser(description='Music Player Test')
parser.add_argument('-v', '--verbose', action="store_true", help="verbose output" )
args = parser.parse_args()

fast = True

if fast:
	import OpenGL
	OpenGL.ERROR_CHECKING = False
	OpenGL.ERROR_LOGGING = False
	OpenGL.ERROR_ON_COPY = True
	OpenGL.STORE_POINTERS = False

if args.verbose:
	print("~ Verbose!")
else:
	print("~ Not so verbose")



class LaunchpadManager:
	MODE_PRO = "Pro"
	MODE_MK2 = "Mk2"
	MODE_CONTROL_XL = "XL"
	MODE_LAUNCHKEY_MINI = "LKM"
	MODE_DICER = "Dcr"
	MODE_MK1 = "Mk1"

	def __init__(self):
		self.mode = None
		self.lp = None

	def setup(self):
		self.mode = None
		self.lp = launchpad.Launchpad();

		if self.lp.Check( 0, "pro" ):
			self.lp = launchpad.LaunchpadPro()
			if self.lp.Open(0,"pro"):
				print("~ Launchpad Pro")
				self.mode = self.MODE_PRO

		elif self.lp.Check( 0, "mk2" ):
			self.lp = launchpad.LaunchpadMk2()
			if self.lp.Open( 0, "mk2" ):
				print("~ Launchpad Mk2")
				self.mode = self.MODE_MK2

		elif self.lp.Check( 0, "control xl" ):
			self.lp = launchpad.LaunchControlXL()
			if self.lp.Open( 0, "control xl" ):
				print("~ Launch Control XL")
				self.mode = self.MODE_CONTROL_XL

		elif self.lp.Check( 0, "launchkey" ):
			self.lp = launchpad.LaunchKeyMini()
			if self.lp.Open( 0, "launchkey" ):
				print("~ LaunchKey (Mini)")
				self.mode = self.MODE_LAUNCHKEY_MINI

		elif self.lp.Check( 0, "dicer" ):
			self.lp = launchpad.Dicer()
			if self.lp.Open( 0, "dicer" ):
				print("~ Dicer")
				self.mode = self.MODE_DICER

		else:
			if self.lp.Open():
				print("~ Launchpad Mk1/S/Mini")
				self.mode = self.MODE_MK1

		if self.mode is None:
			print("Did not find any Launchpads, meh...")

	def test(self):
		assert( self.mode == self.MODE_MK2)

		# Clear the buffer because the Launchpad remembers everything
		self.lp.ButtonFlush()

		# List the class's methods
		print( " - Available methods:" )
		for mName in sorted( dir( self.lp ) ):
			if mName.find( "__") >= 0:
				continue
			if callable( getattr( self.lp, mName ) ):
				print( "     " + str( mName ) + "()" )

		# LedAllOn() test
		print( " - Testing LedAllOn()" )
		for i in [ 5, 21, 79, 3]:
			self.lp.LedAllOn( i )
			time.sleep(0.001 * 500)
		self.lp.LedAllOn( 0 )

		# LedCtrlXY() test
		# -> LedCtrlRaw()
		#    -> midi.RawWriteSysEx()
		#       -> devOut.write_sys_ex()
		print( " - Testing LedCtrlXY()" )
		colors = [ [63,0,0],[0,63,0],[0,0,63],[63,63,0],[63,0,63],[0,63,63],[63,63,63] ]
		for i in range(4):
			for y in range( i + 1, 8 - i + 1 ):
				for x in range( i, 8 - i ):
					self.lp.LedCtrlXY( x, y, colors[i][0], colors[i][1], colors[i][2])
			time.sleep(0.001 * 500)

		# turn all LEDs off
		print( " - Testing Reset()" )
		self.lp.Reset()


	def run(self, lpbox):
		self.setup()

		# Clear the buffer because the Launchpad remembers everything :-)
		self.lp.ButtonFlush()

		butHit = 10

		while True:
			but = self.lp.ButtonStateRaw()

			if but != []:
				print( "Button Event: ", but )
				#self.lp.LedCtrlRaw( random.randint(0,127), random.randint(0,63), random.randint(0,63), random.randint(0,63) )
				if but[1]:
					i = random.randint(0, 128)
					self.lp.LedCtrlRawByCode( but[0], i )
					lpbox.setCodeColor( but[0], i )
				else:
					self.lp.LedCtrlRawByCode( but[0], 0 )
					lpbox.setCodeColor( but[0], 0 )
			else:
				time.sleep(0.001 * 5)

		self.lp.Reset() # turn all LEDs off
		self.lp.Close() # close the Launchpad

fifths = CircleOfFifths(500)
elements.add_element(fifths)

lpbox = LaunchpadBox()
elements.add_element(lpbox)

lp_manager = LaunchpadManager()
lp_thread = Thread(target = lp_manager.run, args = (lpbox,))
lp_thread.start()

def update(dt, window=None):
	elements.update()

gl_prepare()
pyglet.clock.schedule_interval(update, 1./60, window)
pyglet.app.run()
pyglet.clock.schedule_interval(update, 0, window) # Specifying an interval of 0 prevents the function from being called again

if lp_thread:
	lp_thread.join()

print("All threads finished")
