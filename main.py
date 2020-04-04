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

from components.piano_keyboard     import KeyboardManager, PianoElement
from components.novation_launchpad import LaunchpadManager, LaunchpadElement

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
    box.left = lpad
    box.top = piano
    box.center = DummyElement(30, 40)
    box.bottom = DummyElement(50, 10)
    box.right = DummyElement(20, 50)
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
