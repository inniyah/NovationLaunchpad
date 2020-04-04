#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Rsvg', '2.0')

import os
import sys
import math
import json
import time
import random
import argparse

import fluidsynth
import launchpad
import rtmidi
import mido
from threading import Thread, Lock
from colors import COLORS_RGB, LAUNCHPAD_COLORS, hsv_to_rgb

COLORS_RGB       = [(r / 255., g / 255., b / 255.) for (r, g, b) in COLORS_RGB]
LAUNCHPAD_COLORS = [(r / 255., g / 255., b / 255.) for (r, g, b) in LAUNCHPAD_COLORS]

from gi.repository import Gtk
from gi.repository import Rsvg

import cairo

import layout
from layout.elements.base import BaseElement
from layout.elements.mark import SignatureMark

# This works for counting non-zero bits in 64-bit positive numbers
def count_bits(n):
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
    return n

class KeyboardManager:
    def __init__(self, piano):
        #~ self.keyboard_handlers = keyboard_handlers
        #~ self.fs = fluidsynth.Synth()
        #~ self.fs.start(driver="alsa")
        #~ print("~ FluidSynth Started")
        #~ self.sfid = self.fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
        #~ #self.sfid = self.fs.sfload("OmegaGMGS2.sf2")
        #~ #self.sfid = self.fs.sfload("GeneralUser GS 1.471/GeneralUser GS v1.471.sf2")
        #~ #self.sfid = self.fs.sfload("fonts/Compifont_13082016.sf2")
        #~ self.fs.program_select(0, self.sfid, 0, 0)

        self.piano = piano

        self.midi_in = rtmidi.MidiIn()
        available_ports = self.midi_in.get_ports()
        if available_ports:
            midi_port_num = 1
            try:
                self.midi_in_port = self.midi_in.open_port(midi_port_num)
            except rtmidi.InvalidPortError:
                print("Failed to open MIDI input")
                self.midi_in_port = None
                return
            print("Using MIDI input Interface {}: '{}'".format(midi_port_num, available_ports[midi_port_num]))
        else:
            print("Creating virtual MIDI input.")
            self.midi_in_port = self.midi_in.open_virtual_port("midi_driving_in")

        self.midi_in.set_callback(self.midi_received)

    def __del__(self): # See:https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
        #~ self.fs.delete()
        #~ eprint("FluidSynth Closed")
        #~ del self.fs
        pass

    def midi_received(self, midi_event, data=None):
        current_timestamp = time.time_ns() / (10 ** 9) # Converted to floating-point seconds
        midi_msg, delta_time = midi_event
        if len(midi_msg) > 2:
            pressed = (midi_msg[2] != 0)
            note = midi_msg[1]
            pitch_class = midi_msg[1] % 12
            octave = midi_msg[1] // 12
            channel = 16

            print("%s" % ((pressed, note, octave, pitch_class),))
            if self.piano:
                self.piano.pressOrReleaseKey(note, channel, pressed)

class LaunchpadManager:
	MODE_PRO = "Pro"
	MODE_MK2 = "Mk2"
	MODE_CONTROL_XL = "XL"
	MODE_LAUNCHKEY_MINI = "LKM"
	MODE_DICER = "Dcr"
	MODE_MK1 = "Mk1"

	def __init__(self, lpbox):
		self.mode = None
		self.lp = None
		self.running = False
		self.thread = Thread(target = self._run, args = (lpbox,))

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

	def finish(self):
		self.lp.Reset() # turn all LEDs off
		self.lp.Close() # close the Launchpad

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

	def _run(self, lpbox):
		self.setup()

		# Clear the buffer because the Launchpad remembers everything :-)
		self.lp.ButtonFlush()

		butHit = 10

		while self.running:
			but = self.lp.ButtonStateRaw()

			if but != []:
				print( "Button Event: ", but )
				#self.lp.LedCtrlRaw( random.randint(0,127), random.randint(0,63), random.randint(0,63), random.randint(0,63) )
				if but[1]:
					i = random.randint(0, 128)
					self.lp.LedCtrlRawByCode( but[0], i )
					if lpbox:
						lpbox.setCodeColor( but[0], i )
				else:
					self.lp.LedCtrlRawByCode( but[0], 0 )
					if lpbox:
						lpbox.setCodeColor( but[0], 0 )
			else:
				time.sleep(0.001 * 5)

		self.finish()

	def start(self):
		self.running = True
		self.thread.start()

	def stop(self):
		self.running = False
		if self.thread:
			self.thread.join()

