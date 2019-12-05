#!/usr/bin/env python3
'''This module contains the Chip-8 class and its opcodes.'''

from random import randint
from memorybuffer import MemoryBuffer
from timer import Timer

class Chip8:
    '''Emulated Chip-8 machine.

    Parameters:
    program: Chip-8 binary in binary string format
    io_manager: Audio and video manager class

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

        # Timers
        self.reg_dt = Timer()
        self.reg_st = Timer()

        # Stack
        self.stack = [0] * 16

        # Audio, video, input manager
        self.io_manager = io_manager.init()

        # Opcode categories
        self._instruction_category = {
            '0': self._instruction_0,
            '1': self._instruction_1,
            '2': self._instruction_2,
            '3': self._instruction_3,
            '4': self._instruction_4,
            '5': self._instruction_5,
            '6': self._instruction_6,
            '7': self._instruction_7,
            '8': self._instruction_8,
            '9': self._instruction_9,
            'A': self._instruction_A,
            'B': self._instruction_B,
            'C': self._instruction_C,
            'D': self._instruction_D,
            'E': self._instruction_E,
            'F': self._instruction_F
        }

    def run(self):
        '''Emulates the execution of a Chip-8 program.'''
        while True:  # TODO: find an execution endpoint
            to_execute = self.memory.read_word_from_addr(self.reg_pc)
            self._execute_instruction(to_execute)

            io_manager.video.refresh_display()

            self._move_to_next_instruction()

    # Opcode implementations
    def _execute_instruction(self, instruction):
        '''
        Given the instruction xyzw, calls the function _instruction_x with yzw as an argument.
        Serves as a way to call a search tree.
        '''
        self._instruction_category[instruction[0]](instruction[1:])

    def _instruction_0(self, arg):
        '''Redirects to 0nnn [SYS addr], 00E0 [CLS] or 00EE [RET].'''
        if arg == '0E0':
            self._instruction_00E0()
        elif arg == '0EE':
            self._instruction_00EE()
        else:
            self._instruction_0nnn(arg)

    def _instruction_00E0(self):
        '''Instruction 00E0 [CLS].'''
        self.io_manager.video.clear_screen()

    def _instruction_00EE(self):
        '''Instruction 00EE [RET].'''
        return_address = self.pop_from_stack()
        self.reg_pc = return_address

    def _instruction_0nnn(self, addr):
        '''Instruction 0nnn [SYS addr].'''
        # This instruction is supposedly ignored by modern interpreters so I might delete it later
        self.reg_pc = int(addr, 16)

    def _instruction_1(self, addr):
        '''Instruction 1nnn [JP addr].'''
        self.reg_pc = int(addr, 16)

    def _instruction_2(self, addr):
        '''Instruction 2nnn [CALL addr].'''
        self.push_to_stack(self.reg_pc)
        self.reg_pc = int(addr, 16)

    def _instruction_3(self, arg):
        '''Instruction 3xkk [SE Vx, byte].'''
        (x, kk) = (arg[0], arg[1:])
        (x, kk) = (int(x, 16), int(kk, 16))
        if self.reg_v[x] == kk:
            self.move_to_next_instruction()

    def _instruction_4(self, arg):
        '''Instruction 4xkk [SNE Vx, byte].'''
        (x, kk) = (arg[0], arg[1:])
        (x, kk) = (int(x, 16), int(kk, 16))
        if self.reg_v[x] != kk:
            self.move_to_next_instruction()

    def _instruction_5(self, arg):
        '''Instruction 5xy0 [SE Vx, Vy].'''
        (x, y, _) = arg  # Last nibble is not checked to be zero from now, will change if needed
        (x, y) = (int(x), int(y))
        if self.reg_v[x] == self.reg_v[y]:
            self.move_to_next_instruction()

    def _instruction_6(self, arg):
        '''Instruction 6xkk [LD Vx, byte].'''
        (x, kk) = (arg[0], arg[1:])
        (x, kk) = (int(x, 16), int(kk, 16))
        self.reg_v[x] = kk

    def _instruction_7(self, arg):
        '''Instruction 7xkk [ADD Vx, byte].'''
        (x, kk) = (arg[0], arg[1:])
        (x, kk) = (int(x, 16), int(kk, 16))
        self.reg_v[x] += kk

    def _instruction_8(self, arg):
        '''Redirects to 8xy[0-7] and 8xyE.'''
        functions = {
            '0': self._instruction_8xy0,
            '1': self._instruction_8xy1,
            '2': self._instruction_8xy2,
            '3': self._instruction_8xy3,
            '4': self._instruction_8xy4,
            '5': self._instruction_8xy5,
            '6': self._instruction_8xy6,
            '7': self._instruction_8xy7,
            'e': self._instruction_8xyE
        }

        (x, y, instruction_nibble) = arg
        (x, y) = (int(x, 16), int(y, 16))
        functions[instruction_nibble](x, y)

    def _instruction_8xy0(self, x, y):
        '''Instruction 8xy0 [LD Vx, Vy].'''
        self.reg_v[x] = self.reg_v[y]

    def _instruction_8xy1(self, x, y):
        '''Instruction 8xy1 [OR Vx, Vy].'''
        self.reg_v[x] = self.reg_v[x] | self.reg_v[y]

    def _instruction_8xy2(self, x, y):
        '''Instruction 8xy2 [AND Vx, Vy].'''
        self.reg_v[x] = self.reg_v[x] & self.reg_v[y]

    def _instruction_8xy3(self, x, y):
        '''Instruction 8xy3 [XOR Vx, Vy].'''
        self.reg_v[x] = self.reg_v[x] ^ self.reg_v[y]

    def _instruction_8xy4(self, x, y):
        '''Instruction 8xy4 [ADD Vx, Vy].'''
        self.reg_v[x] += self.reg_v[y]

        if self.reg_v[x] > 255:
            self.reg_v[x] %= 255
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

    def _instruction_8xy5(self, x, y):
        '''Instruction 8xy5 [SUB Vx, Vy].'''
        # Set VF to NOT borrow
        if self.reg_v[x] > self.reg_v[y]:
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] -= self.reg_v[y]

    def _instruction_8xy6(self, x, y):
        '''Instruction 8xy6 [SHR Vx {, Vy}].'''
        # Check if the least-significant bit is 1
        if self.reg_v[y] % 2:
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] = self.reg_v[y] // 2

    def _instruction_8xy7(self, x, y):
        '''Instruction 8xy7 [SUBN Vx, Vy].'''
        # Set VF to NOT borrow
        if self.reg_v[y] > self.reg_v[x]:
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] = self.reg_v[y] - self.reg_v[x]

    def _instruction_8xyE(self, x, y):
        '''Instruction 8xyE [SHL Vx {, Vy}].'''
        # Check if there's overflow
        if self.reg_v[y] % 2:
            self.reg_v[15] = 1
        else:
            self.reg_v[15] = 0

        self.reg_v[x] = self.reg_v[y] * 2

    def _instruction_9(self, arg):
        '''Instruction 9xy0 [SNE Vx, Vy].'''
        (x, y, _) = arg

        if x != y:
            self.move_to_next_instruction()

    def _instruction_A(self, arg):
        '''Instruction Annn [LD I, addr].'''
        self.reg_i = int(arg, 16)

    def _instruction_B(self, arg):
        '''Instruction Bnnn [JP V0, addr].'''
        self.reg_pc = self.reg_v[0] + int(arg, 16)

    def _instruction_C(self, arg):
        '''Instruction Cxkk [RND Vx, byte].'''
        (x, kk) = (arg[0], arg[1:])
        (x, kk) = (int(x, 16), int(kk, 16))
        self.reg_v[x] = randint(0, 255) & kk

    def _instruction_D(self, arg):
        '''Instruction Dxyn [DRW Vx, Vy, nibble].'''
        (x, y, bytes_to_read) = arg
        (x, y, bytes_to_read) = (int(x, 16), int(y, 16), int(bytes_to_read, 16))

        sprite = self.memory.read_data_from_addr(self.reg_i, bytes_to_read)

        self.reg_v[15] = self.scr.check_collission(self.reg_v[x], self.reg_v[y], sprite)

        self.scr.draw_sprite(self.reg_v[x], self.reg_v[y], sprite)

    def _instruction_E(self, arg):
        '''Redirects to either [SKP Vx] or [SKNP Vx].'''
        x = int(arg[0], 16)
        last_byte = arg[1:]

        if last_byte == '9E':
            self._instruction_Ex9E(self, x)
        elif last_byte == 'A1':
            self._instruction_ExA1(self, x)
        else:
            raise Exception('ExXX instruction not recognised.')

    def _instruction_Ex9E(self, x):
        '''Instruction Ex9E [SKP Vx].'''
        if self.scr.key_pressed(self.reg_v[x]):
            self.move_to_next_instruction()

    def _instruction_ExA1(self, x):
        '''Instruction ExA1 [SKNP Vx].'''
        if not self.scr.key_pressed(self.reg_v[x]):
            self.move_to_next_instruction()

    def _instruction_F(self, arg):
        '''Redirects to all instructions starting with the F nibble.'''
        functions = {
            '07': self._instruction_Fx07,
            '0A': self._instruction_Fx0A,
            '15': self._instruction_Fx15,
            '18': self._instruction_Fx18,
            '1E': self._instruction_Fx1E,
            '29': self._instruction_Fx29,
            '33': self._instruction_Fx33,
            '55': self._instruction_Fx55,
            '65': self._instruction_Fx65
        }

        x = int(arg[0], 16)
        last_byte = arg[1:]

        functions[last_byte](x)

    def _instruction_Fx07(self, x):
        '''Instruction Fx07 [LD Vx, DT].'''
        # TODO
        pass

    def _instruction_Fx0A(self, x):
        '''Instruction Fx0A [LD Vx, K].'''
        # TODO
        pass

    def _instruction_Fx15(self, x):
        '''Instruction Fx15 [LD DT, Vx].'''
        # TODO
        pass

    def _instruction_Fx18(self, x):
        '''Instruction Fx18 [LD ST, Vx].'''
        # TODO
        pass

    def _instruction_Fx1E(self, x):
        '''Instruction Fx1E [ADD I, Vx].'''
        self.reg_i += self.reg_v[x]

    def _instruction_Fx29(self, x):
        '''Instruction Fx29 [LD F, Vx].'''
        # TODO
        pass

    def _instruction_Fx33(self, x):
        '''Instruction Fx33 [LD B, Vx].'''
        i_addr = self.reg_i

        self.memory.write_word_to_addr((x // 100) % 10, i_addr)
        self.memory.write_word_to_addr((x // 10) % 10, i_addr + 2)
        self.memory.write_word_to_addr(x % 10, i_addr + 4)

    def _instruction_Fx55(self, x):
        '''Instruction Fx55 [LD [I], Vx].'''
        for register_number in range(x):
            self.memory.write_byte_to_addr(self.reg_v[register_number], self.reg_i + register_number)

    def _instruction_Fx65(self, x):
        '''Instruction Fx65 [LD Vx, [I]].'''
        for register_number in range(x):
            self.reg_v[register_number] = self.memory.read_byte_from_addr(self.reg_i + register_number)

    def _move_to_next_instruction(self):
        '''Increases the PC register to point to the next instruction.'''
        self.reg_pc += 2  # Instructions are 2 bytes long

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
