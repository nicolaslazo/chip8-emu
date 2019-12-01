#!/usr/bin/env python3
'''This module contains the Chip-8 class and its opcodes.'''

from random import randint


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
        self.memory[512] = binary_data

    def __setitem__(self, subscript, data):
        if isinstance(subscript, slice):
            slice_size = subscript.stop - subscript.start
            data = data[:slice_size]  # Truncates the data to fit in the slice

            self.memory = self.memory[:subscript.start] + data + self.memory[subscript.stop:]
        else:
            self.memory = self.memory[:subscript] + data + self.memory[subscript+1:]

    def __str__(self):
        print(self.memory)

    def read_word_from_addr(self, addr):
        '''Reads 2 bytes from the specified memory address.'''
        return self._read_data_from_addr(addr, 16)

    def read_byte_from_addr(self, addr):
        '''Reads 1 byte from the specified memory address.'''
        return self._read_data_from_addr(addr, 8)

    def _read_data_from_addr(self, addr, bits):
        '''Reads n bits from the specified memory address.'''
        addr = int(addr, 16)
        return binary_to_hex(self.memory[addr:addr+bits])

    def write_word_to_addr(self, data, addr):
        '''Writes 2 bytes to the specified memory address.'''
        self._write_data_to_addr(data, addr, 16)

    def write_byte_to_addr(self, data, addr):
        '''Writes 1 byte to the specified memory address.'''
        self._write_data_to_addr(data, addr, 8)

    def _write_data_to_addr(self, data, addr, bits):
        '''Writes n bits to the specified memory address.'''
        self.memory[addr:addr+bits] = hex_to_binary(data)


