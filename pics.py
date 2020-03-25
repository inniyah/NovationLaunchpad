#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json

from seagull import scenegraph as sg
from seagull.xml import parse, serialize
from seagull.opengl.utils import gl_prepare, gl_reshape, gl_display
from seagull.scenegraph.transform import product, normalized

from colors import COLORS_RGB, LAUNCHPAD_COLORS

this_dir = os.path.dirname(os.path.realpath(__file__))

class JSONDebugEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return sorted(obj)
        if isinstance(obj, sg.Element):
            return [
                ['%s' % (c,) for c in type.mro(type(obj))],
                obj.__dict__,
            ]
        if isinstance(obj, object):
            return [
                ['%s' % (c,) for c in type.mro(type(obj))],
                obj.__dict__,
            ]
        try:
            ret = json.JSONEncoder.default(self, obj)
        except:
            ret = ('%s' % (obj,))
        return ret

class CircleOfFifths():
    NOTES = ['C', 'G', 'D', 'A', 'E', 'B', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']

    def __init__(self, x_pos=0, y_pos=0):
        with open(os.path.join(this_dir, "CircleOfFifths.svg")) as f:
            svg = f.read()
        self.model_root, self.model_elements = parse(svg)

        #~ sys.stdout.write(serialize(self.model_root))
        #~ sys.stdout.write(f"elements = {self.model_elements}\n")
        #~ json.dump(self.model_root, sys.stdout, cls=JSONDebugEncoder, indent=2, sort_keys=True)
        #~ json.dump(self.model_elements, sys.stdout, cls=JSONDebugEncoder, indent=2, sort_keys=True)
        #~ sys.stdout.write("\n") # Python JSON dump misses last newline

        (x_min, y_min), (x_max, y_max) = self.model_root.aabbox()
        self.width = x_max - x_min
        self.height = y_max - y_min
        self.model_root = sg.Use(
            self.model_root,
            transform=[sg.Translate(x_pos - x_min, y_pos - y_min)]
        )

        self.orig_fill_color = {}
        for note in self.NOTES:
            label = 'inner_' + note
            self.orig_fill_color[label] = self.model_elements[label].fill
            label = 'outer_' + note
            self.orig_fill_color[label] = self.model_elements[label].fill

    def root(self):
        return self.model_root

    def size(self):
        (x_min, y_min), (x_max, y_max) = self.model_root.aabbox()
        return (x_max - x_min), (y_max - y_min)

    def update(self):
        current_timestamp = time.time_ns() / (10 ** 9) # Converted to floating-point seconds

        for num_note in range(0, 12):
            note = self.NOTES[num_note]
            inner_label = 'inner_' + note
            outer_label = 'outer_' + note

            if True:
                self.model_elements[inner_label].fill = COLORS_RGB[1]
                self.model_elements[outer_label].fill = COLORS_RGB[2]
            else:
                self.model_elements[inner_label].fill = self.orig_fill_color[inner_label]
                self.model_elements[outer_label].fill = self.orig_fill_color[outer_label]

class LaunchpadBox():
    def __init__(self, x_pos=0, y_pos=0):
        with open(os.path.join(this_dir, "LaunchpadBox.svg")) as f:
            svg = f.read()
        self.model_root, self.model_elements = parse(svg)

        #~ sys.stdout.write(serialize(self.model_root))
        #~ sys.stdout.write(f"elements = {self.model_elements}\n")
        #~ json.dump(self.model_root, sys.stdout, cls=JSONDebugEncoder, indent=2, sort_keys=True)
        #~ json.dump(self.model_elements, sys.stdout, cls=JSONDebugEncoder, indent=2, sort_keys=True)
        #~ sys.stdout.write("\n") # Python JSON dump misses last newline

        (x_min, y_min), (x_max, y_max) = self.model_root.aabbox()
        self.width = x_max - x_min
        self.height = y_max - y_min
        self.model_root = sg.Use(
            self.model_root,
            transform=[sg.Translate(x_pos - x_min, y_pos - y_min)]
        )

        self.null_color = sg.Color(174, 200, 200)

    def setRgbColor(self, pos, r, g, b):
        pass

    def setCodeColor(self, pos, i):
        label = f"B{pos}"
        if i > 0 and i < len(LAUNCHPAD_COLORS):
            self.model_elements[label].fill = LAUNCHPAD_COLORS[i]
        else:
            self.model_elements[label].fill = self.null_color

    def root(self):
        return self.model_root

    def size(self):
        (x_min, y_min), (x_max, y_max) = self.model_root.aabbox()
        return (x_max - x_min), (y_max - y_min)

    def update(self):
        pass

class PianoOctave():
    def __init__(self, x_pos=0, y_pos=0):
        with open(os.path.join(this_dir, "PianoOctave.svg")) as f:
            svg = f.read()
        self.model_root, self.model_elements = parse(svg)

        #~ sys.stdout.write(serialize(self.model_root))
        #~ sys.stdout.write(f"elements = {self.model_elements}\n")
        #~ json.dump(self.model_root, sys.stdout, cls=JSONDebugEncoder, indent=2, sort_keys=True)
        #~ json.dump(self.model_elements, sys.stdout, cls=JSONDebugEncoder, indent=2, sort_keys=True)
        #~ sys.stdout.write("\n") # Python JSON dump misses last newline

        (x_min, y_min), (x_max, y_max) = self.model_root.aabbox()
        self.width = x_max - x_min
        self.height = y_max - y_min
        self.model_root = sg.Use(
            self.model_root,
            transform=[sg.Translate(x_pos - x_min, y_pos - y_min)]
        )

        #~ self.orig_fill_color = {}
        #~ for note in self.NOTES:
            #~ self.orig_fill_color[note] = self.model_elements[note].fill

    def pressKey(self, key):
        label = f"N{key:02}"
        #~ self.model_elements[key].fill = COLORS_RGB[1]

    def releaseKey(self, key):
        label = f"N{key:02}"

    def root(self):
        return self.model_root

    def size(self):
        (x_min, y_min), (x_max, y_max) = self.model_root.aabbox()
        return (x_max - x_min), (y_max - y_min)

    def update(self):
        pass

class PianoKeyboard():
    def __init__(self, num_octaves=10, x_pos=0, y_pos=0):
        self.octaves = [PianoOctave() for i in range(0, num_octaves)]
        self.elements = []
        self.width = 0
        self.height = 0
        self.keys_pressed = [0] * (12 * num_octaves)
        for octave in self.octaves:
            (x_min, y_min), (x_max, y_max) = octave.root().aabbox()
            element = sg.Use(
                octave.root(),
                transform=[sg.Translate(x_pos + self.width - x_min, y_pos - y_min)]
            )
            self.elements.append(element)
            self.width += x_max - x_min - 1
            self.height = y_max - y_min - 1
        self.model_root = sg.Group(self.elements)

    def root(self):
        return self.model_root

    def press(self, num_key, channel, action=True):
        num_octave = num_key // 12
        if action:
            self.keys_pressed[num_key] |= (1<<channel)
            if self.keys_pressed[num_key]:
                piano.octaves[num_octave].press(MusicKeybOctave.NOTES[num_key % 12], channel)
        else:
            self.keys_pressed[num_key] &= ~(1<<channel)
            if not self.keys_pressed[num_key]:
                piano.octaves[num_octave].release(MusicKeybOctave.NOTES[num_key % 12])

    def show(self, active=True):
        self.model_root.active = active

    def update(self):
        pass
