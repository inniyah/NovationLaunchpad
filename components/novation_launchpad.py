#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import math
import time
import random
import cairo
import layout
from . import launchpad

from threading import Thread, Lock

from .colors import COLORS_RGB, LAUNCHPAD_COLORS, hsv_to_rgb

COLORS_RGB       = [(r / 255., g / 255., b / 255.) for (r, g, b) in COLORS_RGB]
LAUNCHPAD_COLORS = [(r / 255., g / 255., b / 255.) for (r, g, b) in LAUNCHPAD_COLORS]

LAUNCHPAD_LAYOUTS = {
    # (    D    ) (    A    ) (    E    )
    # (    F    ) [    C    ] (    G    )
    # ( G# / Ab ) ( D# / Eb ) ( A# / Bb )
    'VI_V': lambda x, y: (y - 3) * 9 + (x - 3) * 7,

    # (    A    ) (    E    ) (    B    )
    # (    F    ) [    C    ] (    G    )
    # ( C# / Db ) ( G# / Ab ) ( D# / Eb )
    'III_V': lambda x, y: (y - 3) * 4 + (x - 3) * 7,

    # ( C# / Db ) (    E    ) (    G    )
    # (    A    ) [    C    ] ( D# / Eb )
    # (    F    ) ( G# / Ab ) (    B    )
    'III_iii': lambda x, y: (y - 3) * 4 + (x - 3) * 3,

    # ( A# / Bb ) ( C# / Db ) (    E    )
    # (    A    ) [    C    ] ( D# / Eb )
    # ( G# / Ab ) (    B    ) (    D    )
    'ii_iii': lambda x, y: (y - 2) * 1 + (x - 2) * 3,

    # (    B    ) (    D    ) (    F    )
    # (    A    ) [    C    ] ( D# / Eb )
    # (    G    ) ( A# / Bb ) ( C# / Db )
    'II_iii': lambda x, y: (y - 3) * 2 + (x - 3) * 3,
}

class LaunchpadManager:
    MODE_PRO = "Pro"
    MODE_MK2 = "Mk2"
    MODE_CONTROL_XL = "XL"
    MODE_LAUNCHKEY_MINI = "LKM"
    MODE_DICER = "Dcr"
    MODE_MK1 = "Mk1"

    def __init__(self, lpbox, midi_out=None):
        self.mode = None
        self.lp = None
        self.running = False
        self.thread = Thread(target = self._run, args = (lpbox, midi_out))

    def __del__(self): # See:https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
        print("~ Closing LaunchpadManager")
        self.finish()

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
        if not self.lp is None:
            self.lp.Reset() # turn all LEDs off
            self.lp.Close() # close the Launchpad
            self.lp = None

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

    def _run(self, lpbox, midi_out):
        self.setup()

        # Clear the buffer because the Launchpad remembers everything :-)
        self.lp.ButtonFlush()

        butHit = 10

        while self.running:
            but = self.lp.ButtonStateRaw()

            if but != []:
                print( "Button Event: ", but )
                #self.lp.LedCtrlRaw( random.randint(0,127), random.randint(0,63), random.randint(0,63), random.randint(0,63) )
                if but[0] < 100:
                    button_x = but[0] % 10
                    button_y = but[0] // 10
                    if button_x <= 8 and button_y <= 8:
                        channel = 1
                        note = lpbox.music_info.root_note + lpbox.lp_layout(button_x - 1, button_y - 1)
                        velocity = 127 if but[1] else 0
                        print(f"Launchpad Note: [{button_x}, {button_y}] -> {note} ({lpbox.music_info.note_names[note%12]})")
                        if midi_out:
                            midi_out.play_note(channel, note, velocity)
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

class LaunchpadElement(layout.root.LayoutElement):
    def __init__(self, music_info, lp_layout):
        self.music_info = music_info
        self.lp_layout = lp_layout

        self.rows  = 8
        self.cols  = 8

        self.border_gap = 10.
        self.sq_width = 20.
        self.sq_height = 20.
        self.sq_hgap = 5.
        self.sq_vgap = 5.

        self.max_pos = 100
        self.null_color = (0.7, 0.8, 0.8)
        self.color = [self.null_color] * self.max_pos
        self.label = ['xx'] * self.max_pos

        height = (self.cols + 1) * self.sq_width + self.cols * self.sq_hgap + self.border_gap * 2
        width  = (self.rows + 1) * self.sq_height + self.rows * self.sq_vgap + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

    def get_minimum_size(self, ctx):
        return self.size

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()
        xpos += self.border_gap
        ypos += self.border_gap

        color = self.null_color
        border = (0.5, 0.5, 0.5)
        note_names = self.music_info.note_names

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

                #~ label = self.label[button_x + (7 - button_y) * 10]
                label = note_names[(self.music_info.root_note + self.lp_layout(button_x, 7 - button_y)) % 12]
                ctx.set_source_rgb(0.1, 0.1, 0.1)
                ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(min(self.sq_width, self.sq_height) * 0.6)
                text_extents = ctx.text_extents(str(label))
                ctx.move_to(x1 + self.sq_width / 2. - text_extents.width / 2., y1 + self.sq_height / 2. + text_extents.height / 2.)
                ctx.show_text(str(label))

        y = ypos + self.sq_height / 2.
        r = min(self.sq_width, self.sq_height) / 2.
        for button_x in range(self.cols):
            x = xpos + button_x * (self.sq_width + self.sq_hgap) + self.sq_width / 2.

            color = self.color[button_x + 80]
            ctx.set_source_rgb(*color)

            ctx.move_to(x + r, y)
            ctx.line_to(x + r, y)

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
