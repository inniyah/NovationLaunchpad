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

    def __init__(self, music_info):
        self.music_info = music_info
        self.border_gap = 10.
        width, height = 300, 7 * 4 * 5
        self.ims = self.get_base_image(width, height)
        self.size = layout.datatypes.Point(width + self.border_gap * 2, height + self.border_gap * 2)

    def get_minimum_size(self, ctx):
        return self.size

    # See: http://zetcode.com/gfx/pycairo/images/
    # See: https://valadoc.org/cairo/Cairo.Context.set_source_surface.html
    def get_base_image(self, width, height):
        #~ return cairo.ImageSurface.create_from_png(os.path.join("artwork", "grand_staff.png"))

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)

        rsvg_handle = Rsvg.Handle()
        svg = rsvg_handle.new_from_file(os.path.join("artwork", "grand_staff.svg"))
        dimensions = svg.get_dimensions()
        vp = Rsvg.Rectangle()
        vp.x, vp.y, vp.width, vp.height = 0, 0, width, height
        svg.render_document(ctx, vp)

        ctx.set_source_rgba(1, 0, 0, 1);
        ctx.set_line_width(5);
        ctx.move_to(0, 0);
        ctx.line_to(200, 200);
        ctx.stroke();

        svg.close()

        return surface

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()

        cx = xpos + width / 2.
        cy = ypos + height / 2.

        ctx.save()

        ctx.set_operator(cairo.OPERATOR_OVER);
        ctx.set_source_surface(self.ims, xpos + self.border_gap, ypos + self.border_gap)
        ctx.paint()

        score_lines = (43, 47, 50, 53, 57, # G2, B2, D3, F3, A3
                       64, 67, 71, 74, 77) # E4, G4, B4, D5, F5
        diatonic_notes = { 0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 6 }
        for note in range (36, 84 + 1): # from C2 to C6, both included
            octave = note // 12
            cromatic_note = note % 12
            diatonic_note = diatonic_notes[cromatic_note]

            y = ypos + self.border_gap + (height - 2 * self.border_gap) * ( (7 - octave) * 7 - diatonic_note ) / (4 * 8)

            ctx.set_source_rgb(0., 0., 0.)
            ctx.set_line_width(1)
            if note in score_lines:
                ctx.move_to(cx + note - 150, y)
                ctx.line_to(cx + note + 150, y)
            else:
                ctx.move_to(cx + note - 20, y)
                ctx.line_to(cx + note + 20, y)
            ctx.stroke()

            ctx.arc(xpos + 50 + 12 * note, y, 4, 0, 2. * math.pi)
            ctx.fill()

        ctx.restore()
