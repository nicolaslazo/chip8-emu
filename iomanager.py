#!/usr/bin/env python3
'''This module contains the classes that manage the input/output operations of a Chip-8 virtual machine.'''

import json
from asciimatics.screen import Screen


class IOManager:
    def __init__(self):
        self.input = InputManager()
        self.screen = VideoManager()
        self.audio = AudioManager()

    def init(self):
        self.input.init()
        self.screen.init()
        self.audio.init()

    def _draw_screen(self, screen):
        for y_coord in range(32):
            for x_coord in range(64):
                screen.print_at(self.screen_buffer[y_coord][x_coord], x_coord, y_coord)


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
        pass

    def init(self):
        pass


class AudioManager:
    def __init__(self):
        pass

    def init(self):
        pass

    def play_tone(self):
        pass
