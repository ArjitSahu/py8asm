""" Simple CHIP8 assembler, following the T. P. Green's pseudo-assembly syntax
    ; by weld, wtfpl
"""	

""" Cheatsheet for Thomas P. Green modified pseudo-assembly syntax

    (I)nstruction (A)rguments (1), (A)rguments (2), ...
    (I)nstruction Destination, Source, ... 

    Instructions list:
        00E0 - CLS
        00EE - RET
        0nnn - SYS addr
        1nnn - JP addr
        2nnn - CALL addr
        3xkk - SE Vx, byte
        4xkk - SNE Vx, byte
        5xy0 - SE Vx, Vy
        6xkk - LD Vx, byte
        7xkk - ADD Vx, byte
        8xy0 - LD Vx, Vy
        8xy1 - OR Vx, Vy
        8xy2 - AND Vx, Vy
        8xy3 - XOR Vx, Vy
        8xy4 - ADD Vx, Vy
        8xy5 - SUB Vx, Vy
        8xy6 - SHR Vx, Vy
        8xy7 - SUBN Vx, Vy
        8xyE - SHL Vx, VY
        9xy0 - SNE Vx, Vy
        Annn - LD I, addr
        Bnnn - JPV V0, addr
        Cxkk - RND Vx, byte
        Dxyn - DRW Vx, Vy, nibble
        Ex9E - SKP Vx
        ExA1 - SKNP Vx
        Fx07 - LD Vx, DT
        Fx0A - LD Vx, K
        Fx15 - LD DT, Vx
        Fx18 - LD ST, Vx
        Fx1E - ADD I, Vx
        Fx29 - LD F, Vx
        Fx33 - LD B, Vx
        Fx55 - LD [I], Vx
        Fx65 - LD Vx, [I]

    Comments support:
        This pseudo-assembly supports comments, used like this:
            JP 0X00 ; WRITE YOUR COMMENT HERE
    Dumb note :
        You should absolutely use this syntax to assemble the file into a binary
        Some instructions are modified from the original syntax for easy coding
        purpose

        All values should be represented in hexademical (registers too)
"""


"""
    How to improve this assembler ? 

    + labels
    + check size of arg
    + rethink the syntax
    + improve parser efficiency (less code)
"""
### === IMPORT === ###
try:
    from copy import deepcopy
    from sys import exit
    
    import argparse as argp
except ImportError as err:
     print("[ERROR] ImportError : ", err)
### === CONST === ###
"""
    There are 4 "types" of instruction, sorted by the number of arguments they
    take.

    Ex:
        CALL addr           : Take 1 arg
        DRW Vx, Vy, nibble  : Take 3 args

    Hence, we can create a dictionary which's storing nb of args per instr.
"""
instrType = {
    'CLS'   : 0,
    'RET'   : 0,

    'SYS'   : 1,
    'JP'    : 1,
    'CALL'  : 1,
    'SKP'   : 1,
    'SKNP'  : 1,

    'SE'    : 2,
    'SNE'   : 2,
    'LD'    : 2,
    'ADD'   : 2,
    'OR'    : 2,
    'AND'   : 2,
    'XOR'   : 2,
    'SUB'   : 2,
    'SHR'   : 2,
    'SUBN'  : 2,
    'SHL'   : 2,
    'JPV'   : 2,
    'RND'   : 2,

    'DRW'   : 3
}

"""
    We can do the same with arguments 'cause there are 10 types of them:
        addr, byte, register, I, DT, ST, B, F, K, nibble

    This allows us to create a check-type function, merging args into 2-types:
        hex and str
"""

argTypeInt = {'addr', 'byte', 'nibble'}
argTypeStr = {'reg', 'I', 'DT', 'ST', 'B', 'F', 'K', '[I]'}

argType = {
    'addr'  :int,
    'byte'  :int,
    'nibble':int,
    'reg'   :str,
    'I'     :str,
    'DT'    :str,
    'ST'    :str,
    'B'     :str,
    'F'     :str,
    'K'     :str,
    '[I]'   :str
}

### === CLASS === ###
class InvalidReg(Exception):
    def __init__(self, arg):
        self.arg = arg

class InvalidArg(Exception):
    def __init__(self, arg):
        self.arg = arg

