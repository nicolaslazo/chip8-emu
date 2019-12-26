#!/usr/bin/env python3
'''This module contains the MemoryBuffer class.'''


FONTSET = 'F0909090F0\
2060202070\
F010F080F0\
F010F010F0\
9090F01010\
F080F010F0\
F080F090F0\
F010204040\
F090F090F0\
F090F010F0\
F090F09090\
E090E090E0\
F0808080F0\
E0909090E0\
F080F080F0\
F080F08080'


class MemoryBuffer:
    '''Emulated Chip-8 memory.'''
    def __init__(self, program):
        self.memory = ['00'] * 4096
        program_size_in_bytes = len(program) // 2

        self[0:80] = FONTSET
        self[512:512+program_size_in_bytes] = program

    def __setitem__(self, subscript, data):
        if isinstance(subscript, slice):
            new_slice = [data[i:i+2] for i in range(0, len(data), 2)]
            self.memory = self.memory[:subscript.start] + new_slice + self.memory[subscript.stop:]
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
        '''Read 2 bytes from the specified memory address.'''
        return self.read_data_from_addr(addr, 2)

    def read_byte_from_addr(self, addr):
        '''Read 1 byte from the specified memory address.'''
        return self.read_data_from_addr(addr, 1)

    def read_data_from_addr(self, addr, bytes_to_read):
        '''Read n bytes from the specified memory address.'''
        return ''.join(self.memory[addr:addr+bytes_to_read])

    def write_word_to_addr(self, data, addr):
        '''Write 2 bytes to the specified memory address.'''
        self._write_data_to_addr(data, addr, 2)

    def write_byte_to_addr(self, data, addr):
        '''Write 1 byte to the specified memory address.'''
        self._write_data_to_addr(data, addr, 1)

    def _write_data_to_addr(self, data, addr, n_bytes):
        '''Write n bytes to the specified memory address.'''
        data = hex(data)[2:].zfill(n_bytes * 2)
        self.memory[addr:addr+n_bytes] = [data[i:i+2] for i in range(0, len(data), 2)]  # Separates the data into byte-sized chunks
