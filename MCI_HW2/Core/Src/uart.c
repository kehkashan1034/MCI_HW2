#include "stm32f303xc.h"
#include "uart.h"

void uart_init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

    USART2->CR1 &= ~USART_CR1_UE;

    USART2->BRR = 104;

    USART2->CR1 &= ~USART_CR1_M;
    USART2->CR1 &= ~USART_CR1_PCE;
    USART2->CR2 &= ~USART_CR2_STOP;

    USART2->CR1 |= USART_CR1_TE | USART_CR1_RE;

    USART2->CR1 |= USART_CR1_UE;
}

void uart_send_byte(uint8_t data)
{
    while (!(USART2->ISR & USART_ISR_TXE));
    USART2->TDR = data;
}

void uart_send_sample(uint16_t sample)
{
    uart_send_byte((uint8_t)(sample & 0xFF));
    uart_send_byte((uint8_t)(sample >> 8));
}

// Send readable decimal ADC value
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