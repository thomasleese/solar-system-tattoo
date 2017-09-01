#!/usr/bin/env python

from argparse import ArgumentParser
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
        return (self.radius ** (1 / 5)) * (drawing['width'] * 0.0024)

    def draw(self, drawing, fill):
        angle = self.body.hlong

        orbit_radius = self.orbit_radius_for_drawing(drawing)

        centre = (drawing['width'] / 2, drawing['height'] / 2)

        position = (
            centre[0] + orbit_radius * math.cos(angle),
            centre[1] + orbit_radius * math.sin(angle),
        )

        radius = self.planet_radius_for_drawing(drawing)

        circle = drawing.circle(center=position, r=radius, fill=fill)
        drawing.add(circle)


class Orbit(Body):

    def draw(self, drawing, foreground_fill):
        radius = self.orbit_radius_for_drawing(drawing)

        centre = (drawing['width'] / 2, drawing['height'] / 2)

        circle = drawing.circle(
            center=centre, r=radius,
            fill='none', stroke=foreground_fill, stroke_width=1
        )

        drawing.add(circle)


class Sun(Body):

    def __init__(self):
        super().__init__(0)

    def draw(self, drawing, foreground_fill):
        centre = (drawing['width'] / 2, drawing['height'] / 2)
        radius = drawing['width'] * 0.04

        circle = drawing.circle(center=centre, r=radius, fill=foreground_fill)
        drawing.add(circle)


class SolarSystemTattoo:

    background_fill = 'rgb(50, 50, 50)'
    foreground_fill = 'white'

    def __init__(self, date, filename, size):
        self.drawing = svgwrite.Drawing(filename, size=(size, size))

        self.bodies = set(
            [Sun()] +
            [Orbit(i + 1) for i in range(8)] +
            [
                Planet(1, 'Mercury', 2439.7, ephem.Mercury(date)),
                Planet(2, 'Venus', 6051.8, ephem.Venus(date)),
                Planet(3, 'Earth', 6371.0, ephem.Sun(date)),
                Planet(4, 'Mars', 3389.5, ephem.Mars(date)),
                Planet(5, 'Jupiter', 69911, ephem.Jupiter(date)),
                Planet(6, 'Saturn', 58232, ephem.Saturn(date)),
                Planet(7, 'Uranus', 25362, ephem.Uranus(date)),
                Planet(8, 'Neptune', 24622, ephem.Neptune(date)),
            ]
        )

    def draw(self):
        self.draw_background()
        self.draw_bodies()

    def draw_background(self):
        centre = (self.drawing['width'] / 2, self.drawing['height'] / 2)
        radius = self.drawing['width'] / 2

        self.drawing.add(self.drawing.circle(
            center=centre, r=radius, fill=self.background_fill
        ))

    def draw_bodies(self):
        for body in self.bodies:
            body.draw(self.drawing, self.foreground_fill)

    def save(self):
        self.drawing.save()


def main():
    parser = ArgumentParser()
    parser.add_argument('date', type=dateutil.parser.parse)
    parser.add_argument('-o', '--output', default='tattoo.svg')
    parser.add_argument('-s', '--size', default=500, type=int)
    args = parser.parse_args()

    tattoo = SolarSystemTattoo(args.date, args.output, args.size)
    tattoo.draw()
    tattoo.save()


if __name__ == '__main__':
    main()
