# py8asm
Simple CHIP8 assembler, following a T. P. Green's modified pseudo-assembly syntax

### Usage
```
usage: py8asm.py [-h] [-o NAME] path

Simple CHIP8 assembler, following the T. P. Green's pseudo-assembly syntax

positional arguments:
  path                  path to the source file

optional arguments:
  -h, --help            show this help message and exit
  -o NAME, --output NAME
                        Name of the new executable
```

### Syntax

```
Cheatsheet for Thomas P. Green modified pseudo-assembly syntax

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
        You should absolutely use this syntax to assemble the file into a binary.
        
        Some instructions are modified from the original syntax for easy coding
        purpose

        All values should be represented in hexademical (registers too)
```

### References

* [Cowgod's Chip-8 Technical Reference v1.0](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM) -  Technical reference by Thomas P. Green
