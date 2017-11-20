from ropchain.solver import solveWithGadget
from ropchain.gadgets import gadget
from ropchain import emulator
from pwn import asm
import unittest

class TestROPChain(unittest.TestCase):
    def do(self, dests, gadgetsDict, libBase=0x7f000000, avoids=[]):
        lib = buildFromGadgets(gadgetsDict)
        gadgets = gadget.fromDict(gadgetsDict)
        payload = solveWithGadget(dests, gadgets, libBase, avoids).payload()
        testResult = emulator.execROPChain(payload, lib, libBase)
        self.assertTrue(isCorrect(dests, testResult))

    def testPop(self):
        dests = {'eax': 0x0, 'ebx': 0x602030, 'ecx': 0x1000}
        gadgets = {
                0x10000: 'pop eax; ret',
                0x20000: 'pop ebx; ret',
                0x30000: 'pop ecx; ret'
                }
        self.do(dests, gadgets)

    def testIncAdd(self):
        dests = {'eax': 0x12345678}
        gadgets = {
                0x10000: 'xor eax, eax; ret',
                0x20000: 'inc eax; ret',
                0x30000: 'add eax, eax; ret'
            }
        self.do(dests, gadgets)

    def testPopMov(self):
        dests = {'eax': 0x12345678, 'esi': 0x41414141}
        gadgets = {
                0x1000: 'pop esi; ret',
                0x2000: 'mov eax, esi; ret'
            }
        self.do(dests, gadgets)

    def testPopMov6Regs(self):
        dests = {
            'eax': 0x12345678,
            'ebx': 0x87654321,
            'ecx': 0x22222222,
            'edx': 0x7fffffff,
            'esi': 0x41414141,
            'edi': 0x42424242
        }
        gadgets = {
            0x1000: 'pop esi; ret',
            0x2000: 'mov ebx, esi; ret',
            0x3000: 'mov eax, ecx; ret',
            0x4000: 'mov ecx, ebx; ret',
            0x5000: 'mov edx, esi; ret',
            0x6000: 'mov edi, eax; ret',
        }
        self.do(dests, gadgets)

    def testMovWithoutPop(self):
        dests = {'eax':  0x12345678, 'esi':  0x41414141}
        gadgets = {
            0x1000: 'xor esi, esi; ret',
            0x2000: 'inc esi; ret',
            0x3000: 'add esi, esi; ret',
            0x4000: 'mov eax, esi; ret',
        }
        self.do(dests, gadgets)

    def testMovWithoutPop6Regs(self):
        dests = {
            'eax':  0x12345678,
            'ebx':  0x22222222,
            'ecx':  0x33333333,
            'edx':  0x87654321,
            'esi':  0x41414141,
            'edi':  0x42424242,
        }
        gadgets = {
            0x1000: 'xor esi, esi; ret',
            0x2000: 'inc esi; ret',
            0x3000: 'add esi, esi; ret',
            0x4000: 'mov eax, esi; ret',
            0x5000: 'mov ebx, eax; ret',
            0x6000: 'mov edx, ecx; ret',
            0x7000: 'mov edi, edx; ret',
            0x8000: 'mov ecx, ebx; ret',
        }
        self.do(dests, gadgets)

    def testPopXor(self):
        dests = {'eax': 0x12345678, 'esi': 0x41414141}
        gadgets = {
                0x1000: 'pop esi; ret',
                0x2000: 'xor eax, eax; ret',
                0x3000: 'xor eax, esi; ret'
            }
        self.do(dests, gadgets)

    def testPopPop1(self):
        dests = {'eax': 0x12345678, 'esi': 0x41414141}
        gadgets = {
                0x1000: 'pop esi; pop eax; ret',
                0x2000: 'pop eax; ret',
            }
        self.do(dests, gadgets)

    def testPopPop2(self):
        dests = {'eax': 0x12345678, 'esi': 0x41414141}
        gadgets = {
                0x1000: 'pop eax; pop esi; ret',
                0x2000: 'pop esi; ret',
            }
        self.do(dests, gadgets)

    def testAscii(self):
        libBase = 0x55550000
        avoids = set([i for i in range(0x100) if not 0x20 <= i <= 0x7e])
        dests = {'eax': 0x41414141, 'ebx': 0x41424344}
        gadgets = {
                0x5455: 'pop eax; ret',
                0x5555: 'pop ebx; ret',
                }
        self.do(dests, gadgets, libBase, avoids)

    def testAsciiXor(self):
        libBase = 0x55550000
        avoids = set([i for i in range(0x100) if not 0x20 <= i <= 0x7e])
        dests = {'eax': 0xb, 'ebx': 0x55554444}
        gadgets = {
                0x5455: 'mov eax, ebx; ret',
                0x5555: 'xor eax, ebx; ret',
                0x5655: 'pop ebx; ret',
                }
        self.do(dests, gadgets, libBase, avoids)

def buildFromGadgets(gadgets):
    addrs = gadgets.keys()
    insns = list(map(asm, gadgets.values()))
    lib = '\x00' * (max(addrs) + len(max(insns, key=len)))
    for addr, insn in zip(addrs, insns):
        lib = lib[:addr] + insn + lib[addr+len(insn):]
    return lib

def isCorrect(expected, result):
    for reg in expected:
        if result[reg] != expected[reg]:
            return False
    return True

if __name__ == '__main__':
    unittest.main()
