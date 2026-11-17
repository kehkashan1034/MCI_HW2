
#include "stm32f303xc.h"

#include "clock.h"
#include "gpio.h"
#include "timer.h"
#include "adc.h"
#include "uart.h"
#include "pwm.h"

#define PWM_FREQUENCY_HZ 100U

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

    // Configure TIM3 for 100 Hz PWM
    pwm_init(PWM_FREQUENCY_HZ);

    // Start PWM generation
    pwm_start();

    // Start ADC
    adc_start();

    // Start sampling timer
    timer_start();

    while (1)
    {
        // Check if ADC samples are available
        if (adc_tail != adc_head)
        {
            // Read ADC sample
            uint16_t value = adc_buffer[adc_tail];

            // Move buffer position
            adc_tail = (adc_tail + 1) % BUFFER_SIZE;

            // Send each ADC sample as two bytes for plot.py
            uart_send_sample(value);
        }
    }
}
