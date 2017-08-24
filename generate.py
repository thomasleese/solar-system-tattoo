#!/usr/bin/env python

from argparse import ArgumentParser
from collections import namedtuple
import math
import random

import ephem
import dateutil.parser
import svgwrite


Planet = namedtuple('Planet', ['name', 'radius', 'body'])


class SolarSystemTattoo:

    def __init__(self, date, filename, size):
        self.date = date
        self.size = size
        self.half_size = size / 2
        self.center = (self.half_size, self.half_size)
        self.drawing = svgwrite.Drawing(filename, size=(size, size))

        self.planets = [
            Planet('Mercury', 2439.7, ephem.Mercury(date)),
            Planet('Venus', 6051.8, ephem.Venus(date)),
            Planet('Earth', 6371.0, ephem.Sun(date)),
            Planet('Mars', 3389.5, ephem.Mars(date)),
            Planet('Jupiter', 69911, ephem.Jupiter(date)),
            Planet('Saturn', 58232, ephem.Saturn(date)),
            Planet('Uranus', 25362, ephem.Uranus(date)),
            Planet('Neptune', 24622, ephem.Neptune(date)),
        ]

    def draw(self):
        self.draw_orbits()
        self.draw_sun()
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

    def draw_sun(self):
        sun = self.drawing.circle(
            center=self.center,
            r=self.size * 0.04,
            fill='black'
        )

        self.drawing.add(sun)

    def radius_for_planet(self, planet):
        return (planet.radius ** (1 / 5)) * (self.size * 0.0024)

    def angle_for_planet(self, planet):
        return planet.body.hlong

    def draw_planet(self, orbit, planet):
        radius = self.radius_for_orbit(orbit)
        angle = self.angle_for_planet(planet)
        center = (
            self.center[0] + radius * math.cos(angle),
            self.center[1] + radius * math.sin(angle),
        )

        planet = self.drawing.circle(
            center=center,
            r=self.radius_for_planet(planet),
            fill='black'
        )

        self.drawing.add(planet)

    def draw_planets(self):
        for i, planet in enumerate(self.planets):
            self.draw_planet(i, planet)


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
