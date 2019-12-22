#!/usr/bin/env python3
'''This module contains the Chip-8 class and its opcodes.'''

from random import randint
from memorybuffer import MemoryBuffer
from timer import Timer


def nnn_format_to_xkk(arg):
    '''Separates a 12-bit fuction argument into 4-bit and 8-bit arguments.'''
    arg_x = (arg & 0xF00) >> 8
    arg_kk = arg & 0x0FF

    return (arg_x, arg_kk)

def nnn_format_to_xyn(arg):
    '''Separates a 12-bit function argument into three 4-bit arguments.'''
    arg_x = (arg & 0xF00) >> 8
    arg_y = (arg & 0x0F0) >> 4
    arg_n = arg & 0x00F

    return (arg_x, arg_y, arg_n)

def nnn_to_bcd(arg):
    hundreds_digit = arg // 100
    tens_digit = (arg % 100) // 10
    ones_digit = (arg % 10)

    return (hundreds_digit, tens_digit, ones_digit)

class Chip8:
    '''Emulated Chip-8 machine.

    Parameters:
    program: Chip-8 binary in binary string format
    io_manager: Audio and video manager class

    '''
    def __init__(self, program):
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

        # Opcode categories
        self._instruction_lookup = [
            self._instruction_0,
            self._instruction_1,
            self._instruction_2,
            self._instruction_3,
            self._instruction_4,
            self._instruction_5,
            self._instruction_6,
            self._instruction_7,
            self._instruction_8,
            self._instruction_9,
            self._instruction_A,
            self._instruction_B,
            self._instruction_C,
            self._instruction_D,
            self._instruction_E,
            self._instruction_F
        ]

    def set_io_manager(self, io_manager):
        self.io_manager = io_manager

    def step(self):
        '''Emulates the execution of a Chip-8 program.'''
        to_execute = self.memory.read_word_from_addr(self.reg_pc)
        self._execute_instruction(to_execute)

        self._move_to_next_instruction()

    # Opcode implementations
    def _execute_instruction(self, instruction):
        '''
        Given the instruction xyzw, calls the function _instruction_x with yzw as an argument.
        Serves as a way to call a search tree.
        '''
        instruction_int = int(instruction, 16)
        instruction_category = (instruction_int & 0xF000) >> 12
        instruction_argument = instruction_int & 0x0FFF

        self._instruction_lookup[instruction_category](instruction_argument)

    def _instruction_0(self, arg):
        '''Redirects to 0nnn [SYS addr], 00E0 [CLS] or 00EE [RET].'''
        if arg == 0x00E0:
            self._instruction_00E0()
        elif arg == 0x00EE:
            self._instruction_00EE()
        else:
            self._instruction_0nnn(arg)

    def _instruction_00E0(self):
        '''Instruction 00E0 [CLS].'''
        self.io_manager.clear_screen()

    def _instruction_00EE(self):
        '''Instruction 00EE [RET].'''
        self.reg_pc = self.pop_from_stack()

    def _instruction_0nnn(self, addr):
        '''Instruction 0nnn [SYS addr].'''
        # This instruction is supposedly ignored by modern interpreters so I might delete it later
        self.reg_pc = addr

    def _instruction_1(self, addr):
        '''Instruction 1nnn [JP addr].'''
        self.reg_pc = addr

    def _instruction_2(self, addr):
        '''Instruction 2nnn [CALL addr].'''
        self.push_to_stack(self.reg_pc)
        self.reg_pc = addr

    def _instruction_3(self, arg):
        '''Instruction 3xkk [SE Vx, byte].'''
        (arg_x, arg_kk) = nnn_format_to_xkk(arg)
        if self.reg_v[arg_x] == arg_kk:
            self._move_to_next_instruction()

    def _instruction_4(self, arg):
        '''Instruction 4xkk [SNE Vx, byte].'''
        (arg_x, arg_kk) = nnn_format_to_xkk(arg)
        if self.reg_v[arg_x] != arg_kk:
            self._move_to_next_instruction()

    def _instruction_5(self, arg):
        '''Instruction 5xy0 [SE Vx, Vy].'''
        # Last nibble is not checked to be zero for now, will change if needed
        (arg_x, arg_y, _) = nnn_format_to_xyn(arg)
        if self.reg_v[arg_x] == self.reg_v[arg_y]:
            self._move_to_next_instruction()

    def _instruction_6(self, arg):
        '''Instruction 6xkk [LD Vx, byte].'''
        (arg_x, arg_kk) = nnn_format_to_xkk(arg)
        self.reg_v[arg_x] = arg_kk

    def _instruction_7(self, arg):
        '''Instruction 7xkk [ADD Vx, byte].'''
        (arg_x, arg_kk) = nnn_format_to_xkk(arg)
        self.reg_v[arg_x] += arg_kk

        if self.reg_v[arg_x] >= 256:
            self.reg_v[arg_x] %= 256
            self.reg_v[0xF] = 1
        else:
            self.reg_v[0xF] = 0

    def _instruction_8(self, arg):
        '''Redirects to 8xy[0-7] and 8xyE.'''
        functions = {
            0x0: self._instruction_8xy0,
            0x1: self._instruction_8xy1,
            0x2: self._instruction_8xy2,
            0x3: self._instruction_8xy3,
            0x4: self._instruction_8xy4,
            0x5: self._instruction_8xy5,
            0x6: self._instruction_8xy6,
            0x7: self._instruction_8xy7,
            0xE: self._instruction_8xyE
        }

        (arg_x, arg_y, arg_n) = nnn_format_to_xyn(arg)
        functions[arg_n](arg_x, arg_y)

    def _instruction_8xy0(self, arg_x, arg_y):
        '''Instruction 8xy0 [LD Vx, Vy].'''
        self.reg_v[arg_x] = self.reg_v[arg_y]

    def _instruction_8xy1(self, arg_x, arg_y):
        '''Instruction 8xy1 [OR Vx, Vy].'''
        self.reg_v[arg_x] |= self.reg_v[arg_y]

    def _instruction_8xy2(self, arg_x, arg_y):
        '''Instruction 8xy2 [AND Vx, Vy].'''
        self.reg_v[arg_x] &= self.reg_v[arg_y]

    def _instruction_8xy3(self, arg_x, arg_y):
        '''Instruction 8xy3 [XOR Vx, Vy].'''
        self.reg_v[arg_x] ^= self.reg_v[arg_y]

    def _instruction_8xy4(self, arg_x, arg_y):
        '''Instruction 8xy4 [ADD Vx, Vy].'''
        self.reg_v[arg_x] += self.reg_v[arg_y]

        if self.reg_v[arg_x] >= 256:
            self.reg_v[arg_x] %= 256
            self.reg_v[0xF] = 1
        else:
            self.reg_v[0xF] = 0

    def _instruction_8xy5(self, arg_x, arg_y):
        '''Instruction 8xy5 [SUB Vx, Vy].'''
        # Set VF to NOT borrow
        if self.reg_v[arg_x] > self.reg_v[arg_y]:
            self.reg_v[0xF] = 1
        else:
            self.reg_v[0xF] = 0

        self.reg_v[arg_x] -= self.reg_v[arg_y]

    def _instruction_8xy6(self, arg_x, arg_y):
        '''Instruction 8xy6 [SHR Vx {, Vy}].'''
        # Check if the least-significant bit is 1
        if self.reg_v[arg_y] % 2:
            self.reg_v[0xF] = 1
        else:
            self.reg_v[0xF] = 0

        self.reg_v[arg_x] = self.reg_v[arg_y] >> 1

    def _instruction_8xy7(self, arg_x, arg_y):
        '''Instruction 8xy7 [SUBN Vx, Vy].'''
        # Set VF to NOT borrow
        if self.reg_v[arg_y] > self.reg_v[arg_x]:
            self.reg_v[0xF] = 1
        else:
            self.reg_v[0xF] = 0

        self.reg_v[arg_x] = self.reg_v[arg_y] - self.reg_v[arg_x]

    def _instruction_8xyE(self, arg_x, arg_y):
        '''Instruction 8xyE [SHL Vx {, Vy}].'''
        # Check if there's overflow
        if self.reg_v[arg_y] % 2:
            self.reg_v[0xF] = 1
        else:
            self.reg_v[0xF] = 0

        self.reg_v[arg_x] = self.reg_v[arg_y] << 1

    def _instruction_9(self, arg):
        '''Instruction 9xy0 [SNE Vx, Vy].'''
        (arg_x, arg_y, _) = nnn_format_to_xyn(arg)

        if arg_x != arg_y:
            self._move_to_next_instruction()

    def _instruction_A(self, arg):
        '''Instruction Annn [LD I, addr].'''
        self.reg_i = arg

    def _instruction_B(self, arg):
        '''Instruction Bnnn [JP V0, addr].'''
        self.reg_pc = self.reg_v[0] + arg

    def _instruction_C(self, arg):
        '''Instruction Cxkk [RND Vx, byte].'''
        (arg_x, arg_kk) = nnn_format_to_xkk(arg)
        self.reg_v[arg_x] = randint(0, 255) & arg_kk

    def _instruction_D(self, arg):
        '''Instruction Dxyn [DRW Vx, Vy, nibble].'''
        (arg_x, arg_y, arg_n) = nnn_format_to_xyn(arg)

        self.reg_v[0xF] = 0  # Reset the flag register to its default value

        for row_number in range(arg_n):
            sprite = self.memory.read_byte_from_addr(self.reg_i + row_number)
            if self.io_manager.check_collission(sprite, self.reg_v[arg_x], self.reg_v[arg_y]):
                self.reg_v[0xF] = 1
            self.io_manager.draw_sprite(sprite, self.reg_v[arg_x], self.reg_v[arg_y] + row_number)

    def _instruction_E(self, arg):
        '''Redirects to either [SKP Vx] or [SKNP Vx].'''
        (arg_x, arg_kk) = nnn_format_to_xkk(arg)

        if arg_kk == 0x9E:
            self._instruction_Ex9E(arg_x)
        elif arg_kk == 0xA1:
            self._instruction_ExA1(arg_x)
        else:
            raise Exception('ExXX instruction not recognised.')

    def _instruction_Ex9E(self, arg_x):
        '''Instruction Ex9E [SKP Vx].'''
        if self.io_manager.is_key_pressed(self.reg_v[arg_x]):
            self._move_to_next_instruction()

    def _instruction_ExA1(self, arg_x):
        '''Instruction ExA1 [SKNP Vx].'''
        if not self.io_manager.is_key_pressed(self.reg_v[arg_x]):
            self._move_to_next_instruction()

    def _instruction_F(self, arg):
        '''Redirects to all instructions starting with the F nibble.'''
        functions = {
            0x07: self._instruction_Fx07,
            0x0A: self._instruction_Fx0A,
            0x15: self._instruction_Fx15,
            0x18: self._instruction_Fx18,
            0x1E: self._instruction_Fx1E,
            0x29: self._instruction_Fx29,
            0x33: self._instruction_Fx33,
            0x55: self._instruction_Fx55,
            0x65: self._instruction_Fx65
        }

        (arg_x, arg_kk) = nnn_format_to_xkk(arg)

        functions[arg_kk](arg_x)

    def _instruction_Fx07(self, arg_x):
        '''Instruction Fx07 [LD Vx, DT].'''
        self.reg_v[arg_x] = self.reg_dt.value

    def _instruction_Fx0A(self, arg_x):
        '''Instruction Fx0A [LD Vx, K].'''
        self.reg_v[arg_x] = self.io_manager.wait_for_input()

    def _instruction_Fx15(self, arg_x):
        '''Instruction Fx15 [LD DT, Vx].'''
        self.reg_dt.set_value(self.reg_v[arg_x])

    def _instruction_Fx18(self, arg_x):
        '''Instruction Fx18 [LD ST, Vx].'''
        self.reg_st.set_value(self.reg_v[arg_x])
        self.io_manager.play_tone(self.reg_v[arg_x])

    def _instruction_Fx1E(self, arg_x):
        '''Instruction Fx1E [ADD I, Vx].'''
        self.reg_i += self.reg_v[arg_x]

    def _instruction_Fx29(self, arg_x):
        '''Instruction Fx29 [LD F, Vx].'''
        self.reg_i = self.memory.find_sprite_address(self.reg_v[arg_x])

    def _instruction_Fx33(self, arg_x):
        '''Instruction Fx33 [LD B, Vx].'''
        i_addr = self.reg_i
        value_to_convert = self.reg_v[arg_x]
        (hundreds_digit, tens_digit, ones_digit) = nnn_to_bcd(value_to_convert)

        self.memory.write_byte_to_addr(hundreds_digit, i_addr)
        self.memory.write_byte_to_addr(tens_digit, i_addr + 1)
        self.memory.write_byte_to_addr(ones_digit, i_addr + 2)

    def _instruction_Fx55(self, arg_x):
        '''Instruction Fx55 [LD [I], Vx].'''
        for register_number in range(arg_x + 1):
            self.memory.write_byte_to_addr(self.reg_v[register_number], self.reg_i + register_number)

    def _instruction_Fx65(self, arg_x):
        '''Instruction Fx65 [LD Vx, [I]].'''
        for register_number in range(arg_x + 1):
            self.reg_v[register_number] = int(self.memory.read_byte_from_addr(self.reg_i + register_number), 16)

    def _move_to_next_instruction(self):
        '''Increases the PC register to point to the next instruction.'''
        self.reg_pc += 2  # Instructions are 2 bytes long

    def push_to_stack(self, value):
        '''Pushes a value to the stack.'''
        if self.reg_sp == 0xF:
            raise Exception('Full stack.')

        self.stack[self.reg_sp] = value
        self.reg_sp += 1

    def pop_from_stack(self):
        '''Pops a value from the stack.'''
        if self.reg_sp == 0:
            raise Exception('Empty Stack')

        return_val = self.stack[self.reg_sp]
        self.reg_sp -= 1
        return return_val
