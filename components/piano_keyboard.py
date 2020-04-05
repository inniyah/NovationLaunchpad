#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import math
import time
import cairo
import layout
import rtmidi

from .colors import hsv_to_rgb

class KeyboardManager:
    def __init__(self, piano):
        #~ self.keyboard_handlers = keyboard_handlers
        #~ self.fs = fluidsynth.Synth()
        #~ self.fs.start(driver="alsa")
        #~ print("~ FluidSynth Started")
        #~ self.sfid = self.fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
        #~ #self.sfid = self.fs.sfload("OmegaGMGS2.sf2")
        #~ #self.sfid = self.fs.sfload("GeneralUser GS 1.471/GeneralUser GS v1.471.sf2")
        #~ #self.sfid = self.fs.sfload("fonts/Compifont_13082016.sf2")
        #~ self.fs.program_select(0, self.sfid, 0, 0)

        self.piano = piano

        self.midi_in = rtmidi.MidiIn()
        available_ports = self.midi_in.get_ports()
        if available_ports:
            midi_port_num = 1
            try:
                self.midi_in_port = self.midi_in.open_port(midi_port_num)
            except rtmidi.InvalidPortError:
                print("Failed to open MIDI input")
                self.midi_in_port = None
                return
            print("Using MIDI input Interface {}: '{}'".format(midi_port_num, available_ports[midi_port_num]))
        else:
            print("Creating virtual MIDI input.")
            self.midi_in_port = self.midi_in.open_virtual_port("midi_driving_in")

        self.midi_in.set_callback(self.midi_received)

    def __del__(self): # See:https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
        #~ self.fs.delete()
        #~ eprint("FluidSynth Closed")
        #~ del self.fs
        pass

    def midi_received(self, midi_event, data=None):
        current_timestamp = time.time_ns() / (10 ** 9) # Converted to floating-point seconds
        midi_msg, delta_time = midi_event
        if len(midi_msg) > 2:
            pressed = (midi_msg[2] != 0)
            note = midi_msg[1]
            pitch_class = midi_msg[1] % 12
            octave = midi_msg[1] // 12
            channel = 16

            print("%s" % ((pressed, note, octave, pitch_class),))
            if self.piano:
                self.piano.pressOrReleaseKey(note, channel, pressed)

class PianoElement(layout.root.LayoutElement):
    WHITE_KEYS = set([0, 2, 4, 5, 7, 9, 11])

    def __init__(self, music_info):
        self.music_info = music_info

        self.white_key_width = 18.
        self.white_key_height = 100.
        self.octave_start = 3
        self.num_octaves = 5
        self.extra_keys = 1
        self.border_gap = 10.
        height = self.white_key_height + self.border_gap * 2
        width = self.white_key_width * (self.num_octaves * len(self.WHITE_KEYS) + self.extra_keys) + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

        max_octaves = 10
        self.keys_pressed = [0] * (12 * max_octaves)

    def get_minimum_size(self, ctx):
        return self.size

    def render(self, rect, ctx):
        xpos, ypos, width, height = rect.get_data()
        xpos += self.border_gap
        ypos += self.border_gap

        white_key_width = self.white_key_width
        white_key_height = self.white_key_height
        black_key_width = white_key_width * 7. / 12.
        black_key_height = white_key_height * .6

        root_note = self.music_info.root_note % 12
        note_names = self.music_info.note_names

        # White Keys
        pos = 0
        for n in range(12 * self.octave_start, 12 * (self.octave_start + self.num_octaves) + self.extra_keys):
            if not (n % 12) in self.WHITE_KEYS:
                continue

            x1 = xpos + (pos) * white_key_width
            x2 = xpos + (pos + 1) * white_key_width
            pos += 1

            is_pressed = self.keys_pressed[n]
            channel = 1

            color = (1., 1., 1.)
            ctx.move_to(x1, ypos)
            ctx.line_to(x2, ypos)
            ctx.line_to(x2, ypos + white_key_height)
            ctx.line_to(x1, ypos + white_key_height)
            ctx.close_path()
            ctx.set_source_rgb(*color)
            if (n % 12) == root_note:
                ctx.set_source_rgb(1.0, 1.0, 0.8)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.5, 0.5, 0.5)
            ctx.set_line_width(1)
            ctx.stroke()

            press_x = (x1 + x2) / 2.
            press_y = ypos + white_key_height - 10
            press_r = white_key_width / 2

            if is_pressed:
                color = self.get_color_from_channel(channel, 0.5)
                ctx.set_source_rgb(*color)
                ctx.arc(press_x, press_y, press_r, 0, 2. * math.pi)
                ctx.fill()

            label = note_names[n % 12]
            ctx.set_source_rgb(0., 0., 0.)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(8)
            text_extents = ctx.text_extents(str(label))
            ctx.move_to(press_x - text_extents.width/2., press_y + text_extents.height/2.)
            ctx.show_text(str(label))

        # Black Keys
        pos = 0
        for n in range(12 * self.octave_start, 12 * (self.octave_start + self.num_octaves) + self.extra_keys):
            x1 = xpos + (pos) * black_key_width
            x2 = xpos + (pos + 1) * black_key_width
            pos += 1

            if (n % 12) in self.WHITE_KEYS:
                continue

            is_pressed = self.keys_pressed[n]
            channel = 1

            color = (0., 0., 0.)
            ctx.move_to(x1, ypos)
            ctx.line_to(x2, ypos)
            ctx.line_to(x2, ypos + black_key_height)
            ctx.line_to(x1, ypos + black_key_height)
            ctx.close_path()
            ctx.set_source_rgb(*color)
            if (n % 12) == root_note:
                ctx.set_source_rgb(0., 0., 0.5)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.5, 0.5, 0.5)
            ctx.set_line_width(1)
            ctx.stroke()

            press_x = (x1 + x2) / 2.
            press_y = ypos + black_key_height - 6
            press_r = black_key_width / 2

            if is_pressed:
                color = self.get_color_from_channel(channel, 1.0, 0.5)
                ctx.set_source_rgb(*color)
                ctx.arc(press_x, press_y, press_r, 0, 2. * math.pi)
                ctx.fill()

            label = note_names[n % 12]
            ctx.set_source_rgb(1., 1., 1.)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(6)
            text_extents = ctx.text_extents(str(label))
            ctx.move_to(press_x - text_extents.width/2., press_y + text_extents.height/2.)
            ctx.show_text(str(label))

    def get_color_from_note(self, note, saturation=1., value=1.):
        if note == -1:
            return (0.9, 0.9, 0.9)
        return hsv_to_rgb(360. * ((note*7)%12)/12., saturation, value)

    def get_color_from_channel(self, channel, saturation=1., value=1.):
        if channel == -1:
            return (0.9, 0.9, 0.9)
        return hsv_to_rgb(360. * ((channel*17)%32)/32., saturation, value)

    def pressOrReleaseKey(self, num_key, channel, press=True):
        num_octave = num_key // 12
        num_class = num_key % 12
        if press:
            self.keys_pressed[num_key] |= (1<<channel)
        else:
            self.keys_pressed[num_key] &= ~(1<<channel)
