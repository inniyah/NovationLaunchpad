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

        self.half_w = 350 // 2
        self.half_h = 350 // 2

        height = self.half_h * 2 + self.border_gap * 2
        width = self.half_w * 2 + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

        max_octaves = 10
        self.keys_pressed = [0] * (12 * max_octaves)

    def get_minimum_size(self, ctx):
        return self.size

    def getNotePosition(self, diff_n):
        x_base = -3 * diff_n
        y_base = 4 * diff_n
        d_base = 7 * diff_n
        k = math.ceil(10000 + (d_base - 12) / 24) - 10000
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

        ang = -math.pi/4
        scale = 7
        cang = scale * math.cos(ang)
        sang = scale * math.sin(ang)

        q = queue.Queue()

        for semitone in range(6 * 12):
            diff_n = semitone - 12 * 3 + 1
            note = central_note + diff_n
            name = self.music_info.note_names[note % 12]
            px, py = self.getNotePosition(diff_n)
            q.put((note, name, px, -py))

        ixy_list = [
            (0, 0),
            (cang * 12 + sang * 12, cang * 12 - sang * 12),
            (-cang * 12 - sang * 12, -cang * 12 + sang * 12),
        ]

        ctx.save()
        while not q.empty():
            note, name, px, py = q.get()

            x = cx + cang * px + sang * py
            y = cy + cang * py - sang * px

            if self.keys_pressed[note]:
                color = get_color_from_note(note % 12, 1.)
                ctx.set_line_width(5)
            else:
                color = get_color_from_note(note % 12, .3)
                if (note - central_note) % 12 == 0:
                    ctx.set_line_width(2)
                else:
                    ctx.set_line_width(1)
            ctx.set_source_rgb(0.2, 0.2, 0.2)

            label = f"{name}"
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(8)
            text_extents = ctx.text_extents(str(label))

            for ix, iy in ixy_list:
                xx = x + ix
                if xx < cx - self.half_w or xx > cx + self.half_w: continue

                yy = y + iy
                if yy < cy - self.half_h or yy > cy + self.half_h: continue

                ctx.move_to(xx, yy)
                ctx.arc(xx, yy, 9, 0, 2. * math.pi)
                ctx.stroke_preserve()
                ctx.set_source_rgb(*color)
                ctx.fill()

                ctx.set_source_rgb(0.0, 0.0, 0.0)
                ctx.move_to(xx - text_extents.width / 2., yy + text_extents.height / 2.)
                ctx.show_text(str(label))

        ctx.restore()

    def playNote(self, channel, note, velocity):
        if velocity:
            self.keys_pressed[note] |= (1<<channel)
        else:
            self.keys_pressed[note] &= ~(1<<channel)
