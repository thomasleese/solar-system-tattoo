#!/usr/bin/env python

from argparse import ArgumentParser

import dateutil.parser


def main():
    parser = ArgumentParser()
    parser.add_argument('date', type=dateutil.parser.parse)
    parser.add_argument('-o', '--output', default='tattoo.svg')
    args = parser.parse_args()

    print(args)


if __name__ == '__main__':
    main()
