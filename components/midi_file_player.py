#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import math
import time
import cairo
import layout
import mido
import time
import sys

from .general_midi import MIDI_GM1_INSTRUMENT_NAMES, MIDI_PERCUSSION_NAMES
from .hmm_key_finding import find_music_key, get_music_key_name, get_root_note_from_music_key, get_scale_from_music_key

class MidiFileSoundPlayer():
    def __init__(self, midi_out=None):
        self.midi_out = midi_out

        #~ self.fs = fluidsynth.Synth()
        #~ self.fs.start(driver="alsa")
        #~ print("FluidSynth Started")
        #~ self.sfid = self.fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
        #~ for channel in range(0, 16):
            #~ self.fs.program_select(channel, self.sfid, 0, 0)

        self.midi_file = None
        self.chords_per_beat = {}
        self.full_song = {}
        self.instruments = set()
        self.music_key_per_bar = None
        self.running = False

    def load_file(self, filename):
        self.midi_file = mido.MidiFile(filename)
        print('Midi File: {}'.format(self.midi_file.filename))
        length = self.midi_file.length
        print('Song length: {} minutes, {} seconds'.format(int(length / 60), int(length % 60)))

        tempo = 500000
        ticks_per_beat = self.midi_file.ticks_per_beat
        time_signature_numerator = 4
        time_signature_denominator = 4
        clocks_per_click = 24

        count_ticks_in_total = 0
        count_ticks_in_beat = 0
        count_ticks_in_measure = 0
        num_bar = 1
        num_beat = 1
        current_bar_tick = 0
        current_beat_tick = 0
        pitch_classes_in_beat = 0
        bar_ticks = []

        # See: https://www.geeksforgeeks.org/python-find-the-closest-key-in-dictionary/
        self.chords_per_beat = {}

        scale_key = 0 # C
        scale_type = 0 # Major

        pitch_histogram_per_bar = []

        self.full_song = {}

        channel_programs = [0] * 16
        pitch_histogram = [0] * 12
        self.instruments = set()
        for message in mido.midifiles.tracks.merge_tracks(self.midi_file.tracks):
            total_ticks_in_beat = ticks_per_beat * 4 / time_signature_denominator
            total_ticks_in_measure = ticks_per_beat * time_signature_numerator * 4 / time_signature_denominator
            time_of_measure = mido.midifiles.units.tick2second(total_ticks_in_measure, self.midi_file.ticks_per_beat, tempo)

            notes_on = []
            notes_off = []

            if isinstance(message, mido.Message):
                if message.type == 'note_on':
                    if message.channel != 9: # Exclude percussion 
                        pitch_histogram[message.note % 12] += 1
                        pitch_classes_in_beat |= 1 << (message.note % 12)
                        notes_on.append((message.channel, message.note, channel_programs[message.channel]))
                elif message.type == 'note_off':
                    if message.channel != 9: # Exclude percussion 
                        pitch_histogram[message.note % 12] -= 1
                        notes_off.append((message.channel, message.note))
                elif message.type == 'program_change':
                    self.instruments.add(message.program)
                    channel_programs[message.channel] = message.program

                count_ticks_in_total += message.time
                count_ticks_in_measure += message.time
                count_ticks_in_beat += message.time

            elif isinstance(message, mido.MetaMessage):
                if message.type == 'set_tempo':
                    tempo = message.tempo
                elif message.type == 'time_signature':
                    time_signature_numerator = message.numerator
                    time_signature_denominator = message.denominator
                    clocks_per_click = message.clocks_per_click
                    num_ticks = 0
                elif message.type == 'key_signature':
                    #music_key = message.key
                    print('Key signature changed to {}'.format(message.key))

            try:
                current_tick_in_song = self.full_song[count_ticks_in_total]
            except (IndexError, KeyError):
                self.full_song[count_ticks_in_total] = [None, None, None, [], []]
                current_tick_in_song = self.full_song[count_ticks_in_total]
            current_tick_in_song[3] += notes_on
            current_tick_in_song[4] += notes_off

            while count_ticks_in_beat >= total_ticks_in_beat:
                num_beat += 1
                count_ticks_in_beat -= total_ticks_in_beat
                self.chords_per_beat[current_beat_tick] = pitch_classes_in_beat
                self.full_song[current_beat_tick][2] = pitch_classes_in_beat
                print(f"beat@{count_ticks_in_total}: {num_beat}:{current_beat_tick} -> {pitch_classes_in_beat:#06x} = {pitch_classes_in_beat:>012b}")
                current_beat_tick = count_ticks_in_total
                pitch_classes_in_beat = sum([1 << (n % 12) if pitch_histogram[n] > 0 else 0 for n in range(12)])

            while count_ticks_in_measure >= total_ticks_in_measure:
                h = sum([1 << (n % 12) if pitch_histogram[n] > 0 else 0 for n in range(12)])
                pitch_histogram_per_bar.append(h)
                self.full_song[current_bar_tick][1] = h
                print(f"Bar #{num_bar}: {pitch_histogram} ({time_of_measure:1f} s) -> {h:03x} ~ {h:012b}")
                bar_ticks.append(current_bar_tick)
                num_bar += 1
                current_bar_tick = count_ticks_in_total
                count_ticks_in_measure -= total_ticks_in_measure

        print(f"end@{count_ticks_in_total}: {num_beat}:{current_beat_tick} -> {pitch_classes_in_beat:#06x} = {pitch_classes_in_beat:>012b}")
        self.chords_per_beat[current_beat_tick] = pitch_classes_in_beat

        if count_ticks_in_measure:
            bar_ticks.append(current_bar_tick)

        self.music_key_per_bar = find_music_key(pitch_histogram_per_bar)
        print(['{:03x}={}'.format(v, get_music_key_name(s)) for v, s in zip(pitch_histogram_per_bar, self.music_key_per_bar)])

        for i, (v, s) in enumerate(zip(pitch_histogram_per_bar, self.music_key_per_bar)):
            self.full_song[bar_ticks[i]][0] = s
            self.full_song[bar_ticks[i]][1] = v

        print(f"end: {pitch_histogram}")
        print([MIDI_GM1_INSTRUMENT_NAMES[i + 1] for i in self.instruments])

        #print(self.full_song)

    def __del__(self):
        #~ self.fs.delete()
        #~ print("FluidSynth Closed")
        #~ del self.fs
        pass

    def stop(self):
        self.running = False

    def play(self):
        if self.midi_file.type == 2: # Can't merge tracks in type 2 (asynchronous) file
            return

        self.running = True

        #~ if self.keyboard_handlers:
            #~ for keyboard_handler in self.keyboard_handlers:
                #~ keyboard_handler.set_song_score(self.full_song)

        channel_programs = [0] * 16

        start_time = time.time() + 1.
        input_time = 0.0

        # The default tempo is 500000 microseconds per beat, which is 120 beats per minute (BPM)
        # You can use bpm2tempo() and tempo2bpm() to convert to and from beats per minute.
        # Note that tempo2bpm() may return a floating point number.
        tempo = 500000

        # Also called Pulses per Quarter note or PPQ. Typical values range from 96 to 480
        # You can use tick2second() and second2tick() to convert to and from seconds and ticks.
        # Note that integer rounding of the result might be necessary because MIDI files require ticks to be integers.
        ticks_per_beat = self.midi_file.ticks_per_beat

        # A Time Signature is two numbers, one on top of the other. The numerator describes the number of beats in a Bar,
        # while the denominator describes of what note value a beat is (ie, how many quarter notes there are in a beat).
        # If a time signature message is not present in a MIDI sequence, 4/4 signature is assumed.
        # 4/4 would be four quarter-notes per bar (MIDI default)
        # 4/2 would be four half-notes per bar (or 8 quarter notes)
        # 4/8 would be four eighth-notes per bar (or 2 quarter notes)
        # 2/4 would be two quarter-notes per bar
        time_signature_numerator = 4
        time_signature_denominator = 4

        # Metronome pulse in terms of the number of MIDI clock ticks per click
        # Assuming 24 MIDI clocks per quarter note, if the value of the sixth byte is 48, the metronome will click every
        # two quarter notes, or in other words, every half-note
        clocks_per_click = 24

        # Number of 32nd notes per beat. This byte is usually 8 as there is usually one quarter note per beat
        # and one quarter note contains eight 32nd notes.
        # It seems to be useless and unused in practice: https://www.midi.org/forum/473-smf-time-signature-confusion
        notated_32nd_notes_per_beat = 8

        count_ticks_in_total = 0
        count_ticks_in_beat = 0
        count_ticks_in_measure = 0
        num_bar = 1
        num_beat = 1

        pitch_classes_in_beat = self.chords_per_beat[0]
        music_key = self.music_key_per_bar[0]
        print(f"bar #1 (start) -> {get_music_key_name(music_key)}")

        #~ if self.keyboard_handlers:
            #~ for keyboard_handler in self.keyboard_handlers:
                #~ keyboard_handler.change_root(get_root_note_from_music_key(music_key), get_scale_from_music_key(music_key))
                #~ keyboard_handler.set_chord(pitch_classes_in_beat)

        print(f"beat@{count_ticks_in_total}: {num_beat} -> {pitch_classes_in_beat:#06x} = {pitch_classes_in_beat:>012b}")

        for message in mido.midifiles.tracks.merge_tracks(self.midi_file.tracks):
            if not self.running:
                break

            total_ticks_in_beat = ticks_per_beat * 4 / time_signature_denominator
            total_ticks_in_measure = ticks_per_beat * time_signature_numerator * 4 / time_signature_denominator

            if message.time > 0:
                time_delta = mido.midifiles.units.tick2second(message.time, self.midi_file.ticks_per_beat, tempo)
            else:
                time_delta = 0

            input_time += time_delta
            playback_time = time.time() - start_time
            time_to_next_event = input_time - playback_time

            # Find bar:beat:subbeat

            if not isinstance(message, mido.MetaMessage):
                count_ticks_in_total += message.time
                count_ticks_in_measure += message.time
                count_ticks_in_beat += message.time

            while count_ticks_in_beat >= total_ticks_in_beat:
                num_beat += 1
                count_ticks_in_beat -= total_ticks_in_beat
                pitch_classes_in_beat = self.chords_per_beat[count_ticks_in_total]
                print(f"beat@{count_ticks_in_total}: {num_beat} -> {pitch_classes_in_beat:#06x} = {pitch_classes_in_beat:>012b}")

                #~ for keyboard_handler in self.keyboard_handlers:
                    #~ keyboard_handler.set_chord(pitch_classes_in_beat)

            while count_ticks_in_measure >= total_ticks_in_measure:
                try:
                    music_key = self.music_key_per_bar[num_bar-1]
                except IndexError:
                    music_key = None
                num_bar += 1
                count_ticks_in_measure -= total_ticks_in_measure
                if not music_key is None:
                    print(f"bar #{num_bar} -> {get_music_key_name(music_key)}")

                    #~ if self.keyboard_handlers:
                        #~ for keyboard_handler in self.keyboard_handlers:
                            #~ keyboard_handler.change_root(get_root_note_from_music_key(music_key), get_scale_from_music_key(music_key))

                else:
                    print(f"bar #{num_bar}")

            if time_to_next_event > 0.0:
                time.sleep(time_to_next_event)

            current_timestamp = time.time_ns() / (10 ** 9) # Converted to floating-point seconds
            #sys.stdout.write(repr(message) + '\n')
            #sys.stdout.flush()
            if isinstance(message, mido.Message):
                if message.type == 'note_on':
                    if self.midi_out:
                        self.midi_out.play_note(message.channel, message.note, message.velocity)

                    #~ if self.keyboard_handlers:
                        #~ for keyboard_handler in self.keyboard_handlers:
                            #~ #self.last_notes.append((current_timestamp, message.note, message.channel, True))
                            #~ keyboard_handler.press(message.note, message.channel, True, message.channel == 9)

                elif message.type == 'note_off':
                    if self.midi_out:
                        self.midi_out.play_note(message.channel, message.note, 0)

                    #~ if self.keyboard_handlers:
                        #~ for keyboard_handler in self.keyboard_handlers:
                            #~ #self.last_notes.append((current_timestamp, message.note, message.channel, False))
                            #~ keyboard_handler.press(message.note, message.channel, False, message.channel == 9)

                elif message.type == 'control_change':
                    #print('Control {} for {} changed to {}'.format(message.control, message.channel, message.value))
                    pass

                elif message.type == 'program_change':
                    channel_programs[message.channel] = message.program
                    #~ self.fs.program_select(message.channel, self.sfid, 0, message.program)
                    #~ print('Program for {} changed to {} ("{}")'.format(message.channel, message.program, MIDI_GM1_INSTRUMENT_NAMES[message.program + 1]))
                    if self.midi_out:
                        self.midi_out.change_program(message.channel, message.program)

            elif isinstance(message, mido.MetaMessage):
                if message.type == 'set_tempo':
                    tempo = message.tempo
                    print('Tempo changed to {:.1f} BPM.'.format(mido.tempo2bpm(message.tempo)))
                elif message.type == 'time_signature':
                    time_signature_numerator = message.numerator
                    time_signature_denominator = message.denominator
                    clocks_per_click = message.clocks_per_click
                    notated_32nd_notes_per_beat = message.notated_32nd_notes_per_beat
                    num_ticks = 0
                    print(f'Time signature changed to {message.numerator}/{message.denominator}. Clocks per click: {message.clocks_per_click}, Notated 32nd Notes per_Beat: {message.notated_32nd_notes_per_beat}')
                elif message.type == 'key_signature':
                    print(f'Key signature changed to {message.key}')

            #~ if self.keyboard_handlers:
                #~ for keyboard_handler in self.keyboard_handlers:
                    #~ keyboard_handler.set_tick(count_ticks_in_total, tempo * 1e-6 / ticks_per_beat)

        #~ if self.keyboard_handlers:
            #~ for keyboard_handler in self.keyboard_handlers:
                #~ keyboard_handler.set_song_score({})
                #~ keyboard_handler.set_chord(0)
                #~ keyboard_handler.set_tick(0)
