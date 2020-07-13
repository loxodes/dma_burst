#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>
#include <generated/mem.h>


static char *readstr(void)
{
	char c[2];
	static char s[64];
	static int ptr = 0;

	if(readchar_nonblock()) {
		c[0] = readchar();
		c[1] = 0;
		switch(c[0]) {
			case 0x7f:
			case 0x08:
				if(ptr > 0) {
					ptr--;
					putsnonl("\x08 \x08");
				}
				break;
			case 0x07:
				break;
			case '\r':
			case '\n':
				s[ptr] = 0x00;
				putsnonl("\n");
				ptr = 0;
				return s;
			default:
				if(ptr >= (sizeof(s) - 1))
					break;
				putsnonl(c);
				s[ptr] = c[0];
				ptr++;
				break;
		}
	}

	return NULL;
}

static char *get_token(char **str)
{
	char *c, *d;

	c = (char *)strchr(*str, ' ');
	if(c == NULL) {
		d = *str;
		*str = *str+strlen(*str);
		return d;
	}
	*c = 0;
	d = *str;
	*str = c+1;
	return d;
}

static void prompt(void)
{
	printf("RUNTIME>");
}

static void help(void)
{
	puts("Available commands:");
	puts("help                            - this command");
	puts("reboot                          - reboot CPU");
	puts("workaround                      - wishbone dma test with memory write workaround");
	puts("wishbone                        - wishbone dma test");
}

static void reboot(void)
{
  	ctrl_reset_write(1);
}



static void wishbone_test(void)
{
	flush_cpu_icache();
	flush_cpu_dcache();
	printf("wishbone burst test...\n");
	volatile unsigned int *dram_array = (unsigned int *)(ADC_SRAM_BASE);

	dma_burst_burst_size_write(64);
	dma_burst_base_write(ADC_SRAM_BASE);
	dma_burst_offset_write(0);

    dma_burst_start_write(1 << CSR_DMA_BURST_START_START_BURST_OFFSET);

	printf("waiting for ready!\n");
    while(!dma_burst_ready_read())
    {
    	;
    }

	printf("memory readback!\n");
	for(uint16_t i=0; i<64; i++) {
		printf("memory[%d]: %d\n", i, dram_array[i]);
	}
}

static void workaround_test(void)
{
	printf("wishbone burst test with workaround...\n");
	volatile uint32_t *dram_array = (unsigned int *)(MAIN_RAM_BASE);
	for(uint16_t i=0; i<64; i++) {
		if(dram_array[i] == 0)
		{
			;
		}
	}
	
	wishbone_test();
}


static void console_service(void)
{
	char *str;
	char *token;

	str = readstr();
	if(str == NULL) return;
	token = get_token(&str);
	if(strcmp(token, "help") == 0)
		help();
	else if(strcmp(token, "reboot") == 0)
		reboot();
	else if(strcmp(token, "workaround") == 0)
		workaround_test();
	else if(strcmp(token, "wishbone") == 0)
		wishbone_test();
	prompt();
}

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
	irq_setmask(0);
	irq_setie(1);
#endif
	uart_init();

	puts("\nCPU testing software built "__DATE__" "__TIME__"\n");
	help();
	prompt();

	while(1) {
		console_service();
	}

	return 0;
}
