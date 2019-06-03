"""
Chip 8 interpreter module
"""
import ctypes

from random import randint


class Chip8:
    """
    Chip 8 interpreter class
    """
    MEMORY_SIZE_BYTES = 4096

    def __init__(self):
        self.memory = bytearray(Chip8.MEMORY_SIZE_BYTES)

        # 16 8-bit registers (V0, V1, V2, ..., VF)
        self.v_registers = bytearray(16)

        # 16-bit register (I)
        self.i_register = 0

        # 8-bit delay timer
        self.delay_timer = 0

        # 8-bit sound timer
        self.sound_timer = 0

        # 16-bit program counter
        self.pc = 0x0200

        # 8-bit stack pointer
        self.sp = -2

        # 16 16-bit values to store return addresses
        self.stack = bytearray(32)

        self.opcode_func_map = {
            0x0000: self.execute_0000, 0x1000: self.execute_1000,
            0x2000: self.execute_2000, 0x3000: self.execute_3000,
            0x4000: self.execute_4000, 0x5000: self.execute_5000,
            0x6000: self.execute_6000, 0x7000: self.execute_7000,
            0x8000: self.execute_8000, 0x9000: self.execute_9000,
            0xA000: self.execute_A000, 0xB000: self.execute_B000,
            0xC000: self.execute_C000, 0xD000: self.execute_D000,
            0xE000: self.execute_E000, 0xF000: self.execute_F000
        }

    def incr_pc(self):
        """
        Increment the PC. Since instructions are two bytes, increment by two.
        """
        self.pc += 2

    def fetch_opcode(self):
        """
        Fetch the next (2-byte) opcode and increment the pc
        """
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        self.incr_pc()

        return opcode

    def cycle(self):
        """
        Perform a cycle
        """
        opcode = self.fetch_opcode()

        # Get the top 8 bits of opcode
        nib0 = opcode & 0xF000

        execute = self.opcode_func_map.get(nib0)
        execute(opcode)

    def execute_0000(self, opcode):
        """
        00E0 - CLS
            Clear the display
        00EE - RET
            Return from a subroutine
        """
        if opcode == 0x00E0:
            # Clear the display
            pass
        elif opcode == 0x00EE:
            self.pc = int.from_bytes(self.stack[self.sp:self.sp + 2], byteorder='big')
            self.sp -= 2

    def execute_1000(self, opcode):
        """
        1nnn - JP addr
            Jump to location nnnn
        """
        self.pc = opcode & 0x0FFF

    def execute_2000(self, opcode):
        """
        2nnn - CALL addr
            Call subroutine at nnn
        """
        self.sp += 2

        self.stack[self.sp:self.sp + 2] = self.pc.to_bytes(2, byteorder='big')

        self.pc = opcode & 0x0FFF

    def execute_3000(self, opcode):
        """
        3xkk - SE Vx, byte
            Skip next instruction if Vx = kk
        """
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF

        if self.v_registers[x] == kk:
            self.incr_pc()

    def execute_4000(self, opcode):
        """
        4xkk - SNE Vx, byte
            Skip next instruction if Vx != kk
        """
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF

        if self.v_registers[x] != kk:
            self.incr_pc()

    def execute_5000(self, opcode):
        """
        5xy0 - SE Vx, Vy
            Skip next instruction if Vx = Vy
        """
        lsn = opcode & 0x000F

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4

        if lsn == 0x0:
            if self.v_registers[x] == self.v_registers[y]:
                self.incr_pc()

    def execute_6000(self, opcode):
        """
        6xkk - LD Vx, byte
            Set Vx = kk
        """
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF

        self.v_registers[x] = kk

    def execute_7000(self, opcode):
        """
        7xkk - ADD Vx, byte
            Adds the value kk to the value in register Vx
        """
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF

        self.v_registers[x] = ctypes.c_ubyte(self.v_registers[x] + kk).value

    def execute_8000(self, opcode):
        """
        8xy0 - LD Vx, Vy
            Stores the value of register Vy in register Vx
        8xy1 - OR Vx, Vy
            Bitwise OR Vx and Vy, store result in Vx
        8xy2 - AND Vx, Vy
            Bitwise AND Vx and Vy, store result in Vx
        8xy3 - XOR Vx, Vy
            Bitwise XOR Vx and Vy, store result in Vx
        8xy4 - ADD Vx, Vy
            Set Vx = Vx + Vy, set VF = carry
        8xy5 - SUB Vx, Vy
            Set Vx = Vx - Vy, set VF = NOT borrow
        8xy6 - SHR Vx
            Set Vx = Vx >> 1
        8xy7 - SUBN Vx, Vy
            Set Vx = Vy - Yx, set VF = NOT borrow
        8xyE - SHL Vx
            Set Vx = Vx << 1
        """

        # Least significant nibble
        lsn = opcode & 0x000F

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4

        if lsn == 0x0:
            self.v_registers[x] = self.v_registers[y]
        elif lsn == 0x1:
            self.v_registers[x] |= self.v_registers[y]
        elif lsn == 0x2:
            self.v_registers[x] &= self.v_registers[y]
        elif lsn == 0x3:
            self.v_registers[x] ^= self.v_registers[y]
        elif lsn == 0x4:
            res = self.v_registers[x] + self.v_registers[y]

            self.v_registers[0xF] = 1 if res > 255 else 0
            self.v_registers[x] = ctypes.c_ubyte(res).value
        elif lsn == 0x5:
            x_val = self.v_registers[x]
            y_val = self.v_registers[y]

            self.v_registers[0xF] = 1 if x_val > y_val else 0
            self.v_registers[x] = ctypes.c_ubyte(x_val - y_val).value
        elif lsn == 0x6:
            x_val = self.v_registers[x]

            # If the least significant bit of Vx is 1,
            # set VF to 1, otherwise set VF to 0
            self.v_registers[0xF] = x_val & 1

            self.v_registers[x] = ctypes.c_ubyte(x_val >> 1).value
        elif lsn == 0x7:
            x_val = self.v_registers[x]
            y_val = self.v_registers[y]

            self.v_registers[0xF] = 1 if y_val > x_val else 0
            self.v_registers[x] = ctypes.c_ubyte(y_val - x_val).value
        elif lsn == 0xE:
            x_val = self.v_registers[x]

            self.v_registers[0xF] = (x_val & 0x80) >> 7
            self.v_registers[x] = ctypes.c_ubyte(x_val << 1).value

    def execute_9000(self, opcode):
        """
        9xy0 - SNE Vx, Vy
            Skip next instruction if Vx != Vy
        """
        lsn = opcode & 0x000F

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4

        if lsn == 0x0:
            if self.v_registers[x] != self.v_registers[y]:
                self.incr_pc()

    def execute_A000(self, opcode):
        """
        Annn - LD I, addr
            Set I = nnn
        """
        self.i_register = opcode & 0x0FFF

    def execute_B000(self, opcode):
        """
        Bnnn - JP V0, addr
            Jump to location nnn + V0
        """
        self.pc = (opcode & 0x0FFF) + self.v_registers[0]

    def execute_C000(self, opcode):
        """
        Cxkk - RND Vx, byte
            Set Vx = random byte AND kk
        """
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF

        self.v_registers[x] = randint(0, 0xFF) & kk

    def execute_D000(self, opcode):
        print('0xD000: {:x}'.format(opcode))

    def execute_E000(self, opcode):
        print('0xE000: {:x}'.format(opcode))

    def execute_F000(self, opcode):
        print('0xF000: {:x}'.format(opcode))
