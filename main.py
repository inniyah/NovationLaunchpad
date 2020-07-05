#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from gi.repository import Gtk
from gi.repository import Rsvg

import cairo
import layout

import rtmidi

from components.piano_keyboard     import KeyboardManager, PianoElement
from components.novation_launchpad import LaunchpadManager, LaunchpadElement, LAUNCHPAD_LAYOUTS
from components.diagram_of_thirds  import DiagramOfThirdsElement
from components.circle_of_fifths   import CircleOfFifthsElement
from components.tonal_map          import TonalMapElement
from components.musical_info       import MusicDefs, MusicalInfo

import components.fluidsynth as fluidsynth

# This works for counting non-zero bits in 64-bit positive numbers
def count_bits(n):
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
    return n

class DummyElement(layout.root.LayoutElement):
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

import PIL.Image as Image

class ImageElement(layout.root.LayoutElement):
    def __init__(self, height, width):
        self.size = layout.datatypes.Point(height, width)
        self.surface = None
    def set_image(filename):
        img = Image.open(filename)
        self.surface = from_pil(img)
    def from_pil(im, alpha=1.0, format=cairo.FORMAT_ARGB32):
        """
        :param im: Pillow Image
        :param alpha: 0..1 alpha to add to non-alpha images
        :param format: Pixel format for output surface
        """
        assert format in (cairo.FORMAT_RGB24, cairo.FORMAT_ARGB32), "Unsupported pixel format: %s" % format
        if 'A' not in im.getbands():
            im.putalpha(int(alpha * 256.))
        arr = bytearray(im.tobytes('raw', 'BGRa'))
        surface = cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
        return surface
    def get_minimum_size(self, ctx):
        return self.size
    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()

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
        #~ self.svg = rsvg_handle.new_from_file("CircleOfTriads.svg")

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
        #~ cr.show_text("Novation Launchpad MIDI Player")

        #~ self.svg.render_cairo(cr)

        for element in  self.elements:
            cr.save()
            element.render(self.rect, cr)
            cr.restore()
        self.queue_draw()

class MidiOutput:
    def __init__(self, port_name):
        self.port_name = port_name
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_virtual_port(self.port_name)
        print(f"~ Virtual MIDI port: '{self.port_name}'")

        self.fs = fluidsynth.Synth()
        self.fs.start(driver="alsa")
        print("~ FluidSynth Started")

        self.sfid = self.fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
        for channel in range(0, 16):
            self.fs.program_select(channel, self.sfid, 0, 0)

    def __del__(self): # See:https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
        print("~ Closing MidiOutput")
        self.fs.delete()
        print("~ FluidSynth Closed")
        del self.fs

    def press(self, key, velocity=64, duration=0.5):
        self.fs.noteon(0, key + 19, velocity)
        if self.keyboard_handlers:
            for keyboard_handler in self.keyboard_handlers:
                keyboard_handler.press(key + 19, 1, True)
        time.sleep(duration)
        self.fs.noteoff(0, key + 19)
        if self.keyboard_handlers:
            for keyboard_handler in self.keyboard_handlers:
                keyboard_handler.press(key + 19, 1, False)

    @staticmethod
    def random_key(mean_key=44):
        x = random.gauss(mean_key, 10.0)
        if x < 1: x = 1
        elif x > 88: x = 88
        return int(round(x))
    @staticmethod
    def random_velocity():
        x = random.gauss(100.0, 10.0)
        if x < 1: x = 1
        elif x > 127: x = 127
        return int(round(x))
    @staticmethod
    def random_duration(self, mean_duration=2.0):
        x = random.gauss(mean_duration, 2.0)
        if x < 0.2: x = 0.2
        return x
    def random_play(self, num, mean_key, mean_duration):
        while num != 0:
            num -= 1
            key = self.random_key(mean_key)
            velocity = self.random_velocity()
            duration = self.random_duration(mean_duration)
            self.press(key, velocity, duration)

    def play_note(self, channel, note, velocity):
        print(f"[MIDI Output] ({channel}, {note}, {velocity})")
        if velocity > 0:
            self.fs.noteon(channel, note, velocity)
        else:
            self.fs.noteoff(channel, note)


def main():
    parser = argparse.ArgumentParser(description="Novation Launchpad MIDI Player")
    parser.add_argument('-m', '--midi-out', help="MIDI output port name to create", dest='port_name', default="LaunchpadMidi")
    parser.add_argument('-l', '--layout', help="Launchpad Layout", dest='layout', default="III_iii")
    args = parser.parse_args()

    midi_out = MidiOutput(args.port_name)

    music_info = MusicalInfo()
    music_info.set_root(60)

    piano = PianoElement(music_info)
    lpad = LaunchpadElement(music_info, LAUNCHPAD_LAYOUTS[args.layout])
    dthirds = DiagramOfThirdsElement(music_info)
    cfifths = CircleOfFifthsElement(music_info)
    tonalmap = TonalMapElement(music_info)

    box = layout.BoxLM()
    box.left = lpad
    box.top = piano
    box.center = tonalmap #dthirds
    box.bottom = DummyElement(50, 10)
    box.right = cfifths
    box.margin = 1

    window = MainWindow([box])

    piano_manager = KeyboardManager(piano, midi_out)

    lp_manager = LaunchpadManager(lpad, midi_out)
    lp_manager.start()

    Gtk.main()

    lp_manager.stop()

    print("All threads finished")

if __name__ == "__main__":    
    main()
