#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import math
import time
import cairo
import layout

from .colors import get_color_from_note

class DiagramOfThirdsElement(layout.root.LayoutElement):
    #PIANO_NOTE_NAMES = ['I', 'ii', 'II', 'iii', 'III', 'IV', 'v', 'V', 'vi', 'VI', 'vii', 'VII']
    PIANO_NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

    SCALE_MAJOR_DIATONIC = (1<<0) + (1<<2) + (1<<4) + (1<<5) + (1<<7) + (1<<9) + (1<<11)

    def __init__(self):
        self.first_note = 48 - 2
        self.last_note = 84 + 2
        self.num_notes = self.last_note - self.first_note + 1
        self.step_size = 18

        self.border_gap = 10.
        height = 400 + self.border_gap * 2
        width = self.step_size * self.num_notes + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

        self.set_root(0)

    def set_root(self, note):
        self.root_note = note
        scale = self.SCALE_MAJOR_DIATONIC
        self.notes_in_scale = [(scale & 1<<((r - self.root_note) % 12) != 0) for r in range(12)]

    def get_minimum_size(self, ctx):
        return self.size

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()

        note_radius = self.step_size * 1.5 / 2.0
        base_y = ypos + height - self.border_gap - note_radius
        effective_h = (height - 2. * self.border_gap - 2. * note_radius)

        for i in range(self.num_notes):
            n = self.first_note + i
            x = xpos + self.border_gap + self.step_size * (i + 1)

            y_steps = (((n - self.root_note) * 7 - 7) % 24)
            y_step_height = effective_h / 23.
            y = base_y - y_step_height * y_steps

            ctx.set_source_rgb(0.9, 0.9, 0.9)
            ctx.move_to(x, ypos + self.border_gap)
            ctx.line_to(x, ypos + height - self.border_gap)
            ctx.stroke()

            if i >= 4 and y_steps >= 4:
                if self.notes_in_scale[n % 12] and self.notes_in_scale[(n + 8) % 12]:
                    ctx.set_source_rgb(0.0, 0.0, 0.0)
                else:
                    ctx.set_source_rgb(0.8, 0.8, 0.8)
                ctx.move_to(x, y)
                ctx.line_to(x - 4. * self.step_size, y + 4. * y_step_height)
                ctx.stroke()

            if i < self.num_notes - 3 and y_steps >= 3:
                if self.notes_in_scale[n % 12] and self.notes_in_scale[(n + 3) % 12]:
                    ctx.set_source_rgb(0.0, 0.0, 0.0)
                else:
                    ctx.set_source_rgb(0.8, 0.8, 0.8)
                ctx.move_to(x, y)
                ctx.line_to(x + 3. * self.step_size, y + 3. * y_step_height)
                ctx.stroke()

        for i in range(self.num_notes):
            n = self.first_note + i
            x = xpos + self.border_gap + self.step_size * (i + 1)
            y = base_y - effective_h / 23. * (((n - self.root_note) * 7 - 7) % 24)
            if self.notes_in_scale[n % 12]:
                r = note_radius
            else:
                r = note_radius * .7

            ctx.set_source_rgb(0., 0., 0.)
            ctx.move_to(x, y)
            ctx.line_to(x, y)
            ctx.stroke()

            border_color = (0., 0., 0.)
            if self.notes_in_scale[n % 12]:
                note_color = get_color_from_note(n, 1.)
                note_border = 2.0
            else:
                note_color = get_color_from_note(n, .1)
                note_border = 1.0

            ctx.set_source_rgb(*note_color)
            ctx.arc(x, y, r, 0, 2. * math.pi)
            ctx.set_line_width(1.0)
            ctx.fill_preserve()
            ctx.set_source_rgb(*border_color)
            ctx.set_line_width(note_border)
            ctx.stroke()

            if (n % 12 == self.root_note):
                ctx.set_source_rgb(0., 0., 0.)
                ctx.arc(x, y, r + 6., 0, 2. * math.pi)
                ctx.set_line_width(1.0)
                ctx.stroke()

            label = self.PIANO_NOTE_NAMES[n % 12]
            ctx.set_source_rgb(0.1, 0.1, 0.1)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(r + 2)
            text_extents = ctx.text_extents(str(label))
            ctx.move_to(x - text_extents.width / 2., y + text_extents.height / 2.)
            ctx.show_text(str(label))
