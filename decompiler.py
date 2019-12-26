#!/usr/bin/env python3
'''This module decompiles any Chip-8 ROM file.'''

from sys import argv


def decompile_instruction(instruction):
    return _instruction_category[instruction[0]](instruction[1:])


def _instruction_0(arg):
    '''Redirect to 0nnn [SYS addr], 00E0 [CLS] or 00EE [RET].'''
    if arg == '0E0':
        return _instruction_00E0()
    elif arg == '0EE':
        return _instruction_00EE()
    else:
        return _instruction_0nnn(arg)


def _instruction_00E0():
    '''Instruction 00E0 [CLS].'''
    return 'CLS'


def _instruction_00EE():
    '''Instruction 00EE [RET].'''
    return 'RET'


def _instruction_0nnn(addr):
    '''Instruction 0nnn [SYS addr].'''
    return f'SYS { addr }'


def _instruction_1(addr):
    '''Instruction 1nnn [JP addr].'''
    return f'JP { addr }'


def _instruction_2(addr):
    '''Instruction 2nnn [CALL addr].'''
    return f'CALL { addr }'


def _instruction_3(arg):
    '''Instruction 3xkk [SE Vx, byte].'''
    return f'SE V{ arg[0] }, { arg[1:] }'


def _instruction_4(arg):
    '''Instruction 4xkk [SNE Vx, byte].'''
    return f'SNE V{ arg[0] }, { arg[1:] }'


def _instruction_5(arg):
    '''Instruction 5xy0 [SE Vx, Vy].'''
    return f'SNE V{ arg[0] }, V{ arg[1] }'


def _instruction_6(arg):
    '''Instruction 6xkk [LD Vx, byte].'''
    return f'LD V{ arg[0] }, { arg[1:] }'


def _instruction_7(arg):
    '''Instruction 7xkk [ADD Vx, byte].'''
    return f'ADD V{ arg[0] }, { arg[1:] }'


def _instruction_8(arg):
    '''Redirect to 8xy[0-7] and 8xyE.'''
    functions = {
        '0': _instruction_8xy0,
        '1': _instruction_8xy1,
        '2': _instruction_8xy2,
        '3': _instruction_8xy3,
        '4': _instruction_8xy4,
        '5': _instruction_8xy5,
        '6': _instruction_8xy6,
        '7': _instruction_8xy7,
        'E': _instruction_8xyE
    }

    (x, y, instruction_nibble) = arg
    return functions[instruction_nibble](x, y)


def _instruction_8xy0(x, y):
    '''Instruction 8xy0 [LD Vx, Vy].'''
    return f'LD V{ x }, V{ y }'


def _instruction_8xy1(x, y):
    '''Instruction 8xy1 [OR Vx, Vy].'''
    return f'OR V{ x }, V{ y }'


def _instruction_8xy2(x, y):
    '''Instruction 8xy2 [AND Vx, Vy].'''
    return f'AND V{ x }, V{ y }'


def _instruction_8xy3(x, y):
    '''Instruction 8xy3 [XOR Vx, Vy].'''
    return f'XOR V{ x }, V{ y }'


def _instruction_8xy4(x, y):
    '''Instruction 8xy4 [ADD Vx, Vy].'''
    return f'ADD V{ x }, V{ y }'


def _instruction_8xy5(x, y):
    '''Instruction 8xy5 [SUB Vx, Vy].'''
    return f'SUB V{ x }, V{ y }'


def _instruction_8xy6(x, y):
    '''Instruction 8xy6 [SHR Vx {, Vy}].'''
    return f'SHR V{ x }, {{, V{ y }}}'


def _instruction_8xy7(x, y):
    '''Instruction 8xy7 [SUBN Vx, Vy].'''
    return f'SNE V{ x }, V{ y }'


def _instruction_8xyE(x, y):
    '''Instruction 8xyE [SHL Vx {, Vy}].'''
    return f'SNE V{ x }, {{, V{ y }}}'


def _instruction_9(arg):
    '''Instruction 9xy0 [SNE Vx, Vy].'''
    return f'SNE V{ arg[0] }, V{ arg[1] }'


