#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>

static void busy_wait(unsigned int ds)
{
	timer0_en_write(0);
	timer0_reload_write(0);
	timer0_load_write(SYSTEM_CLOCK_FREQUENCY/10000*ds);
	timer0_en_write(1);
	timer0_update_value_write(1);
	while(timer0_value_read()) timer0_update_value_write(1);
}


static char *readstr(void)
{
	char c[2];
	static char s[64];
	static unsigned int ptr = 0;

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
	printf("WUPYO>");
}

static void help(void)
{
	printf("Available commands:\n");
	printf("help                            - this command\n");
	printf("reboot                          - reboot CPU\n");
	printf("display                         - display test\n");
	printf("led                             - led test\n");
	printf("rgb                             - rgb test\n");
	printf("count                           - gpio inp counter\n");
}

static void reboot(void)
{
	asm("call r0");
}

static void display_test(void)
{

	printf("display_test yo...\n");

	for( unsigned int j=0; j<=0xffffffff; j++ )
	{		
		int x = j;
		for(int i=0; i<8; i++) {
			int y = x&0xf;
			display_sel_write(7-i);
			display_value_write(y);
			display_write_write(100);
			x >>= 4;
		}
	}
}

static void led_test(void)
{
	printf("led_test yo...\n");
	for( int j=0; j<10; j++ )
		for(int i=0; i<65536; i++) {
			leds_out_write(i);
			busy_wait(1);
		}
}

static void count(void)
{
	bool prev[8] = { false,false,false,false, false,false,false,false };
	unsigned int num_changes[8] = {0,0,0,0, 0,0,0,0};

	while(true)
	{
		/////////////////////////////////
		// reload 1 second on countdown timer
		/////////////////////////////////

		timer0_en_write(0);
		timer0_reload_write(0);
		timer0_load_write(SYSTEM_CLOCK_FREQUENCY); // 1HZ
		timer0_en_write(1);
		timer0_update_value_write(1);

		/////////////////////////////////
		// until 1 second...
		/////////////////////////////////

		while(timer0_value_read()){

			timer0_update_value_write(1);

			/////////////////////////////////
			// count bit changes 
			/////////////////////////////////

			char ch = counter_in_read();

			for( int i=0; i<8; i++ )
			{
				bool bit = ch&(1<<i);

				if( bit != prev[i] )
					(num_changes[i])++;

				prev[i] = bit;

			}
		}

		/////////////////////////////////
		// report..
		/////////////////////////////////

		printf( "////////////////\n");
		printf( "// change report\n");
		printf( "////////////////\n");

		for( int i=0; i<8; i++ ){
			printf( "changes/sec bit<%d> -> <%d>\n", i, num_changes[i] );
			num_changes[i] = 0;
		}

		printf( "\n");
	}
}

static void rgb_test(void)
{
	rgbled_r_enable_write(1);
	rgbled_g_enable_write(1);
	rgbled_b_enable_write(1);

	rgbled_r_period_write(256);
	rgbled_g_period_write(256);
	rgbled_b_period_write(256);

	auto l = [](int i){
		rgbled_r_width_write( (i>>14) & 0xff);
		rgbled_g_width_write( (i>>15) & 0xff);
		rgbled_b_width_write( (i>>20) & 0xff);
	};

	for( int i=0; i<(1<<26); i++ )
		l(i);

	rgbled_r_enable_write(0);
	rgbled_g_enable_write(0);
	rgbled_b_enable_write(0);
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
	else if(strcmp(token, "display") == 0)
		display_test();
	else if(strcmp(token, "led") == 0)
		led_test();
	else if(strcmp(token, "rgb") == 0)
		rgb_test();
	else if(strcmp(token, "count") == 0)
		count();

	prompt();
}

int main(void)
{
	irq_setmask(0);
	irq_setie(1);
	uart_init();

	printf("\nLab004 - CPU testing software built " __DATE__ " " __TIME__ "\n");
	help();
	prompt();



	while(1) {
		console_service();
	}

	return 0;
}