class PianoElement():
    WHITE_KEYS = set([0, 2, 4, 5, 7, 9, 11])
    PIANO_NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

    def __init__(self):
        self.white_key_width = 18.
        self.white_key_height = 100.
        self.octave_start = 3
        self.num_octaves = 5
        self.extra_keys = 1
        self.border_gap = 10.
        height = self.white_key_height + self.border_gap * 2
        width = self.white_key_width * (self.num_octaves * len(self.WHITE_KEYS) + self.extra_keys) + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

        max_octaves = 10
        self.keys_pressed = [0] * (12 * max_octaves)

    def get_minimum_size(self, data):
        return self.size

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()
        xpos += self.border_gap
        ypos += self.border_gap

        white_key_width = self.white_key_width
        white_key_height = self.white_key_height
        black_key_width = white_key_width * 7. / 12.
        black_key_height = white_key_height * .6

        # White Keys
        pos = 0
        for n in range(12 * self.octave_start, 12 * (self.octave_start + self.num_octaves) + self.extra_keys):
            if not (n % 12) in self.WHITE_KEYS:
                continue

            x1 = xpos + (pos) * white_key_width
            x2 = xpos + (pos + 1) * white_key_width
            pos += 1

            root_note = 0
            is_pressed = self.keys_pressed[n]
            channel = 1

            color = (1., 1., 1.)
            ctx.move_to(x1, ypos)
            ctx.line_to(x2, ypos)
            ctx.line_to(x2, ypos + white_key_height)
            ctx.line_to(x1, ypos + white_key_height)
            ctx.close_path()
            ctx.set_source_rgb(*color)
            if (n % 12) == root_note:
                ctx.set_source_rgb(1.0, 1.0, 0.8)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.5, 0.5, 0.5)
            ctx.set_line_width(1)
            ctx.stroke()

            press_x = (x1 + x2) / 2.
            press_y = ypos + white_key_height - 10
            press_r = white_key_width / 2

            if is_pressed:
                color = self.get_color_from_channel(channel, 0.5)
                ctx.set_source_rgb(*color)
                ctx.arc(press_x, press_y, press_r, 0, 2. * math.pi)
                ctx.fill()

            label = self.PIANO_NOTE_NAMES[n % 12]
            ctx.set_source_rgb(0., 0., 0.)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(8)
            text_extents = ctx.text_extents(str(label))
            ctx.move_to(press_x - text_extents.width/2., press_y + text_extents.height/2.)
            ctx.show_text(str(label))

        # Black Keys
        pos = 0
        for n in range(12 * self.octave_start, 12 * (self.octave_start + self.num_octaves) + self.extra_keys):
            x1 = xpos + (pos) * black_key_width
            x2 = xpos + (pos + 1) * black_key_width
            pos += 1

            if (n % 12) in self.WHITE_KEYS:
                continue

            is_pressed = self.keys_pressed[n]
            channel = 1

            color = (0., 0., 0.)
            ctx.move_to(x1, ypos)
            ctx.line_to(x2, ypos)
            ctx.line_to(x2, ypos + black_key_height)
            ctx.line_to(x1, ypos + black_key_height)
            ctx.close_path()
            ctx.set_source_rgb(*color)
            if (n % 12) == root_note:
                ctx.set_source_rgb(0., 0., 0.5)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.5, 0.5, 0.5)
            ctx.set_line_width(1)
            ctx.stroke()

            press_x = (x1 + x2) / 2.
            press_y = ypos + black_key_height - 6
            press_r = black_key_width / 2

            if is_pressed:
                color = self.get_color_from_channel(channel, 1.0, 0.5)
                ctx.set_source_rgb(*color)
                ctx.arc(press_x, press_y, press_r, 0, 2. * math.pi)
                ctx.fill()

            label = self.PIANO_NOTE_NAMES[n % 12]
            ctx.set_source_rgb(1., 1., 1.)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(6)
            text_extents = ctx.text_extents(str(label))
            ctx.move_to(press_x - text_extents.width/2., press_y + text_extents.height/2.)
            ctx.show_text(str(label))

    def get_color_from_note(self, note, saturation=1., value=1.):
        if note == -1:
            return (0.9, 0.9, 0.9)
        return hsv_to_rgb(360. * ((note*7)%12)/12., saturation, value)

    def get_color_from_channel(self, channel, saturation=1., value=1.):
        if channel == -1:
            return (0.9, 0.9, 0.9)
        return hsv_to_rgb(360. * ((channel*17)%32)/32., saturation, value)

    def pressOrReleaseKey(self, num_key, channel, press=True):
        num_octave = num_key // 12
        num_class = num_key % 12
        if press:
            self.keys_pressed[num_key] |= (1<<channel)
        else:
            self.keys_pressed[num_key] &= ~(1<<channel)

