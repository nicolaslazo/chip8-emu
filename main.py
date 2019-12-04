#!/usr/bin/env python3
'''This module is the main body of the emulator.'''

from sys import argv
from vm import Chip8
from iomanager import IOManager


def load_rom(input_file):
    '''Loads ROM file from the command line.'''
    try:
        with open(input_file, 'rb') as rom_file:
            return rom_file.read().hex()
    except IOError:
        print("Error: file not found")
        exit(1)


if __name__ == "__main__":
    GAME_ROM = load_rom(argv[1])

    io_manager = IOManager()
    io_manager.init()

    chip8 = Chip8(GAME_ROM, io_manager)
    chip8.run()
