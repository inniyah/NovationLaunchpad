#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import math
import time
import cairo
import layout

class DiagramOfThirdsElement(layout.root.LayoutElement):

    def __init__(self):

        self.border_gap = 10.
        height = 100 + self.border_gap * 2
        width = 100 + self.border_gap * 2
        self.size = layout.datatypes.Point(width, height)

    def get_minimum_size(self, data):
        return self.size

    def render(self, rect, ctx):
        pass
