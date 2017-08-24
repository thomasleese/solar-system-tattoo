#!/usr/bin/env python

from argparse import ArgumentParser

import dateutil.parser
import svgwrite


class SolarSystemTattoo:

    def __init__(self, date, filename, size):
        self.date = date
        self.size = size
        self.half_size = size / 2
        self.center = (self.half_size, self.half_size)
        self.drawing = svgwrite.Drawing(filename, size=(size, size))

    def draw(self):
        self.draw_orbits()

    def save(self):
        self.drawing.save()

    def radius_for_orbit(self, orbit):
        return 50 + ((self.half_size - 50) / 8) * orbit

    def draw_orbits(self):
        for i in range(8):
            radius = self.radius_for_orbit(i)
            orbit = self.drawing.circle(
                center=self.center, r=radius,
                fill='none', stroke='black', stroke_width=1
            )
            self.drawing.add(orbit)


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
