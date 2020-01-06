# chip8-emu

A Chip-8 emulator built in Python

I started this because of my interest in emulation since I was a kid. My plan is to eventually collaborate to state-of-the-art emulators if I have the time, but this is a start.

Thanks to Cowgod for his technical reference. (http://devernay.fr2ee.fr/hacks/chip8/C8TECH10.HTM)

# Project goals
  * Learn how to use an open source library from scratch and create a terminal GUI
  * Put into practice everything I've learnt in my programming paradigms class about object oriented programming while getting back in touch with the first modern programming language I've learnt, Python
  * Get familiar with the Python threading library and manage race conditions
  * Get used to work with the PEP 8 code conventions
  
# Obstacles
  * Apparently asciimatics has to run in the main thread, which ruins the hierarchy that I had planned for the project where the Chip8 class was at the center of all operations. Now IOManager and Chip8 are coupled more than I'd like them to be. Calling __init__() is not enough to initialise the Chip8 class, it also has to call set_io_manager() and that is just awful.
  * For most of the development I couldn't do any debugging because the sprites just wouldn't render. Turns out that I was only refreshing my own display buffer and not the UI library's and that's why nothing would show up on screen. That double buffer is another hack, but I decided to go with it because drawing sprites on screen involves XORing whatever is already shown at those coordinates and I didn't want to constantly call this huge library and do type conversions every time anything is drawn.
  * The Chip-8 graphics system is poorly documented. I had to do a lot of guesswork and there's still a lot to figure out. Apparently some games are not so sure of how it works either.
  * I suspect there is some input buffer being manipulated somewhere in asciimatics because the input lag is very noticeable. Performance in general could be much better.
  
# Lessons learned
  * Language choice in a project isn't simply a matter of ease of development vs. performance, implementing a low level interpreter in a high level scripting language feels really awkward.
  * I need to test out a library in a small scale project before commiting to something like this. Asciimatics is a terminal graphics library, yes, but it's mostly oriented to the arrangement of pre-built widgets. Maybe curses would've been a better pick for me. I might try that later on.
  * I have to find a better way to debug console graphics code. Asciimatics messed with the pdb output and debugging was a confusing and annoying process that I tried to avoid as much as possible and that lead to a excruciatingly long bug fixing phase down the line.

# Compatibility

My goal was to reach 100% compatibility with all Chip-8 programs but this project was getting too long and sometimes you have to learn when to cut it short. The programs I tested where separated into three folders, by how well they work at the current time. "Broken" holds programs that simply show garbage or crash the emulator. "Partially working" contains programs that look like they might easily work if you fix a bug or two. "Working" is self explanatory.

One important detail to note is that some of the programs in the "broken" category might not work because they were poorly documented and they were actually meant to run in a Super Chip-48.
