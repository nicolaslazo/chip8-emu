#!/usr/bin/env python3
'''This module handles all code related to Chip-8 timers.'''

import threading
import time


class Timer:
    def __init__(self):
        self.value = 0
        self._value_lock = threading.Lock()
        self._next_countdown_call = time.time()
        self._count_down()

    def _count_down(self):
        '''Reduce the timer\'s value by 1 60 times per second (every  0.017 seconds).'''
        # function taken from https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python
        with self._value_lock:
            if self.value > 0:
                self.value -= 1
        self._next_countdown_call += 0.017

        threading.Timer(self._next_countdown_call - time.time(), self._count_down).start()

    def set_value(self, new_value):
        '''Set the value of the timer to new_value.'''
        with self._value_lock:
            self.value = new_value

    def get_value(self):
        '''Get the value of the timer'''
        with self._value_lock:
            return self.value
