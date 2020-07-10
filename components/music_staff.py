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

    SCORE_MIN_NOTE, SCORE_MAX_NOTE = 36, 84 # from C2 to C6, both included
    SCORE_LINES = (43, 47, 50, 53, 57, 64, 67, 71, 74, 77) # G2, B2, D3, F3, A3, E4, G4, B4, D5, F5
    DIATONIC_NOTES = { 0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 6 }

    def __init__(self, music_info):
        self.music_info = music_info
        self.border_gap = 10.
        width, height = 300, 7 * 4 * 5
        self.size = layout.datatypes.Point(width + self.border_gap * 2, height + self.border_gap * 2)

        self.clefs_svg = Rsvg.Handle().new_from_file(os.path.join("artwork", "clefs.svg"))
        #~ self.ims = self.get_base_image(width, height)

    def __del__(self):
        self.clefs_svg.close()

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
        #~ self.clefs_svg.render_document(ctx, vp)
        self.clefs_svg.render_element(ctx, "#treble", vp)
        self.clefs_svg.render_element(ctx, "#bass", vp)

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
            print(f"Score Note {note}: octave = {octave} + cromatic = {cromatic_note} -> diatonic = {diatonic_note} -> yslot = {yslot}")
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
        vp.x, vp.y, vp.width, vp.height = score_xpos, score_ypos + self.yslot_for_note(80) * yslot_height, score_width, yslot_height * 11
        self.clefs_svg.render_element(ctx, "#treble", vp)
        vp.x, vp.y, vp.width, vp.height = score_xpos, score_ypos + self.yslot_for_note(61) * yslot_height, score_width, yslot_height * 11
        self.clefs_svg.render_element(ctx, "#bass", vp)

        for note in range(self.SCORE_MIN_NOTE, self.SCORE_MAX_NOTE + 1):
            x = cx + 10 * (note % 12)
            yslot = self.yslot_for_note(note)
            y = score_ypos + yslot * yslot_height

            ledger_line = note not in self.SCORE_LINES

            if ledger_line:
                ctx.set_source_rgb(0., 0., 0.)
                ctx.set_line_width(1)
                ctx.move_to(x - 6, y)
                ctx.line_to(x + 6, y)
                ctx.stroke()

            ctx.arc(x, y, 4, 0, 2. * math.pi)
            ctx.fill()

        ctx.restore()
