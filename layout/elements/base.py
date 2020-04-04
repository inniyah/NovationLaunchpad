# -*- coding: utf-8 -*-

import math
import cairo

from ..root import LayoutElement
from ..datatypes import Point, Rectangle

class BaseElement(LayoutElement):
    NullPoint = Point(0, 0)

    def __init__(self):
        pass

    def get_minimum_size(self, ctx):
        return BaseElement.NullPoint

    def render(self, Rectangle, ctx):
        pass

    def save_state(self, ctx):
        ctx.save()

    def restore_state(self, ctx):
        ctx.restore()

    def translate(self, ctx, x, y):
        ctx.translate(x, y)

    def scale(self, ctx, x, y):
        ctx.scale(x, y)

    def rotate(self, ctx, degrees):
        ctx.rotate(degrees * math.pi / 180)

    def text_width(self, ctx, text, *, font_name, font_size):
        ctx.save()
        ctx.select_font_face(font_name)
        ctx.set_font_size(font_size)
        _, _, _, _, x_adv, _ = ctx.text_extents(text)
        ctx.restore()
        return x_adv

    def draw_text(self, ctx, text, x, y, *, font_name, font_size, fill):
        ctx.save()
        ctx.select_font_face(font_name)
        ctx.set_font_size(font_size)
        ctx.set_source_rgb(*fill)
        ctx.translate(x, y)
        ctx.move_to(0, 0)
        ctx.scale(1, -1)
        ctx.show_text(text)
        ctx.restore()

    def _fill_and_stroke(self, ctx, stroke, stroke_width, stroke_dash, fill):
        if fill:
            ctx.set_source_rgb(*fill)
            ctx.fill_preserve()
        if stroke:
            ctx.set_source_rgb(*stroke)
            ctx.set_line_width(stroke_width)
            if stroke_dash:
                ctx.set_dash(stroke_dash)
            ctx.stroke()
        ctx.new_path()

    def draw_line(self, ctx, x0, y0, x1, y1, *, stroke,
            stroke_width=1, stroke_dash=None):
        ctx.save()
        ctx.new_path()
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        self._fill_and_stroke(stroke, stroke_width, stroke_dash, None)
        ctx.restore()

    def draw_rect(self, ctx, x, y, w, h, *,
            stroke=None, stroke_width=1, stroke_dash=None, fill=None):
        ctx.save()
        ctx.new_path()
        ctx.rectangle(x, y, w, h)
        self._fill_and_stroke(stroke, stroke_width, stroke_dash, fill)
        ctx.restore()

    def draw_image(self, ctx, img_filename, x, y, w, h):
        raise NotImplemented()

    def draw_polygon(self, ctx, *pts,
            close_path=True, stroke=None, stroke_width=1, stroke_dash=None, fill=None):
        """Draws the given polygon."""
        ctx.save()
        ctx.new_path()
        for x,y in zip(*[iter(pts)]*2):
            ctx.line_to(x, y)
        if close_path:
            ctx.close_path()
        self._fill_and_stroke(stroke, stroke_width, stroke_dash, fill)
        ctx.restore()

    def show_page(self, ctx):
        ctx.show_page()

    def clip_rect(self, ctx, x, y, w, h):
        ctx.rectangle(x, y, w, h)
        ctx.clip()
