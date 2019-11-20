#!/usr/bin/env python3
'''This module is the main body of the emulator.'''

from sys import argv
from binascii import hexlify
from machine import Chip8


def load_rom(input_file):
    '''Loads ROM file from the command line.'''
    try:
        with open(input_file, 'rb') as rom_file:
            return hexlify(rom_file.read())
    except IOError:
        print("Error: file not found")
        exit(1)


if __name__ == "__main__":
    chip_8 = Chip8()

    GAME_ROM = load_rom(argv[1])
    chip_8.load_binary(GAME_ROM)
