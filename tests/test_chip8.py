import random
import unittest

from context import chip8


class Chip8TestSuite(unittest.TestCase):

    def test_00EE(self):
        c = chip8.Chip8()

        # Return
        c.memory[512:514] = [0x00, 0xEE]

        # Push return address on to the stack
        c.stack[0:2] = [0x0A, 0xBC]

        # Set stack pointer to point to the return address that was just loaded
        c.sp = 0

        c.cycle()

        self.assertEqual(0x0ABC, c.pc)
        self.assertEqual(-2, c.sp)

    def test_1nnn(self):
        c = chip8.Chip8()

        # Jump to 0x0C4A
        c.memory[512:514] = [0x1C, 0x4A]

        c.cycle()

        self.assertEqual(0x0C4A, c.pc)

    def test_2nnn(self):
        c = chip8.Chip8()

        # Call subroutine
        c.memory[512:514] = [0x21, 0xD4]

        c.cycle()

        self.assertEqual(0, c.sp)
        self.assertEqual(0x0202, int.from_bytes(c.stack[0:2], byteorder='big'))
        self.assertEqual(0x01D4, c.pc)

    def test_3xkk_pass(self):
        c = chip8.Chip8()

        # Skip next instruction if register V5 == 0x24
        c.memory[512:514] = [0x35, 0x24]
        c.v_registers[5] = 0x24

        c.cycle()

        self.assertEqual(516, c.pc)

    def test_3xkk_fail(self):
        c = chip8.Chip8()

        # Skip next instruction if register V5 == 0x24
        c.memory[512:514] = [0x35, 0x24]
        c.v_registers[5] = 0x25

        c.cycle()

        self.assertEqual(514, c.pc)

    def test_4xkk_pass(self):
        c = chip8.Chip8()

        # Skip next instruction if register VB != 0x69
        c.memory[512:514] = [0x4B, 0x69]
        c.v_registers[0xB] = 0x70

        c.cycle()

        self.assertEqual(516, c.pc)

    def test_4xkk_fail(self):
        c = chip8.Chip8()

        # Skip next instruction if register VB != 0x69
        c.memory[512:514] = [0x4B, 0x69]
        c.v_registers[0xB] = 0x69

        c.cycle()

        self.assertEqual(514, c.pc)

    def test_5xy0_pass(self):
        c = chip8.Chip8()

        # Skip next instruction if register V4 == register VA
        c.memory[512:514] = [0x54, 0xA0]
        c.v_registers[4] = 0x09
        c.v_registers[0xA] = 0x09

        c.cycle()

        self.assertEqual(516, c.pc)

    def test_5xy0_fail(self):
        c = chip8.Chip8()

        # Skip next instruction if register V4 == register VA
        c.memory[512:514] = [0x54, 0xA0]
        c.v_registers[4] = 0x09
        c.v_registers[0xA] = 0x05

        c.cycle()

        self.assertEqual(514, c.pc)

    def test_6xkk(self):
        c = chip8.Chip8()

        # Load 0x42 into register V3
        c.memory[512:514] = [0x63, 0x42]

        c.cycle()

        self.assertEqual(0x42, c.v_registers[3])

    def test_7xkk(self):
        c = chip8.Chip8()

        # Add 0x05 to register VE
        c.memory[512:514] = [0x7E, 0x05]
        c.v_registers[0xE] = 0x45

        c.cycle()

        self.assertEqual(0x4A, c.v_registers[0xE])

    def test_7xkk_overflow(self):
        c = chip8.Chip8()

        # Add 0x05 to register VE
        c.memory[512:514] = [0x7E, 0xAB]
        c.v_registers[0xE] = 0x80

        c.cycle()

        # 0xAB + 0x80 = 0x012B
        self.assertEqual(0x2B, c.v_registers[0xE])

    def test_8xy0(self):
        c = chip8.Chip8()

        # Store value of Vy in Vx
        c.memory[512:514] = [0x80, 0x10]
        c.v_registers[1] = 0x23

        c.cycle()

        self.assertEqual(0x23, c.v_registers[0])

    def test_8xy1(self):
        c = chip8.Chip8()

        # Or V0 and V1, store in V0
        c.memory[512:514] = [0x80, 0x11]
        c.v_registers[0] = 0x12
        c.v_registers[1] = 0x23

        c.cycle()

        self.assertEqual(51, c.v_registers[0])

    def test_8xy2(self):
        c = chip8.Chip8()

        # AND V0 and V1, store in V0
        c.memory[512:514] = [0x80, 0x12]
        c.v_registers[0] = 0x12
        c.v_registers[1] = 0x23

        c.cycle()

        self.assertEqual(2, c.v_registers[0])

    def test_8xy3(self):
        c = chip8.Chip8()

        # XOR V0 and V1, store in V0
        c.memory[512:514] = [0x80, 0x13]
        c.v_registers[0] = 0x12
        c.v_registers[1] = 0x23

        c.cycle()

        self.assertEqual(49, c.v_registers[0])

    def test_8xy4_carry(self):
        c = chip8.Chip8()

        # ADD V0 and V1, set carry
        c.memory[512:514] = [0x80, 0x14]
        c.v_registers[0] = 0xFF
        c.v_registers[1] = 0x50

        c.cycle()

        self.assertEqual(0x4F, c.v_registers[0])
        self.assertEqual(0x01, c.v_registers[0xF])

    def test_8xy4_no_carry(self):
        c = chip8.Chip8()

        # ADD V0 and V1, don't set carry
        c.memory[512:514] = [0x80, 0x14]
        c.v_registers[0] = 0x30
        c.v_registers[1] = 0x45

        # Set the VF register to make sure it gets unset
        c.v_registers[0xF] = 0x01

        c.cycle()

        self.assertEqual(0x75, c.v_registers[0])
        self.assertEqual(0x00, c.v_registers[0xF])

    def test_8xy5_borrow(self):
        c = chip8.Chip8()

        # SUB V1 from V0, borrow
        c.memory[512:514] = [0x80, 0x15]
        c.v_registers[0] = 0x30
        c.v_registers[1] = 0x45

        # Set the VF register to make sure it gets unset
        c.v_registers[0xF] = 0x01

        c.cycle()

        self.assertEqual(235, c.v_registers[0])
        self.assertEqual(0x00, c.v_registers[0xF])

    def test_8xy5_no_borrow(self):
        c = chip8.Chip8()

        # SUB V1 from V0, don't borrow
        c.memory[512:514] = [0x80, 0x15]
        c.v_registers[0] = 0x45
        c.v_registers[1] = 0x30

        c.cycle()

        self.assertEqual(0x15, c.v_registers[0])
        self.assertEqual(0x01, c.v_registers[0xF])

    def test_8xy6_odd(self):
        c = chip8.Chip8()

        # Bitshift V0 right by 1, set VF
        c.memory[512:514] = [0x80, 0x16]
        c.v_registers[0] = 0x8F

        c.cycle()

        self.assertEqual(71, c.v_registers[0])
        self.assertEqual(0x01, c.v_registers[0xF])

    def test_8xy6_even(self):
        c = chip8.Chip8()

        # Bitshift V0 right by 1, clear VF
        c.memory[512:514] = [0x80, 0x16]
        c.v_registers[0] = 0x8e

        c.v_registers[0xF] = 0x01

        c.cycle()

        self.assertEqual(71, c.v_registers[0])
        self.assertEqual(0x00, c.v_registers[0xF])

    def test_8xy7_borrow(self):
        c = chip8.Chip8()

        # SUB V0 from V1, borrow
        c.memory[512:514] = [0x80, 0x17]
        c.v_registers[0] = 0x8A
        c.v_registers[1] = 0x1F

        # Set the VF register to make sure it gets unset
        c.v_registers[0xF] = 0x01

        c.cycle()

        self.assertEqual(149, c.v_registers[0])
        self.assertEqual(0x00, c.v_registers[0xF])

    def test_8xy7_no_borrow(self):
        c = chip8.Chip8()

        # SUB V0 from V1, don't borrow
        c.memory[512:514] = [0x80, 0x17]
        c.v_registers[0] = 0x1F
        c.v_registers[1] = 0x8A

        c.cycle()

        self.assertEqual(107, c.v_registers[0])
        self.assertEqual(0x01, c.v_registers[0xF])

    def test_8xyE_msb_0(self):
        c = chip8.Chip8()

        # Bitshift V0 left by 1, clear VF
        c.memory[512:514] = [0x80, 0x1E]

        # V0 = 0101 0001
        c.v_registers[0] = 81

        c.v_registers[0xF] = 0x01

        c.cycle()

        # V0 == 1010 0010
        self.assertEqual(162, c.v_registers[0])
        self.assertEqual(0x00, c.v_registers[0xF])

    def test_8xyE_msb_1(self):
        c = chip8.Chip8()

        # Bitshift V0 left by 1, set VF
        c.memory[512:514] = [0x80, 0x1E]

        # V0 = 1101 0001
        c.v_registers[0] = 209

        c.cycle()

        # V0 == 1010 0010
        self.assertEqual(162, c.v_registers[0])
        self.assertEqual(0x01, c.v_registers[0xF])

    def test_9xy0_pass(self):
        c = chip8.Chip8()

        # Skip next instruction if register V4 != register VA
        c.memory[512:514] = [0x94, 0xA0]
        c.v_registers[4] = 0x09
        c.v_registers[0xA] = 0x05

        c.cycle()

        self.assertEqual(516, c.pc)

    def test_9xy0_fail(self):
        c = chip8.Chip8()

        # Skip next instruction if register V4 != register VA
        c.memory[512:514] = [0x94, 0xA0]
        c.v_registers[4] = 0x09
        c.v_registers[0xA] = 0x09

        c.cycle()

        self.assertEqual(514, c.pc)

    def test_Annn(self):
        c = chip8.Chip8()

        # Load 0xabc into register I
        c.memory[512:514] = [0xAA, 0xBC]

        c.cycle()

        self.assertEqual(0xABC, c.i_register)

    def test_Bnnn(self):
        c = chip8.Chip8()

        # Load 0xabc into register I
        c.memory[512:514] = [0xBA, 0xBC]
        c.v_registers[0] = 0x34

        c.cycle()

        self.assertEqual(0xAF0, c.pc)

    def test_Cxkk(self):
        c = chip8.Chip8()

        # Load 0xabc into register I
        c.memory[512:514] = [0xC8, 0x13]

        random.seed(1337)

        c.cycle()

        self.assertEqual(19, c.v_registers[8])


if __name__ == '__main__':
    unittest.main()
