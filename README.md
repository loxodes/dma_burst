# Project to illustrate issue with wishbone writing to RAM.

Steps to replicate on an ECP5\_EVN:
1. Connect an ecp5\_evn eval board
1. Run 'make' in the firmware directory.
1. Run ecp5\_evn.py --load --build
1. Open up litex\_term, load firmware.bin (run term.sh)
1. Run the "wishbone" command, this will trigger the Wishbone\_DMA\_Burst module to write a value to the first 64 locations in ADC\_SRAM. The value written to memory should increment by 1 each time the command is run.
1. Run it again and note that memory locations after an offset of 15 are not reliably updated.
1. Run the "workaround" command, and see that all memory locations are updated.
The workaround function reads 64 locations from the MAIN\_RAM prior to triggering a burst write. 


# Solution
[Solved by Greg Davill](https://github.com/loxodes/dma\_burst/issues/), I needed to invalidate the CPU cache before accessing shared memory with the following:
```
flush_cpu_icache();
flush_cpu_dcache();
```

# Example Output
```
jtklein@aiur:~/repos/dma_burst$ ./term.sh 
[LXTERM] Starting....

        __   _ __      _  __
       / /  (_) /____ | |/_/
      / /__/ / __/ -_)>  <
     /____/_/\__/\__/_/|_|
   Build your hardware, easily!

 (c) Copyright 2012-2020 Enjoy-Digital
 (c) Copyright 2007-2015 M-Labs

 BIOS built on Jul 12 2020 13:19:21
 BIOS CRC passed (39bd1bc9)

 Migen git sha1: --------
 LiteX git sha1: e7646416

--=============== SoC ==================--
CPU:       VexRiscv @ 60MHz
BUS:       WISHBONE 32-bit @ 4GiB
CSR:       8-bit data
ROM:       32KiB
SRAM:      8KiB
MAIN-RAM:  32KiB

--============== Boot ==================--
Booting from serial...
Press Q or ESC to abort boot completely.
sL5DdSMmkekro
[LXTERM] Received firmware download request from the device.
[LXTERM] Uploading firmware/firmware.bin to 0x40000000 (8208 bytes)...
[LXTERM] Upload complete (3.7KB/s).
[LXTERM] Booting the device.
[LXTERM] Done.
Executing booted program at 0x40000000

--============= Liftoff! ===============--

CPU testing software built Jul 12 2020 13:33:27

Available commands:
help                            - this command
reboot                          - reboot CPU
workaround                      - wishbone dma test with memory write workaround
wishbone                        - wishbone dma test
RUNTIME>wishbone
wishbone burst test...
waiting for ready!
memory readback!
memory[0]: 0
memory[1]: 0
memory[2]: 0
memory[3]: 0
memory[4]: 0
memory[5]: 0
memory[6]: 0
memory[7]: 0
memory[8]: 0
memory[9]: 0
memory[10]: 0
memory[11]: 0
memory[12]: 0
memory[13]: 0
memory[14]: 0
memory[15]: 0
memory[16]: 0
memory[17]: 0
memory[18]: 0
memory[19]: 0
memory[20]: 0
memory[21]: 0
memory[22]: 0
memory[23]: 0
memory[24]: 0
memory[25]: 0
memory[26]: 0
memory[27]: 0
memory[28]: 0
memory[29]: 0
memory[30]: 0
memory[31]: 0
memory[32]: 0
memory[33]: 0
memory[34]: 0
memory[35]: 0
memory[36]: 0
memory[37]: 0
memory[38]: 0
memory[39]: 0
memory[40]: 0
memory[41]: 0
memory[42]: 0
memory[43]: 0
memory[44]: 0
memory[45]: 0
memory[46]: 0
memory[47]: 0
memory[48]: 0
memory[49]: 0
memory[50]: 0
memory[51]: 0
memory[52]: 0
memory[53]: 0
memory[54]: 0
memory[55]: 0
memory[56]: 0
memory[57]: 0
memory[58]: 0
memory[59]: 0
memory[60]: 0
memory[61]: 0
memory[62]: 0
memory[63]: 0
RUNTIME>wishbone
wishbone burst test...
waiting for ready!
memory readback!
memory[0]: 1
memory[1]: 1
memory[2]: 1
memory[3]: 1
memory[4]: 1
memory[5]: 1
memory[6]: 1
memory[7]: 1
memory[8]: 1
memory[9]: 1
memory[10]: 1
memory[11]: 1
memory[12]: 1
memory[13]: 1
memory[14]: 1
memory[15]: 1
memory[16]: 0
memory[17]: 0
memory[18]: 0
memory[19]: 0
memory[20]: 0
memory[21]: 0
memory[22]: 0
memory[23]: 0
memory[24]: 1
memory[25]: 1
memory[26]: 1
memory[27]: 1
memory[28]: 1
memory[29]: 1
memory[30]: 1
memory[31]: 1
memory[32]: 0
memory[33]: 0
memory[34]: 0
memory[35]: 0
memory[36]: 0
memory[37]: 0
memory[38]: 0
memory[39]: 0
memory[40]: 0
memory[41]: 0
memory[42]: 0
memory[43]: 0
memory[44]: 0
memory[45]: 0
memory[46]: 0
memory[47]: 0
memory[48]: 0
memory[49]: 0
memory[50]: 0
memory[51]: 0
memory[52]: 0
memory[53]: 0
memory[54]: 0
memory[55]: 0
memory[56]: 1
memory[57]: 1
memory[58]: 1
memory[59]: 1
memory[60]: 1
memory[61]: 1
memory[62]: 1
memory[63]: 1
RUNTIME>wishbone
wishbone burst test...
waiting for ready!
memory readback!
memory[0]: 2
memory[1]: 2
memory[2]: 2
memory[3]: 2
memory[4]: 2
memory[5]: 2
memory[6]: 2
memory[7]: 2
memory[8]: 2
memory[9]: 2
memory[10]: 2
memory[11]: 2
memory[12]: 2
memory[13]: 2
memory[14]: 2
memory[15]: 2
memory[16]: 0
memory[17]: 0
memory[18]: 0
memory[19]: 0
memory[20]: 0
memory[21]: 0
memory[22]: 0
memory[23]: 0
memory[24]: 2
memory[25]: 2
memory[26]: 2
memory[27]: 2
memory[28]: 2
memory[29]: 2
memory[30]: 2
memory[31]: 2
memory[32]: 0
memory[33]: 0
memory[34]: 0
memory[35]: 0
memory[36]: 0
memory[37]: 0
memory[38]: 0
memory[39]: 0
memory[40]: 0
memory[41]: 0
memory[42]: 0
memory[43]: 0
memory[44]: 0
memory[45]: 0
memory[46]: 0
memory[47]: 0
memory[48]: 0
memory[49]: 0
memory[50]: 0
memory[51]: 0
memory[52]: 0
memory[53]: 0
memory[54]: 0
memory[55]: 0
memory[56]: 2
memory[57]: 2
memory[58]: 2
memory[59]: 2
memory[60]: 2
memory[61]: 2
memory[62]: 2
memory[63]: 2
RUNTIME>workaround
wishbone burst test with workaround...
wishbone burst test...
waiting for ready!
memory readback!
memory[0]: 3
memory[1]: 3
memory[2]: 3
memory[3]: 3
memory[4]: 3
memory[5]: 3
memory[6]: 3
memory[7]: 3
memory[8]: 3
memory[9]: 3
memory[10]: 3
memory[11]: 3
memory[12]: 3
memory[13]: 3
memory[14]: 3
memory[15]: 3
memory[16]: 3
memory[17]: 3
memory[18]: 3
memory[19]: 3
memory[20]: 3
memory[21]: 3
memory[22]: 3
memory[23]: 3
memory[24]: 3
memory[25]: 3
memory[26]: 3
memory[27]: 3
memory[28]: 3
memory[29]: 3
memory[30]: 3
memory[31]: 3
memory[32]: 3
memory[33]: 3
memory[34]: 3
memory[35]: 3
memory[36]: 3
memory[37]: 3
memory[38]: 3
memory[39]: 3
memory[40]: 3
memory[41]: 3
memory[42]: 3
memory[43]: 3
memory[44]: 3
memory[45]: 3
memory[46]: 3
memory[47]: 3
memory[48]: 3
memory[49]: 3
memory[50]: 3
memory[51]: 3
memory[52]: 3
memory[53]: 3
memory[54]: 3
memory[55]: 3
memory[56]: 3
memory[57]: 3
memory[58]: 3
memory[59]: 3
memory[60]: 3
memory[61]: 3
memory[62]: 3
memory[63]: 3
RUNTIME>wishbone
wishbone burst test...
waiting for ready!
memory readback!
memory[0]: 4
memory[1]: 4
memory[2]: 4
memory[3]: 4
memory[4]: 4
memory[5]: 4
memory[6]: 4
memory[7]: 4
memory[8]: 4
memory[9]: 4
memory[10]: 4
memory[11]: 4
memory[12]: 4
memory[13]: 4
memory[14]: 4
memory[15]: 4
memory[16]: 3
memory[17]: 3
memory[18]: 3
memory[19]: 3
memory[20]: 3
memory[21]: 3
memory[22]: 3
memory[23]: 3
memory[24]: 3
memory[25]: 3
memory[26]: 3
memory[27]: 3
memory[28]: 3
memory[29]: 3
memory[30]: 3
memory[31]: 3
memory[32]: 4
memory[33]: 4
memory[34]: 4
memory[35]: 4
memory[36]: 4
memory[37]: 4
memory[38]: 4
memory[39]: 4
memory[40]: 3
memory[41]: 3
memory[42]: 3
memory[43]: 3
memory[44]: 3
memory[45]: 3
memory[46]: 3
memory[47]: 3
memory[48]: 3
memory[49]: 3
memory[50]: 3
memory[51]: 3
memory[52]: 3
memory[53]: 3
memory[54]: 3
memory[55]: 3
memory[56]: 4
memory[57]: 4
memory[58]: 4
memory[59]: 4
memory[60]: 4
memory[61]: 4
memory[62]: 4
memory[63]: 4
RUNTIME>
```
