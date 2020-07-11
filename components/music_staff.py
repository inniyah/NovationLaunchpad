#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Rsvg', '2.0')

import sys
sys.path.append('..')

import os
import math
import time
import cairo
import layout

from gi.repository import Rsvg

from .colors import get_color_from_note
from .musical_info import MusicDefs

class MusicStaffElement(layout.root.LayoutElement):

    MIN_NOTE, MAX_NOTE = 36, 84 # from C2 to C6, both included
    SCORE_MIN_NOTE, SCORE_MAX_NOTE, SCORE_MID_NOTE = 42, 78, 60
    SCORE_LINES = (43, 47, 50, 53, 57, 64, 67, 71, 74, 77) # G2, B2, D3, F3, A3, E4, G4, B4, D5, F5
    DIATONIC_NOTES = { 0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 6 }

    MAJOR_KEY_SIGNATURES = {
            0:  ( 0,  0,  0,  0,  0,  0,  0 ), # C Major

            #    Cb  Db  Eb  Fb  Gb  Ab  Bb
            5:  ( 0,  0,  0,  0,  0,  0, -1 ), # F Major
            10: ( 0,  0, -1,  0,  0,  0, -1 ), # Bb Major
            3:  ( 0,  0, -1,  0,  0, -1, -1 ), # Eb Major
            8:  ( 0, -1, -1,  0,  0, -1, -1 ), # Ab Major
            1:  ( 0, -1, -1,  0, -1, -1, -1 ), # Db Major
            6:  (-1, -1, -1,  0, -1, -1, -1 ), # Gb Major

            #     C#  D#  E#  F#  G#  A#  B#
            7:  ( 0,  0,  0,  1,  0,  0,  0 ), # G Major
            2:  ( 1,  0,  0,  1,  0,  0,  0 ), # D Major
            9:  ( 1,  0,  0,  1,  1,  0,  0 ), # A Major
            4:  ( 1,  1,  0,  1,  1,  0,  0 ), # E Major
            11: ( 1,  1,  0,  1,  1,  1,  0 ), # B Major
            6:  ( 1,  1,  1,  1,  1,  1,  0 ), # F# Major
    }

    def __init__(self, music_info):
        self.music_info = music_info
        self.border_gap = 10.
        width, height = 300, 7 * 4 * 5
        self.size = layout.datatypes.Point(width + self.border_gap * 2, height + self.border_gap * 2)

        self.symbols_svg = Rsvg.Handle().new_from_file(os.path.join("artwork", "music_symbols.svg"))
        #~ self.ims = self.get_base_image(width, height)

    def __del__(self):
        self.symbols_svg.close()

    def get_minimum_size(self, ctx):
        return self.size

    # See: http://zetcode.com/gfx/pycairo/images/
    # See: https://valadoc.org/cairo/Cairo.Context.set_source_surface.html
    def get_base_image(self, width, height):
        #~ return cairo.ImageSurface.create_from_png(os.path.join("artwork", "grand_staff.png"))

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)

        vp = Rsvg.Rectangle()
        vp.x, vp.y, vp.width, vp.height = 0, 0, width, height
        #~ self.symbols_svg.render_document(ctx, vp)
        self.symbols_svg.render_element(ctx, "#treble", vp)
        self.symbols_svg.render_element(ctx, "#bass", vp)

        ctx.set_source_rgba(1, 0, 0, 1);
        ctx.set_line_width(5);
        ctx.move_to(0, 0);
        ctx.line_to(200, 200);
        ctx.stroke();

        return surface

    def yslot_for_note(self, note):
            octave = note // 12
            cromatic_note = note % 12
            diatonic_note = self.DIATONIC_NOTES[cromatic_note]
            yslot = ( (7 - octave) * 7 - diatonic_note )
            #~ print(f"Score Note {note}: octave = {octave} + cromatic = {cromatic_note} -> diatonic = {diatonic_note} -> yslot = {yslot}")
            return yslot

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()

        cx = xpos + width / 2.
        cy = ypos + height / 2.

        ctx.save()

        #~ ctx.set_operator(cairo.OPERATOR_OVER);
        #~ ctx.set_source_surface(self.ims, xpos + self.border_gap, ypos + self.border_gap)
        #~ ctx.paint()

        score_xpos = xpos + self.border_gap
        score_ypos = ypos + self.border_gap
        score_width = (width - 2 * self.border_gap)
        score_height = (height - 2 * self.border_gap)
        yslot_height = score_height / (4 * 7)

        ctx.set_source_rgb(0.0, 0.1, 0.3)
        ctx.set_line_width(1)
        for note in self.SCORE_LINES:
            yslot = self.yslot_for_note(note)
            y = score_ypos + yslot * yslot_height
            ctx.move_to(score_xpos, y)
            ctx.line_to(score_xpos + score_width, y)
            ctx.stroke()

        vp = Rsvg.Rectangle()
        vp.width, vp.height = score_width, yslot_height * 13
        vp.x, vp.y = score_xpos, score_ypos + self.yslot_for_note(81) * yslot_height
        self.symbols_svg.render_element(ctx, "#treble", vp)
        vp.x, vp.y = score_xpos, score_ypos + self.yslot_for_note(62) * yslot_height
        self.symbols_svg.render_element(ctx, "#bass", vp)

        max_note = self.SCORE_MAX_NOTE
        for note in range(self.MAX_NOTE, max_note, -1):
            if self.music_info.keys_pressed[note]:
                max_note = note
                break

        min_note = self.SCORE_MIN_NOTE
        for note in range(self.MIN_NOTE, min_note - 1, 1):
            if self.music_info.keys_pressed[note]:
                min_note = note
                break

        vp = Rsvg.Rectangle()
        vp.width, vp.height = yslot_height * 2.5, yslot_height * 5

        for note in range(self.MIN_NOTE, self.MAX_NOTE + 1):
            x = cx
            yslot = self.yslot_for_note(note)
            y = score_ypos + yslot * yslot_height

            if (yslot % 2) == 0:
                ledger_line = note > self.SCORE_MAX_NOTE and note <= max_note

                if (note > self.SCORE_MAX_NOTE and note <= max_note) or \
                   (note < self.SCORE_MIN_NOTE and note >= min_note) or \
                   (note == self.SCORE_MID_NOTE and self.music_info.keys_pressed[note]):
                        ctx.set_source_rgb(0.0, 0.1, 0.3)
                        ctx.set_line_width(1)
                        ctx.move_to(x - 6, y)
                        ctx.line_to(x + 6, y)
                        ctx.stroke()

            if self.music_info.keys_pressed[note]:
                ctx.set_source_rgb(0.0, 0.0, 0.0)
                ctx.arc(x, y, 4, 0, 2. * math.pi)
                ctx.fill()

                vp.x, vp.y = x - vp.width, y - vp.height / 2
                #~ self.symbols_svg.render_element(ctx, "#flat", vp)
                #~ self.symbols_svg.render_element(ctx, "#sharp", vp)

        ctx.restore()