class LaunchpadElement():
    def __init__(self):
        self.rows  = 8
        self.cols  = 8

        self.border_gap = 10.
        self.sq_width = 20.
        self.sq_height = 20.
        self.sq_hgap = 4.
        self.sq_vgap = 4.

        self.max_pos = 100
        self.null_color = (0., 0., 0.)
        self.color = [self.null_color] * self.max_pos

        height = (self.cols + 1) * self.sq_width + self.cols * self.sq_hgap + self.border_gap * 2
        width  = (self.rows + 1) * self.sq_height + self.rows * self.sq_vgap + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

    def get_minimum_size(self, data):
        return self.size

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()
        xpos += self.border_gap
        ypos += self.border_gap

        color = self.null_color
        border = (0.5, 0.5, 0.5)

        for button_y in range(self.rows):
            y1 = ypos + (1 + button_y) * (self.sq_height + self.sq_vgap)
            y2 = y1 + self.sq_height
            for button_x in range(self.cols):
                x1 = xpos + button_x * (self.sq_width + self.sq_hgap)
                x2 = x1 + self.sq_width
                color = self.color[button_x + (7 - button_y) * 10]

                ctx.move_to(x1, y1)
                ctx.line_to(x2, y1)
                ctx.line_to(x2, y2)
                ctx.line_to(x1, y2)
                ctx.close_path()
                ctx.set_source_rgb(*color)
                ctx.fill_preserve()
                ctx.set_source_rgb(*border)
                ctx.set_line_width(1)
                ctx.stroke()

        y = ypos + self.sq_height / 2.
        r = min(self.sq_width, self.sq_height) / 2.
        for button_x in range(self.cols):
            x = xpos + button_x * (self.sq_width + self.sq_hgap) + self.sq_width / 2.
            color = self.color[button_x + 80]
            ctx.set_source_rgb(*color)
            ctx.arc(x, y, r, 0, 2. * math.pi)
            ctx.fill_preserve()
            ctx.set_source_rgb(*border)
            ctx.set_line_width(1)
            ctx.stroke()

        x = xpos + self.cols * (self.sq_width + self.sq_hgap) + self.sq_width / 2.
        for button_y in range(self.rows):
            y = ypos + (1 + button_y) * (self.sq_height + self.sq_vgap) + self.sq_height / 2.
            color = self.color[8 + (7 - button_y) * 10]
            ctx.set_source_rgb(*color)
            ctx.arc(x, y, r, 0, 2. * math.pi)
            ctx.fill_preserve()
            ctx.set_source_rgb(*border)
            ctx.set_line_width(1)
            ctx.stroke()

    def setRgbColor(self, pos, r, g, b):
        pass

    def setCodeColor(self, pos, i):
        if pos >= 104 and pos <= 111: pos -= 13
        x = pos % 10 - 1
        y = pos // 10 - 1
        if i > 0 and i < len(LAUNCHPAD_COLORS):
            self.color[x + y * 10] = LAUNCHPAD_COLORS[i]
        else:
            self.color[x + y * 10] = self.null_color

class DummyElement(BaseElement):
    def __init__(self, height, width):
        self.size = layout.datatypes.Point(height, width)
    def get_minimum_size(self, ctx):
        return self.size
    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()
        color = (1., 0., 1.)
        ctx.move_to(xpos, ypos)
        ctx.line_to(xpos + width, ypos)
        ctx.line_to(xpos + width, ypos + height)
        ctx.line_to(xpos, ypos + height)
        ctx.close_path()
        ctx.set_source_rgb(*color)
        ctx.fill_preserve()
        ctx.set_source_rgb(1., 1., 0.)
        ctx.set_line_width(2)
        ctx.stroke()

class MainWindow(Gtk.Window):
    def __init__(self, elements):
        super(MainWindow, self).__init__()
        self.elements = elements

        min_width, min_height = 0, 0
        for element in  self.elements:
            element_width, element_height = element.get_minimum_size(None)
            min_width = max(min_width, element_width)
            min_height = max(min_height, element_height)
        self.rect = layout.datatypes.Rectangle(0, 0, min_width, min_height)
        self.init_ui()

        rsvg_handle = Rsvg.Handle()
        self.svg = rsvg_handle.new_from_file("CircleOfTriads.svg")

    def init_ui(self):
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.add(darea)

        self.set_title("GTK window")
        self.resize(self.rect.w, self.rect.h)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_draw(self, wid, cr):
        #~ cr.set_source_rgb(0, 0, 0)
        #~ cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        #~ cr.set_font_size(40)
        
        #~ cr.move_to(10, 50)
        #~ cr.show_text("Disziplin ist Macht.")

        #~ self.svg.render_cairo(cr)

        for element in  self.elements:
            element.render(self.rect, cr)
        self.queue_draw()

def main():
    piano = PianoElement()
    lpad = LaunchpadElement()

    box = layout.BoxLM()
    box.left = DummyElement(20, 50)
    box.top = piano
    box.center = DummyElement(30, 40)
    box.bottom = DummyElement(50, 10)
    box.right = lpad
    box.margin = 1

    window = MainWindow([box])

    piano_manager = KeyboardManager(piano)

    lp_manager = LaunchpadManager(lpad)
    lp_manager.start()

    Gtk.main()

    lp_manager.stop()

    print("All threads finished")

if __name__ == "__main__":    
    main()