def _instruction_A(arg):
    '''Instruction Annn [LD I, addr].'''
    return f'LD I, { arg }'


def _instruction_B(arg):
    '''Instruction Bnnn [JP V0, addr].'''
    return f'JP V0, { addr }'


def _instruction_C(arg):
    '''Instruction Cxkk [RND Vx, byte].'''
    return f'RND V{ arg[0] }, { arg[1:] }'


def _instruction_D(arg):
    '''Instruction Dxyn [DRW Vx, Vy, nibble].'''
    return f'DRW V{ arg[0] }, V{ arg[1] }, { arg[2] }'


def _instruction_E(arg):
    '''Redirect to either [SKP Vx] or [SKNP Vx].'''
    last_byte = arg[1:]

    if last_byte == '9E':
        return _instruction_Ex9E(arg[0])
    elif last_byte == 'A1':
        return _instruction_ExA1(arg[0])
    else:
        raise Exception('ExXX instruction not recognised.')


def _instruction_Ex9E(x):
    '''Instruction Ex9E [SKP Vx].'''
    return f'SKP V{ x }'


def _instruction_ExA1(x):
    '''Instruction ExA1 [SKNP Vx].'''
    return f'SKNP V{ x }'


def _instruction_F(arg):
    '''Redirect to all instructions starting with the F nibble.'''
    functions = {
        '07': _instruction_Fx07,
        '0A': _instruction_Fx0A,
        '15': _instruction_Fx15,
        '18': _instruction_Fx18,
        '1E': _instruction_Fx1E,
        '29': _instruction_Fx29,
        '33': _instruction_Fx33,
        '55': _instruction_Fx55,
        '65': _instruction_Fx65
    }

    last_byte = arg[1:]

    return functions[last_byte](arg[0])


def _instruction_Fx07(x):
    '''Instruction Fx07 [LD Vx, DT].'''
    return f'LD V{ x }, DT'


def _instruction_Fx0A(x):
    '''Instruction Fx0A [LD Vx, K].'''
    return f'LD V{ x }, K'


def _instruction_Fx15(x):
    '''Instruction Fx15 [LD DT, Vx].'''
    return f'LD DT, V{ x }'


def _instruction_Fx18(x):
    '''Instruction Fx18 [LD ST, Vx].'''
    return f'LD ST, V{ x }'


def _instruction_Fx1E(x):
    '''Instruction Fx1E [ADD I, Vx].'''
    return f'ADD I, V{ x }'


def _instruction_Fx29(x):
    '''Instruction Fx29 [LD F, Vx].'''
    return f'LD F, V{ x }'


def _instruction_Fx33(x):
    '''Instruction Fx33 [LD B, Vx].'''
    return f'LD B, V{ x }'


def _instruction_Fx55(x):
    '''Instruction Fx55 [LD [I], Vx].'''
    return f'LD [I], V{ x }'


def _instruction_Fx65(x):
    '''Instruction Fx65 [LD Vx, [I]].'''
    return f'LD V{ x }, [I]'


_instruction_category = {
    '0': _instruction_0,
    '1': _instruction_1,
    '2': _instruction_2,
    '3': _instruction_3,
    '4': _instruction_4,
    '5': _instruction_5,
    '6': _instruction_6,
    '7': _instruction_7,
    '8': _instruction_8,
    '9': _instruction_9,
    'A': _instruction_A,
    'B': _instruction_B,
    'C': _instruction_C,
    'D': _instruction_D,
    'E': _instruction_E,
    'F': _instruction_F
}


if __name__ == '__main__':
    rom_file = open(argv[1], 'rb')

    counter = 512

    print(f'Instructions in the ROM file { argv[1] }:')
    print('=' * 32)

    while True:
        read_word = rom_file.read(2).hex().upper()

        if not read_word:
            break

        try:
            decompiled_instruction = decompile_instruction(read_word)
        except:
            decompiled_instruction = 'SPRITE???'

        print('{0:03X}: {1:s}'.format(counter, decompiled_instruction))

        counter += 2
