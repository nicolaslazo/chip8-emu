#!/usr/bin/env python3
'''This module contains the Chip-8 class and its opcodes.'''


def data_to_binary(data):
    '''Returns the binary equivalent of hex data.'''
    return bin(int(data, 16))[2:]


class MemoryBuffer(program):
    '''Emulated Chip-8 memory'''
    def __init__(self, program):
        self.memory = '0' * 4096

        binary_data = data_to_binary(program)
        self.memory[512:512+len(binary_data)] = binary_data

    def __setitem__(self, index, data):
        binary_data = data_to_binary(data)
        self.memory = self.memory[:index] + binary_data + self.memory[index+len(data)]


class Chip8():
    '''Emulated Chip-8 machine.'''
    def __init__(self, program):
        # Memory buffer
        self.memory = MemoryBuffer(program)

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
