#!/usr/bin/env python

from argparse import ArgumentParser
from collections import namedtuple
import math
import random

import dateutil.parser
import svgwrite


Planet = namedtuple('Planet', ['name', 'radius'])


class SolarSystemTattoo:

    def __init__(self, date, filename, size):
        self.date = date
        self.size = size
        self.half_size = size / 2
        self.center = (self.half_size, self.half_size)
        self.drawing = svgwrite.Drawing(filename, size=(size, size))

        self.planets = [
            Planet('Mercury', 2439.7),
            Planet('Venus', 6051.8),
            Planet('Earth', 6371.0),
            Planet('Mars', 3389.5),
            Planet('Jupiter', 69911),
            Planet('Saturn', 58232),
            Planet('Uranus', 25362),
            Planet('Neptune', 24622),
        ]

    def draw(self):
        self.draw_orbits()
        self.draw_planets()

    def save(self):
        self.drawing.save()

    def radius_for_orbit(self, orbit):
        return 50 + ((self.half_size - 50) / 8) * orbit

    def draw_orbit(self, orbit):
        radius = self.radius_for_orbit(orbit)
        orbit = self.drawing.circle(
            center=self.center, r=radius,
            fill='none', stroke='black', stroke_width=1
        )
        self.drawing.add(orbit)

    def draw_orbits(self):
        for i, planet in enumerate(self.planets):
            self.draw_orbit(i)

    def radius_for_planet(self, planet):
        return (planet.radius ** (1 / 5)) * 1.2

    def draw_planet(self, orbit, angle, planet):
        radius = self.radius_for_orbit(orbit)
        center = (
            self.center[0] + radius * math.cos(angle),
            self.center[1] + radius * math.sin(angle),
        )

        planet = self.drawing.circle(
            center=center, r=self.radius_for_planet(planet), fill='black'
        )

        self.drawing.add(planet)

    def draw_planets(self):
        for i, planet in enumerate(self.planets):
            self.draw_planet(i, random.random() * math.pi, planet)


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
