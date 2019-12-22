#!/usr/bin/env python3
'''This module contains the classes that manage the input/output operations of a Chip-8 virtual machine.'''

import json
import threading
import time
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent


def hex_to_binary(hex_value):
    binary_length = len(hex_value) * 4
    return (bin(int(hex_value, 16))[2:]).zfill(binary_length)

def fix_overflowing_coordinates(coord_x, coord_y):
    return (coord_x % 64, coord_y + coord_x // 64)


class IOManager():
    def __init__(self, chip8):
        # Virtual machine
        self.chip8 = chip8
        self.chip8.set_io_manager(self)

        # Input setup
        self._load_key_bindings_config()

        # Video setup
        self.display_buffer = [[0] * 64 for _ in range(32)]  # 64x32 resolution
        self._display_lock = threading.Lock()
        Screen.wrapper(self.main_loop)

    def main_loop(self, screen):
        self.screen = screen

        while True:
            self.chip8.step()

            with self._display_lock:
                self.print_debug_info()
                self._draw_screen()
                screen.refresh()

    def draw_sprite(self, sprite, pos_x, pos_y):
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
        (corrected_x, corrected_y) = fix_overflowing_coordinates(pos_x, pos_y)
        with self._display_lock:
            sprite_displayed = self._get_displayed_sprite_at(corrected_x, corrected_y)

        return int(sprite, 16) & sprite_displayed

    def print_debug_info(self):
        self.screen.print_at(' ' * 64, 0, 34)
        self.screen.print_at(' ' * 64, 0, 35)
        self.screen.print_at(' ' * 64, 0, 36)
        self.screen.print_at(f'REGISTERS: { self.chip8.reg_v }', 0, 34)
        self.screen.print_at(f'STACK: { self.chip8.stack }', 0, 35)
        self.screen.print_at(f'PC: { hex(self.chip8.reg_pc - 2)[2:].upper() }    I: { self.chip8.reg_i }', 0, 36)

    def _get_displayed_sprite_at(self, pos_x, pos_y):
        retval = '0b'

        for index in range(8):
            (corrected_x, corrected_y) = fix_overflowing_coordinates(pos_x + index, pos_y)
            if chr(self.screen.get_from(corrected_x, corrected_y)[0]) == 'X': 
                retval += '1'
            else:
                retval += '0'

        return int(retval, 2)

    def _draw_screen(self):
        for coord_y in range(32):
            for coord_x in range(64):
                if self.display_buffer[coord_y][coord_x] == 1:
                    self.screen.print_at('X', coord_x, coord_y)
                else:
                    self.screen.print_at(' ', coord_x, coord_y)

    def is_key_pressed(self, value):
        key_event = self.screen.get_event()
        if isinstance(key_event, KeyboardEvent):
            key_pressed = chr(key_event.key_code)

        return self.key_binding[key_pressed] == value

    def wait_for_input(self):
        '''Stops execution until a key is pressed.'''
        key_pressed = self.screen.wait_for_input()

        return self.key_binding[key_pressed]

    def _load_key_bindings_config(self):
        with open('key_bindings.json') as CONFIG_FILE:
            self.key_binding = json.load(CONFIG_FILE)

    def play_tone(self, time):
        pass  
        # Empty until I figure out how to play a single tone with Python 3.8.0 on a Windows WSL
