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

from threading import Thread, Lock

class EventDeviceManager:
    def __init__(self, evdev_list, midi_out=None):
        print(f"~ Creating EventDeviceManager: {evdev_list}")
        self.running = False
        self.thread = Thread(target = self._run, args = (midi_out,))

    def __del__(self): # See:https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
        print("~ Closing EventDeviceManager")
        self.finish()

    def setup(self):
        pass

    def finish(self):
        pass

    def _run(self, midi_out):
        print("~ Running EventDeviceManager")

        self.setup()

        while self.running:
                time.sleep(0.001 * 5)

        self.finish()

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
