#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import math
import time
import cairo
import layout

from .colors import get_color_from_note
from .musical_info import MusicDefs

class CircleOfFifthsElement(layout.root.LayoutElement):
    #PIANO_NOTE_NAMES = ['I', 'ii', 'II', 'iii', 'III', 'IV', 'v', 'V', 'vi', 'VI', 'vii', 'VII']
    PIANO_NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

    def __init__(self):
        self.border_gap = 10.
        height = 230 + self.border_gap * 2
        width = 230 + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

        self.set_root(MusicDefs.SCALE_DIATONIC_MAJOR, 0)

    def set_root(self, scale, note):
        self.scale = scale
        self.root_note = note % 12
        self.notes_in_scale = [(self.scale & 1<<((r - self.root_note) % 12) != 0) for r in range(12)]

    def get_minimum_size(self, ctx):
        return self.size

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()

        cx = xpos + width / 2.
        cy = ypos + height / 2.
        cr = min(width / 2. - self.border_gap, height / 2. - self.border_gap) - 30

        nx = [cx + cr * math.sin(2. * math.pi * ((n * 7) % 12) / 12.) for n in range(12)]
        ny = [cy - cr * math.cos(2. * math.pi * ((n * 7) % 12) / 12.) for n in range(12)]

        for n1 in range(12):
            for n_inc in [3, 4, 5, 7]:
                n2 = (n1 + n_inc) % 12
                ctx.set_source_rgb(0.9, 0.9, 0.9)
                ctx.set_line_width(1.0)
                ctx.move_to(nx[n1], ny[n1])
                ctx.line_to(nx[n2], ny[n2])
                ctx.stroke()

        #~ ctx.save()
        #~ for chord_signature, chord_root, chord_name, chord_intervals in self.chords_found:
            #~ if chord_intervals:
                #~ chord_color = self.get_chord_color(chord_root, chord_intervals)
                #~ ctx.set_source_rgb(*chord_color)
                #~ ctx.set_line_width(50.0)
                #~ ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                #~ n1 = chord_root
                #~ for d in chord_intervals + [chord_intervals[0]]:
                    #~ n2 = (chord_root + d) % 12
                    #~ ctx.move_to(nx[n1], ny[n1])
                    #~ ctx.line_to(nx[n2], ny[n2])
                    #~ ctx.stroke()
                    #~ n1 = n2
        #~ ctx.restore()

        #~ for n1 in range(12):
            #~ for n_inc in [3, 4]:
                #~ n2 = (n1 + n_inc) % 12
                #~ notes_in_scale = (self.notes_in_scale[n1] and self.notes_in_scale[n2])
                #~ if notes_in_scale:
                    #~ ctx.set_source_rgb(0.5, 0.5, 0.5)
                    #~ ctx.set_line_width(2.0)
                    #~ ctx.move_to(nx[n1], ny[n1])
                    #~ ctx.line_to(nx[n2], ny[n2])
                    #~ ctx.stroke()

        #~ for n1 in range(12):
            #~ for n_inc in [3, 4]:
                #~ n2 = (n1 + n_inc) % 12
                #~ notes_pressed = (self.pitch_classes_active[n1] > 0 and self.pitch_classes_active[n2] > 0)
                #~ if notes_pressed:
                    #~ ctx.set_source_rgb(0.3, 0.3, 0.3)
                    #~ ctx.set_line_width(6.0)
                    #~ ctx.move_to(nx[n1], ny[n1])
                    #~ ctx.line_to(nx[n2], ny[n2])
                    #~ ctx.stroke()

        for n in range(12):
            is_pressed = False

            if self.notes_in_scale[n % 12]:
                note_radius = 15
                note_border = 2.0
                color = get_color_from_note(n, 1.)
            else:
                note_radius = 10
                note_border = 1.0
                color = get_color_from_note(n, .1)

            ctx.set_source_rgb(*color)
            ctx.arc(nx[n], ny[n], note_radius, 0, 2. * math.pi)
            ctx.fill()

            if is_pressed:
                ctx.set_line_width(6.0)
            else:
                ctx.set_line_width(note_border)

            #ctx.move_to(x + note_radius, y)
            ctx.set_source_rgb(0.3, 0.3, 0.3)
            ctx.arc(nx[n], ny[n], note_radius, 0, 2. * math.pi)
            ctx.stroke()

            if (n % 12 == self.root_note):
                ctx.set_source_rgb(0., 0., 0.)
                ctx.arc(nx[n], ny[n], note_radius + 6., 0, 2. * math.pi)
                ctx.set_line_width(1.0)
                ctx.stroke()

            label = self.PIANO_NOTE_NAMES[n % 12]
            ctx.set_source_rgb(0.1, 0.1, 0.1)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(note_radius + 2)
            text_extents = ctx.text_extents(str(label))
            ctx.move_to(nx[n] - text_extents.width / 2., ny[n] + text_extents.height / 2.)
            ctx.show_text(str(label))

        #~ ctx.restore()
