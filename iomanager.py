#!/usr/bin/env python3
'''This module contains the classes that manage the input/output operations of a Chip-8 virtual machine.'''

import json
import threading
import time
from decompiler import decompile_instruction
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent


def hex_to_binary(hex_value):
    '''Return the binary equivalent of a hexadecimal value.'''
    binary_length = len(hex_value) * 4
    return (bin(int(hex_value, 16))[2:]).zfill(binary_length)


def fix_overflowing_coordinates(coord_x, coord_y):
    '''If a sprite coordinate gets out of the display bounds, returns its fixed position.'''
    return (coord_x % 64, coord_y % 32)


class IOManager():
    '''Chip-8 machine input/output manager.'''
    def __init__(self, chip8):
        # Virtual machine
        self.chip8 = chip8
        self.chip8.set_io_manager(self)

        # Input setup
        self._load_key_bindings_config()

        # Video setup
        self.display_buffer = [[0] * 64 for _ in range(32)]  # 64x32 resolution
        self._display_lock = threading.Lock()
        Screen.wrapper(self.main_loop, catch_interrupt=False)

    def main_loop(self, screen):
        '''Emulates a Chip-8 machine cycle.'''
        self.screen = screen

        while True:
            self.chip8.step()

            with self._display_lock:
                self.print_debug_info()
                self._draw_screen()
                screen.refresh()

    def draw_sprite(self, sprite, pos_x, pos_y):
        '''Draw a sprite in the specified coordinates.'''
        binary_sprite = hex_to_binary(sprite)

        with self._display_lock:
            for (index, sprite_bit) in enumerate(binary_sprite):
                xored_bit = 0
                (corrected_x, corrected_y) = fix_overflowing_coordinates(pos_x + index, pos_y)
                screen_char = chr(self.screen.get_from(corrected_x, corrected_y)[0])
                if (sprite_bit == '0' and screen_char == 'X') or (sprite_bit == '1' and screen_char == ' '):
                    xored_bit = 1
                self.display_buffer[corrected_y][corrected_x] = xored_bit

    def check_collission(self, sprite, pos_x, pos_y):
        '''Returns True if sprite collides with what is already drawn in the given coordinates.'''
        (corrected_x, corrected_y) = fix_overflowing_coordinates(pos_x, pos_y)
        with self._display_lock:
            sprite_displayed = self._get_displayed_sprite_at(corrected_x, corrected_y)

        return int(sprite, 16) & sprite_displayed

    def print_debug_info(self):
        '''Print CPU-related info to the screen for debugging purposes.'''
        self.screen.print_at(' ' * 96, 0, 34)
        self.screen.print_at(' ' * 64, 0, 35)
        self.screen.print_at(' ' * 64, 0, 36)
        self.screen.print_at(f'REGISTERS: { self.chip8.reg_v }', 0, 34)
        self.screen.print_at(f'STACK: { self.chip8.stack }', 0, 35)
        self.screen.print_at(f'PC: { hex(self.chip8.reg_pc)[2:].upper() }    I: { hex(self.chip8.reg_i)[2:].upper() }   DT: { self.chip8.delay_timer.get_value() }', 0, 36)

        """
        self.screen.print_at('                       ', 34, 1)
        self.screen.print_at('                       ', 34, 2)
        self.screen.print_at('                       ', 34, 3)
        self.screen.print_at('                       ', 34, 4)
        self.screen.print_at('                       ', 34, 5)

        try:
            self.screen.print_at('    ' + decompile_instruction(self.chip8.memory.read_word_from_addr(self.chip8.reg_pc - 4)) + '    ', 34, 1)
            self.screen.print_at('    ' + decompile_instruction(self.chip8.memory.read_word_from_addr(self.chip8.reg_pc - 2)) + '    ', 34, 2)
        except:
            pass

        self.screen.print_at('--> ' + decompile_instruction(self.chip8.memory.read_word_from_addr(self.chip8.reg_pc)) + ' <--', 34, 3)
        self.screen.print_at('    ' + decompile_instruction(self.chip8.memory.read_word_from_addr(self.chip8.reg_pc + 2)) + '    ', 34, 4)
        self.screen.print_at('    ' + decompile_instruction(self.chip8.memory.read_word_from_addr(self.chip8.reg_pc + 4)) + '    ', 34, 5)
        """

    def clear_screen(self):
        '''Set all the display buffer bytes to zero.'''
        self.display_buffer = [[0] * 64 for _ in range(32)]

    def is_key_pressed(self, value):
        '''Returns true if the key binding of the pressed key equals value.'''
        self.screen.wait_for_input(.00000001)
        key_event = self.screen.get_event()
        if key_event is None or not isinstance(key_event, KeyboardEvent):
            return False
        key_pressed = chr(key_event.key_code)

        try:
            return self.key_binding[key_pressed] == value
        except KeyError:
            return self.is_key_pressed(value)

    def wait_for_input(self):
        '''Stop execution until a key is pressed, and return its key binding.'''
        self.screen.wait_for_input(999999)
        key_event = self.screen.get_event()

        try:
            key_pressed = chr(key_event.key_code)
            return self.key_binding[key_pressed]
        except AttributeError:
            return self.wait_for_input()
        except KeyError:
            return self.wait_for_input()

    def play_tone(self, time):
        '''Play a single tone for (time * 1/60) seconds.'''
        # Empty because the Windows WSL where I work doesn't support audio
        pass

    def _get_displayed_sprite_at(self, pos_x, pos_y):
        '''Fetch what is being displayed at the given coordinates.'''
        retval = '0b'

        for index in range(8):
            (corrected_x, corrected_y) = fix_overflowing_coordinates(pos_x + index, pos_y)
            if chr(self.screen.get_from(corrected_x, corrected_y)[0]) == 'X':
                retval += '1'
            else:
                retval += '0'

        return int(retval, 2)

    def _draw_screen(self):
        '''Copy the display buffer to the graphics library buffer.'''
        for coord_y in range(32):
            for coord_x in range(64):
                if self.display_buffer[coord_y][coord_x] == 1:
                    self.screen.print_at('X', coord_x, coord_y, bg=Screen.COLOUR_WHITE)
                else:
                    self.screen.print_at(' ', coord_x, coord_y, bg=Screen.COLOUR_BLACK)

    def _load_key_bindings_config(self):
        '''Load key binding settings from key_bindings.json.'''
        with open('key_bindings.json') as CONFIG_FILE:
            self.key_binding = json.load(CONFIG_FILE)
