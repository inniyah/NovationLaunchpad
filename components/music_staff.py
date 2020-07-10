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
        width, height = 300, 200
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

        ctx.restore()
