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
        c.v_registers[11] = 0x70

        c.cycle()

        self.assertEqual(516, c.pc)

    def test_4xkk_fail(self):
        c = chip8.Chip8()

        # Skip next instruction if register VB != 0x69
        c.memory[512:514] = [0x4B, 0x69]
        c.v_registers[11] = 0x69

        c.cycle()

        self.assertEqual(514, c.pc)

    def test_5xy0_pass(self):
        c = chip8.Chip8()

        # Skip next instruction if register V4 == register VA
        c.memory[512:514] = [0x54, 0xA0]
        c.v_registers[4] = 0x09
        c.v_registers[10] = 0x09

        c.cycle()

        self.assertEqual(516, c.pc)

    def test_5xy0_fail(self):
        c = chip8.Chip8()

        # Skip next instruction if register V4 == register VA
        c.memory[512:514] = [0x54, 0xA0]
        c.v_registers[4] = 0x09
        c.v_registers[10] = 0x05

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
        c.v_registers[14] = 0x45

        c.cycle()

        self.assertEqual(0x4A, c.v_registers[14])

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

    def text_8xy3(self):
        c = chip8.Chip8()

        # XOR V0 and V1, store in V0
        c.memory[512:514] = [0x80, 0x13]
        c.v_registers[0] = 0x12
        c.v_registers[1] = 0x23

        c.cycle()

        self.assertEqual(49, c.v_registers[0])

    def test_8xy4(self):
        pass

    def text_8xy5(self):
        pass

    def text_8xy6(self):
        pass

    def text_8xy7(self):
        pass


if __name__ == '__main__':
    unittest.main()
