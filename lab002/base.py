from migen import *
from migen.build.generic_platform import *
from migen.build.xilinx import XilinxPlatform
from migen.genlib.cdc import MultiReg

from tick import *
from display import *
from bcd import *
from core import *


#
# platform
#

_io = [
    ("user_led",  0, Pins("H17"), IOStandard("LVCMOS33")),

    ("user_sw",  0, Pins("J15"), IOStandard("LVCMOS33")),

    ("user_btn_r", 0, Pins("M17"), IOStandard("LVCMOS33")),
    ("user_btn_l", 0, Pins("P17"), IOStandard("LVCMOS33")),

    ("clk100", 0, Pins("E3"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),

    ("display_cs_n",  0, Pins("J17"), IOStandard("LVCMOS33")),
    ("display_abcdefg",  0, Pins("T10 R10 K16 K13 P15 T11 L18 H15"), IOStandard("LVCMOS33")),
]


class Platform(XilinxPlatform):
    default_clk_name = "clk100"
    default_clk_period = 10.0

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a100t-CSG324-1", _io, toolchain="vivado")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)

#
# design
#

# user button detection
class UserButtonPress(Module):
    def __init__(self, user_btn):
        self.rising = Signal()

        # # #

        _user_btn = Signal()
        _user_btn_d = Signal()

        # resynchronize user_btn
        self.specials += MultiReg(user_btn, _user_btn)
        # detect rising edge
        self.sync += [
            _user_btn_d.eq(user_btn),
            self.rising.eq(_user_btn & ~_user_btn_d)
        ]

# create our platform (fpga interface)
platform = Platform()

# create our main module (fpga description)
class Clock(Module):
    sys_clk_freq = int(100e6)
    def __init__(self):
        # -- TO BE COMPLETED --
        # Tick generation : timebase

        # Display

        # Core : counts ss/mm/hh

        # set mm/hh

        # Binary Coded Decimal: convert ss/mm/hh to decimal values

        # use the generated verilog file
    
        # combinatorial assignement
        self.comb += [
            # Connect tick to core (core timebase)

            # Set minutes/hours

            # Convert core seconds to bcd and connect
            # to display

            # Convert core minutes to bcd and connect
            # to display

            # Convert core hours to bcd and connect
            # to display

            # Connect display to pads
        ]
        # -- TO BE COMPLETED --

module = Clock()

#
# build
#

platform.build(module)
