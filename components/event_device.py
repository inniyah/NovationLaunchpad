#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import array
import math
import time
import random
import cairo
import layout
import evdev
import asyncio
import selectors

from threading import Thread, Lock

class EventDeviceManager:

    KEY2MIDI = {
        evdev.ecodes.ecodes['KEY_Z']: 60,
        evdev.ecodes.ecodes['KEY_S']: 61,
        evdev.ecodes.ecodes['KEY_X']: 62,
        evdev.ecodes.ecodes['KEY_D']: 63,
        evdev.ecodes.ecodes['KEY_C']: 64,
        evdev.ecodes.ecodes['KEY_V']: 65,
        evdev.ecodes.ecodes['KEY_G']: 66,
        evdev.ecodes.ecodes['KEY_B']: 67,
        evdev.ecodes.ecodes['KEY_H']: 68,
        evdev.ecodes.ecodes['KEY_N']: 69,
        evdev.ecodes.ecodes['KEY_J']: 70,
        evdev.ecodes.ecodes['KEY_M']: 71,
        evdev.ecodes.ecodes['KEY_Q']: 72,
        evdev.ecodes.ecodes['KEY_2']: 73,
        evdev.ecodes.ecodes['KEY_W']: 74,
        evdev.ecodes.ecodes['KEY_3']: 75,
        evdev.ecodes.ecodes['KEY_E']: 76,
        evdev.ecodes.ecodes['KEY_R']: 77,
        evdev.ecodes.ecodes['KEY_5']: 78,
        evdev.ecodes.ecodes['KEY_T']: 79,
        evdev.ecodes.ecodes['KEY_6']: 80,
        evdev.ecodes.ecodes['KEY_Y']: 81,
        evdev.ecodes.ecodes['KEY_7']: 82,
        evdev.ecodes.ecodes['KEY_U']: 83,
        evdev.ecodes.ecodes['KEY_I']: 84,
        evdev.ecodes.ecodes['KEY_9']: 85,
        evdev.ecodes.ecodes['KEY_O']: 86,
        evdev.ecodes.ecodes['KEY_0']: 87,
        evdev.ecodes.ecodes['KEY_P']: 88,
    }

    def __init__(self, evdev_list, midi_out=None):
        print(f"~ Creating EventDeviceManager: {evdev_list}")
        self.running = False
        self.thread = Thread(target = self._run, args = (evdev_list, True, midi_out))
        self.asyncio_loop = None

    def __del__(self): # See:https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
        print("~ Closing EventDeviceManager")
        self.stop()

    def _run(self, evdev_paths, grab, midi_out):
        print(f"~ Running EventDeviceManager Thread ('{evdev_paths}')")

        self.asyncio_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.asyncio_loop)

        devices = [evdev.InputDevice(path) for path in evdev_paths]

        if grab:
            for device in devices:
                device.grab()

        selector = selectors.DefaultSelector()

        for device in devices:
            selector.register(device, selectors.EVENT_READ) # This works because InputDevice has a `fileno()` method.

        ctrl_down = False
        while self.running:
            for key, mask in selector.select(0.1):
                device = key.fileobj
                for event in device.read():
                    #~ print(device.path, evdev.categorize(event), sep=': ')

                    if event.type == evdev.ecodes.EV_KEY:
                        if event.code == evdev.ecodes.KEY_LEFTCTRL:
                            ctrl_down = event.value != 0
                        elif event.code == evdev.ecodes.KEY_C:
                            if ctrl_down:
                                print("^C detected, exiting")
                                self.running = False
                                break

                    note = self.KEY2MIDI.get(event.code)
                    if note is not None and midi_out:
                        if event.value == 1:
                            midi_out.play_note(2, note, 127)
                        elif event.value == 0:
                            midi_out.play_note(2, note, 0)

        print(f"~ Stopping EventDeviceManager Thread ('{evdev_paths}')")

        self.asyncio_loop.stop()
        self.asyncio_loop.close()
        self.asyncio_loop = None

        if grab:
            for device in devices:
                device.ungrab()

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.thread = None
