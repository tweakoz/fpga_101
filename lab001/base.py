#!/usr/bin/env python3 
from migen import *
from migen.build.generic_platform import *
from migen.build.xilinx import XilinxPlatform

#
# platform
#

_io = [
    ("red_led",  0, Pins("K6"), IOStandard("LVCMOS33")),
    ("grn_led",  0, Pins("H6"), IOStandard("LVCMOS33")),
    ("blu_led",  0, Pins("L16"), IOStandard("LVCMOS33")),

    ("user_sw",  0, Pins("U9"), IOStandard("LVCMOS33")),

    ("user_btn", 0, Pins("F15"), IOStandard("LVCMOS33")),

    ("clk100", 0, Pins("E3"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),
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


# create our platform (fpga interface)
platform = Platform()
red_led = platform.request("red_led")
grn_led = platform.request("grn_led")
blu_led = platform.request("blu_led")

# create our module (fpga description)
module = Module()

# create a counter and blink a led
counter = Signal(27)
module.comb += red_led.eq(counter[24])
module.comb += grn_led.eq(counter[25])
module.comb += blu_led.eq(counter[26])

module.sync += counter.eq(counter + 1)

#
# build
#

platform.build(module)
