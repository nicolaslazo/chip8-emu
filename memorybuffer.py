#!/usr/bin/env python3
'''This module contains the MemoryBuffer class.'''


class MemoryBuffer:
    '''Emulated Chip-8 memory.'''
    def __init__(self, program):
        self.memory = ['0'] * 4096

        program_size_in_bytes = int(len(program) / 2)

        self[512:512+program_size_in_bytes] = program

    def __setitem__(self, subscript, data):
        if isinstance(subscript, slice):
            self.memory = self.memory[:subscript.start] + [data[i:i+2] for i in range(0, len(data) // 2, 2)]+ self.memory[subscript.stop:]
        else:
            self.memory = self.memory[:subscript] + data + self.memory[subscript+1:]

    def __getitem__(self, subscript):
        if isinstance(subscript, slice):
            return ''.join(self.memory[slice.start, slice.stop])
        else:
            return self.memory[subscript]

    def __str__(self):
        print(self.memory)

    def read_word_from_addr(self, addr):
        '''Reads 2 bytes from the specified memory address.'''
        return self.read_data_from_addr(addr, 2)

    def read_byte_from_addr(self, addr):
        '''Reads 1 byte from the specified memory address.'''
        return self.read_data_from_addr(addr, 1)

    def read_data_from_addr(self, addr, bytes_to_read):
        '''Reads n bytes from the specified memory address.'''
        if isinstance(addr, str):
            addr = int(addr, 16)
        return ''.join(self.memory[addr:addr+bytes_to_read])

    def write_word_to_addr(self, data, addr):
        '''Writes 2 bytes to the specified memory address.'''
        self._write_data_to_addr(data, addr, 2)

    def write_byte_to_addr(self, data, addr):
        '''Writes 1 byte to the specified memory address.'''
        self._write_data_to_addr(data, addr, 1)

    def _write_data_to_addr(self, data, addr, bits):
        '''Writes n bits to the specified memory address.'''
        if isinstance(addr, str):
            addr = int(addr, 16)
        self.memory[addr:addr+bits] = [data[i:i+2] for i in range(0, len(data, 2))]  # Separates the data into byte-sized chunks
