import asciimatics.screen import Screen

class IOManager:
    def __init__():
        # Screen buffer
        self.screen_buffer = [[0] * 64] * 32
        self.bit_overwritten_in_sprite_draw = 0

        # Pressed key buffer
        self.key_buffer = 0
        self._load_key_bindings_config()

    @ManagedScreen
    def init():
        pass

    def _draw_screen(self, screen):
        for y_coord in range(32):
            for x_coord in range(64):
                screen.print_at(self.screen_buffer[y_coord][x_coord], x_coord, y_coord)


class InputManager:
    def wait_for_input(self):
        key_pressed = self.screen.wait_for_input()

        return key_binding[key_pressed]
