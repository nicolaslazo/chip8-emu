#!/usr/bin/env python3
'''This module contains the classes that manage the input/output operations of a Chip-8 virtual machine.'''

import json
from asciimatics.screen import Screen


def hex_to_binary(hex_value):
    binary_length = len(hex_value) * 4
    return (bin(int(h, 16))[2:]).zfill(binary_length)


class IOManager:
    def __init__(self):
        self.input = InputManager()
        self.screen = VideoManager()
        self.audio = AudioManager()

    def init(self):
        self.input.init()
        self.screen.init()
        self.audio.init()


class InputManager:
    def __init__(self):
        self._load_key_bindings_config()

    def wait_for_input(self):
        '''Stops execution until a key is pressed.'''
        key_pressed = self.screen.wait_for_input()

        return key_binding[key_pressed]

    def _load_key_bindings_config(self):
        with open('key_bindings.json') as CONFIG_FILE:
            self.key_bindings = json.load(CONFIG_FILE)


class VideoManager:
    def __init__(self):
        self.display_buffer = [[0] * 64] * 32  # 64x32 resolution
        self._display_lock = Lock()

    def init(self):
        Screen.wrapper(self.run)

    def run(self, screen):
        while True:
            with self._display_lock:
                self._draw_screen(screen)

    def draw_sprite(self, sprite, pos_x, pos_y):
        if self._sprite_overflows(sprite, pos_x):
            self.draw_sprite()

    def _draw_screen(self, screen):
        for coord_y in range(32):
            for coord_x in range(64):
                if self.display_buffer[coord_y][coord_x] == '1':
                    screen.print_at('X', coord_x, coord_y)


class AudioManager:
    def init(self):
        pass  # Empty until I figure out how to play a single tone with Python on a Windows WSL
