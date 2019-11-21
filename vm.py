#!/usr/bin/env python3
'''This module contains the Chip-8 class and its opcodes.'''


def data_to_binary(data):
    '''Returns the binary equivalent of hex data.'''
    return bin(int(data, 16))[2:]


class Chip8():
    '''Emulated Chip-8 machine.'''
    def __init__(self):
        self.memory = '0' * 4096

        # Registers
        self.reg_v = [0] * 16
        self.reg_i = 0

        # Pseudo-registers
        self.reg_pc = 512  # Start of user available memory
        self.reg_sp = 0

        # Stack
        self.stack = [0] * 16

        # Keyboard input
        self.keyboard_input = 0

        # Display
        self.screen = [[0] * 64] * 32

    def load_binary(self, data):
        '''Loads a string of data unto memory, starting from 0x200.'''
        self.clear_memory()

        binary_data = data_to_binary(data)

        for (bit_value, bit_position) in enumerate(binary_data, 512):
            self.memory[bit_position] = str(bit_value)

        breakpoint()

    def clear_memory(self):
        '''Sets all the memory to zeroes.'''
        self.memory = '0' * 4096
