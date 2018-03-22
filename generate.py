#!/usr/bin/env python

from argparse import ArgumentParser
import calendar
from collections import namedtuple
import math
import random

import ephem
import dateutil.parser
import svgwrite


class Body:

    def __init__(self, orbit):
        self.orbit = orbit

    def orbit_radius_for_drawing(self, drawing):
        if self.orbit == 0:
            return 0
        return 50 + (((drawing['width'] / 2) - 50) / 8) * (self.orbit - 1)


class Planet(Body):

    def __init__(self, orbit, name, radius, body):
        super().__init__(orbit)

        self.name = name
        self.radius = radius
        self.body = body

    def planet_radius_for_drawing(self, drawing):
        return (self.radius ** (1 / 6)) * (drawing['width'] * 0.005)

    def draw(self, drawing, style):
        angle = self.body.hlong + 2.9939488041

        orbit_radius = self.orbit_radius_for_drawing(drawing)

        centre = (drawing['width'] / 2, drawing['height'] / 2)

        position = (
            centre[0] + orbit_radius * math.cos(angle),
            centre[1] + orbit_radius * math.sin(angle),
        )

        radius = self.planet_radius_for_drawing(drawing)

        circle = drawing.circle(
            center=position, r=radius, fill=style.planet_fill
        )

        drawing.add(circle)


class Orbit(Body):

    stroke_width = 2

    def draw(self, drawing, style):
        radius = self.orbit_radius_for_drawing(drawing)

        centre = (drawing['width'] / 2, drawing['height'] / 2)

        circle = drawing.circle(
            center=centre, r=radius,
            fill='none', stroke=style.orbit_stroke,
            stroke_width=self.stroke_width,
        )

        drawing.add(circle)


class Sun(Body):

    def __init__(self):
        super().__init__(0)

    def draw(self, drawing, style):
        centre = (drawing['width'] / 2, drawing['height'] / 2)
        radius = drawing['width'] * 0.04

        circle = drawing.circle(
            center=centre, r=radius, fill=style.planet_fill
        )

        drawing.add(circle)


class ClockHand(Body):

    def __init__(self, orbit, proportion, width):
        super().__init__(orbit)
        self.angle = (proportion - 0.25) * 2 * math.pi
        self.stroke_width = width

    def draw(self, drawing, style):
        centre = (drawing['width'] / 2, drawing['height'] / 2)
        radius = self.orbit_radius_for_drawing(drawing)

        end = (
            centre[0] + radius * math.cos(self.angle),
            centre[1] + radius * math.sin(self.angle),
        )

        line = drawing.line(
            start=centre, end=end,
            stroke=style.clock_stroke, stroke_width=self.stroke_width
        )

        drawing.add(line)


class MonthMarker(Body):

    stroke_width = 3

    def __init__(self, year, month):
        super().__init__(3)

        total_days = 366 if calendar.isleap(year) else 365
        current_day = 0
        for i in range(1, month):
            current_day += calendar.monthrange(year, i)[1]

        proportion = current_day / total_days

        self.angle = (proportion - 0.25) * 2 * math.pi

    def draw(self, drawing, style):
        centre = (drawing['width'] / 2, drawing['height'] / 2)
        radius = self.orbit_radius_for_drawing(drawing)

        start = (
            centre[0] + radius * math.cos(self.angle),
            centre[1] + radius * math.sin(self.angle),
        )

        end = (
            centre[0] + (radius + 8) * math.cos(self.angle),
            centre[1] + (radius + 8) * math.sin(self.angle),
        )

        line = drawing.line(
            start=start, end=end,
            stroke=style.month_marker_stroke, stroke_width=self.stroke_width
        )

        drawing.add(line)


