#!/usr/bin/env python3
'''This module contains the Chip-8 class and its opcodes.'''


def hex_to_binary(data):
    '''Returns the binary equivalent of hexadecimal data.'''
    return bin(int(data, 16))[2:]

def binary_to_hex(data):
    '''Returns the hexadecimal equivalent of binary data.'''
    return hex(int(data, 2))[2:]


class MemoryBuffer:
    '''Emulated Chip-8 memory.'''
    def __init__(self, program):
        self.memory = '0' * 4096

        binary_data = hex_to_binary(program)
        self[512] = binary_data

    def __setitem__(self, subscript, data):
        if isinstance(subscript, slice):
            slice_size = subscript.stop - subscript.start
            data = data[:slice_size]  # Truncates the data to fit in the slice

            self.memory = self.memory[:subscript.start] + data + [subscript.stop:]
        else:
            self.memory = self.memory[:subscript] + data + self.memory[subscript+1:]

    def __str__(self):
        print(self.memory)

    def read_word_from_addr(self, addr):
        '''Reads 2 bytes from addr.'''
        addr = int(addr, 16)
        return binary_to_hex(self.memory[addr:addr+16])

    def write_word_to_addr(self, data, addr):
        '''Writes 2 bytes to the specified memory address.'''
        memory[addr:addr+16] = hex_to_binary(data)


class Chip8:
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

    def push_to_stack(self, value):
        '''Pushes a value to the stack.'''
        if self.rg_sp == 15:
            throw Exception('Full stack.')

        self.reg_sp += 1
        self.stack[self.reg_sp] = value

    def pop_from_stack(self):
        '''Pops a value from the stack.'''
        if self.rg_sp == 0:
            throw Exception('Empty Stack')

        return_val = self.stack[self.rg_sp]
        self.rg_sp -= 1
        return return_val

    def execute_instruction(self, instruction):
        '''
        Given the instruction xyzw, calls the function instruction_x with yzw as an argument. Serves as an instruction search tree
        '''
        self.instruction_function[instruction[0]](instruction[1:])
