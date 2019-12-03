#!/usr/bin/env python3
'''This module decompiles any Chip-8 ROM file.'''

from sys import argv
from binascii import hexlify


if __name__ == '__main__':
    rom_file = read(argv[1], 'rb')

    counter = 0

    while True:
        read_word = f.read(2)[0]

        if not read_word:
            break
        
        print('{0:06x}: {}'.format(counter, decompile_instruction(read_word)))