class DayOfWeekMarker(Body):

    def __init__(self, orbit, angle):
        super().__init__(orbit)
        self.angle = angle

    def draw(self, drawing, style):
        orbit_radius = self.orbit_radius_for_drawing(drawing)

        centre = (drawing['width'] / 2, drawing['height'] / 2)

        position = (
            centre[0] + orbit_radius * math.cos(self.angle),
            centre[1] + orbit_radius * math.sin(self.angle),
        )

        radius = drawing['width'] * 0.008

        circle = drawing.circle(
            center=position, r=radius, fill=style.clock_stroke
        )

        drawing.add(circle)


class Clock:

    def __init__(self, date):
        weekday = calendar.weekday(date.year, date.month, date.day)

        minute_proportion = date.minute / 60

        self.parts = (
            [MonthMarker(date.year, month) for month in range(1, 13)] +
            [
                ClockHand(6, (date.hour % 12) / 12, 3),
                ClockHand(9, minute_proportion, 2),
            ] +
            [DayOfWeekMarker(i + 1.5, (minute_proportion - 0.25) * 2 * math.pi) for i in range(weekday + 1)]
        )

    def draw(self, drawing, style):
        for part in self.parts:
            part.draw(drawing, style)


class SolarSystemTattoo:

    def __init__(self, date, filename, size, style, inner_planets_only):
        self.drawing = svgwrite.Drawing(filename, size=(size, size))

        self.style = style

        planets = [
            Planet(1, 'Mercury', 2439.7, ephem.Mercury(date)),
            Planet(2, 'Venus', 6051.8, ephem.Venus(date)),
            Planet(3, 'Earth', 6371.0, ephem.Sun(date)),
            Planet(4, 'Mars', 3389.5, ephem.Mars(date)),
        ]

        if not inner_planets_only:
            planets += [
                Planet(5, 'Jupiter', 69911, ephem.Jupiter(date)),
                Planet(6, 'Saturn', 58232, ephem.Saturn(date)),
                Planet(7, 'Uranus', 25362, ephem.Uranus(date)),
                Planet(8, 'Neptune', 24622, ephem.Neptune(date)),
            ]

        self.bodies = (
            [Orbit(i + 1) for i in range(4 if inner_planets_only else 8)] +
            ([Clock(date)] if style.show_clock else []) +
            planets +
            [Sun()]
        )

    def draw(self):
        self.draw_background()
        self.draw_bodies()

    def draw_background(self):
        centre = (self.drawing['width'] / 2, self.drawing['height'] / 2)
        radius = self.drawing['width'] / 2

        self.drawing.add(self.drawing.circle(
            center=centre, r=radius, fill=self.style.background_fill
        ))

    def draw_bodies(self):
        for body in self.bodies:
            body.draw(self.drawing, self.style)

    def save(self):
        self.drawing.save()


class LightStyle:
    background_fill = 'none'
    planet_fill = 'rgb(70, 70, 70)'
    orbit_stroke = 'rgb(120, 120, 120)'

    show_clock = False
    clock_stroke = 'rgb(150, 150, 150)'
    month_marker_stroke = 'rgb(150, 150, 150)'


class DarkStyle:
    background_fill = 'rgb(100, 100, 100)'
    planet_fill = 'white'
    orbit_stroke = 'rgb(200, 200, 200)'

    show_clock = False
    clock_stroke = 'rgb(180, 180, 180)'
    month_marker_stroke = 'rgb(220, 220, 220)'


def main():
    styles = {
        'light': LightStyle,
        'dark': DarkStyle,
    }

    parser = ArgumentParser()
    parser.add_argument('date', type=dateutil.parser.parse)
    parser.add_argument('-o', '--output', default='tattoo.svg')
    parser.add_argument('-s', '--size', default=500, type=int)
    parser.add_argument('-t', '--style', choices=list(styles.keys()), default='dark')
    parser.add_argument('-i', '--inner', default=False, action='store_true')
    args = parser.parse_args()

    style = styles[args.style]

    tattoo = SolarSystemTattoo(args.date, args.output, args.size, style, args.inner)
    tattoo.draw()
    tattoo.save()


if __name__ == '__main__':
    main()
