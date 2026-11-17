#include "stm32f303xc.h"
#include "uart.h"

void uart_init(void)
{
    // Enable the USART2 clock through APB1ENR.USART2EN.
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

    // Clear CR1.UE before configuring USART2.
    USART2->CR1 &= ~USART_CR1_UE;

    // Set BRR for approximately 230400 baud with a 24 MHz USART clock.
    USART2->BRR = 104;

    // Clear CR1.M to select 8 data bits.
    USART2->CR1 &= ~USART_CR1_M;

    // Clear CR1.PCE to disable parity.
    USART2->CR1 &= ~USART_CR1_PCE;

    // Clear CR2.STOP to select one stop bit.
    USART2->CR2 &= ~USART_CR2_STOP;

    // Set CR1.TE and CR1.RE to enable transmitter and receiver.
    USART2->CR1 |= USART_CR1_TE | USART_CR1_RE;

    // Set CR1.UE to enable USART2.
    USART2->CR1 |= USART_CR1_UE;
}

void uart_send_byte(uint8_t data)
{
    // Wait until USART_ISR.TXE says the transmit register is empty.
    while (!(USART2->ISR & USART_ISR_TXE));

    // Write the byte to USART2_TDR for transmission.
    USART2->TDR = data;
}

void uart_send_sample(uint16_t sample)
{
    // Send ADC bits 0–7 as the low byte.
    uart_send_byte((uint8_t)(sample & 0xFF));

    // Mark the high byte with 0xA0; its low nibble carries ADC bits 8–11.
    uart_send_byte((uint8_t)(0xA0 | ((sample >> 8) & 0x0F)));
}

// Send a readable decimal ADC value.
void uart_print_value(uint16_t value)
{
    char digits[5];
    int i = 0;

    if (value == 0)
    {
        uart_send_byte('0');
    }
    else
    {
        while (value > 0)
        {
            digits[i++] = (value % 10) + '0';
            value /= 10;
        }

        while (i > 0)
        {
            uart_send_byte(digits[--i]);
        }
    }

    uart_send_byte('\r');
    uart_send_byte('\n');
}