class Assembler:
    def __init__(self, filePath,name):
        self._filename = filePath
        self._name = self._filename.split('.')[0] + '.c8' if name == '' else name + '.c8'

        self._asmFile = []
        self._binaryFile = []

        self._open_asm()
        self._remove_empty_lines()
        self._assemble()
        self._write_binary()
    
    def _open_asm(self):
        with open(self._filename) as FILE:
            lines = FILE.readlines()
            for ln in lines:
                ln = ln.replace(',', ' ')
                if ';' in ln:
                    l = ln[0: ln.find(';')]
                else:
                    l = ln
                l = l.split()
                self._asmFile.append(l)
    
    def _write_binary(self):
        with open(self._name, 'wb') as FILE:
            for i in self._binaryFile:
                FILE.write(bytes(((i & 0xFF00)>>8,)))
                FILE.write(bytes(((i & 0x00FF),)))
    
    def _remove_empty_lines(self):
        temp = []
        for i in self._asmFile:
            if len(i) != 0:
                temp.append(i)
        self._asmFile = deepcopy(temp)

    @staticmethod
    def _ret_reg(reg):
        a = int(reg[1:], 16)
        if a < 0x0 or a > 0xF:
            raise InvalidReg(reg)
        else:
            return a

    def _check_arg(self, arg, targ): # Two types, 
        try:
            if targ in argTypeInt:
                return argType[targ](arg, 16)
            elif targ in argTypeStr:
                if targ == 'reg':
                    return self._ret_reg(arg)
                elif targ in argTypeStr:
                    return str(arg)
        except ValueError as err:
            raise InvalidArg(err.args[0].split()[-1])
        except InvalidReg as err:
            raise InvalidReg(err.arg)

    @staticmethod
    def _check_type(val):       # Return true if type val is int; else, that's a string
        try:
            ret = True
            int(val, 16)
        except ValueError:
            ret = False
        finally:
            return ret
    """
        Note that some instructions are useless but I prefer to keep a certain
        structured code for every asm instructions.

        Parsing instructions, line by line ; keep in mind the syntax 
            INSTR Arg1, Arg2, ...
    """
    def _assemble(self):
        line = 0
        for I in self._asmFile:
            try:
                line += 1               # Line counter
                if instrType[I[0]] == 0: 
                    if I[0] == 'CLS' :
                        self._binaryFile.append(0x00E0)
                    elif I[0] == 'RET' :
                        self._binaryFile.append(0x00EE)

                elif instrType[I[0]] == 1:
                    if I[0] == 'SYS':       #0nnn - SYS addr
                        arg_1 = self._check_arg(I[1], 'addr')
                        self._binaryFile.append(0x0000 | arg_1)
                    elif I[0] == 'JP':      #1nnn - JP addr
                        arg_1 = self._check_arg(I[1], 'addr')
                        self._binaryFile.append(0x1000 | arg_1)
                    elif I[0] == 'CALL':    #2nnn - CALL addr
                        arg_1 = self._check_arg(I[1], 'addr')
                        self._binaryFile.append(0x2000 | arg_1)
                    elif I[0] == 'SKP':     #Ex9E - SKP Vx
                        arg_1 = self._check_arg(I[1], 'reg')
                        self._binaryFile.append(0xE09E | arg_1<<8)
                    elif I[0] == 'SKNP':    #ExA1 - SKNP Vx
                        arg_1 = self._check_arg(I[1], 'reg')
                        self._binaryFile.append(0xE0A1 | arg_1<<8)
                
                elif instrType[I[0]] == 2:
                    if I[0] == 'SE':
                        if self._check_type(I[2]):  #3xkk - SE Vx, byte
                            arg_1 = self._check_arg(I[1], 'reg')
                            arg_2 = self._check_arg(I[2], 'byte')
                            self._binaryFile.append(0x3000 | arg_1<<8 | (arg_2 & 0x00FF))
                        else:                       #5xy0 - SE Vx, Vy
                            arg_1 = self._check_arg(I[1], 'reg')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0x5000 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'SNE':
                        if self._check_type(I[2]):  #4xkk - SNE Vx, byte
                            arg_1 = self._check_arg(I[1], 'reg')
                            arg_2 = self._check_arg(I[2], 'byte')
                            self._binaryFile.append(0x4000 | arg_1<<8 | (arg_2 & 0x00FF))
                        else:                       #9xy0 - SNE Vx, Vy
                            arg_1 = self._check_arg(I[1], 'reg')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0x9000 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'LD':
                        if I[1] == 'I':             #Annn - LD I, addr
                            arg_1 = self._check_arg(I[1], 'I')
                            arg_2 = self._check_arg(I[2], 'addr')
                            self._binaryFile.append(0xA000 | arg_2)
                        elif I[1] == 'DT':          #Fx15 - LD DT, Vx
                            arg_1 = self._check_arg(I[1], 'DT')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0xF015 | arg_2<<8)
                        elif I[1] == 'ST':          #Fx18 - LD ST, Vx
                            arg_1 = self._check_arg(I[1], 'ST')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0xF018 | arg_2<<8)
                        elif I[1] == 'B':           #Fx33 - LD B, Vx
                            arg_1 = self._check_arg(I[1], 'B')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0xF033 | arg_2<<8)
                        elif I[1] == 'F':           #Fx29 - LD F, Vx
                            arg_1 = self._check_arg(I[1], 'F')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0xF029 | arg_2<<8)
                        elif I[1] == '[I]':         #Fx55 - LD [I], Vx
                            arg_1 = self._check_arg(I[1], '[I]')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0xF055 | arg_2<<8)
                        else:
                            if self._check_type(I[2]):  #6xkk - LD Vx, byte
                                arg_1 = self._check_arg(I[1], 'reg')
                                arg_2 = self._check_arg(I[2], 'byte')
                                self._binaryFile.append(0x6000 | arg_1<<8 | (arg_2 & 0x00FF))
                            elif I[2] == 'DT':          #Fx07 - LD Vx, DT
                                arg_1 = self._check_arg(I[1], 'reg')
                                arg_2 = self._check_arg(I[2], 'DT')
                                self._binaryFile.append(0xF007 | arg_1<<8)
                            elif I[2] == 'K':           #Fx0A - LD Vx, K
                                arg_1 = self._check_arg(I[1], 'reg')
                                arg_2 = self._check_arg(I[2], 'K')
                                self._binaryFile.append(0xF00A | arg_1<<8)
                            elif I[2] == '[I]':         #Fx65 - LD Vx, [I]
                                arg_1 = self._check_arg(I[1], 'reg')
                                arg_2 = self._check_arg(I[2], '[I]')
                                self._binaryFile.append(0xF065 | arg_1)
                            else:                       #8xy0 - LD Vx, Vy
                                arg_1 = self._check_arg(I[1], 'reg')
                                arg_2 = self._check_arg(I[2], 'reg')
                                self._binaryFile.append(0x8000 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'ADD':
                        if I[1] == 'I':                 #Fx1E - ADD I, Vx
                            arg_1 = self._check_arg(I[1], 'I')
                            arg_2 = self._check_arg(I[2], 'reg')
                            self._binaryFile.append(0xF01E | arg_2<<8)
                        else:
                            if self._check_type(I[2]):  #7xkk - ADD Vx, byte
                                arg_1 = self._check_arg(I[1], 'reg')
                                arg_2 = self._check_arg(I[2], 'byte')
                                self._binaryFile.append(0x7000 | arg_1<<8 | (arg_2 & 0x00FF))
                            else:                       #8xy4 - ADD Vx, Vy
                                arg_1 = self._check_arg(I[1], 'reg')
                                arg_2 = self._check_arg(I[2], 'reg')
                                self._binaryFile.append(0x8004 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'OR':                  #8xy1 - OR Vx, Vy
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        self._binaryFile.append(0x8001 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'AND':                 #8xy2 - AND Vx, Vy
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        self._binaryFile.append(0x8002 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'XOR':                 #8xy3 - XOR Vx, Vy
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        self._binaryFile.append(0x8003 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'SUB':                 #8xy5 - SUB Vx, Vy
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        self._binaryFile.append(0x8005 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'SHR':                 #8xy6 - SHR Vx, Vy
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        self._binaryFile.append(0x8006 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'SUBN':                #8xy7 - SUBN Vx, Vy
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        self._binaryFile.append(0x8007 | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'SHL':                 #8xyE - SHL Vx, VY
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        self._binaryFile.append(0x800E | arg_1<<8 | arg_2<<4)
                    elif I[0] == 'JPV':                 #Bnnn - JPV V0, addr
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'addr')
                        self._binaryFile.append(0xB000 | (arg_2 & 0x0FFF))
                    elif I[0] == 'RND':                 #Cxkk - RND Vx, byte
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'byte')
                        self._binaryFile.append(0xC000 | arg_1<<8 | (arg_2 & 0x00FF))
                
                elif instrType[I[0]] == 3:
                    if I[0] == 'DRW':                   #Dxyn - DRW Vx, Vy, nibble
                        arg_1 = self._check_arg(I[1], 'reg')
                        arg_2 = self._check_arg(I[2], 'reg')
                        arg_3 = self._check_arg(I[3], 'nibble')
                        self._binaryFile.append(0xD000 | arg_1<<8 | arg_2<<4 | (arg_3 & 0x000F))
            except InvalidReg as err:
                print("[%i] %s register does not exist" % (line, err.arg))
                exit(1)
            except InvalidArg as err:
                print("[%i] %s is not in the expected type" % (line, err.arg))
                exit(1)
                
    
### === FUNCTIONS === ###
### === ENTRY POINT === ###
if __name__ == "__main__":
    try:
        parser = argp.ArgumentParser(description="Simple CHIP8 assembler, following the T. P. Green's pseudo-assembly syntax")
        parser.add_argument('path', help='path to the source file')
        parser.add_argument('-o', '--output', default='', metavar=('NAME'), help='Name of the new executable')

        r = vars(parser.parse_args( ))
        if r['path']:
            Assembler(r['path'], r['output'])
        else:
            raise argp.ArgumentError
    except argp.ArgumentError:
        parser.print_help()
