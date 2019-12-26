#!/usr/bin/env python3
'''This module handles all code related to Chip-8 timers.'''

import threading
import time


class Timer(threading.Thread):
    def __init__(self):
        super(Timer, self).__init__(daemon=True)

        self.value = 0
        self._value_lock = threading.Lock()
        self._next_countdown_call = time.time()

    def run(self):
        '''Reduce the timer\'s value by 1 60 times per second (every  0.017 seconds).
        Function taken from https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python'''
        while True:
            with self._value_lock:
                if self.value > 0:
                    self.value -= 1
            self._next_countdown_call += 0.017
            time.sleep(max(self._next_countdown_call - time.time(), 0))

    def set_value(self, new_value):
        '''Set the value of the timer to new_value.'''
        with self._value_lock:
            self.value = new_value

    def get_value(self):
        '''Get the value of the timer'''
        with self._value_lock:
            return self.value
