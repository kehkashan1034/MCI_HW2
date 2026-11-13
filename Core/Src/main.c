
#include "stm32f303xc.h"

#include "clock.h"
#include "gpio.h"
#include "timer.h"
#include "adc.h"
#include "uart.h"

int main(void)
{
    // Configure system clock
    clock_init();

    // Configure GPIO pins
    gpio_init();

    // Configure UART
    uart_init();

    // Configure ADC
    adc_init();

    // Configure timer
    timer_init();

    // Start ADC
    adc_start();

    // Start sampling timer
    timer_start();

    uint16_t count = 0;

    while (1)
    {
        // Check if ADC samples are available
        if (adc_tail != adc_head)
        {
            // Read ADC sample
            uint16_t value = adc_buffer[adc_tail];

            // Move buffer position
            adc_tail = (adc_tail + 1) % BUFFER_SIZE;

            // Print every 100th sample
            count++;

            if (count >= 100)
            {
                uart_print_value(value);
                count = 0;
            }
        }
    }
}
