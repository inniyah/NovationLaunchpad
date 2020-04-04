#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pyglet
import time

from seagull import scenegraph as sg
from seagull.opengl.utils import gl_prepare, gl_reshape, gl_display


class Window(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		pyglet.window.Window.__init__(self, *args, **kwargs)
		self.alive = True

	def on_close(self):
		self.alive = False

	def run(self):
		while self.alive:
			self.on_draw()
			event = self.dispatch_events()
			sleep(1./100.)

window_width, window_height = 800, 600

window = pyglet.window.Window(width=window_width, height=window_height, vsync=False, resizable=True)
fps_display = pyglet.window.FPSDisplay(window)

LEFT, MIDDLE, RIGHT = range(3)

BUTTONS = {
	pyglet.window.mouse.LEFT:   LEFT,
	pyglet.window.mouse.MIDDLE: MIDDLE,
	pyglet.window.mouse.RIGHT:  RIGHT,
}


class GraphicElements():
	def __init__(self):
		self._elements = set()
		self._changed()

	def _changed(self):
		self._scene = sg.Group([e.root() for e in self._elements])
		self._feedback = sg.Group(fill=None, stroke=sg.Color.red)

	def add_element(self, e):
		self._elements.add(e)
		self._changed()

	def remove_element(self, e):
		self._elements.discard(e)
		self._changed()

	def update(self):
		for e in self._elements:
			e.update()

	def elements(self):
		return self._elements

	def scene(self):
		return self._scene

	def feedback(self):
		return self._feedback

elements = GraphicElements()

def keyboard(c):
	if c == 'q':
		sys.exit(0)

def mouse_button(button, pressed, x, y):
	pass

def mouse_move(x1, y1, drag):
	pass

@window.event
def on_resize(width, height):
	gl_reshape(width, height)

@window.event
def on_draw():
	start_time = time.time()

	pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
	pyglet.gl.glHint(pyglet.gl.GL_LINE_SMOOTH_HINT, pyglet.gl.GL_DONT_CARE)
	gl_display(elements.scene(), elements.feedback())

	#window.clear()
	#fps_display.draw()

	end_time = time.time()
	print(end_time-start_time)

@window.event
def on_key_press(symbol, modifiers):
	keyboard(chr(symbol))

@window.event
def on_mouse_press(x, y, button, modifiers):
	mouse_button(BUTTONS[button], True, x, window.height-y)

@window.event
def on_mouse_release(x, y, button, modifiers):
	mouse_button(BUTTONS[button], False, x, window.height-y)

@window.event
def on_mouse_motion(x, y, dx, dy):
	mouse_move(x, window.height-y, False)

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	mouse_move(x, window.height-y, True)

