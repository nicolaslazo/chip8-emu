#!/usr/bin/env python2
'''This module contains the classes that manage the input/output operations of a Chip-8 virtual machine.'''

import json
import threading
from asciimatics.screen import Screen


def hex_to_binary(hex_value):
    binary_length = len(hex_value) * 4
    return (bin(int(h, 16))[2:]).zfill(binary_length)


class IOManager:
    def __init__(self):
        self.display = VideoManager()
        self.input = InputManager(self.display.screen)
        self.audio = AudioManager(self.display.screen)


class VideoManager:
    def __init__(self):
        self.display_buffer = [[0] * 64] * 32  # 64x32 resolution
        self._display_lock = threading.Lock()

        self.start_display_thread()

    def start_display_thread(self):
        self.screen = Screen.wrapper(self.run)
        self.screen.clear()

    def run(self, screen):
        while True:
            with self._display_lock:
                self._draw_screen(self.display_buffer)

    def draw_sprite(self, sprite, pos_x, pos_y):
        sprite = list(hex_to_binary(sprite))

        with self._display_lock:
            self.display_buffer[pos_y][pos_x:pos_x + len(sprite)] = sprite

    def _draw_screen(self, screen):
        for coord_y in range(32):
            for coord_x in range(64):
                if self.display_buffer[coord_y][coord_x] == '1':
                    screen.print_at('X', coord_x, coord_y)


class InputManager:
    def __init__(self, screen):
        self.screen = screen
        self._load_key_bindings_config()

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


class AudioManager:
    def play_tone(self, time):
        pass  # Empty until I figure out how to play a single tone with Python 3.8.0 on a Windows WSL
