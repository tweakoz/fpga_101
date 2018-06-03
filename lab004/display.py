from migen import *

from tick import Tick

from litex.soc.interconnect.csr import *


class _SevenSegment(Module):
    def __init__(self):
        # module's interface
        self.value = value = Signal(4)      # input
        self.abcdefg = abcdefg = Signal(7)  # output

        # # #

        # value to abcd segments dictionary.
        # Here we create a table to translate each of the 16 possible input
        # values to abdcefg segments control.
        cases = {
          0x0: abcdefg.eq(0b0111111),
          0x1: abcdefg.eq(0b0000110),
          0x2: abcdefg.eq(0b1011011),
          0x3: abcdefg.eq(0b1001111),
          0x4: abcdefg.eq(0b1100110),
          0x5: abcdefg.eq(0b1101101),
          0x6: abcdefg.eq(0b1111101),
          0x7: abcdefg.eq(0b0000111),
          0x8: abcdefg.eq(0b1111111),
          0x9: abcdefg.eq(0b1101111),
          0xa: abcdefg.eq(0b1110111),
          0xb: abcdefg.eq(0b1111100),
          0xc: abcdefg.eq(0b0111001),
          0xd: abcdefg.eq(0b1011110),
          0xe: abcdefg.eq(0b1111001),
          0xf: abcdefg.eq(0b1110001),
        }

        # combinatorial assignement
        self.comb += Case(value, cases)


class _Display(Module):
    def __init__(self, sys_clk_freq, cs_period=0.001):
        # module's interface
        self.values = Array(Signal(5) for i in range(8))  # input

        self.cs = Signal(8)      # output
        self.abcdefg = Signal(7) # output

        # # #

        # create our seven segment controller
        seven_segment = _SevenSegment()
        self.submodules += seven_segment
        self.comb += self.abcdefg.eq(seven_segment.abcdefg)

        # create a tick every cs_period
        self.submodules.tick = Tick(sys_clk_freq, cs_period)

        # rotate cs 6 bits signals to alternate seven segments
        # cycle 0 : 0b000001
        # cycle 1 : 0b000010
        # cycle 2 : 0b000100
        # cycle 3 : 0b001000
        # cycle 4 : 0b010000
        # cycle 5 : 0b100000s
        # cycle 6 : 0b000001
        cs = Signal(8, reset=0b00000001)
        # synchronous assigment
        self.sync += [
            If(self.tick.ce,     # at the next tick:
                cs[1].eq(cs[0]), # bit1 takes bit0 value 
                cs[2].eq(cs[1]), # bit2 takes bit1 value 
                cs[3].eq(cs[2]), # bit3 takes bit2 value 
                cs[4].eq(cs[3]), # bit4 takes bit3 value 
                cs[5].eq(cs[4]), # bit5 takes bit4 value 
                cs[6].eq(cs[5]), # bit5 takes bit4 value 
                cs[7].eq(cs[6]), # bit5 takes bit4 value 
                cs[0].eq(cs[7])  # bit0 takes bit5 value 
            )
        ]
        # cominatorial assigment
        self.comb += self.cs.eq(cs)

        # cs to value selection.
        # Here we create a table to translate each of the 6 cs possible values
        # to input value selection.
        cases = {
            0b00000001 : seven_segment.value.eq(self.values[0]),
            0b00000010 : seven_segment.value.eq(self.values[1]),
            0b00000100 : seven_segment.value.eq(self.values[2]),
            0b00001000 : seven_segment.value.eq(self.values[3]),
            0b00010000 : seven_segment.value.eq(self.values[4]),
            0b00100000 : seven_segment.value.eq(self.values[5]),
            0b01000000 : seven_segment.value.eq(self.values[6]),
            0b10000000 : seven_segment.value.eq(self.values[7])
        }
        # cominatorial assigment
        self.comb += Case(self.cs, cases)


class Display(Module, AutoCSR):
    def __init__(self, sys_clk_freq):
        self.sel = CSRStorage(4)
        self.value = CSRStorage(4)
        self.write = CSR()

        self.cs = Signal(8)      # output
        self.abcdefg = Signal(7) # output

        # # #

        # Create _Display module
        display = _Display(sys_clk_freq)
        self.submodules += display
        self.comb += [
            self.cs.eq(display.cs),
            self.abcdefg.eq(display.abcdefg)
        ]

        cases = {}
        self.sync += [
            # When CPU access write CSR
            If(self.write.re,
                # Select witch value to update based on sel register
                Case(self.sel.storage, {
                    0 : display.values[0].eq(self.value.storage),
                    1 : display.values[1].eq(self.value.storage),
                    2 : display.values[2].eq(self.value.storage),
                    3 : display.values[3].eq(self.value.storage),
                    4 : display.values[4].eq(self.value.storage),
                    5 : display.values[5].eq(self.value.storage),
                    6 : display.values[6].eq(self.value.storage),
                    7 : display.values[7].eq(self.value.storage),
                    }
                )
            )
        ]


if __name__ == '__main__':
    # seven segment simulation
    print("Seven Segment simulation")
    dut = _SevenSegment()

    def show_seven_segment(abcdefg):
        line0 = ["   ", " _ "]
        line1 = ["   ", "  |", " _ ", " _|", "|  ", "| |" , "|_ ", "|_|"]
        a = abcdefg & 0b1;
        fgb = ((abcdefg >> 1) & 0b001) | ((abcdefg >> 5) & 0b010) | ((abcdefg >> 3) & 0b100)
        edc = ((abcdefg >> 2) & 0b001) | ((abcdefg >> 2) & 0b010) | ((abcdefg >> 2) & 0b100)
        print(line0[a])
        print(line1[fgb])
        print(line1[edc])

    def dut_tb(dut):
        for i in range(16):
            yield dut.value.eq(i)
            yield
            show_seven_segment((yield dut.abcdefg))

    run_simulation(dut, dut_tb(dut), vcd_name="seven_segment.vcd")

    # Display simulation
    print("Display simulation")
    dut = _Display(100e6, 0.000001)
    def dut_tb(dut):
        for i in range(4096):
            for j in range(6):
                yield dut.values[j].eq(i + j)
            yield

    run_simulation(dut, dut_tb(dut), vcd_name="display.vcd")
