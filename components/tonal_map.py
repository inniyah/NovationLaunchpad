#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import math
import time
import cairo
import layout
import queue

from .colors import get_color_from_note
from .musical_info import MusicDefs

class TonalMapElement(layout.root.LayoutElement):
    NOTE_NAMES = ['I', 'ii', 'II', 'iii', 'III', 'IV', 'v', 'V', 'vi', 'VI', 'vii', 'VII']
    LOG_12TH_ROOT_OF_2 = math.log(math.pow(2,1/12))

    def __init__(self, music_info):
        self.music_info = music_info

        self.step_size = 10
        self.border_gap = 10.

        height = 350 + self.border_gap * 2
        width = 350 + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

    def get_minimum_size(self, ctx):
        return self.size

    def getNotePosition(self, diff_n):
        x_base = -3 * diff_n
        y_base = 4 * diff_n
        d_base = 7 * diff_n
        k = math.ceil((d_base - 12) / 24)
        x = x_base + 12 * k
        y = y_base - 12 * k
        d = y - x
        return (x, y)

    def getFreqPosition(self, f, f0=440):
        diff_n = math.log(f / f0) / self.LOG_12TH_ROOT_OF_2
        return self.getNotePosition(diff_n)

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()
        central_note = self.music_info.root_note
        notes_in_scale = self.music_info.notes_in_scale

        cx = xpos + width / 2.
        cy = ypos + height / 2.

        freq_base = 440.00
        midi_base = 69

        q = queue.Queue()

        scale = 7
        for semitone, name in enumerate( (self.NOTE_NAMES * 6)[1:] ):
            diff_n = semitone - 12 * 3 + 1
            color = get_color_from_note((central_note + diff_n) % 12, .3)
            x, y = self.getNotePosition(diff_n)
            q.put((name, color, cx + x * scale, cy - y * scale))

        ctx.save()
        while not q.empty():
            name, color, x, y = q.get()

            ctx.move_to(x, y)
            ctx.set_line_width(2)
            ctx.set_source_rgb(0.2, 0.2, 0.2)
            ctx.arc(x, y, 9, 0, 2. * math.pi)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*color)
            ctx.fill()
            
            label = f"{name}"
            ctx.set_source_rgb(0.0, 0.0, 0.0)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(8)
            text_extents = ctx.text_extents(str(label))
            ctx.move_to(x - text_extents.width / 2., y + text_extents.height / 2.)
            ctx.show_text(str(label))

        ctx.restore()
