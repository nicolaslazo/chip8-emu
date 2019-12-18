#!/usr/bin/env python3
'''This module contains the classes that manage the input/output operations of a Chip-8 virtual machine.'''

import json
import threading
from asciimatics.screen import Screen


def hex_to_binary(hex_value):
    binary_length = len(hex_value) * 4
    return (bin(int(h, 16))[2:]).zfill(binary_length)


class IOManager(threading.Thread):
    def __init__(self):
        super(IOManager, self).__init__()
        self.display_buffer = [[0] * 64] * 32  # 64x32 resolution

    def run(self):
        self._load_key_bindings_config()
        self._display_lock = threading.Lock()
        self.screen = Screen.wrapper(self.main_loop)
        self.screen.clear()

    def main_loop(self, screen):
        while True:
            with self._display_lock:
                self._draw_screen(self.display_buffer)

    def draw_sprite(self, sprite, pos_x, pos_y):
        binary_sprite = hex_to_binary(sprite)

        with self._display_lock:
            xor_sprite = []
            for (index, sprite_bit) in enumerate(binary_sprite):
                screen_char = self.screen.get_from(pos_x + index, pos_y)
                if sprite_bit == '1' and screen_char == 'X':
                    xor_sprite.append(0)
                elif (sprite_bit == '0' and screen_char == 'X') or (sprite_bit == '1' and screen_char == ' '):
                    xor_sprite.append(1)
                else:
                    xor_sprite.append(0)
            self.display_buffer[pos_y][pos_x:pos_x + len(xor_sprite)] = xor_sprite

    def check_collission(self, pos_x, pos_y, sprite):
        with self._display_lock:
            sprite_displayed = self._get_displayed_sprite_at(pos_x, pos_y)

        return int(sprite, 16) & int(sprite_displayed, 16)

    def print_debug_info(self, v_registers, pc_register, running_instruction):
        with self._display_lock:
            screen.print_at(' ' * 64, 0, 34)
            screen.print_at(' ' * 64, 0, 35)
            screen.print_at(f"REGISTERS: { ' '.join(v_registers) }", 0, 34)
            screen.print_at(f'PC: { pc_register }   CURRENT INSTRUCTION: { running_instruction }', 0, 35)

    def _get_displayed_sprite_at(self, pos_x, pos_y):
        return ''.join([self.screen.get_from(pos_x + index, pos_y) for index in range(5)])

    def _draw_screen(self, screen):
        for coord_y in range(32):
            for coord_x in range(64):
                if self.display_buffer[coord_y][coord_x] == '1':
                    screen.print_at('X', coord_x, coord_y)
                else:
                    screen.print_at(' ', coord_x, coord_y)

    def get_input(self):
        key_event = self.screen.get_event()
        key_pressed = chr(key_event.key_code)

        return self.key_binding[key_pressed]

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