class Chip8:
    '''Emulated Chip-8 machine.

    Parameters:
    io_manager: Audio and video manager class
    program: Chip-8 binary in binary string format

    '''
    def __init__(self, program, io_manager):
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

        # Audio, video, input manager
        self.io_manager = io_manager

        # Opcode categories
        self.instruction_category = {
            '0': self.instruction_0,
            '1': self.instruction_1,
            '2': self.instruction_2,
            '3': self.instruction_3,
            '4': self.instruction_4,
            '5': self.instruction_5,
            '6': self.instruction_6,
            '7': self.instruction_7,
            '8': self.instruction_8,
            '9': self.instruction_9,
            'a': self.instruction_a,
            'b': self.instruction_b,
            'c': self.instruction_c,
            'd': self.instruction_d,
            'e': self.instruction_e,
            'f': self.instruction_f
        }

    # Opcode implementations
    def execute_instruction(self, instruction):
        '''
        Given the instruction xyzw, calls the function instruction_x with yzw as an argument.
        Serves as a way to call a search tree.
        '''
        self.instruction_category[instruction[0]](instruction[1:])

    def instruction_0(self, arg):
        '''Redirects to 0nnn [SYS addr], 00E0 [CLS] or 00EE [RET].'''
        if arg == '0e0':
            self.instruction_00e0()
        elif arg == '0ee':
            self.instruction_00ee()
        else:
            self.instruction_0nnn(arg)

    def instruction_00e0(self):
        '''Instruction 00E0 [CLS].'''
        self.io_manager.video.clear_screen()

    def instruction_00ee(self):
        '''Instruction 00EE [RET].'''
        return_address = self.pop_from_stack()
        self.reg_pc = return_address

    def instruction_0nnn(self, addr):
        '''Instruction 0nnn [SYS addr].'''
        # This instruction is supposedly ignored by modern interpreters so I might delete it later
        self.reg_pc = int(addr)

    def instruction_1(self, addr):
        '''Instruction 1nnn [JP addr].'''
        self.reg_pc = int(addr)

    def instruction_2(self, addr):
        '''Instruction 2nnn [CALL addr].'''
        self.push_to_stack(self.reg_pc)
        self.reg_pc = int(addr)

    def instruction_3(self, arg):
        '''Instruction 3xkk [SE Vx, byte].'''
        x = arg[0]; kk = arg[1:]
        x = int(x); kk = int(kk)
        if self.reg_v[x] == kk:
            self.move_to_next_instruction()

    def instruction_4(self, arg):
        '''Instruction 4xkk [SNE Vx, byte].'''
        x = arg[0]; kk = arg[1:]
        x = int(x); kk = int(kk)
        if self.reg_v[x] != kk:
            self.move_to_next_instruction()

    def instruction_5(self, arg):
        '''Instruction 5xy0 [SE Vx, Vy].'''
        x, y, _ = arg  # Last nibble is not checked to be zero from now, will change if needed
        x = int(x); y = int(y)
        if self.reg_v[x] == self.reg_v[y]:
            self.move_to_next_instruction()

    def instruction_6(self, arg):
        '''Instruction 6xkk [LD Vx, byte].'''
        x = arg[0]; kk = arg[1:]
        x = int(x); kk = int(kk)
        self.reg_v[x] = kk

    def instruction_7(self, arg):
        '''Instruction 7xkk [ADD Vx, byte].'''
        x = arg[0]; kk = arg[1:]
        x = int(x); kk = int(kk)
        self.reg_v[x] += kk

    def instruction_8(self, arg):
        '''Redirects to 8xy[0-7] and 8xyE.'''
        functions = {
            '0': self.instruction_8xy0,
            '1': self.instruction_8xy1,
            '2': self.instruction_8xy2,
            '3': self.instruction_8xy3,
            '4': self.instruction_8xy4,
            '5': self.instruction_8xy5,
            '6': self.instruction_8xy6,
            '7': self.instruction_8xy7,
            'e': self.instruction_8xyE
        }

        (x, y, instruction_byte) = arg
        x = int(x, 16); y = int(y, 16)
        functions[instruction_byte](x, y)

    def instruction_8xy0(self, x, y):
        '''Instruction 8xy0 [LD Vx, Vy].'''
        self.reg_v[x] = self.reg_v[y]

    def instruction_8xy1(self, x, y):
        '''Instruction 8xy1 [OR Vx, Vy].'''
        self.reg_v[x] = self.reg_v[x] | self.reg_v[y]

    def instruction_8xy2(self, x, y):
        '''Instruction 8xy2 [AND Vx, Vy].'''
        self.reg_v[x] = self.reg_v[x] & self.reg_v[y]

    def instruction_8xy3(self, x, y):
        '''Instruction 8xy3 [XOR Vx, Vy].'''
        self.reg_v[x] = self.reg_v[x] ^ self.reg_v[y]

    def instruction_8xy4(self, x, y):
        '''Instruction 8xy4 [ADD Vx, Vy].'''
        self.reg_v[x] += self.reg_v[y]

        if self.reg_v[x] > 255:
            self.reg_v[x] -= 255
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

    def instruction_8xy5(self, x, y):
        '''Instruction 8xy5 [SUB Vx, Vy].'''
        # Set VF to NOT borrow
        if self.reg_v[x] > self.reg_v[y]:
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] -= self.reg_v[y]

    def instruction_8xy6(self, x, y):
        '''Instruction 8xy6 [SHR Vx {, Vy}].'''
        # Check if the least-significant bit is 1
        if self.reg_v[x] % 2:
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] /= 2

    def instruction_8xy7(self, x, y):
        '''Instruction 8xy7 [SUBN Vx, Vy].'''
        # Set VF to NOT borrow
        if self.reg_v[y] > self.reg_v[x]:
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] = self.reg_v[y] - self.reg_v[x]

    def instruction_8xyE(self, x, y):
        '''Instruction 8xyE [SHL Vx {, Vy}].'''
        # Check if there's overflow
        if bin(x)[2] == '1':
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] *= 2

    def instruction_9(self, arg):
        '''Instruction 9xy0 [SNE Vx, Vy].'''
        [x, y, _] = arg

        if x != y:
            self.move_to_next_instruction()

    def instruction_a(self, arg):
        '''Instruction Annn [LD I, addr].'''
        self.reg_i = int(arg, 16)

    def instruction_b(self, arg):
        '''Instruction Bnnn [JP V0, addr].'''
        self.reg_pc = self.reg_v[0] + int(addr, 16)

    def instruction_c(self, arg):
        '''Instruction Cxkk [RND Vx, byte].'''
        x = int(arg[0], 16); kk = int(arg[1:], 16)
        self.reg_v[x] = randint(0, 255) & int(kk, 16)
        
    def instruction_d(self, arg):
        '''Instruction Dxyn [DRW Vx, Vy, nibble].'''
        [x, y, bytes_to_read] = arg
        x = int(x, 16)
        y = int(y, 16)
        bytes_to_read = int(bytes_to_read, 16)

        sprite = self.memory.read_bytes_from_addr(self.reg_i, bytes_to_read)

        self.reg_v[15] = self.scr.check_collission(self.reg_v[x], self.reg_v[y], sprite)

        self.scr.draw_sprite(self.reg_v[x], self.reg_v[y], sprite)

    def instruction_e(self, arg):
        '''Redirects to either [SKP Vx] or [SKNP Vx].'''
        x = int(arg[0], 16)
        last_byte = arg[1:]

        if last_byte == '9e':
            self.instruction_Ex9E(self, x)
        elif last_byte == 'a1':
            self.instruction_ExA1(self, x)
        else:
            raise Exception('9xXX instruction not recognised.')

    def instruction_Ex9E(self, x):
        '''Instruction Ex9E [SKP Vx].'''
        if self.scr.key_pressed(self.reg_v[x]):
            self.move_to_next_instruction()

    def instruction_ExA1(self, x):
        '''Instruction ExA1 [SKNP Vx].'''
        if not self.scr.key_pressed(self.reg_v[x]):
            self.move_to_next_instruction()

    def instruction_f(self, arg):
        '''Redirects to all instructions starting with the F nibble.'''
        functions = {
            '07': self.instruction_Fx07,
            '0A': self.instruction_Fx0A,
            '15': self.instruction_Fx15,
            '18': self.instruction_Fx18,
            '1E': self.instruction_Fx1E,
            '29': self.instruction_Fx29,
            '33': self.instruction_Fx33,
            '55': self.instruction_Fx55,
            '65': self.instruction_Fx65
        }

        x = int(arg[0], 16)
        last_byte = arg[1:]

        functions[last_byte](x)

    def instruction_Fx07(self, x):
        '''Instruction Fx07 [LD Vx, DT].'''
        #TODO
        pass

    def instruction_Fx0A(self, x):
        '''Instruction Fx0A [LD Vx, K].'''
        #TODO
        pass

    def instruction_Fx15(self, x):
        '''Instruction Fx15 [LD DT, Vx].'''
        #TODO
        pass

    def instruction_Fx18(self, x):
        '''Instruction Fx18 [LD ST, Vx].'''
        #TODO
        pass

    def instruction_Fx1E(self, x):
        '''Instruction Fx1E [ADD I, Vx].'''
        self.reg_i += self.reg_v[x]

    def instruction_Fx29(self, x):
        '''Instruction Fx29 [LD F, Vx].'''
        #TODO
        pass

    def instruction_Fx33(self, x):
        '''Instruction Fx33 [LD B, Vx].'''
        i_addr = self.reg_i

        self.memory.write_word_to_addr((x // 100) % 10, i_addr)
        self.memory.write_word_to_addr((x // 10) % 10, i_addr + 16)
        self.memory.write_word_to_addr(x % 10, i_addr + 32)

    def instruction_Fx55(self, x):
        '''Instruction Fx55 [LD [I], Vx].'''
        for register_number in range(x):
            self.memory.write_byte_to_addr(self.reg_v[register_number], reg_i + 8 * register_number)

    def instruction_Fx65(self, x):
        '''Instruction Fx65 [LD Vx, [I]].'''
        for register_number in range(x):
            self.reg_v[register_number] = memory.read_byte_from_addr(self.reg_i + 8 * register_number)

    def move_to_next_instruction(self):
        '''Increases the PC register to point to the next instruction.'''
        self.reg_pc += 16  # Instructions are 2 bytes long

    def push_to_stack(self, value):
        '''Pushes a value to the stack.'''
        if self.reg_sp == 15:
            raise Exception('Full stack.')

        self.reg_sp += 1
        self.stack[self.reg_sp] = value

    def pop_from_stack(self):
        '''Pops a value from the stack.'''
        if self.reg_sp == 0:
            raise Exception('Empty Stack')

        return_val = self.stack[self.reg_sp]
        self.reg_sp -= 1
        return return_val
