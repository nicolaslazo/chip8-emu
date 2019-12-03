from asciimatics.screen import Screen


class IOManager:
    def __init__():
        self.input = InputManager()
        self.screen = VideoManager()
        self.audio = AudioManager()

    def init():
        self.input.init()
        self.screen.init()
        self.audio.init()

    def _draw_screen(self, screen):
        for y_coord in range(32):
            for x_coord in range(64):
                screen.print_at(self.screen_buffer[y_coord][x_coord], x_coord, y_coord)


class InputManager:
    def __init__(self):
        pass

    def init(self):
        pass

    def wait_for_input(self):
        key_pressed = self.screen.wait_for_input()

        return key_binding[key_pressed]

    def _load_key_bindings_config(self):
        self.key_bindings = json.loads


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
