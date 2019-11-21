#!/usr/bin/env python3
'''This module contains the Chip-8 class and its opcodes.'''


def hex_to_binary(data):
    '''Returns the binary equivalent of hex data.'''
    return bin(int(data, 16))[2:]


class MemoryBuffer(program):
    '''Emulated Chip-8 memory.'''
    def __init__(self, program):
        self.memory = '0' * 4096

        binary_data = hex_to_binary(program)
        self.memory[512:512+len(binary_data)] = binary_data

    def __setitem__(self, index, data):
        binary_data = hex_to_binary(data)
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

    def move_to_next_instruction(self):
        '''Increases the PC register to point to the next instruction.'''
        self.reg_pc += 16  # Instructions are 2 bytes long

    def read_nibble_from_addr(self, addr):
        '''Reads 2 bytes from addr.'''
        return self.memory[addr:addr+16]
