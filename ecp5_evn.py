#!/usr/bin/env python3

# This file is Copyright (c) 2019 Arnaud Durand <arnaud.durand@unifr.ch>
# License: BSD

import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import ecp5_evn

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.soc.cores.dma import WishboneDMAWriter
from litex.soc.interconnect.csr import AutoCSR, CSRStorage, CSRStatus, CSRField
from litex.soc.interconnect import wishbone

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, x5_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # clk / rst
        clk = clk12 = platform.request("clk12")
        rst_n = platform.request("rst_n")
        if x5_clk_freq is not None:
            clk = clk50 = platform.request("ext_clk50")
            self.comb += platform.request("ext_clk50_en").eq(1)
            platform.add_period_constraint(clk50, 1e9/x5_clk_freq)

        # pll
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk, x5_clk_freq or 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~rst_n)

class Wishbone_DMA_Burst(Module, AutoCSR):
    def __init__(self):
        self.wishbone = wishbone.Interface()

        self._start = CSRStorage(fields=[CSRField("start_burst", size=1, offset=0, pulse=True)])
        self._ready = CSRStatus(8)
        self._burst_size = CSRStorage(16)
        self._base = CSRStorage(32)
        self._offset = CSRStorage(32) 

        words_count = Signal(16)
        pass_count = Signal(5)
        
        self.wb_dma = wb_dma = WishboneDMAWriter(self.wishbone, endianness="big")
        self.submodules += wb_dma
        self.comb += [
            self.wb_dma.sink.address.eq((self._base.storage >> 2) + (self._offset.storage>>2) + words_count),
            self.wb_dma.sink.data.eq(pass_count),
        ]
                   
        fsm = FSM(reset_state="WAIT-FOR-TRIGGER")
        self.submodules += fsm

        
        fsm.act("WAIT-FOR-TRIGGER",
            self._ready.status.eq(1),
            NextValue(words_count, 0),
            If(self._start.fields.start_burst,
                NextState("WRITE-DATA"),
            )
        )

        fsm.act("WRITE-DATA",
            self.wb_dma.sink.valid.eq(1),

            If(self.wb_dma.sink.ready,    
                NextValue(words_count, words_count+1),
                If(words_count == (self._burst_size.storage-1),
                    NextState("WAIT-FOR-TRIGGER"),
                    NextValue(pass_count, pass_count+1)
                )
            )
        )

# BaseSoC ------------------------------------------------------------------------------------------
class BaseSoC(SoCCore):
    mem_map = {
        "adc_sram" : 0x30000000,
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, sys_clk_freq=int(50e6), x5_clk_freq=None,  toolchain="trellis", **kwargs):
        platform = ecp5_evn.Platform(toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on ECP5 Evaluation Board",
            ident_version  = True,
            integrated_main_ram_size=0x8000,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        crg = _CRG(platform, sys_clk_freq, x5_clk_freq)
        self.submodules.crg = crg

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = Cat(*[platform.request("user_led", i) for i in range(8)]),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

        # Wishbone DMA Burst Testing
        # block of SRAM of WB dma testing
        self.add_ram("adc_sram", self.mem_map["adc_sram"], 8*4*4096)

        self.submodules.dma_burst = Wishbone_DMA_Burst()
        self.add_csr("dma_burst")
        self.add_wb_master(self.dma_burst.wishbone)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on ECP5 Evaluation Board")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    parser.add_argument("--toolchain", default="trellis", help="Gateware toolchain to use, trellis (default) or diamond")
    builder_args(parser)
    soc_core_args(parser)
    parser.add_argument("--sys-clk-freq", default=60e6, help="System clock frequency (default=60MHz)")
    parser.add_argument("--x5-clk-freq",  type=int,     help="Use X5 oscillator as system clock at the specified frequency")
    args = parser.parse_args()

    soc = BaseSoC(toolchain=args.toolchain,
        sys_clk_freq = int(float(args.sys_clk_freq)),
        x5_clk_freq  = args.x5_clk_freq,
        **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".svf"))

if __name__ == "__main__":
    main()
