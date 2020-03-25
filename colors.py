#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import math

from seagull import scenegraph as sg

def adj_color(red, green, blue, factor=1.0):
    return (int(red*factor), int(green*factor), int(blue*factor))

# See: https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
COLORS_RGB = [
    (60, 180, 75),   (230, 25, 75),   (67, 99, 216),   (255, 225, 25),  (245, 130, 49),
    (145, 30, 180),  (66, 212, 244),  (240, 50, 230),  (191, 239, 69),  (250, 190, 190),
    (70, 153, 144),  (230, 190, 255), (154, 99, 36),   (255, 250, 200), (128, 0, 0),
    (170, 255, 195), (128, 128, 0),   (255, 216, 177), (0, 0, 117),     (169, 169, 169),
]

COLORS_RGB = [sg.Color(*adj_color(r, g, b)) for (r, g, b) in COLORS_RGB]

def compass_to_rgb(self, hue, saturation=1., value=1.):
	h = float(hue)
	s = float(saturation)
	v = float(value)
	h60 = h / 60.0
	h60f = math.floor(h60)
	hi = int(h60f) % 6
	f = h60 - h60f
	p = v * (1 - s)
	q = v * (1 - f * s)
	t = v * (1 - (1 - f) * s)
	r, g, b = 0, 0, 0
	if hi == 0: r, g, b = v, t, p
	elif hi == 1: r, g, b = q, v, p
	elif hi == 2: r, g, b = p, v, t
	elif hi == 3: r, g, b = p, q, v
	elif hi == 4: r, g, b = t, p, v
	elif hi == 5: r, g, b = v, p, q
	return r, g, b

def get_color_from_note(self, note, saturation=1., value=1.):
	if note == -1:
		return (0.9, 0.9, 0.9)
	return self.compass_to_rgb(360. * ((note*7)%12)/12., saturation, value)

LAUNCHPAD_COLORS = [
	(0, 0, 0),       (37, 37, 37),    (143, 143, 143), (253, 253, 253),
	(255, 102, 88),  (255, 41, 0),    (110, 10, 0),    (34, 1, 0),
	(255, 200, 117), (255, 109, 0),   (110, 41, 0),    (48, 31, 0),
	(253, 250, 41),  (253, 250, 0),   (107, 105, 0),   (32, 31, 0),
	(142, 248, 54),  (68, 248, 0),    (23, 104, 0),    (23, 52, 0),
	(50, 248, 56),   (0, 248, 0),     (0, 104, 0),     (0, 31, 0),
	(49, 248, 87),   (0, 248, 0),     (0, 104, 0),     (0, 31, 0),
	(47, 249, 144),  (0, 248, 74),    (0, 105, 26),    (0, 36, 18),
	(42, 249, 190),  (0, 248, 162),   (0, 105, 64),    (0, 31, 18),
	(66, 203, 255),  (0, 183, 255),   (0, 81, 100),    (0, 20, 32),
	(80, 156, 255),  (0, 108, 255),   (0, 39, 109),    (0, 6, 33),
	(88, 101, 255),  (4, 51, 255),    (1, 16, 110),    (0, 2, 33),
	(151, 102, 255), (100, 53, 255),  (30, 19, 122),   (12, 6, 65),
	(255, 109, 255), (255, 64, 255),  (110, 22, 109),  (34, 3, 33),
	(255, 104, 150), (255, 44, 100),  (110, 12, 36),   (45, 2, 20),
	(255, 52, 0),    (173, 72, 0),    (142, 99, 0),    (78, 117, 0),
	(0, 70, 0),      (0, 101, 65),    (0, 103, 145),   (4, 51, 255),
	(0, 85, 96),     (37, 42, 219),   (143, 143, 143), (43, 43, 43),
	(255, 41, 0),    (196, 249, 0),   (183, 236, 0),   (97, 248, 0),
	(0, 150, 0),     (0, 248, 141),   (0, 183, 255),   (3, 63, 255),
	(70, 52, 255),   (140, 54, 255),  (195, 50, 144),  (83, 43, 0),
	(255, 98, 0),    (146, 226, 0),   (114, 248, 0),   (0, 248, 0),
	(0, 248, 0),     (75, 248, 116),  (0, 249, 212),   (97, 156, 255),
	(51, 102, 211),  (149, 146, 241), (222, 63, 255),  (255, 44, 109),
	(255, 145, 0),   (198, 188, 0),   (152, 248, 0),   (149, 111, 0),
	(74, 53, 0),     (6, 92, 2),      (0, 97, 71),     (24, 26, 54),
	(19, 45, 109),   (126, 77, 30),   (188, 26, 0),    (233, 104, 68),
	(229, 125, 0),   (255, 228, 0),   (167, 227, 0),   (111, 190, 0),
	(36, 37, 64),    (226, 250, 102), (132, 249, 197), (167, 171, 255),
	(158, 125, 255), (81, 81, 81),    (135, 135, 135), (228, 252, 253),
	(181, 24, 0),    (70, 4, 0),      (0, 213, 0),     (0, 79, 0),
	(198, 188, 0),   (78, 62, 0),     (195, 113, 0),   (93, 28, 0),
]


LAUNCHPAD_COLORS = [sg.Color(*adj_color(r, g, b)) for (r, g, b) in LAUNCHPAD_COLORS]